"""Supabase client initialization."""

from supabase import create_client, Client
from app.config import get_settings


def get_supabase() -> Client:
    """Get Supabase client with service role key (full access)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


# Singleton client for reuse
_client: Client | None = None


def get_db() -> Client:
    """Get singleton Supabase client."""
    global _client
    if _client is None:
        _client = get_supabase()
    return _client
