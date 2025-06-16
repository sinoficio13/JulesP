from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader # OAuth2PasswordBearer removed from here unless strictly needed for other non-security-dependency reasons
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import uuid
# import jwt # Keep if specific JWT error types are caught, otherwise can be removed if only using supabase.auth.get_user

from app.core import get_supabase_client, settings
from supabase import Client

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login") # Ensured this is commented out or removed

bearer_auth_scheme = APIKeyHeader(
    name="Authorization",
    description="Enter Bearer token in the format: **Bearer &lt;YOUR_TOKEN&gt;** (e.g., 'Bearer eyJ...')",
    auto_error=True
)

class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    email: Optional[EmailStr] = None
    user_metadata: Dict[str, Any] = Field(default_factory=dict)

async def get_current_authenticated_user(
    token_from_header: str = Depends(bearer_auth_scheme), # Correctly uses bearer_auth_scheme
    supabase: Client = Depends(get_supabase_client)
) -> AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token format.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token_from_header:
        raise credentials_exception

    parts = token_from_header.split()
    if not (len(parts) == 2 and parts[0].lower() == "bearer"):
        print(f"Invalid Authorization header format. Header received: '{token_from_header}'")
        raise credentials_exception

    token = parts[1]

    try:
        user_response = supabase.auth.get_user(jwt=token)

        if user_response.user:
            return AuthenticatedUser(
                id=user_response.user.id,
                email=user_response.user.email,
                user_metadata=user_response.user.user_metadata or {}
            )
        else:
            print("Token seemed valid (no exception from get_user) but no user data returned.")
            raise credentials_exception

    except Exception as e:
        print(f"Token validation/Supabase error: {str(e)}")
        raise credentials_exception


async def get_current_authenticated_doctor(
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user) # This correctly depends on the above function
) -> AuthenticatedUser:
    user_role = current_user.user_metadata.get("role")
    if user_role == "doctor":
        return current_user
    else:
        print(f"User {current_user.id} does not have 'doctor' role. Actual role: '{user_role}'. Access forbidden.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have doctor privileges."
        )
