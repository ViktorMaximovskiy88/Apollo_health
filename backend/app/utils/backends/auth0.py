import jwt

from fastapi import Header, status, HTTPException, Depends
from fastapi.security import SecurityScopes, OAuth2
from backend.app.core.settings import settings
from backend.common.models.user import User

oauth2_scheme = OAuth2()

class Auth0Backend(object):
    def __init__(self):
        self.jwks_client = jwt.PyJWKClient(
            settings.auth0.wellknown_url,
            cache_keys=True,
        )

    def get_bearer_token(self, authorization: str) -> str:
        return authorization.split(" ")[1]

    def get_signing_key(self, token: str) -> str:
        return self.jwks_client.get_signing_key_from_jwt(token).key

    def authenticate(
        self,
        authorization: str,
    ) -> dict:
        token = self.get_bearer_token(authorization)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        signing_key = self.get_signing_key(token)

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
        user_scopes = set(payload["scopes"])
        required_scopes = set(security_scopes.scopes)

        has_valid_scopes = required_scopes.issubset(user_scopes)

        if not has_valid_scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return payload

    async def get_current_user(
        self,
        security_scopes: SecurityScopes = SecurityScopes(scopes=["email"]),
        authorization: str = Depends(oauth2_scheme),
    ) -> User:
        
        # load user from DB
        payload = self.authenticate(authorization)
        self.authorize(payload, security_scopes)
        # temp until auth0 is updated
        payload["email"] = "admin@mmitnetwork.com"
        user = await User.by_email(payload["email"])

        return user
