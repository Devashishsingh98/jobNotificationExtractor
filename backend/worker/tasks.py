"""Celery tasks for scraping, matching, and delivering notifications."""

from worker.celery_app import celery_app
from app.database import get_db
from app.services.eligibility import check_eligibility, matches_preferences
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
    When a new notification is stored, find all users with matching preferences
    and record matches. Deliver via Telegram to premium users.
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

    # Get ALL users with preferences
    users_result = (
        db.table("users")
        .select("id, telegram_chat_id, is_premium, is_active")
        .eq("is_active", True)
        .execute()
    )

    if not users_result.data:
        print("No active users")
        return

    matched = 0
    delivered = 0

    for user in users_result.data:
        user_id = user["id"]

        # Get user preferences
        pref_result = (
            db.table("user_preferences")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        preferences = pref_result.data[0] if pref_result.data else {}

        # Check preference match
        match = matches_preferences(preferences, notification)
        if not match["matches"]:
            continue

        # Get user profile for eligibility
        profile_result = (
            db.table("user_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        profile = profile_result.data[0] if profile_result.data else None

        # Check eligibility
        eligibility = None
        if profile:
            eligibility = check_eligibility(profile, notification)

        # Record match for all users (for "For You" feed)
        try:
            db.table("notification_matches").insert({
                "user_id": user_id,
                "notification_id": notification_id,
                "match_score": match["score"],
                "match_reasons": match["reasons"],
            }).execute()
            matched += 1
        except Exception:
            pass  # Already matched

        # Deliver via Telegram to premium users only
        if user.get("is_premium") and user.get("telegram_chat_id"):
            if eligibility and eligibility["status"] == "not_eligible":
                continue  # Don't send ineligible notifications to premium users

            message = format_notification_message(notification, eligibility)
            success = send_telegram_message_sync(user["telegram_chat_id"], message)

            if success:
                try:
                    db.table("notification_deliveries").insert({
                        "user_id": user_id,
                        "notification_id": notification_id,
                        "delivery_type": "auto",
                    }).execute()
                    delivered += 1
                except Exception:
                    pass

    print(f"📬 Notification {notification_id}: matched {matched} users, delivered to {delivered} premium users")


@celery_app.task(name="worker.tasks.reprocess_notifications")
def reprocess_notifications():
    """Re-process existing notifications with AI for richer data."""
    db = get_db()
    from scraper.parser import parse_notification

    # Get notifications with missing critical fields
    result = (
        db.table("notifications")
        .select("id, raw_text")
        .is_("organization", "null")
        .limit(20)
        .execute()
    )

    if not result.data:
        print("No notifications need re-processing")
        return

    updated = 0
    for notif in result.data:
        if not notif.get("raw_text"):
            continue

        parsed = parse_notification(notif["raw_text"])
        # Only update fields that are now non-null
        update_data = {}
        for key in ["title", "organization", "exam_type", "last_date",
                     "min_age", "max_age", "education_required", "total_vacancies"]:
            if parsed.get(key) is not None:
                update_data[key] = parsed[key]

        if update_data:
            db.table("notifications").update(update_data).eq("id", notif["id"]).execute()
            updated += 1
            print(f"  ✅ Re-processed #{notif['id']}: {update_data.get('organization', '?')}")

    print(f"📊 Re-processed {updated}/{len(result.data)} notifications")


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
