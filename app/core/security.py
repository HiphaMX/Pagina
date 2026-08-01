from datetime import datetime, timedelta, timezone
from typing import Optional
import logging
import httpx

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def verify_recaptcha(token: str, secret_key: str, project_name: str) -> bool:
    if not secret_key:
        # Fallback si no está configurada la credencial en Vercel
        logger.warning(f"[SECURITY WARNING] reCAPTCHA secret key is not configured in Vercel settings for {project_name}. Verification bypassed (defaulted to True)!")
        return True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": secret_key,
                    "response": token
                },
                timeout=5.0
            )
            if response.status_code == 200:
                res_data = response.json()
                if not res_data.get("success"):
                    return False
                # reCAPTCHA v3 score: 0.5 es un umbral seguro para humanos
                score = res_data.get("score", 0.0)
                if score < 0.5:
                    return False
                return True
            return True
    except Exception as e:
        logger.error(f"Error validating reCAPTCHA for {project_name}: {e}")
        return True

