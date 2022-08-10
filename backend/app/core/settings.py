from pydantic import AnyUrl, BaseSettings, Field, HttpUrl, RedisDsn

from backend.common.core.config import env_type, load_dotenv

load_dotenv(env_type)


class ReactApp(BaseSettings):
    auth0_domain: HttpUrl = Field(env="REACT_APP_AUTH0_DOMAIN")
    auth0_client_id: str = Field(env="REACT_APP_AUTH0_CLIENT_ID")
    auth0_audience: str = Field(env="REACT_APP_AUTH0_AUDIENCE")


class Auth0Settings(BaseSettings):
    wellknown_url: HttpUrl = Field(env="AUTH0_WELLKNOWN_URL")
    audience: str = Field(env="AUTH0_AUDIENCE")
    issuer: str = Field(env="AUTH0_ISSUER")
    email_key: str = Field(default="https://mmit.com/email")
    grant_key: str = Field(default="gty")
    user_info_url: str = Field(default="https://mmit-test.auth0.com/userinfo")


class Settings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int

    auth0: Auth0Settings = Auth0Settings()
    frontend: ReactApp = ReactApp()

    is_local: bool = env_type == "local"
    env_type: str = env_type

    mongo_url: AnyUrl
    mongo_db: str
    mongo_user: str
    mongo_password: str

    aws_region: str | None
    aws_access_key_id: str | None
    aws_secret_access_key: str | None

    s3_endpoint_url: str
    s3_document_bucket: str

    redis_url: RedisDsn
    redis_password: str

    disable_proxies: bool = False

    disable_scrape_scheduling: bool = False


settings = Settings()

if settings.is_local:
    print(f"Env Loaded:\n\n {settings}\n\n")
