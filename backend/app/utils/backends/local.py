import logging
import jwt

from fastapi import Header, status, HTTPException, Depends
from fastapi.security import SecurityScopes, HTTPBearer
from backend.app.core.settings import settings
from backend.common.models.user import User
from pydantic import EmailStr, BaseModel



oauth2_scheme = HTTPBearer()

class LocalBackend(object):
    def get_signing_key(self) -> str:
        return settings.secret_key

    def authenticate(
        self,
        authorization: str,
    ) -> dict:

        token = authorization.credentials

        if not token:
            logging.error("Missing authorization header token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        signing_key = self.get_signing_key()
        payload = None

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["HS256"],
            )
        except Exception as ex:
            logging.error(ex)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        payload["scopes"] = payload["scope"].split(" ")
        return payload

    def authorize(self, payload: dict, security_scopes: SecurityScopes):
        # todo error handling
        user_scopes = set(payload["scopes"])
        required_scopes = set(security_scopes.scopes)

        has_valid_scopes = required_scopes.issubset(user_scopes)
        if not has_valid_scopes:
            logging.error("User is missing the reuqired scopes")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return payload

    async def get_current_user(
        self,
        security_scopes: SecurityScopes = SecurityScopes(scopes=[]),
        authorization: str = Depends(oauth2_scheme),
    ) -> User:
        # load user from DB
        payload = self.authenticate(authorization)
        self.authorize(payload, security_scopes)

        user = await User.by_email(payload["sub"])
        return user

class LocalUserLoginSchema(BaseModel):
    username: EmailStr
    password: str        