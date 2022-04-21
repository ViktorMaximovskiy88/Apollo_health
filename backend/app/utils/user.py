from fastapi import Cookie, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError
from backend.app.core.settings import settings
from backend.common.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

ALGORITHM = "HS256"


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


async def get_current_user(token: str | None = Depends(get_token)):
    try:
        payload = jwt.decode(token, str(settings.secret_key), algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    email = payload.get("sub")
    user = await User.by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorized user could not be found",
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is disabled"
        )
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User is not admin")
    return current_user
