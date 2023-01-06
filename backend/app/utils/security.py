from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext

from backend.app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_auth_payload(
    sub: str,
    aud: str,
    exp: int,
    scope: str,
    iss: str,
):
    payload = {
        "iss": iss,
        "aud": aud,
        "exp": exp,
        "sub": sub,
        "scope": scope,
    }
    payload[settings.auth0.email_key] = sub
    return payload


def create_access_token(
    subject: Union[str, Any],
    scopes: list[str] = [],
) -> str:

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    payload = create_auth_payload(
        aud=settings.auth0.audience,
        exp=expire,
        sub=str(subject),
        iss=settings.auth0.issuer,
        scope=" ".join(scopes),
    )

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
        headers={"kid": "local"},
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return (
        plain_password and hashed_password and pwd_context.verify(plain_password, hashed_password)
    )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
