from pydantic import BaseSettings, HttpUrl, Field, AnyUrl, RedisDsn
from backend.common.core.config import load_dotenv, env_type

load_dotenv(env_type)

class Auth0Settings(BaseSettings):
    wellknown_url: HttpUrl = Field(env='auth0_wellknown_url')
    audience: str = Field(env='auth0_audience')
    issuer: str = Field(env='auth0_issuer')
    email_key: str = Field(default='https://mmit.com/email')

class Settings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int

    auth0: Auth0Settings = Auth0Settings()

    is_local: bool = env_type == "local"
    env_type: str = env_type

    mongo_url: AnyUrl
    mongo_db: str
    mongo_user: str
    mongo_password: str
    
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    
    s3_endpoint_url: str
    s3_document_bucket: str
    
    redis_url: RedisDsn
    redis_password: str
    
    disable_proxies: bool

settings = Settings()

if settings.is_local:
    print(f"Env Loaded:\n\n {settings}\n\n")
