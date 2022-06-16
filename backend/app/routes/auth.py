from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from backend.app.utils.security import verify_password
from backend.common.models.user import User, UserAuth
from backend.app.core.settings import settings
from backend.app.utils.security import create_access_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])


def raise_or_redirect(redirect, email, error):
    if redirect:
        return RedirectResponse(
            f"/login?email={email}&error={error}", status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


@router.post("/login")
async def login_access_token(
    model: UserAuth,
    redirect: str | None = Query(default=None),
):

    user = await User.by_email(model.email)

    if not user or not verify_password(model.password, user.hashed_password):
        return raise_or_redirect(redirect, model.email, "invalid")
    elif user.disabled:
        return raise_or_redirect(redirect, model.email, "disabled")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        user.email,
        scopes=[],
        expires_delta=access_token_expires,
    )

    if redirect:
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, samesite="strict"
        )
        return response
    else:
        return {"access_token": access_token}
