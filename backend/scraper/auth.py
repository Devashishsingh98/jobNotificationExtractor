"""Telethon auth helper.

Run this once to authorize Telethon with your personal Telegram account.
It will ask for your phone number and OTP, then save a session file.

Usage:
    cd backend
    python -m scraper.auth
"""

import asyncio
from app.config import get_settings
from scraper.telegram_client import get_telethon_client


async def authorize():
    """Interactive Telethon authorization."""
    client = get_telethon_client()

    print("🔐 Telegram Authorization")
    print("=" * 40)
    print("This will send an OTP to your Telegram app.")
    print("You only need to do this once.\n")

    await client.start()

    me = await client.get_me()
    print(f"\n✅ Authorized as: {me.first_name} (@{me.username})")
    print(f"📱 Phone: +{me.phone}")
    print("Session file saved. You won't need to do this again.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(authorize())
