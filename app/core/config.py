from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Union, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "HiphaMX API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./database.db"
    SECRET_KEY: str = "fallback-secret-key-for-dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    WEBFLOW_API_TOKEN: str = ""
    WEBFLOW_SITE_ID: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: Union[int, str] = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = ""

    # AMDI Specific SMTP settings
    AMDI_SMTP_HOST: str = ""
    AMDI_SMTP_PORT: Union[int, str] = 587
    AMDI_SMTP_USER: str = ""
    AMDI_SMTP_PASSWORD: str = ""
    AMDI_EMAILS_FROM_EMAIL: str = ""
    AMDI_EMAILS_FROM_NAME: str = ""

    GOOGLE_PLACES_API_KEY: str = ""

    @validator("SMTP_PORT", "AMDI_SMTP_PORT", pre=True, always=True)
    @classmethod
    def coerce_port(cls, v):
        if v == "" or v is None:
            return 587
        try:
            return int(v)
        except ValueError:
            return 587

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
