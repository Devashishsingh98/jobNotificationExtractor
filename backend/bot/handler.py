"""
Telegram Bot — handles /start command for user onboarding.

Users send /start to the bot, and it links their Telegram chat_id
to their account so they can receive notifications.

Run with: python -m bot.handler
"""

import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import get_settings
from app.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — link user's Telegram to their account."""
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    db = get_db()

    # Try to find user by Telegram username
    user = None
    if username:
        result = db.table("users").select("id, email, is_premium").eq(
            "telegram_username", username
        ).execute()
        if result.data:
            user = result.data[0]

    if user:
        # Link chat_id to this user
        db.table("users").update({"telegram_chat_id": chat_id}).eq("id", user["id"]).execute()

        tier = "⭐ Premium" if user.get("is_premium") else "Free"
        await update.message.reply_text(
            f"✅ Welcome, {first_name}!\n\n"
            f"Your Telegram is now linked to: {user['email']}\n"
            f"Account tier: {tier}\n\n"
            f"You will now receive job notifications here based on your preferences.\n\n"
            f"📋 /help — See available commands\n"
            f"🔔 /status — Check your notification settings"
        )
        logger.info(f"Linked user {user['email']} to chat_id {chat_id}")
    else:
        await update.message.reply_text(
            f"👋 Hi {first_name}!\n\n"
            f"I couldn't find an account linked to your Telegram username (@{username or 'not set'}).\n\n"
            f"To get started:\n"
            f"1️⃣ Register at our website\n"
            f"2️⃣ Set your Telegram username during registration\n"
            f"3️⃣ Come back here and type /start again\n\n"
            f"Your chat ID is: {chat_id}"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help — show available commands."""
    await update.message.reply_text(
        "📋 *Available Commands*\n\n"
        "/start — Link your Telegram account\n"
        "/status — Check your notification settings\n"
        "/help — Show this help message\n\n"
        "💡 *How it works:*\n"
        "• Set your preferences on the website\n"
        "• We scrape government job channels every 5 hours\n"
        "• Matching notifications are sent to you here\n"
        "• Premium users get unlimited Telegram notifications",
        parse_mode="Markdown"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status — show user's notification settings."""
    chat_id = update.effective_chat.id
    db = get_db()

    result = db.table("users").select(
        "id, email, is_premium, telegram_username"
    ).eq("telegram_chat_id", chat_id).execute()

    if not result.data:
        await update.message.reply_text(
            "❌ Your Telegram is not linked to any account.\n"
            "Use /start to link your account."
        )
        return

    user = result.data[0]

    # Get preferences
    prefs = db.table("user_preferences").select("*").eq("user_id", user["id"]).execute()
    pref_data = prefs.data[0] if prefs.data else {}

    exam_types = ", ".join(pref_data.get("preferred_exam_types", [])) or "All"
    states = ", ".join(pref_data.get("preferred_states", [])) or "All India"
    orgs = ", ".join(pref_data.get("preferred_orgs", [])) or "All"

    tier = "⭐ Premium (unlimited)" if user.get("is_premium") else "Free (website only)"

    await update.message.reply_text(
        f"📊 *Your Status*\n\n"
        f"📧 Email: {user['email']}\n"
        f"🎫 Tier: {tier}\n\n"
        f"*Preferences:*\n"
        f"📋 Exam types: {exam_types}\n"
        f"📍 States: {states}\n"
        f"🏛 Organizations: {orgs}\n\n"
        f"Update preferences on the website to receive better matches.",
        parse_mode="Markdown"
    )


async def post_init(app: Application):
    """Set bot commands after initialization."""
    await app.bot.set_my_commands([
        BotCommand("start", "Link your Telegram account"),
        BotCommand("status", "Check notification settings"),
        BotCommand("help", "Show available commands"),
    ])


def main():
    settings = get_settings()
    token = settings.telegram_bot_token

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return

    app = Application.builder().token(token).post_init(post_init).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))

    print("🤖 Bot is running... Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
