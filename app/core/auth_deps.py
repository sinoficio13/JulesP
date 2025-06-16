from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pydantic import BaseModel, EmailStr, Field # Added Field
import jwt # PyJWT or python-jose. Supabase uses standard JWTs.
from typing import Optional, Dict, Any # Added Dict, Any
import uuid

from app.core import get_supabase_client, settings # For Supabase client and potentially JWT secret/config
from supabase import Client
from supabase.lib.client_options import ClientOptions # Required for user_metadata access with some versions


# This scheme can be used in swagger UI to make it easy to add the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login") # Keep this for openapi doc

# New scheme for Bearer token input
bearer_auth_scheme = APIKeyHeader(
    name="Authorization",
    description="Enter Bearer token in the format: **Bearer &lt;YOUR_TOKEN&gt;** (e.g., 'Bearer eyJ...')",
    auto_error=True
)

class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    email: Optional[EmailStr] = None
    # Add user_metadata to potentially access roles or other custom claims
    user_metadata: Dict[str, Any] = Field(default_factory=dict)
    # role: Optional[str] = None # Could be extracted from user_metadata

async def get_current_authenticated_user(
    token: str = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase_client)
) -> AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        # supabase.auth.get_user(jwt=token) validates the token and returns user details
        user_response = supabase.auth.get_user(jwt=token)

        if user_response.user:
            # print(f"Authenticated user from token: {user_response.user.id}, email: {user_response.user.email}, metadata: {user_response.user.user_metadata}")
            return AuthenticatedUser(
                id=user_response.user.id,
                email=user_response.user.email,
                user_metadata=user_response.user.user_metadata or {} # Ensure user_metadata is a dict
            )
        else:
            print("Token seemed valid but no user data returned by supabase.auth.get_user()")
            raise credentials_exception

    except jwt.ExpiredSignatureError: # If using PyJWT directly (supabase-py might raise its own error type)
        print("Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e: # Catch other PyJWT errors if using PyJWT directly
        print(f"JWT validation error: {e}")
        raise credentials_exception
    except Exception as e: # Catch-all for other errors from supabase.auth.get_user()
        print(f"An unexpected error occurred during token validation: {str(e)}")
        # Check if the error message indicates an invalid token specifically
        if "invalid JWT" in str(e).lower() or "token is invalid" in str(e).lower():
             raise credentials_exception
        # For other unexpected errors from supabase client during auth, a 500 might be more appropriate
        # or log it and still return 401 for security.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred processing authentication: {str(e)}"
        )


async def get_current_authenticated_doctor(
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user)
) -> AuthenticatedUser:
    '''
    Dependency to get the current authenticated user and verify they have 'doctor' role.
    Assumes role is stored in user.user_metadata.role.
    '''
    # print(f"Checking doctor role for user: {current_user.id}. Metadata: {current_user.user_metadata}")
    user_role = current_user.user_metadata.get("role")

    if user_role == "doctor":
        return current_user # User is authenticated and has 'doctor' role
    else:
        print(f"User {current_user.id} does not have 'doctor' role. Actual role: '{user_role}'. Access forbidden.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have doctor privileges."
        )
