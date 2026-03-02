"""Seed popular Indian govt job notification Telegram channels."""

from app.database import get_db

CHANNELS = [
    {
        "channel_username": "saborkoj",
        "channel_name": "Sarkari Job",
        "is_active": True,
    },
    {
        "channel_username": "rojgar_result",
        "channel_name": "Rojgar Result",
        "is_active": True,
    },
    {
        "channel_username": "govaborkoj",
        "channel_name": "Government Jobs",
        "is_active": True,
    },
]


def seed():
    db = get_db()

    # Check existing
    existing = db.table("telegram_channels").select("channel_username").execute()
    existing_names = {ch["channel_username"] for ch in (existing.data or [])}

    added = 0
    for ch in CHANNELS:
        if ch["channel_username"] not in existing_names:
            db.table("telegram_channels").insert(ch).execute()
            print(f"  ✅ Added @{ch['channel_username']}")
            added += 1
        else:
            print(f"  ⏭️  @{ch['channel_username']} already exists")

    print(f"\n📡 {added} channel(s) added, {len(CHANNELS) - added} already existed.")


if __name__ == "__main__":
    seed()
