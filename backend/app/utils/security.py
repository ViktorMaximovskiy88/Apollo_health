import jwt
from datetime import datetime, timedelta
from typing import Any, Union, List
from passlib.context import CryptContext
from backend.app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta,
    scopes: List[str] = [],
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {
        "aud": settings.auth0.audience,
        "exp": expire,
        "sub": str(subject),
        "scope": " ".join(scopes)
    }

    encoded_jwt = jwt.encode(
        to_encode,
        str(settings.secret_key),
        algorithm=ALGORITHM,
        headers={"kid": "local"},
    )

    return encoded_jwt


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
