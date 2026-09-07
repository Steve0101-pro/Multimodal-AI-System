from datetime import datetime
from datetime import timedelta
from datetime import timezone

import uuid

from jose import jwt
from passlib.context import CryptContext

from app.config import settings



pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto",)


def hash_password(password: str,) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password or not password_hash:
        return False
    try:
        return pwd_context.verify(password, password_hash)
    except (TypeError, ValueError):
        return False


def create_access_token(user_id: uuid.UUID,role: str,) -> str:

    expires_at = (datetime.now(timezone.utc)+ timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expires_at,}

    return jwt.encode(payload,settings.JWT_SECRET_KEY.get_secret_value(),algorithm=settings.JWT_ALGORITHM,)


def decode_access_token(token: str,) -> dict:
    return jwt.decode(token,settings.JWT_SECRET_KEY.get_secret_value(),algorithms=[settings.JWT_ALGORITHM],)