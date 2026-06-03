from functools import lru_cache

from pydantic import Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Banco de dados ───────────────────────────────────────────────────────
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="postgresql://user:pass@host:port/db",
    )
    DB_POOL_SIZE: int = Field(10, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(20, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(30, ge=5)
    DB_POOL_RECYCLE: int = Field(1800, ge=60)
    DB_ECHO: bool = Field(False)

    # ─── JWT ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field("HS256", pattern=r"^(HS256|HS384|HS512|RS256)$")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, ge=1, le=10080)

    # ─── Aplicação ────────────────────────────────────────────────────────────
    ENVIRONMENT: str = Field(
        "development",
        pattern=r"^(development|staging|production)$",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_placeholder(cls, v: str) -> str:
        forbidden = {"changeme", "secret", "troque", "example", "test", "substitua"}
        if any(word in v.lower() for word in forbidden):
            raise ValueError(
                "SECRET_KEY parece ser um placeholder. "
                "Gere uma chave real com: openssl rand -hex 32"
            )
        return v

    @model_validator(mode="after")
    def no_db_echo_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.DB_ECHO:
            raise ValueError(
                "DB_ECHO=true não é permitido em produção — vaza SQL nos logs."
            )
        return self

    @property
    def DATABASE_URL_str(self) -> str:
        """Retorna DATABASE_URL como string — SQLAlchemy não aceita Url do Pydantic."""
        return str(self.DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    """Singleton: lê o .env uma única vez em toda a vida da aplicação."""
    return Settings()


settings: Settings = get_settings()