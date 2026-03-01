"""Celery tasks for scraping, matching, and delivering notifications."""

from worker.celery_app import celery_app
from app.database import get_db
from app.services.eligibility import check_eligibility
from app.services.delivery import format_notification_message, send_telegram_message_sync


@celery_app.task(name="worker.tasks.scrape_all_channels")
def scrape_all_channels():
    """Periodic task: scrape all active Telegram channels."""
    from scraper.telegram_client import run_scraper
    print("🔄 Starting scheduled Telegram scrape...")
    run_scraper()
    print("✅ Scrape complete.")


@celery_app.task(name="worker.tasks.match_and_deliver")
def match_and_deliver(notification_id: int):
    """
    When a new notification is stored, find all eligible premium users
    and send them the notification via Telegram.
    """
    db = get_db()

    # Get the notification
    notif_result = (
        db.table("notifications")
        .select("*")
        .eq("id", notification_id)
        .execute()
    )
    if not notif_result.data:
        print(f"Notification {notification_id} not found")
        return

    notification = notif_result.data[0]

    # Get all premium users with telegram_chat_id and profile
    users_result = (
        db.table("users")
        .select("id, telegram_chat_id")
        .eq("is_premium", True)
        .eq("is_active", True)
        .not_.is_("telegram_chat_id", "null")
        .execute()
    )

    if not users_result.data:
        print("No premium users to notify")
        return

    delivered = 0
    for user in users_result.data:
        # Get user profile
        profile_result = (
            db.table("user_profiles")
            .select("*")
            .eq("user_id", user["id"])
            .execute()
        )
        if not profile_result.data:
            continue

        profile = profile_result.data[0]

        # Check eligibility
        eligibility = check_eligibility(profile, notification)
        if eligibility["status"] == "not_eligible":
            continue

        # Format and send message
        message = format_notification_message(notification, eligibility)
        success = send_telegram_message_sync(user["telegram_chat_id"], message)

        if success:
            # Record delivery
            try:
                db.table("notification_deliveries").insert({
                    "user_id": user["id"],
                    "notification_id": notification_id,
                    "delivery_type": "auto",
                }).execute()
                delivered += 1
            except Exception:
                pass  # Already delivered

    print(f"📬 Notification {notification_id}: delivered to {delivered} premium users")


@celery_app.task(name="worker.tasks.deliver_selected_notifications")
def deliver_selected_notifications(user_id: str):
    """
    Deliver notifications that a free user has selected via checkboxes.
    """
    db = get_db()

    # Get user's Telegram chat ID
    user_result = (
        db.table("users")
        .select("telegram_chat_id")
        .eq("id", user_id)
        .execute()
    )
    if not user_result.data or not user_result.data[0].get("telegram_chat_id"):
        print(f"User {user_id} has no Telegram chat ID")
        return

    chat_id = user_result.data[0]["telegram_chat_id"]

    # Get undelivered selections
    selections = (
        db.table("user_selections")
        .select("notification_id")
        .eq("user_id", user_id)
        .eq("is_delivered", False)
        .execute()
    )

    if not selections.data:
        return

    # Get user profile for eligibility
    profile_result = (
        db.table("user_profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    user_profile = profile_result.data[0] if profile_result.data else None

    for sel in selections.data:
        nid = sel["notification_id"]

        # Get notification
        notif_result = (
            db.table("notifications").select("*").eq("id", nid).execute()
        )
        if not notif_result.data:
            continue

        notification = notif_result.data[0]

        # Check eligibility if profile exists
        eligibility = None
        if user_profile:
            eligibility = check_eligibility(user_profile, notification)

        # Send message
        message = format_notification_message(notification, eligibility)
        success = send_telegram_message_sync(chat_id, message)

        if success:
            # Mark as delivered
            db.table("user_selections").update(
                {"is_delivered": True}
            ).eq("user_id", user_id).eq("notification_id", nid).execute()

            # Record delivery
            try:
                db.table("notification_deliveries").insert({
                    "user_id": user_id,
                    "notification_id": nid,
                    "delivery_type": "manual",
                }).execute()
            except Exception:
                pass
