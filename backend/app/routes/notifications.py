"""Notification listing, filtering, and selection routes."""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional

from app.models.schemas import (
    NotificationResponse,
    NotificationListResponse,
    SelectionCreate,
)
from app.database import get_db
from app.routes.auth import verify_token
from app.services.eligibility import check_eligibility, matches_preferences

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return verify_token(authorization.split(" ")[1])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    exam_type: Optional[str] = None,
    search: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    """List notifications with optional filtering. Adds eligibility status if user is logged in."""
    db = get_db()

    # Build query — only show notifications with meaningful data
    query = db.table("notifications").select("*", count="exact")
    query = query.not_.is_("organization", "null")  # Must have AI-extracted org

    if exam_type:
        query = query.eq("exam_type", exam_type)
    if search:
        query = query.ilike("title", f"%{search}%")

    # Pagination
    offset = (page - 1) * per_page
    query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)

    result = query.execute()

    # If user is logged in, add eligibility info
    notifications = result.data or []
    user_profile = None

    if authorization and authorization.startswith("Bearer "):
        try:
            user_id = verify_token(authorization.split(" ")[1])
            profile_result = (
                db.table("user_profiles").select("*").eq("user_id", user_id).execute()
            )
            if profile_result.data:
                user_profile = profile_result.data[0]
        except Exception:
            pass  # Not logged in or invalid token, still show notifications

    enriched = []
    for notif in notifications:
        if user_profile:
            elig = check_eligibility(user_profile, notif)
            notif["eligibility_status"] = elig["status"]
            notif["eligibility_reasons"] = elig["reasons"]
        else:
            notif["eligibility_status"] = None
            notif["eligibility_reasons"] = []
        enriched.append(notif)

    return NotificationListResponse(
        notifications=enriched,
        total=result.count or 0,
        page=page,
        per_page=per_page,
    )


@router.get("/matched", response_model=NotificationListResponse)
async def matched_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    authorization: Optional[str] = Header(None),
):
    """Get notifications matching the user's preferences."""
    user_id = get_current_user_id(authorization)
    db = get_db()

    # Get user preferences
    pref_result = db.table("user_preferences").select("*").eq("user_id", user_id).execute()
    preferences = pref_result.data[0] if pref_result.data else {}

    # Get user profile for eligibility
    profile_result = db.table("user_profiles").select("*").eq("user_id", user_id).execute()
    user_profile = profile_result.data[0] if profile_result.data else None

    # Fetch all recent notifications (last 200)
    notif_result = (
        db.table("notifications")
        .select("*", count="exact")
        .order("created_at", desc=True)
        .limit(200)
        .execute()
    )

    all_notifs = notif_result.data or []

    # Filter by preferences
    matched = []
    for notif in all_notifs:
        match = matches_preferences(preferences, notif)
        if match["matches"]:
            # Add eligibility info
            if user_profile:
                elig = check_eligibility(user_profile, notif)
                notif["eligibility_status"] = elig["status"]
                notif["eligibility_reasons"] = elig["reasons"]
            else:
                notif["eligibility_status"] = None
                notif["eligibility_reasons"] = []
            matched.append(notif)

    # Paginate matched results
    total = len(matched)
    offset = (page - 1) * per_page
    page_items = matched[offset:offset + per_page]

    return NotificationListResponse(
        notifications=page_items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    authorization: Optional[str] = Header(None),
):
    """Get single notification with eligibility info."""
    db = get_db()
    result = (
        db.table("notifications").select("*").eq("id", notification_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif = result.data[0]

    if authorization and authorization.startswith("Bearer "):
        try:
            user_id = verify_token(authorization.split(" ")[1])
            profile_result = (
                db.table("user_profiles").select("*").eq("user_id", user_id).execute()
            )
            if profile_result.data:
                elig = check_eligibility(profile_result.data[0], notif)
                notif["eligibility_status"] = elig["status"]
                notif["eligibility_reasons"] = elig["reasons"]
        except Exception:
            pass

    return notif


@router.post("/select")
async def select_notifications(
    data: SelectionCreate,
    authorization: Optional[str] = Header(None),
):
    """Free users select notifications they want delivered via Telegram."""
    user_id = get_current_user_id(authorization)
    db = get_db()

    inserted = 0
    for nid in data.notification_ids:
        try:
            db.table("user_selections").insert({
                "user_id": user_id,
                "notification_id": nid,
            }).execute()
            inserted += 1
        except Exception:
            pass  # Already selected, skip

    # Trigger delivery task
    from worker.tasks import deliver_selected_notifications
    deliver_selected_notifications.delay(user_id)

    return {"status": "ok", "selected": inserted}
