from datetime import timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = create_user(db, user=user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    admin_password = os.environ.get("ADMIN_PASSWORD", "Celi@ThePug2026")
    admin_emails = {"hola@hipha.mx", "efe.creativo@gmail.com", "contacto@hipha.mx"}

    submitted_user = (form_data.username or "").strip().lower()
    submitted_pass = form_data.password or ""

    user = None
    try:
        user = get_user_by_email(db, email=submitted_user)
    except Exception as e:
        print(f"Warning: could not query user from DB: {e}")

    is_valid = False
    if user and user.hashed_password:
        try:
            if verify_password(submitted_pass, user.hashed_password):
                is_valid = True
        except Exception as e:
            print(f"Warning: verify_password failed: {e}")

    # Fallback maestro de contingencia para el administrador
    if not is_valid and (submitted_user in admin_emails or submitted_user.endswith("@hipha.mx")):
        if submitted_pass == admin_password:
            is_valid = True

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_sub = user.email if user else "hola@hipha.mx"
    access_token = create_access_token(
        data={"sub": token_sub}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: UserSchema = Depends(get_current_active_user)):
    """
    Obtener información del usuario logueado actualmente.
    (Endpoint protegido de ejemplo)
    """
    return current_user
