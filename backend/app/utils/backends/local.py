import jwt

from fastapi import Header, status, HTTPException, Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from backend.app.core.settings import settings
from backend.common.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

class LocalBackend(object):
    def get_signing_key(self) -> str:
        return settings.secret_key

    def authenticate(
        self,
        authorization: str,
    ) -> dict:
        token = authorization

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        signing_key = self.get_signing_key()
        payload = None

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=settings.auth0.audience,
                issuer=settings.auth0.issuer,
            )
        except:
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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return payload

    async def get_current_user(
        self,
        security_scopes: SecurityScopes = SecurityScopes(scopes=[]),
        authorization: str = Depends(oauth2_scheme),
    ) -> User:
        print(authorization)
        # load user from DB
        payload = self.authenticate(authorization)
        self.authorize(payload, security_scopes)

        user = await User.by_email(payload["email"])

        return user