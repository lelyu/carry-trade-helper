import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import (
    create_magic_link_token,
    create_access_token,
    verify_token,
    get_current_user,
)
from app.core.config import settings
from app.core.tokens import (
    create_refresh_jwt,
    decode_refresh_jwt,
    hash_token,
    get_token_expiry,
    verify_token as verify_token_hash,
)
from app.models.user import User
from app.models.magic_link import MagicLink
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    MagicLinkRequest,
    MagicLinkVerify,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    SessionsResponse,
    SessionInfo,
    RevokeSessionRequest,
    LogoutRequest,
)
from app.services.resend_client import send_magic_link_email

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/request-magic-link", status_code=status.HTTP_200_OK)
async def request_magic_link(
    request: MagicLinkRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=request.email)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_magic_link_token(request.email)

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.MAGIC_LINK_EXPIRE_MINUTES
    )

    magic_link = MagicLink(user_id=user.id, token=token, expires_at=expires_at)
    db.add(magic_link)
    await db.commit()

    await send_magic_link_email(request.email, token)

    return {"message": "Magic link sent to your email"}


@router.post("/verify-magic-link", response_model=TokenResponse)
async def verify_magic_link(
    request: MagicLinkVerify,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = verify_token(request.token)

    match payload.get("type"):
        case "magic_link":
            pass
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

    result = await db.execute(select(MagicLink).where(MagicLink.token == request.token))
    magic_link = result.scalar_one_or_none()

    if not magic_link or magic_link.used:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or used magic link",
        )

    if datetime.now(timezone.utc) > magic_link.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Magic link expired"
        )

    result = await db.execute(select(User).where(User.email == payload.get("sub")))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    user.is_verified = True
    user.last_login = datetime.now(timezone.utc)
    magic_link.used = True

    jti = uuid.uuid4()
    refresh_token_jwt = create_refresh_jwt(user.email, jti)
    refresh_token_hash = hash_token(refresh_token_jwt)

    device_info_dict = None
    if request.device_info:
        device_info_dict = request.device_info.model_dump()

    client_host = http_request.client.host if http_request.client else None
    user_agent_header = http_request.headers.get("user-agent", None)
    if user_agent_header and len(user_agent_header) > 500:
        user_agent_header = user_agent_header[:500]

    db_refresh_token = RefreshToken(
        jti=jti,
        user_id=user.id,
        token_hash=refresh_token_hash,
        device_info=device_info_dict,
        ip_address=client_host,
        user_agent=user_agent_header,
        expires_at=get_token_expiry(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        last_used_at=datetime.now(timezone.utc),
    )
    db.add(db_refresh_token)

    await db.commit()

    access_token = create_access_token(data={"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_jwt,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_refresh_jwt(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    jti = uuid.UUID(payload.get("jti"))

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.revoked.is_(False),
        )
    )
    refresh_token = result.scalar_one_or_none()

    if (
        not refresh_token
        or not verify_token_hash(request.refresh_token, refresh_token.token_hash)
        or datetime.now(timezone.utc) > refresh_token.expires_at
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    result = await db.execute(select(User).where(User.id == refresh_token.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    refresh_token.revoked = True

    new_jti = uuid.uuid4()
    new_refresh_token_jwt = create_refresh_jwt(user.email, new_jti)
    new_refresh_token_hash = hash_token(new_refresh_token_jwt)

    client_host = http_request.client.host if http_request.client else None
    user_agent_header = http_request.headers.get("user-agent", None)
    if user_agent_header and len(user_agent_header) > 500:
        user_agent_header = user_agent_header[:500]

    new_refresh_token = RefreshToken(
        jti=new_jti,
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        device_info=refresh_token.device_info,
        ip_address=client_host,
        user_agent=user_agent_header,
        expires_at=get_token_expiry(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        last_used_at=datetime.now(timezone.utc),
    )
    db.add(new_refresh_token)

    await db.commit()

    access_token = create_access_token(data={"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token_jwt,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_refresh_jwt(request.refresh_token)
    if not payload:
        return None

    jti = uuid.UUID(payload.get("jti"))

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.user_id == current_user.id,
        )
    )
    token = result.scalar_one_or_none()

    if token:
        token.revoked = True
        await db.commit()

    return None


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id)
        .values(revoked=True)
    )
    await db.commit()

    return None


@router.get("/sessions", response_model=SessionsResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked.is_(False),
        )
        .order_by(RefreshToken.last_used_at.desc())
    )
    sessions = result.scalars().all()

    session_infos = [
        SessionInfo(
            id=session.id,
            device_info=session.device_info,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            created_at=session.created_at,
            last_used_at=session.last_used_at,
            expires_at=session.expires_at,
            is_current=False,
        )
        for session in sessions
    ]

    return SessionsResponse(sessions=session_infos, current_session_id=None)


@router.post("/revoke-session", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    request: RevokeSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.id == request.session_id,
            RefreshToken.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session.revoked = True
    await db.commit()

    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
