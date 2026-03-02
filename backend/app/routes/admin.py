"""Admin routes for managing channels and viewing stats."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.models.schemas import ChannelCreate, ChannelResponse
from app.database import get_db
from app.routes.auth import verify_token

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(authorization: Optional[str] = Header(None)) -> str:
    """Verify user is authenticated and has admin role."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    user_id = verify_token(authorization.split(" ")[1])

    # Check if user has admin role
    db = get_db()
    result = db.table("users").select("role").eq("id", user_id).execute()

    if not result.data or result.data[0].get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user_id


@router.get("/channels", response_model=list[ChannelResponse])
async def list_channels(authorization: Optional[str] = Header(None)):
    """List all monitored Telegram channels."""
    require_admin(authorization)
    db = get_db()
    result = db.table("telegram_channels").select("*").order("id").execute()
    return result.data or []


@router.post("/channels", response_model=ChannelResponse)
async def add_channel(data: ChannelCreate, authorization: Optional[str] = Header(None)):
    """Add a Telegram channel to monitor."""
    require_admin(authorization)
    db = get_db()

    # Strip @ prefix if present
    username = data.channel_username.lstrip("@")

    result = db.table("telegram_channels").insert({
        "channel_username": username,
        "channel_name": data.channel_name or username,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to add channel")
    return result.data[0]


@router.delete("/channels/{channel_id}")
async def remove_channel(channel_id: int, authorization: Optional[str] = Header(None)):
    """Remove a channel from monitoring."""
    require_admin(authorization)
    db = get_db()
    db.table("telegram_channels").delete().eq("id", channel_id).execute()
    return {"status": "deleted"}


@router.patch("/channels/{channel_id}/toggle")
async def toggle_channel(channel_id: int, authorization: Optional[str] = Header(None)):
    """Toggle channel active/inactive."""
    require_admin(authorization)
    db = get_db()

    current = db.table("telegram_channels").select("is_active").eq("id", channel_id).execute()
    if not current.data:
        raise HTTPException(status_code=404, detail="Channel not found")

    new_state = not current.data[0]["is_active"]
    db.table("telegram_channels").update({"is_active": new_state}).eq("id", channel_id).execute()
    return {"status": "ok", "is_active": new_state}


@router.get("/stats")
async def get_stats(authorization: Optional[str] = Header(None)):
    """Get system stats."""
    require_admin(authorization)
    db = get_db()

    users = db.table("users").select("id", count="exact").execute()
    premium = db.table("users").select("id", count="exact").eq("is_premium", True).execute()
    notifications = db.table("notifications").select("id", count="exact").execute()
    deliveries = db.table("notification_deliveries").select("id", count="exact").execute()
    channels = db.table("telegram_channels").select("id", count="exact").eq("is_active", True).execute()

    return {
        "total_users": users.count or 0,
        "premium_users": premium.count or 0,
        "total_notifications": notifications.count or 0,
        "total_deliveries": deliveries.count or 0,
        "active_channels": channels.count or 0,
    }


@router.get("/users")
async def list_users(authorization: Optional[str] = Header(None)):
    """List all registered users (admin only)."""
    require_admin(authorization)
    db = get_db()
    result = (
        db.table("users")
        .select("id, email, telegram_username, telegram_chat_id, is_premium, is_active, role, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.patch("/users/{user_id}/toggle-premium")
async def toggle_premium(user_id: str, authorization: Optional[str] = Header(None)):
    """Toggle a user's premium status (admin only)."""
    require_admin(authorization)
    db = get_db()

    current = db.table("users").select("is_premium, email").eq("id", user_id).execute()
    if not current.data:
        raise HTTPException(status_code=404, detail="User not found")

    new_status = not current.data[0]["is_premium"]
    db.table("users").update({"is_premium": new_status}).eq("id", user_id).execute()

    email = current.data[0]["email"]
    return {"status": "ok", "email": email, "is_premium": new_status}


@router.post("/trigger-scrape")
async def trigger_scrape(authorization: Optional[str] = Header(None)):
    """Manually trigger a scrape of all channels (admin only)."""
    require_admin(authorization)
    from worker.tasks import scrape_all_channels
    scrape_all_channels.delay()
    return {"status": "ok", "message": "Scrape triggered"}


@router.post("/reprocess")
async def trigger_reprocess(authorization: Optional[str] = Header(None)):
    """Re-process notifications with AI (admin only)."""
    require_admin(authorization)
    from worker.tasks import reprocess_notifications
    reprocess_notifications.delay()
    return {"status": "ok", "message": "Re-processing triggered"}
