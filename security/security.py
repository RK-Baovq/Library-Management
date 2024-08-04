from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Any
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import APIKeyHeader
from fastapi import HTTPException, status
from database.db import SessionLocal
from constants import target


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Authorization = APIKeyHeader(name="Authorization", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def check_authenticated(authorization: str):
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chua dung dang token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return param


def get_token(user) -> Any:
    expiration_time = datetime.now() + timedelta(seconds=3600 * 24)
    to_encode = {
        "exp": expiration_time,
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
    encoded_token = jwt.encode(to_encode, target.SECRET_KEY, target.ALGORITHM)
    return encoded_token


def load_token(authorization: str):
    try:
        token = check_authenticated(authorization)
        payload = jwt.decode(token, target.SECRET_KEY, target.ALGORITHM)
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token hết hạn"
            )
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED"
        )
    return payload
