import jwt
import logging

from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from backend.app.core.settings import settings
from backend.common.models.user import User

scheme = HTTPBearer(auto_error=False)

jwks_client = jwt.PyJWKClient(
    settings.auth0.wellknown_url,
    cache_keys=True,
)

# key, alg
def get_provider_detail(token: str):
    header = jwt.get_unverified_header(token)
    if 'kid' in header and header['kid'] == 'local':
        return (str(settings.secret_key), header['alg'])
    else:
        return (jwks_client.get_signing_key_from_jwt(token).key, header['alg'])

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(scheme)) -> User:
    
    try:
        token = auth.credentials
        email_key = settings.auth0.email_key
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

    # local only for now until we decide on user mgmt
    if settings.is_local and not user:
        user = User(
            email=email,
            full_name=email.partition("@")[0],
            is_admin=True,
            hashed_password="",
        )
        await user.save()

    if not user:
        logging.error(f"User not found: email={email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user.disabled:
        logging.error(f"User account disabled: email={email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # check perms

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is not admin")
    return current_user
