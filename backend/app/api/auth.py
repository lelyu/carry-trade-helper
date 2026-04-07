from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.core.security import create_magic_link_token, create_access_token, verify_token
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
    
    magic_link = MagicLink(
        user_id=user.id,
        token=token
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
    
    if datetime.utcnow() > magic_link.expires_at:
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
    user.last_login = datetime.utcnow()
    magic_link.used = True
    
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(lambda: None)
):
    from app.core.security import get_current_user
    return UserResponse.from_orm(current_user)