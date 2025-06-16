from supabase import create_client, Client
from app.core.config import settings
import os

# Option 1: Use environment variables directly (if settings object isn't preferred for some reason here)
# supabase_url: str = os.environ.get("SUPABASE_URL")
# supabase_key: str = os.environ.get("SUPABASE_KEY")

# Option 2: Use the Pydantic settings object (recommended)
supabase_url: str = settings.SUPABASE_URL
supabase_key: str = settings.SUPABASE_KEY

if not supabase_url or not supabase_key:
    # This check is more for runtime if .env is missing or vars not set,
    # Pydantic settings might raise an error earlier if vars are None and not Optional.
    # Adjust based on how strictly you want to enforce their presence at startup.
    print("Warning: SUPABASE_URL or SUPABASE_KEY environment variables are not set.")
    print("Supabase client will not be initialized.")
    supabase: Client | None = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        supabase: Client | None = None

def get_supabase_client() -> Client:
    if supabase is None:
        # This could happen if the environment variables were not set at startup.
        # You might want to raise an exception here or handle it based on your application's needs.
        raise RuntimeError("Supabase client is not initialized. Check environment variables SUPABASE_URL and SUPABASE_KEY.")
    return supabase
