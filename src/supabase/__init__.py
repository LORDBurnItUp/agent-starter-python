"""Supabase client for data persistence (optional).

This module provides a Supabase client for storing conversation data,
user preferences, or any other persistent data your agent needs.
"""

from .client import get_supabase_client, SupabaseClient

__all__ = ["get_supabase_client", "SupabaseClient"]
