from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import os
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Resume Service API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")

    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    max_tokens: int = Field(default=800, env="MAX_TOKENS") 
    temperature: float = Field(default=0.7, env="TEMPERATURE")

    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", env="CORS_ORIGINS")

    sqlalchemy_echo: bool = Field(default=False, env="SQLALCHEMY_ECHO")
    sqlalchemy_pool_size: int = Field(default=20, env="SQLALCHEMY_POOL_SIZE")
    sqlalchemy_max_overflow: int = Field(default=10, env="SQLALCHEMY_MAX_OVERFLOW")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def get_cors_origins_list(self) -> list:
        """Parse cors_origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @field_validator("sqlalchemy_echo", mode="before")
    @classmethod
    def parse_echo(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expire(cls, v):
        if v < 1:
            raise ValueError("access_token_expire_minutes must be at least 1")
        if v > 525600:
            raise ValueError("access_token_expire_minutes cannot exceed 1 year")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
