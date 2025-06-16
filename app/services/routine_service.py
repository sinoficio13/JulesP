import uuid
from typing import Dict, Any, List
from app.core import get_supabase_client # Import Supabase client
from supabase import Client # For type hinting
from app.models.routine import Routine, DailyRoutine, ExerciseInRoutine, FullRoutineDetail
from app.models.exercise import Exercise as ExerciseModel

class RoutineAssemblyService:
    def __init__(self):
        # self._mock_exercise_db is no longer needed as we fetch from Supabase
        print("RoutineAssemblyService initialized (will use Supabase for exercise details).")

    async def _get_exercise_details(self, exercise_name: str, supabase: Client) -> ExerciseModel | None:
        print(f"RoutineAssemblyService: Fetching details for exercise '{exercise_name}' from Supabase")
        try:
            response = supabase.table("exercises").select("*").eq("name", exercise_name).maybe_single().execute()
            # maybe_single() returns at most one row. If no row, data is None. If multiple, error.
            # Using maybe_single() as exercise names should ideally be unique.

            if response.data:
                return ExerciseModel(**response.data)
            elif response.error:
                # Log the error, but don't let it stop the whole routine assembly if one exercise fails.
                print(f"Supabase error fetching details for '{exercise_name}': {response.error.message}")
                return None
            return None # No data, no error
        except Exception as e:
            print(f"Exception fetching exercise details for '{exercise_name}' from Supabase: {e}")
            return None # Return None on other errors too

    async def assemble_full_routine(self, user_id: uuid.UUID, ai_generated_routine: Dict[str, Any]) -> FullRoutineDetail:
        supabase_client = get_supabase_client() # Obtain client instance
        print(f"RoutineAssemblyService: Assembling full routine for user {user_id}")

        detailed_daily_routines: List[DailyRoutine] = []

        for day_data in ai_generated_routine.get("days", []):
            detailed_exercises_in_day: List[ExerciseInRoutine] = []
            for ai_exercise in day_data.get("exercises", []):
                exercise_name = ai_exercise.get("exercise_name")
                if not exercise_name:
                    print(f"Warning: AI routine exercise missing name: {ai_exercise}")
                    continue

                exercise_details = await self._get_exercise_details(exercise_name, supabase_client) # Pass client

                exercise_in_routine = ExerciseInRoutine(
                    name=exercise_name,
                    sets=ai_exercise.get("sets"),
                    reps=ai_exercise.get("reps"),
                    rest_period=str(ai_exercise.get("rest_period_seconds")) + " seconds" if ai_exercise.get("rest_period_seconds") else None,
                    notes_specifics_ia=ai_exercise.get("notes_specifics_ia"),
                    description_detailed=exercise_details.description if exercise_details else "Description not found.",
                    precautions=exercise_details.precautions if exercise_details else "Precautions not available.",
                    image_url=str(exercise_details.image_url) if exercise_details and exercise_details.image_url else None,
                    video_url=str(exercise_details.video_url) if exercise_details and exercise_details.video_url else None,
                )
                detailed_exercises_in_day.append(exercise_in_routine)

            daily_routine = DailyRoutine(
                day=day_data.get("day_of_week"),
                focus=day_data.get("focus"),
                exercises=detailed_exercises_in_day
            )
            detailed_daily_routines.append(daily_routine)

        full_routine = FullRoutineDetail(
            user_id=user_id,
            routine_name=ai_generated_routine.get("routine_name", f"AI Routine for {user_id}"),
            daily_routines=detailed_daily_routines
        )

        print(f"RoutineAssemblyService: Full routine assembled for user {user_id} (exercise details from Supabase).")
        return full_routine
