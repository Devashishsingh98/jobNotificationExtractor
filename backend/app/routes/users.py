"""User profile routes."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.models.schemas import UserProfileCreate, UserProfileResponse, UserResponse
from app.database import get_db
from app.routes.auth import verify_token

router = APIRouter(prefix="/api/users", tags=["users"])


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user_id from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token = authorization.split(" ")[1]
    return verify_token(token)


@router.get("/me", response_model=UserResponse)
async def get_me(authorization: Optional[str] = Header(None)):
    """Get current user info."""
    user_id = get_current_user_id(authorization)
    db = get_db()
    result = db.table("users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(authorization: Optional[str] = Header(None)):
    """Get current user's eligibility profile."""
    user_id = get_current_user_id(authorization)
    db = get_db()
    result = db.table("user_profiles").select("*").eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result.data[0]


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    data: UserProfileCreate,
    authorization: Optional[str] = Header(None),
):
    """Update current user's eligibility profile."""
    user_id = get_current_user_id(authorization)
    db = get_db()

    update_data = data.model_dump(exclude_none=True)
    if data.dob:
        update_data["dob"] = data.dob.isoformat()
    update_data["updated_at"] = "now()"

    result = (
        db.table("user_profiles")
        .update(update_data)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result.data[0]


@router.put("/telegram-chat-id")
async def set_telegram_chat_id(
    chat_id: int,
    authorization: Optional[str] = Header(None),
):
    """Set user's Telegram chat ID (called after user starts the bot)."""
    user_id = get_current_user_id(authorization)
    db = get_db()
    db.table("users").update({"telegram_chat_id": chat_id}).eq("id", user_id).execute()
    return {"status": "ok"}
