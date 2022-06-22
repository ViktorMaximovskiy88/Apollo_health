from auth0.v3.management import Auth0
from backend.app.core.settings import settings
from auth0.v3.authentication import GetToken
from typing import List

roles = {
    "Admin": "rol_kRjUyJ4sup90w0Ha"
}

#TODO add caching
def get_management_token():
    token = GetToken(settings.auth0.domain).client_credentials(
        settings.auth0.client_id,
        settings.auth0.client_secret,
        f"https://{settings.auth0.domain}/api/v2/",
    )
    return token['access_token']

def management_api():
    token = get_management_token()
    auth0 = Auth0(settings.auth0.domain, token)
    return auth0


def create_user(email: str, password: str, first_name: str, last_name: str):
    api = management_api()
    payload = {
        "email": email,
        "given_name": first_name,
        "family_name": last_name,
        "name": f"{first_name} {last_name}",
        "connection": "Username-Password-Authentication",
        "password": password,
    }

    user_result = api.users.create(payload)
    api.users.add_roles(user_result["user_id"], [roles["Admin"]])
    
    return user_result
    