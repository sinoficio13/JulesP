# In app/core/__init__.py
from .config import settings
from .supabase_client import get_supabase_client, supabase
from .auth_deps import get_current_authenticated_user, AuthenticatedUser, get_current_authenticated_doctor # Added

__all__ = [
    "settings",
    "get_supabase_client",
    "supabase",
    "get_current_authenticated_user",
    "AuthenticatedUser",
    "get_current_authenticated_doctor" # Added
]
