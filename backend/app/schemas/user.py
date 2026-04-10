from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Any


class DeviceInfo(BaseModel):
    user_agent: str | None = None
    platform: str | None = None
    language: str | None = None
    screen_resolution: str | None = None
    timezone: str | None = None


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    email: str
    is_verified: bool
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerify(BaseModel):
    token: str
    device_info: DeviceInfo | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SessionInfo(BaseModel):
    id: UUID
    device_info: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class SessionsResponse(BaseModel):
    sessions: list[SessionInfo]
    current_session_id: UUID | None


class RevokeSessionRequest(BaseModel):
    session_id: UUID


class LogoutRequest(BaseModel):
    refresh_token: str
