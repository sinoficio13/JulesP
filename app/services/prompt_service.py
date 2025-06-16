import uuid
from typing import List, Dict, Any
from app.core import get_supabase_client # Import Supabase client
from supabase import Client # For type hinting
# Import Pydantic models if needed for structuring data within the service, though it mostly returns dicts for the prompt
# from app.models.user import UserProfileDB, MedicalInfoDB

class PromptPreparationService:
    def __init__(self):
        pass # Client obtained per-method or could be injected if service is a FastAPI dependency

    async def _get_user_data(self, user_id: uuid.UUID, supabase: Client) -> Dict[str, Any]:
        print(f"PromptService: Fetching user profile for {user_id} from Supabase")
        try:
            # Fetch from user_profiles table
            # Assuming UserProfileDB model fields: objectives, experience_level, preferences
            response = supabase.table("user_profiles").select("objectives, experience_level, preferences").eq("user_id", str(user_id)).single().execute()

            if response.data:
                # Add user_id to the returned dict as it's used in the prompt structure
                user_profile_data = response.data
                user_profile_data["user_id"] = str(user_id)
                return user_profile_data
            elif response.error and "PGRST116" in response.error.message: # Row not found
                print(f"PromptService: User profile not found for {user_id}. Using default/empty data.")
                # Return a default structure or raise an error depending on desired behavior
                # For prompt generation, providing default/empty values might be better than failing.
                return {"user_id": str(user_id), "objectives": [], "experience_level": "unknown", "preferences": {}}
            elif response.error:
                print(f"Supabase error fetching user profile for {user_id}: {response.error.message}")
                raise ValueError(f"Could not fetch user profile: {response.error.message}") # Or return default
            else: # No data, no error (should be caught by PGRST116 with .single())
                print(f"PromptService: User profile not found for {user_id} (no data, no error). Using default/empty data.")
                return {"user_id": str(user_id), "objectives": [], "experience_level": "unknown", "preferences": {}}
        except Exception as e:
            print(f"Exception fetching user profile for {user_id}: {e}")
            # Depending on strictness, either raise or return default values
            raise ValueError(f"Exception fetching user profile: {str(e)}")


    async def _get_medical_info(self, user_id: uuid.UUID, supabase: Client) -> Dict[str, Any]:
        print(f"PromptService: Fetching medical info for user {user_id} from Supabase")
        try:
            # Fetch latest medical record for the user.
            # Assuming MedicalInfoDB model fields: conditions, limitations, recommendations
            # If multiple records exist, logic to pick the "active" or "latest" one might be needed.
            # For now, let's assume we take the most recent one if a 'created_at' field exists and is maintained.
            # Or, if only one record is expected per user from the doctors' endpoint, a simple select is fine.
            # The current doctors.py GET returns a list, so let's fetch all and potentially process.
            # For the prompt, we probably want a consolidated view or the most relevant.
            # Let's assume for now we take the first record if multiple exist, or an empty dict if none.

            # Fetch all records for the user (as GET in doctors.py returns List[MedicalInfoDB])
            response = supabase.table("medical_records").select("conditions, limitations, recommendations").eq("user_id", str(user_id)).execute() # order by created_at desc if available

            if response.data:
                # For the prompt, we need a single consolidated record.
                # This example takes the first record found. More sophisticated merging or selection might be needed.
                # E.g., concatenating all conditions/limitations from multiple records.
                # For simplicity, using the first record:
                first_record = response.data[0]
                return {
                    "conditions": first_record.get("conditions"),
                    "limitations": first_record.get("limitations"),
                    "recommendations": first_record.get("recommendations")
                }
            elif response.error:
                print(f"Supabase error fetching medical info for {user_id}: {response.error.message}")
                # Return empty/default rather than failing prompt generation
                return {"conditions": [], "limitations": [], "recommendations": ""}
            else: # No data, no error
                print(f"PromptService: No medical records found for user {user_id}.")
                return {"conditions": [], "limitations": [], "recommendations": ""}
        except Exception as e:
            print(f"Exception fetching medical info for {user_id}: {e}")
            # Return empty/default values
            return {"conditions": [], "limitations": [], "recommendations": ""}

    async def _get_available_exercises(self, supabase: Client) -> List[Dict[str, Any]]:
        # This method is already updated to use Supabase, keep as is.
        print("PromptService: Fetching available exercises from Supabase")
        try:
            response = supabase.table("exercises").select("name").execute()
            if response.data:
                return response.data
            elif response.error:
                print(f"Supabase error fetching exercises: {response.error}")
                return []
            return []
        except Exception as e:
            print(f"Exception fetching exercises from Supabase: {e}")
            return []

    async def prepare_gemini_prompt(self, user_id: uuid.UUID) -> Dict[str, Any]:
        supabase_client = get_supabase_client() # Obtain client instance
        print(f"PromptService: Preparing Gemini prompt for user {user_id} using Supabase data.")

        try:
            user_data = await self._get_user_data(user_id, supabase_client)
            medical_info = await self._get_medical_info(user_id, supabase_client)
        except ValueError as e: # Catch errors from _get_user_data or _get_medical_info if they raise critical errors
            print(f"Critical error fetching user/medical data for prompt: {e}")
            # Handle this critical failure, perhaps by raising an HTTPException if this service is a FastAPI dependency
            # For now, re-raise to be caught by the router
            raise

        available_exercises_data = await self._get_available_exercises(supabase_client)
        exercise_names = [ex["name"] for ex in available_exercises_data if "name" in ex]

        prompt_data = {
            "user_profile": {
                "user_id": user_data.get("user_id"), # Will be present from _get_user_data
                "goals": user_data.get("objectives"),
                "experience_level": user_data.get("experience_level"),
                "preferences": user_data.get("preferences")
            },
            "medical_information": {
                "conditions": medical_info.get("conditions"),
                "limitations": medical_info.get("limitations"),
                "physician_recommendations": medical_info.get("recommendations")
            },
            "exercise_database": exercise_names,
            "output_format_instructions": { /* ... same as before ... */ },
            "request_specifics": { /* ... same as before ... */ }
        }
        # Copying the output_format_instructions and request_specifics from previous version for brevity
        prompt_data["output_format_instructions"] = {
                "type": "JSON",
                "schema": {
                    "days": [
                        {
                            "day_of_week": "e.g., Monday",
                            "focus": "e.g., Full Body Strength",
                            "exercises": [
                                {
                                    "exercise_name": "Name of the exercise from exercise_database",
                                    "sets": "Number of sets (e.g., 3)",
                                    "reps": "Repetitions (e.g., '8-12' or 10)",
                                    "rest_period_seconds": "Rest time in seconds (e.g., 60)",
                                    "notes_specifics_ia": "Specific instructions or modifications from AI based on medical info/goals."
                                }
                            ]
                        }
                    ]
                }
            }
        prompt_data["request_specifics"] = {
                "duration_weeks": 4,
                "days_per_week": 3
            }

        print(f"PromptService: Gemini prompt fully prepared for user {user_id} using Supabase data.")
        return prompt_data
