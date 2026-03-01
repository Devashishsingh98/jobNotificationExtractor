"""Telegram bot delivery service.

Sends notification messages to users via the Telegram Bot API.
"""

import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from app.config import get_settings


def get_bot() -> Bot:
    settings = get_settings()
    return Bot(token=settings.telegram_bot_token)


def format_notification_message(notification: dict, eligibility: dict | None = None) -> str:
    """Format a notification into a Telegram message."""
    lines = []

    # Title
    lines.append(f"🔔 *{_escape_md(notification.get('title', 'New Notification'))}*")
    lines.append("")

    # Organization
    if notification.get("organization"):
        lines.append(f"🏛 *Org:* {_escape_md(notification['organization'])}")

    # Exam type
    if notification.get("exam_type"):
        lines.append(f"📋 *Type:* {_escape_md(notification['exam_type'])}")

    # Vacancies
    if notification.get("total_vacancies"):
        lines.append(f"👥 *Vacancies:* {notification['total_vacancies']}")

    # Education
    if notification.get("education_required"):
        lines.append(f"🎓 *Education:* {_escape_md(notification['education_required'])}")

    # Age
    if notification.get("min_age") or notification.get("max_age"):
        age_str = ""
        if notification.get("min_age"):
            age_str += f"{notification['min_age']}"
        age_str += "-"
        if notification.get("max_age"):
            age_str += f"{notification['max_age']}"
        lines.append(f"📅 *Age:* {age_str} years")

    # Last date
    if notification.get("last_date"):
        lines.append(f"⏰ *Last Date:* {notification['last_date']}")

    lines.append("")

    # Eligibility status
    if eligibility:
        status = eligibility.get("status", "unknown")
        if status == "eligible":
            lines.append("✅ *You are eligible\\!*")
        elif status == "partial":
            lines.append("⚠️ *Partially eligible*")
        elif status == "not_eligible":
            lines.append("❌ *Not eligible*")

        for reason in eligibility.get("reasons", [])[:3]:
            lines.append(f"  • {_escape_md(reason)}")
        lines.append("")

    # Links
    if notification.get("original_pdf_url"):
        lines.append(
            f"📄 [Download Official PDF]({notification['original_pdf_url']})"
        )
    elif notification.get("official_website_url"):
        lines.append(
            f"🌐 [Official Website]({notification['official_website_url']})"
        )

    return "\n".join(lines)


def _escape_md(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    special_chars = [
        "_", "*", "[", "]", "(", ")", "~", "`", ">", "#",
        "+", "-", "=", "|", "{", "}", ".", "!",
    ]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send a message via the Telegram bot."""
    try:
        bot = get_bot()
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return True
    except Exception as e:
        print(f"Failed to send Telegram message to {chat_id}: {e}")
        return False


def send_telegram_message_sync(chat_id: int, text: str) -> bool:
    """Synchronous wrapper for sending Telegram messages (for Celery tasks)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(send_telegram_message(chat_id, text))
    finally:
        loop.close()
