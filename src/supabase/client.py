"""Supabase client setup for data persistence."""

import os
from typing import Optional

try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    SupabaseClient = None


def get_supabase_client() -> Optional[SupabaseClient]:
    """Create and return a Supabase client if configured.

    Returns:
        Supabase client if environment variables are set, None otherwise.

    Environment Variables:
        SUPABASE_URL: Your Supabase project URL
        SUPABASE_ANON_KEY: Your Supabase anonymous key (for client-side)
        or
        SUPABASE_SERVICE_KEY: Your Supabase service key (for server-side with elevated permissions)

    Example:
        ```python
        from src.supabase import get_supabase_client

        supabase = get_supabase_client()
        if supabase:
            # Store conversation data
            result = supabase.table('conversations').insert({
                'session_id': 'abc123',
                'user_message': 'Hello',
                'agent_response': 'Hi there!'
            }).execute()
        ```
    """
    if not SUPABASE_AVAILABLE:
        return None

    url = os.getenv("SUPABASE_URL")
    # Prefer service key for server-side operations, fall back to anon key
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        return None

    return create_client(url, key)
