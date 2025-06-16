from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # Standard way to define token location
from pydantic import BaseModel, EmailStr
import jwt # PyJWT or python-jose. Supabase uses standard JWTs.
from typing import Optional
import uuid

from app.core import get_supabase_client, settings # For Supabase client and potentially JWT secret/config
from supabase import Client


# This scheme can be used in swagger UI to make it easy to add the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login") # Points to our login endpoint

class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    email: Optional[EmailStr] = None
    # Add other fields from JWT if needed, like 'role'
    # role: Optional[str] = None

async def get_current_authenticated_user(
    token: str = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase_client)
) -> AuthenticatedUser:
    '''
    Dependency to get the current authenticated user from a Supabase JWT.
    This is a placeholder for full JWT validation.
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token: # Should be caught by oauth2_scheme, but as a safeguard
        raise credentials_exception

    try:
        # In a real scenario, you would validate the Supabase JWT.
        # This typically involves:
        # 1. Fetching Supabase's JWKS (JSON Web Key Set) URI.
        # 2. Decoding the token using the correct public key from JWKS.
        # 3. Verifying signature, issuer (iss), audience (aud), expiry (exp).
        # Supabase-py's `auth.get_user(jwt=token)` does this.

        user_response = supabase.auth.get_user(jwt=token)

        if user_response.user:
            # print(f"Authenticated user from token: {user_response.user.id}, email: {user_response.user.email}")
            return AuthenticatedUser(
                id=user_response.user.id, # This is a UUID
                email=user_response.user.email
                # role=user_response.user.role # If you have roles in your Supabase user
            )
        else:
            # This case might occur if token is valid but user somehow doesn't exist or other error
            print("Token seemed valid but no user data returned by supabase.auth.get_user()")
            raise credentials_exception

    except jwt.ExpiredSignatureError: # If using PyJWT directly
        print("Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e: # Catch other PyJWT errors if using PyJWT directly
        print(f"JWT validation error: {e}")
        raise credentials_exception
    except Exception as e:
        # Catch-all for other errors, including issues with supabase.auth.get_user() if it fails unexpectedly
        print(f"An unexpected error occurred during token validation: {e}")
        raise credentials_exception

# Placeholder for a similar dependency for "doctors" if they have specific roles/claims
# async def get_current_authenticated_doctor(...) -> AuthenticatedDoctor: ...
