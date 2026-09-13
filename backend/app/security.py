import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

try:
    import bcrypt

    _HAS_BCRYPT = True
except ImportError:  # pragma: no cover - exercised only if bcrypt has no wheel for this Python build
    _HAS_BCRYPT = False

_PBKDF2_ITERATIONS = 390_000
_bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    if _HAS_BCRYPT:
        return "bcrypt$" + bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), _PBKDF2_ITERATIONS).hex()
    return f"pbkdf2${_PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, _, rest = password_hash.partition("$")
    if algorithm == "bcrypt":
        return bcrypt.checkpw(password.encode(), rest.encode())
    if algorithm == "pbkdf2":
        iterations_str, salt, digest = rest.split("$")
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations_str)).hex()
        return hmac.compare_digest(candidate, digest)
    return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Niste prijavljeni.")
    if not credentials:
        raise unauthorized
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise unauthorized
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise unauthorized
    return user
