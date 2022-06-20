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


# key, aud, email key name
def get_provider_detail(token: str):
    header = jwt.get_unverified_header(token)
    if 'kid' in header:
        return (jwks_client.get_signing_key_from_jwt(token).key, header['alg'], "email", settings.auth0.audience)
    else:
        return (str(settings.secret_key), header['alg'], "sub", "local")

async def get_current_user(token: str | None = Depends(get_token)):
    try:
        [signing_key, algorithm, email_key, audience] = get_provider_detail(token)
        payload = jwt.decode(token, signing_key, algorithms=[algorithm], audience=audience)
    except Exception as ex:
        logging.error(ex)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    email = payload.get(email_key)
    
    #TODO remove when auth0 returns this to us ....
    email = "admin@mmitnetwork.com"

    user = await User.by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorized user could not be found",
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled"
        )

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is not admin")
    return current_user
