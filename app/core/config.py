from typing import List, Optional, Annotated, Union

from pydantic import AnyHttpUrl, PostgresDsn, AmqpDsn, EmailStr, RedisDsn, field_validator, UrlConstraints
from pydantic_core import Url
from pydantic_settings import BaseSettings

# SQLAlchemy doesn't support other schemes than postgresql://
StrictPostgresDsn = Annotated[PostgresDsn, UrlConstraints(allowed_schemes=['postgresql'])]

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # Server
    SERVER_NAME: str = "almanach-api"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"

    # Environment
    ENVIRONMENT: str = "development"

    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        if v not in ["development", "production"]:
            raise ValueError("ENVIRONMENT must be 'development' or 'production'")
        return v

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # Database
    POSTGRES_DSN: StrictPostgresDsn

    # Message Broker
    BROKER_DSN: Union[AmqpDsn, RedisDsn]

    # Contact
    CONTACT_EMAIL: Optional[EmailStr] = None
    CONTACT_NAME: Optional[str] = None


settings = Settings()
