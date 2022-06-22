import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from backend.app.utils.security import verify_password
from backend.common.models.user import User, UserAuth
from backend.app.core.settings import settings
from backend.app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/authorize")
async def login_access_token(
    model: UserAuth
):
    email = model.email
    user = await User.by_email(email)

    if not user:
        logging.error(f"User not found: email={email}")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not verify_password(model.password, user.hashed_password):
        logging.error(f"User password incorrect: email={email}")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user.disabled:
        logging.error(f"User account disabled: email={email}")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        user.email,
        scopes=[],
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token}
