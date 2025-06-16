from fastapi import APIRouter, HTTPException, status, Depends # Removed Path
from typing import List, Optional # Keep these
import uuid

from app.core import get_supabase_client # Import Supabase client
from supabase import Client # For type hinting
from app.core import get_current_authenticated_user, AuthenticatedUser # Import the new dependency and model

# Import the new UserProfile models
from app.models.user import UserProfileDB, UserProfileCreate, UserProfileUpdate
from app.models.routine import FullRoutineDetail # For routine generation endpoint

# Services (assuming they will be updated later to fetch real data for prompts)
from app.services.prompt_service import PromptPreparationService
from app.services.gemini_service import GeminiService
from app.services.routine_service import RoutineAssemblyService


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Placeholder for actual authentication (e.g., validating JWT from Supabase)
# For now, we'll just use user_id from path, assuming it's an authenticated user.
# In a real app, you'd have a dependency that extracts user_id from a valid token.
# async def get_current_user_id_from_path(user_id: uuid.UUID = Path(...)) -> uuid.UUID: # REMOVED
    # Here, you might add checks if the user_id from path matches an authenticated user from a token
    # For this step, we just return it.
    # return user_id

@router.post("/{user_id}/profile", response_model=UserProfileDB, status_code=status.HTTP_201_CREATED)
async def create_or_update_user_profile(
    profile_data: UserProfileCreate, # Use UserProfileCreate for payload
    user_id: uuid.UUID = Depends(get_current_user_id_from_path), # Get user_id from path (simulating auth) # This will be updated next
    supabase: Client = Depends(get_supabase_client)
):
    '''
    Creates or updates a user's profile information (objectives, experience, preferences).
    Supabase's `upsert` is useful here.
    The user_id from the path is considered the authenticated user.
    '''
    print(f"Attempting to create/update profile for user_id: {user_id}")

    profile_dict = profile_data.model_dump()
    profile_dict["user_id"] = str(user_id) # Ensure user_id is in the dict for upsert

    try:
        # Upsert will insert if no row with user_id exists, or update if it does.
        response = supabase.table("user_profiles").upsert(profile_dict).execute()

        print(f"Supabase upsert response for user_profiles: {response}")

        if response.data:
            # Fetch the possibly updated/inserted data to return it, including any server-set fields
            # Upsert often returns the modified data directly in response.data[0]
            # We also add email from auth.users as an example of combining data
            auth_user_response = supabase.auth.admin.get_user_by_id(str(user_id)) # Requires service_role key
            email = auth_user_response.user.email if auth_user_response.user else None

            return UserProfileDB(**response.data[0], email=email)
        elif response.error:
            print(f"Supabase error: {response.error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.error.message)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error during profile update.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating/updating user profile for {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Update GET /users/{user_id}/profile to /users/me/profile
@router.get("/me/profile", response_model=UserProfileDB) # Changed path
async def get_my_user_profile( # Renamed function for clarity
    # user_id: uuid.UUID = Depends(get_current_user_id_from_path), # REMOVE this line
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user), # ADD this line
    supabase: Client = Depends(get_supabase_client)
):
    '''
    Retrieves the profile information of the currently authenticated user.
    '''
    user_id = current_user.id # Get user_id from the authenticated user's token
    print(f"Attempting to retrieve profile for authenticated user_id: {user_id}")
    try:
        # Fetch profile from user_profiles table
        profile_response = supabase.table("user_profiles").select("*").eq("user_id", str(user_id)).single().execute()

        print(f"Supabase select response for user_profiles: {profile_response}")

        if profile_response.data:
            # Email is already in current_user from the token, so no need for admin call here if it's sufficient
            return UserProfileDB(**profile_response.data, email=current_user.email)
        elif profile_response.error and "PGRST116" in profile_response.error.message: # PGRST116: Row not found
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found for user {user_id}.")
        elif profile_response.error:
            print(f"Supabase error: {profile_response.error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=profile_response.error.message)
        else: # Should not happen if .single() is used and no error, but as a safeguard
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found for user {user_id}.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving user profile for {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Keep the existing generate-routine endpoint, it will be updated later
# to use the Supabase-backed data via the services.
@router.post("/{user_id}/generate-routine", response_model=FullRoutineDetail)
async def generate_user_routine(
    user_id: uuid.UUID = Depends(get_current_user_id_from_path), # This will also need to change to use current_user.id
    prompt_service: PromptPreparationService = Depends(PromptPreparationService),
    gemini_service: GeminiService = Depends(GeminiService),
    routine_assembly_service: RoutineAssemblyService = Depends(RoutineAssemblyService)
):
    print(f"User {user_id}: Received request to generate routine (using existing mock services).")
    try:
        gemini_prompt = await prompt_service.prepare_gemini_prompt(user_id)
        ai_generated_routine = await gemini_service.generate_routine(gemini_prompt)
        full_routine_details = await routine_assembly_service.assemble_full_routine(user_id, ai_generated_routine)
        return full_routine_details
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error generating routine.")
