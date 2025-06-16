from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from supabase import Client # For type hinting Supabase response if needed
from app.core import get_supabase_client # Import the Supabase client getter
# Replace old model imports with these:
from app.models.user import UserCreateAPI, UserLoginAPI, AuthResponseAPI

router = APIRouter()

@router.post("/register", response_model=AuthResponseAPI, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreateAPI, supabase: Client = Depends(get_supabase_client)):
    '''
    Registers a new user using Supabase Auth.
    '''
    try:
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })

        print(f"Supabase sign_up response: {response}")

        if response.user and response.user.id:
            # User created, but might require email confirmation depending on Supabase settings
            if response.session: # Session is typically returned if email confirmation is off or auto-confirmed
                 return AuthResponseAPI(
                    message="User registered successfully and logged in.",
                    user_id=str(response.user.id),
                    access_token=response.session.access_token
                )
            else: # User created, but email confirmation might be pending
                return AuthResponseAPI(
                    message="User registered. Please check your email to confirm registration.",
                    user_id=str(response.user.id)
                )
        elif response.error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.error.message)
        else:
            # This case should ideally not be reached if Supabase client behaves as expected
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during registration.")

    except HTTPException as e:
        # Re-raise HTTPExceptions directly
        raise e
    except Exception as e:
        # Catch any other unexpected errors (e.g., network issues with Supabase)
        print(f"Error during user registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/login", response_model=AuthResponseAPI)
async def login_user(user_data: UserLoginAPI, supabase: Client = Depends(get_supabase_client)):
    '''
    Logs in an existing user using Supabase Auth.
    '''
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })

        print(f"Supabase sign_in response: {response}")

        if response.session and response.session.user and response.session.access_token:
            return AuthResponseAPI(
                message="User logged in successfully.",
                user_id=str(response.session.user.id),
                access_token=response.session.access_token
            )
        elif response.error:
            # Common errors: "Invalid login credentials", "Email not confirmed"
            detail = response.error.message
            if "Email not confirmed" in detail:
                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed. Please check your inbox.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail or "Invalid login credentials.")
        else:
            # This case should ideally not be reached
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during login.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during user login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

# Note: Doctor registration/login might need separate handling if they are a different Supabase user type
# or if additional profile setup is required upon registration (e.g., creating a 'doctors' table entry).
# For now, this assumes doctors use the same user pool and auth flow.
# If you have specific "doctor" roles or profiles, you'd typically:
# 1. Register them as a normal user.
# 2. After successful registration, create an entry in a 'doctors' table associated with their user_id.
# 3. Potentially assign a custom claim/role via Supabase functions if needed for row-level security.
