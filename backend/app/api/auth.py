from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas.auth import ChangePasswordRequest, GoogleAuthRequest, LoginRequest, SignupRequest, TokenResponse, UserRead
from app.security import create_access_token, get_current_user, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Nalog"])


def issue_token(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


def _first_user_role(db: Session) -> str:
    """The very first registered account becomes the tenant owner (role „Vlasnik")."""
    return "Vlasnik" if (db.scalar(select(func.count()).select_from(User)) or 0) == 0 else "Korisnik"


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status_code=409, detail="Nalog sa ovim email-om već postoji.")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        auth_provider="local",
        role=_first_user_role(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_token(user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    invalid = HTTPException(status_code=401, detail="Pogrešan email ili lozinka.")
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise invalid
    return issue_token(user)


@router.post("/google", response_model=TokenResponse)
def google_login(data: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google prijava nije podešena na serveru.")
    try:
        payload = google_id_token.verify_oauth2_token(
            data.id_token, google_requests.Request(), audience=settings.google_client_id
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Nevažeći Google token.")

    google_id = payload["sub"]
    email = payload.get("email")
    name = payload.get("name") or email or "Korisnik"
    user = db.scalar(select(User).where(User.google_id == google_id))
    if not user and email:
        user = db.scalar(select(User).where(User.email == email))
    if user:
        if not user.google_id:
            user.google_id = google_id
    else:
        user = User(
            name=name,
            email=email,
            google_id=google_id,
            auth_provider="google",
            role=_first_user_role(db),
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return issue_token(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/change-password", response_model=UserRead)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if current_user.password_hash:
        if not data.current_password or not verify_password(data.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Trenutna lozinka nije tačna.")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    db.refresh(current_user)
    return current_user
