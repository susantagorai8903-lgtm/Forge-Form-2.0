from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Forge & Form Personal Training"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/forgeform"
    jwt_secret_key: str = "development-only-replace-this-secret-key"
    jwt_access_token_expire_minutes: int = Field(default=15, gt=0)
    jwt_refresh_token_expire_days: int = Field(default=14, gt=0)
    frontend_url: str = "http://localhost:3000"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    kafka_bootstrap_servers: str = ""
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    kafka_consumer_group_id: str = "forgeform-workers"
    email_provider: str = "console"
    email_api_key: str = ""
    email_from_address: str = ""
    business_email: str = "training@forgeandform.com"
    business_phone: str = "(503) 555-0139"
    business_address: str = "1900 Division Street, Portland, OR 97202"
    booking_timezone: str = "America/Los_Angeles"
    booking_capacity_per_slot: int = Field(default=0, ge=0)
    max_request_bytes: int = Field(default=65536, gt=0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url")
    @classmethod
    def require_async_database_driver(cls, value: str) -> str:
        url = make_url(value)
        if url.drivername in {"postgres", "postgresql"}:
            url = url.set(drivername="postgresql+asyncpg")
        query = dict(url.query)
        sslmode = query.pop("sslmode", None)
        if sslmode and "ssl" not in query:
            query["ssl"] = sslmode
        return url.set(query=query).render_as_string(hide_password=False)

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env == "production":
            if len(self.jwt_secret_key) < 32 or self.jwt_secret_key.startswith(("development-only", "replace-with")):
                raise ValueError("Production requires a strong, unique JWT_SECRET_KEY")
            if "*" in self.cors_origins:
                raise ValueError("Production CORS_ORIGINS must not contain a wildcard")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
