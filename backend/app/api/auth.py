from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import create_magic_link_token, create_access_token, verify_token, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.magic_link import MagicLink
from app.schemas.user import MagicLinkRequest, MagicLinkVerify, TokenResponse, UserResponse
from app.services.resend_client import send_magic_link_email

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/request-magic-link", status_code=status.HTTP_200_OK)
async def request_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(email=request.email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    token = create_magic_link_token(request.email)
    
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)
    
    magic_link = MagicLink(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(magic_link)
    await db.commit()
    
    await send_magic_link_email(request.email, token)
    
    return {"message": "Magic link sent to your email"}


@router.post("/verify-magic-link", response_model=TokenResponse)
async def verify_magic_link(
    request: MagicLinkVerify,
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(request.token)
    
    if payload.get("type") != "magic_link":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    result = await db.execute(
        select(MagicLink).where(MagicLink.token == request.token)
    )
    magic_link = result.scalar_one_or_none()
    
    if not magic_link or magic_link.used:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or used magic link"
        )
    
    if datetime.now(timezone.utc) > magic_link.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Magic link expired"
        )
    
    result = await db.execute(
        select(User).where(User.email == payload.get("sub"))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user.is_verified = True
    user.last_login = datetime.now(timezone.utc)
    magic_link.used = True
    
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)
