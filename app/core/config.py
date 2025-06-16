from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gym Routine AI Backend"
    API_V1_STR: str = "/api/v1" # Example API prefix

    # Supabase settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None # This is typically the anon key or service role key

    # Gemini API settings
    GEMINI_API_KEY: Optional[str] = None

    # For Uvicorn server if needed directly in code, though usually handled by Procfile or command
    # SERVER_HOST: str = "0.0.0.0"
    # SERVER_PORT: int = 8000

    # model_config allows loading from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()
