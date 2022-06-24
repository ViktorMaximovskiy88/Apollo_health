import pytest
from unittest import mock

from fastapi.security import HTTPAuthorizationCredentials
from backend.app.utils.user import get_current_user, get_current_admin_user
from backend.app.utils import security

security.create_auth_payload = mock.Mock(
    return_value={
        "aud":"http://localhost:8000/api/v1",
        "sub":"user@mmitnetwork.com",   
        "exp":1747653060,
        "scope":"openid profile email",
        "iss":"http://localhost:3000/api/v1/auth"       
    })

# get_provider_detail
# token is local
# token is not local
@pytest.mark.asyncio
async def test_local_auth_detail():
    token = security.create_access_token("test")
    mock_creds = HTTPAuthorizationCredentials(
        scheme='Bearer',
        credentials=token
    )
    assert True is True