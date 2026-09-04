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
    HIPHA_RECAPTCHA_SECRET_KEY: str = ""

    # AMDI Specific SMTP settings
    AMDI_SMTP_HOST: str = ""
    AMDI_SMTP_PORT: Union[int, str] = 587
    AMDI_SMTP_USER: str = ""
    AMDI_SMTP_PASSWORD: str = ""
    AMDI_EMAILS_FROM_EMAIL: str = ""
    AMDI_EMAILS_FROM_NAME: str = ""
    AMDI_RECAPTCHA_SECRET_KEY: str = ""

    # CHILECHILLON Specific SMTP settings
    CHILECHILLON_SMTP_HOST: str = ""
    CHILECHILLON_SMTP_PORT: Union[int, str] = 587
    CHILECHILLON_SMTP_USER: str = ""
    CHILECHILLON_SMTP_PASSWORD: str = ""
    CHILECHILLON_EMAILS_FROM_EMAIL: str = ""
    CHILECHILLON_EMAILS_FROM_NAME: str = ""
    CHILECHILLON_RECAPTCHA_SECRET_KEY: str = ""

    # WHITECLEAN Specific SMTP settings
    WHITECLEAN_SMTP_HOST: str = ""
    WHITECLEAN_SMTP_PORT: Union[int, str] = 587
    WHITECLEAN_SMTP_USER: str = ""
    WHITECLEAN_SMTP_PASSWORD: str = ""
    WHITECLEAN_EMAILS_FROM_EMAIL: str = ""
    WHITECLEAN_EMAILS_FROM_NAME: str = ""
    WHITECLEAN_RECAPTCHA_SECRET_KEY: str = ""

    # GRUPOGARI Specific SMTP settings
    GRUPOGARI_SMTP_HOST: str = ""
    GRUPOGARI_SMTP_PORT: Union[int, str] = 587
    GRUPOGARI_SMTP_USER: str = ""
    GRUPOGARI_SMTP_PASSWORD: str = ""
    GRUPOGARI_EMAILS_FROM_EMAIL: str = ""
    GRUPOGARI_EMAILS_FROM_NAME: str = ""
    GRUPOGARI_RECAPTCHA_SECRET_KEY: str = ""

    # VALENCIA Specific SMTP settings
    VALENCIA_SMTP_HOST: str = ""
    VALENCIA_SMTP_PORT: Union[int, str] = 587
    VALENCIA_SMTP_USER: str = ""
    VALENCIA_SMTP_PASSWORD: str = ""
    VALENCIA_EMAILS_FROM_EMAIL: str = ""
    VALENCIA_EMAILS_FROM_NAME: str = ""
    VALENCIA_RECAPTCHA_SECRET_KEY: str = ""

    # BOTICA Specific SMTP settings
    BOTICA_SMTP_HOST: str = ""
    BOTICA_SMTP_PORT: Union[int, str] = 587
    BOTICA_SMTP_USER: str = ""
    BOTICA_SMTP_PASSWORD: str = ""
    BOTICA_EMAILS_FROM_EMAIL: str = ""
    BOTICA_EMAILS_FROM_NAME: str = ""
    BOTICA_RECAPTCHA_SECRET_KEY: str = ""

    # HEALTHYICE Specific SMTP settings
    HEALTHYICE_SMTP_HOST: str = ""
    HEALTHYICE_SMTP_PORT: Union[int, str] = 587
    HEALTHYICE_SMTP_USER: str = ""
    HEALTHYICE_SMTP_PASSWORD: str = ""
    HEALTHYICE_EMAILS_FROM_EMAIL: str = ""
    HEALTHYICE_EMAILS_FROM_NAME: str = ""
    HEALTHYICE_RECAPTCHA_SECRET_KEY: str = ""

    # UROONCOLOGY Specific SMTP settings (Pendiente de credenciales)
    UROONCOLOGY_SMTP_HOST: str = ""
    UROONCOLOGY_SMTP_PORT: Union[int, str] = 587
    UROONCOLOGY_SMTP_USER: str = ""
    UROONCOLOGY_SMTP_PASSWORD: str = ""
    UROONCOLOGY_EMAILS_FROM_EMAIL: str = ""
    UROONCOLOGY_EMAILS_FROM_NAME: str = ""
    UROONCOLOGY_RECAPTCHA_SECRET_KEY: str = ""

    # UROLOGIAAVANZADA Specific SMTP settings (Pendiente de credenciales)
    UROLOGIAAVANZADA_SMTP_HOST: str = ""
    UROLOGIAAVANZADA_SMTP_PORT: Union[int, str] = 587
    UROLOGIAAVANZADA_SMTP_USER: str = ""
    UROLOGIAAVANZADA_SMTP_PASSWORD: str = ""
    UROLOGIAAVANZADA_EMAILS_FROM_EMAIL: str = ""
    UROLOGIAAVANZADA_EMAILS_FROM_NAME: str = ""
    UROLOGIAAVANZADA_RECAPTCHA_SECRET_KEY: str = ""

    # JESSICAMENDOZA Specific SMTP settings (Pendiente de credenciales)
    JESSICAMENDOZA_SMTP_HOST: str = ""
    JESSICAMENDOZA_SMTP_PORT: Union[int, str] = 587
    JESSICAMENDOZA_SMTP_USER: str = ""
    JESSICAMENDOZA_SMTP_PASSWORD: str = ""
    JESSICAMENDOZA_EMAILS_FROM_EMAIL: str = ""
    JESSICAMENDOZA_EMAILS_FROM_NAME: str = ""
    JESSICAMENDOZA_RECAPTCHA_SECRET_KEY: str = ""

    # LETRERAMA Specific SMTP settings (Pendiente de credenciales)
    LETRERAMA_SMTP_HOST: str = ""
    LETRERAMA_SMTP_PORT: Union[int, str] = 587
    LETRERAMA_SMTP_USER: str = ""
    LETRERAMA_SMTP_PASSWORD: str = ""
    LETRERAMA_EMAILS_FROM_EMAIL: str = ""
    LETRERAMA_EMAILS_FROM_NAME: str = ""
    LETRERAMA_RECAPTCHA_SECRET_KEY: str = ""

    GOOGLE_PLACES_API_KEY: str = ""

    @validator("SMTP_PORT", pre=True, always=True)
    @classmethod
    def coerce_port(cls, v):
        if v == "" or v is None:
            return 587
        try:
            return int(v)
        except ValueError:
            return 587

    @validator("AMDI_SMTP_HOST", pre=True, always=True)
    @classmethod
    def get_amdi_host(cls, v):
        import os
        return v or os.getenv("AMDI2_SMTP_HOST", "")

    @validator("AMDI_SMTP_PORT", pre=True, always=True)
    @classmethod
    def get_amdi_port(cls, v):
        import os
        port_val = v or os.getenv("AMDI2_SMTP_PORT", "")
        if port_val == "" or port_val is None:
            return 587
        try:
            return int(port_val)
        except ValueError:
            return 587

    @validator("AMDI_SMTP_USER", pre=True, always=True)
    @classmethod
    def get_amdi_user(cls, v):
        import os
        return v or os.getenv("AMDI2_SMTP_USER", "")

    @validator("AMDI_SMTP_PASSWORD", pre=True, always=True)
    @classmethod
    def get_amdi_password(cls, v):
        import os
        return v or os.getenv("AMDI2_SMTP_PASSWORD", "")

    @validator("AMDI_EMAILS_FROM_EMAIL", pre=True, always=True)
    @classmethod
    def get_amdi_from_email(cls, v):
        import os
        return v or os.getenv("AMDI2_EMAILS_FROM_EMAIL", "")

    @validator("AMDI_EMAILS_FROM_NAME", pre=True, always=True)
    @classmethod
    def get_amdi_from_name(cls, v):
        import os
        return v or os.getenv("AMDI2_EMAILS_FROM_NAME", "")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
