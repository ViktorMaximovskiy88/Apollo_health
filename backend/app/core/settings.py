from pprint import pprint

from pydantic import AnyUrl, BaseSettings, Field, HttpUrl, RedisDsn

from backend.common.core.config import env_type, load_dotenv

load_dotenv(env_type)


class ReactApp(BaseSettings):
    auth0_domain: HttpUrl = Field(default=None, env="REACT_APP_AUTH0_DOMAIN")
    auth0_client_id: str = Field(default=None, env="REACT_APP_AUTH0_CLIENT_ID")
    auth0_audience: str = Field(default=None, env="REACT_APP_AUTH0_AUDIENCE")


class Auth0Settings(BaseSettings):
    wellknown_url: HttpUrl = Field(default=None, env="AUTH0_WELLKNOWN_URL")
    audience: str = Field(default=None, env="AUTH0_AUDIENCE")
    issuer: str = Field(default=None, env="AUTH0_ISSUER")
    email_key: str = Field(default="https://mmit.com/email")
    grant_key: str = Field(default="gty")
    userinfo_url: str = Field(default=None, env="AUTH0_USERINFO_URL")


class FormularyNavigator(BaseSettings):
    formulary_navigator_username: str = Field(default=None, env="FORMULARY_NAVIGATOR_USERNAME")
    formulary_navigator_password: str = Field(default=None, env="FORMULARY_NAVIGATOR_PASSWORD")


class Settings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int

    auth0: Auth0Settings = Auth0Settings()
    frontend: ReactApp = ReactApp()

    is_local: bool = env_type == "local"
    env_type: str = env_type

    mongo_url: AnyUrl
    mongo_db: str
    mongo_user: str | None
    mongo_password: str | None

    aws_region: str | None
    aws_access_key_id: str | None
    aws_secret_access_key: str | None

    s3_endpoint_url: str
    s3_document_bucket: str

    task_worker_queue_url: str | None

    redis_url: RedisDsn
    redis_password: str

    formulary_navigator: FormularyNavigator = FormularyNavigator()

    disable_proxies: bool = False
    log_level: str = "INFO"

    disable_scrape_scheduling: bool = False
    debug: bool = Field(default=False, env="DEBUG")


settings = Settings()

if settings.is_local:
    pprint(f"Env Loaded: {settings}")
