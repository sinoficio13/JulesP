from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv # Import load_dotenv
import os # Import os

# --- Explicit .env loading ---
# Construct the path to the .env file expected in the project root
# __file__ refers to the current file: app/core/config.py
# os.path.abspath(__file__) gives absolute path to config.py
# os.path.dirname(...) navigates up directories
# Project root is three levels up from app/core/config.py
# However, a more robust way to find project root if structure changes slightly
# is to assume this file is 'app/core/config.py' and go up two levels from 'app'
# Or, if we expect 'app' to be a direct child of project root:
current_file_path = os.path.abspath(__file__)
# app/core/config.py -> app/core -> app -> project_root
project_root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
dotenv_path = os.path.join(project_root_path, ".env")

try:
    if os.path.exists(dotenv_path):
        print(f"INFO:     Attempting to load .env file from: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path, override=True)
        # override=True ensures that .env variables take precedence over system environment variables if they conflict.
        print(f"INFO:     .env file loaded successfully from {dotenv_path}.")
    else:
        # This print is important for debugging if the .env file is not found where expected.
        print(f"WARNING:  .env file not found at calculated path: {dotenv_path}. Environment variables should be set globally.")
except Exception as e:
    print(f"ERROR:    An error occurred while trying to load .env file: {e}")
# --- End explicit .env loading ---

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gym Routine AI Backend"
    API_V1_STR: str = "/api/v1"

    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Pydantic-settings will still try to load from .env by default if env_file is not set,
    # or from the specified env_file. If we've already loaded with load_dotenv,
    # the variables will be in the environment, and Pydantic-settings will pick them up.
    # Explicitly giving the path to model_config can also be an option.
    model_config = SettingsConfigDict(
        env_file=dotenv_path if os.path.exists(dotenv_path) else None, # Pass path only if it exists, else pydantic-settings might warn/error
        env_file_encoding='utf-8',
        extra='ignore' # Ignore extra environment variables not defined in Settings
    )

settings = Settings()

# Optional: Add a print statement here to see if settings were loaded,
# but be careful not to print sensitive keys directly in production logs.
# This is more for local debugging.
# print(f"DEBUG:    Settings loaded: SUPABASE_URL is set: {bool(settings.SUPABASE_URL)}, GEMINI_API_KEY is set: {bool(settings.GEMINI_API_KEY)}")
# The print in supabase_client.py ("Supabase client initialized successfully" or the warning)
# will serve as a good indicator if SUPABASE_URL and SUPABASE_KEY were loaded.
