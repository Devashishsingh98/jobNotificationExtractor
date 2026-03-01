"""Authentication routes: register, login, token verification."""

from fastapi import APIRouter, HTTPException, Depends
from passlib.hash import bcrypt
from datetime import datetime, timedelta, timezone
import jwt

from app.models.schemas import UserRegister, UserLogin, TokenResponse
from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def create_token(user_id: str) -> str:
    """Create a JWT token for the user."""
    settings = get_settings()
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> str:
    """Verify JWT token and return user_id."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    """Register a new user."""
    db = get_db()

    # Check if email already exists
    existing = db.table("users").select("id").eq("email", data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    password_hash = bcrypt.hash(data.password)
    result = db.table("users").insert({
        "email": data.email,
        "password_hash": password_hash,
        "telegram_username": data.telegram_username,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user_id = result.data[0]["id"]

    # Create empty profile
    db.table("user_profiles").insert({"user_id": user_id}).execute()

    token = create_token(user_id)
    return TokenResponse(access_token=token, user_id=user_id)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login with email and password."""
    db = get_db()

    result = db.table("users").select("id, password_hash").eq("email", data.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = result.data[0]
    if not bcrypt.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["id"])
    return TokenResponse(access_token=token, user_id=user["id"])
