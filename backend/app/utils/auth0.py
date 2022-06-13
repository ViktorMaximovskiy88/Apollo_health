import jwt

from fastapi import Header, status, HTTPException
from fastapi.security import SecurityScopes

# todo move config to env
class Auth0(object):
    def __init__(self):
        self.jwks_client = jwt.PyJWKClient(
            f"https://mmit-test.auth0.com/.well-known/jwks.json",
            cache_keys=True,
        )

    def get_bearer_token(self, authorization: str) -> str:
        return authorization.split(" ")[1]


    def get_current_user(
        self,
        security_scopes: SecurityScopes,        
        authorization: str = Header(default=""),
    ) -> dict:
        token = self.get_bearer_token(authorization)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        signing_key = self.jwks_client.get_signing_key_from_jwt(token).key        

        # todo error handling
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=f"http://localhost:8000/api/v1",
            issuer=f"https://mmit-test.auth0.com/",
        )

        user_scopes = set(payload['scope'].split(" "))
        required_scopes = set(security_scopes.scopes)

        has_valid_scopes = required_scopes.issubset(user_scopes)

        if not has_valid_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN
            )

        return payload

# convenience for now ...
# check .. is this a singleton or nah...? 
auth0 = Auth0()
