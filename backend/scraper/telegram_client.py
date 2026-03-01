"""Telegram channel scraper using Telethon.

Monitors configured public Telegram channels for new job notifications.
Uses your personal Telegram account via Telethon (not Bot API).
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument

from app.config import get_settings
from app.database import get_db
from scraper.parser import is_job_notification, parse_notification, extract_urls
from scraper.pdf_sourcer import find_original_pdf

# Session file stored in backend directory
SESSION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(SESSION_DIR, "telegram_scraper")


def get_telethon_client() -> TelegramClient:
    """Create a Telethon client with personal account credentials."""
    settings = get_settings()
    return TelegramClient(
        SESSION_FILE,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )


async def scrape_channels():
    """
    Main scraping function. Checks all active channels for new messages
    since the last scraped message ID.
    """
    settings = get_settings()
    client = get_telethon_client()

    async with client:
        # Ensure we're connected
        if not await client.is_user_authorized():
            print("⚠️  Telethon not authorized. Run 'python -m scraper.auth' first.")
            return

        db = get_db()

        # Get active channels
        channels_result = (
            db.table("telegram_channels")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        channels = channels_result.data or []

        if not channels:
            print("No active channels configured. Add channels via /api/admin/channels.")
            return

        for channel_config in channels:
            try:
                await scrape_single_channel(client, db, channel_config)
            except Exception as e:
                print(f"Error scraping @{channel_config['channel_username']}: {e}")


async def scrape_single_channel(client: TelegramClient, db, channel_config: dict):
    """Scrape a single Telegram channel for new notifications."""
    username = channel_config["channel_username"]
    last_id = channel_config.get("last_scraped_id", 0) or 0
    channel_id = channel_config["id"]

    print(f"📡 Scraping @{username} (last_id: {last_id})...")

    try:
        entity = await client.get_entity(username)
    except Exception as e:
        print(f"  ❌ Cannot find channel @{username}: {e}")
        return

    # Fetch messages newer than last_scraped_id
    new_count = 0
    max_id = last_id

    async for message in client.iter_messages(entity, min_id=last_id, limit=50):
        if not message.text:
            continue

        # Track the highest message ID
        if message.id > max_id:
            max_id = message.id

        # Check if it's a job notification
        if not is_job_notification(message.text):
            continue

        # Check for duplicate
        existing = (
            db.table("notifications")
            .select("id")
            .eq("source_channel", username)
            .eq("source_message_id", message.id)
            .execute()
        )
        if existing.data:
            continue

        # Parse the notification
        parsed = parse_notification(message.text)
        parsed["source_channel"] = username
        parsed["source_message_id"] = message.id

        # Try to find official PDF
        urls = extract_urls(message.text)
        pdf_info = await find_original_pdf(urls)
        parsed["original_pdf_url"] = pdf_info.get("original_pdf_url")
        parsed["official_website_url"] = pdf_info.get("official_website_url")

        # Store in database
        try:
            db.table("notifications").insert(parsed).execute()
            new_count += 1
            print(f"  ✅ New: {parsed['title'][:60]}...")
        except Exception as e:
            print(f"  ⚠️ Failed to store notification: {e}")

    # Update last scraped ID
    if max_id > last_id:
        db.table("telegram_channels").update(
            {"last_scraped_id": max_id}
        ).eq("id", channel_id).execute()

    print(f"  📊 @{username}: {new_count} new notifications, last_id → {max_id}")


def run_scraper():
    """Synchronous entry point for running the scraper (for Celery tasks)."""
    asyncio.run(scrape_channels())


if __name__ == "__main__":
    run_scraper()
