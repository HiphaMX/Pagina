from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "HiphaMX API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./database.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    WEBFLOW_API_TOKEN: str = ""
    WEBFLOW_SITE_ID: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = ""
    class Config:
        env_file = ".env"


settings = Settings()
