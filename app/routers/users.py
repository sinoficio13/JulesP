from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
import uuid

# Assuming models are in app.models
from app.models.user import User # Import User model
from app.models.routine import FullRoutineDetail # For future routine generation endpoint
from pydantic import BaseModel # Added for UserPreferencesUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"] # Tag for API documentation
)

# In-memory storage for demonstration purposes.
# Replace with Supabase interaction later.
db_users: dict[uuid.UUID, User] = {}

# Dependency to "authenticate" user (placeholder)
async def get_current_user(user_id: uuid.UUID) -> User:
    # In a real app, this would involve token validation and fetching user from DB
    # For now, we'll simulate by checking if a user_id exists in our mock DB
    # user = db_users.get(user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # For this placeholder, we'll just create a dummy user object if not found,
    # or assume any UUID is a valid "authenticated" user for now.
    print(f"Mock authentication for user_id: {user_id}")
    return User(user_id=user_id, email=f"{user_id}@example.com")

class UserPreferencesUpdate(BaseModel):
    objectives: Optional[List[str]] = None
    experience_level: Optional[str] = None
    preferences: Optional[dict] = None


@router.post("/{user_id}/preferences", response_model=User)
async def update_user_preferences(
    user_id: uuid.UUID,
    prefs_payload: UserPreferencesUpdate,
    # current_user: User = Depends(get_current_user) # Placeholder for auth
):
    '''
    Allows a user to update their training objectives, experience level, and general preferences.
    - **user_id**: The ID of the user whose preferences are being updated.
    - **prefs_payload**: The preferences data.
    '''
    print(f"User {user_id} attempting to update preferences.")

    # In a real implementation, you would:
    # 1. Verify the user (current_user or via token) is authorized to update their own profile.
    # 2. Fetch the user's current data from Supabase.
    # 3. Update the fields provided in prefs_payload.
    # 4. Save the updated user data back to Supabase.

    # For now, fetch or create user in mock DB and update
    user = db_users.get(user_id)
    if not user:
        # If user doesn't exist in mock DB, create a new one (for demo purposes)
        # In a real app, you'd likely get a 404 or this endpoint might be part of a larger user profile update
        user = User(user_id=user_id, email=f"{user_id}@example.com") # Basic user
        db_users[user_id] = user
        print(f"User {user_id} not found in mock DB, created a new entry.")


    if prefs_payload.objectives is not None:
        user.objectives = prefs_payload.objectives
    if prefs_payload.experience_level is not None:
        user.experience_level = prefs_payload.experience_level
    if prefs_payload.preferences is not None:
        user.preferences = prefs_payload.preferences

    db_users[user_id] = user # Update mock DB

    print(f"Preferences updated for user {user_id}: {user.dict()}")
    return user

@router.get("/{user_id}/preferences", response_model=User)
async def get_user_preferences(
    user_id: uuid.UUID,
    # current_user: User = Depends(get_current_user) # Placeholder for auth
):
    '''
    Retrieves a user's training objectives, experience level, and general preferences.
    - **user_id**: The ID of the user whose preferences are being retrieved.
    '''
    print(f"Attempting to retrieve preferences for user {user_id}.")
    user = db_users.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found or no preferences set.")

    return user

# Placeholder for the routine generation endpoint, will be developed in a later step
# @router.post("/{user_id}/generate-routine", response_model=FullRoutineDetail)
# async def generate_user_routine(
#     user_id: uuid.UUID,
#     # current_user: User = Depends(get_current_user) # Placeholder for auth
# ):
#     # This will orchestrate calls to PromptPreparationService, GeminiService, and RoutineAssemblyService
#     # For now, returning a placeholder
#     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Routine generation not yet implemented.")
