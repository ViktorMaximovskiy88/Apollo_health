import jwt
import logging

from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from backend.app.core.settings import settings
from backend.common.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

jwks_client = jwt.PyJWKClient(
    settings.auth0.wellknown_url,
    cache_keys=True,
)

def get_token_from_request(request: Request) -> str | None:
    cookie_token = request.cookies.get("access_token")
    bearer_token = request.headers.get("Authorization", "").split(" ")[-1]
    return cookie_token or bearer_token


def get_cookie_token(request: Request):
    cookie_token = request.cookies.get("access_token")
    return cookie_token


def get_token(
    bearer_token: str | None = Depends(oauth2_scheme),
    cookie_token: str | None = Depends(get_cookie_token),
):
    return bearer_token or cookie_token


# key, alg
def get_provider_detail(token: str):
    header = jwt.get_unverified_header(token)
    if 'kid' in header and header['kid'] == 'local':
        return (str(settings.secret_key), header['alg'])
    else:
        return (jwks_client.get_signing_key_from_jwt(token).key, header['alg'])


async def get_current_user(token: str = Depends(get_token)):
    try:
        email_key = "http://mmit.com/email"
        audience = settings.auth0.audience
        [signing_key, algorithm] = get_provider_detail(token)
        payload = jwt.decode(token, signing_key, algorithms=[algorithm], audience=audience)
    except Exception as ex:
        logging.error(ex)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    email = payload.get(email_key)
    user = await User.by_email(email)

    if not user:
        logging.error(f"User not found: email={email}")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user.disabled:
        logging.error(f"User account disabled: email={email}")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # check perms

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is not admin")
    return current_user
