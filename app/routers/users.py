# At the top of app/routers/users.py
import traceback
# ... other imports like fastapi, uuid, etc. ...
from fastapi import APIRouter, HTTPException, status, Depends # Removed Path as it's no longer used for user_id
from typing import List, Optional # Keep these
import uuid

from app.core import get_supabase_client, get_current_authenticated_user, AuthenticatedUser # Updated imports
from supabase import Client

from app.models.user import UserProfileDB, UserProfileCreate, UserProfileUpdate
from app.models.routine import FullRoutineDetail

from app.services.prompt_service import PromptPreparationService
from app.services.gemini_service import GeminiService
from app.services.routine_service import RoutineAssemblyService


router = APIRouter(
    tags=["users"]
)

# Removed: async def get_current_user_id_from_path(user_id: uuid.UUID = Path(...)) -> uuid.UUID:

@router.post("/me/profile", response_model=UserProfileDB, status_code=status.HTTP_201_CREATED)
async def create_or_update_my_user_profile( # Renamed function
    profile_data: UserProfileCreate,
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user), # Use new auth dep
    supabase: Client = Depends(get_supabase_client)
):
    '''
    Creates or updates the currently authenticated user's profile information.
    '''
    user_id = current_user.id # Get user_id from token
    print(f"Attempting to create/update profile for authenticated user_id: {user_id}")

    profile_dict = profile_data.model_dump()
    profile_dict["user_id"] = str(user_id)
    # profile_dict["email"] = current_user.email # Optionally set email from token if model expects it and it's not auto-set by DB trigger or similar

    try:
        response = supabase.table("user_profiles").upsert(profile_dict).execute()

        print(f"Supabase upsert response for user_profiles: {response}")

        if response.data:
            # Email is already in current_user.email from token
            return UserProfileDB(**response.data[0], email=current_user.email)
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


@router.get("/me/profile", response_model=UserProfileDB) # This was already updated, shown for context
async def get_my_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user),
    supabase: Client = Depends(get_supabase_client)
):
    '''
    Retrieves the profile information of the currently authenticated user.
    '''
    user_id = current_user.id
    print(f"Attempting to retrieve profile for authenticated user_id: {user_id}")
    try:
        # This is the block we are wrapping
        print(f"DEBUG: Supabase client object in get_my_user_profile: {supabase}") # Debug client
        profile_response = supabase.table("user_profiles").select("*").eq("user_id", str(user_id)).single().execute()
        print(f"DEBUG: Supabase select response for user_profiles: {profile_response}") # Debug response

        if profile_response.data:
            return UserProfileDB(**profile_response.data, email=current_user.email)

        # Handling cases where .single() might not find data or errors occur
        # (though .single() usually errors if not exactly one row, or data is None if maybe_single())
        # The supabase-py library might raise specific exceptions for "not found" with .single()
        # or if response.error has content.

        # Check for explicit error in response, even if no exception was raised by .execute()
        if profile_response.error:
            print(f"!!!! DATABASE QUERY ERROR (Supabase response.error) !!!!")
            print(f"Error type: PostgrestAPIError (presumed)") # Or whatever type it is
            print(f"Error details: {profile_response.error.message}")
            print(f"Error code: {profile_response.error.code}")
            print(f"Error hint: {profile_response.error.hint}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database query error: {profile_response.error.message}")

        # If no data and no explicit error, it implies .single() didn't find the row.
        # This should ideally be caught by specific exceptions if the library raises them,
        # but as a fallback:
        if not profile_response.data:
             print(f"!!!! DATABASE QUERY NO DATA !!!! Profile not found for user {user_id} (PGRST116 expected if .single() fails to find).")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found for user {user_id}.")

        # This part should ideally not be reached if the above conditions cover all scenarios
        # or if supabase-py raises exceptions for errors from .single().execute()
        # For safety, keeping a generic 404 if somehow we get here with no data.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found for user {user_id} (unexpected state).")

    except HTTPException as e_http: # Re-raise HTTPExceptions we've thrown
        raise e_http
    except Exception as e: # Catch any other exceptions (from Supabase client, Pydantic, etc.)
        print(f"!!!! DATABASE QUERY FAILED (General Exception) !!!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}") # This will print the full traceback to console
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {type(e).__name__} - Check server logs for traceback.")


@router.post("/me/generate-routine", response_model=FullRoutineDetail) # Changed path
async def generate_my_user_routine( # Renamed function
    current_user: AuthenticatedUser = Depends(get_current_authenticated_user), # Use new auth dep
    prompt_service: PromptPreparationService = Depends(PromptPreparationService),
    gemini_service: GeminiService = Depends(GeminiService),
    routine_assembly_service: RoutineAssemblyService = Depends(RoutineAssemblyService)
):
    '''
    Generates a personalized gym routine for the currently authenticated user.
    '''
    user_id = current_user.id # Get user_id from token
    print(f"User {user_id}: Received request to generate routine for authenticated user.")
    try:
        gemini_prompt = await prompt_service.prepare_gemini_prompt(user_id) # Services use user_id
        ai_generated_routine = await gemini_service.generate_routine(gemini_prompt)
        full_routine_details = await routine_assembly_service.assemble_full_routine(user_id, ai_generated_routine)
        return full_routine_details
    except ValueError as e: # Specific errors from services might be ValueErrors
        print(f"ValueError during routine generation for user {user_id}: {e}")
        # Check if it's a "not found" type error or something else
        if "not found" in str(e).lower() or "could not fetch" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e: # Gemini service might raise RuntimeError for critical failures
        print(f"RuntimeError during routine generation for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        print(f"Unexpected exception during routine generation for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while generating the routine.")
