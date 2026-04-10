import uuid
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return pwd_context.hash(token)


def verify_token(plain_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token, hashed_token)


def is_token_expired(expires_at: datetime) -> bool:
    return datetime.now(timezone.utc) > expires_at


def get_token_expiry(days: int = 14) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def create_refresh_jwt(user_email: str, jti: uuid.UUID) -> str:
    payload = {
        "sub": user_email,
        "jti": str(jti),
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_refresh_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
