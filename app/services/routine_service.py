import uuid
from typing import Dict, Any, List

# Assuming models are in app.models
from app.models.routine import Routine, DailyRoutine, ExerciseInRoutine, FullRoutineDetail
from app.models.exercise import Exercise as ExerciseModel # Renaming to avoid confusion

# Placeholder for Supabase client/service import
# from app.core.supabase_client import get_supabase_client

class RoutineAssemblyService:
    def __init__(self):
        # self.supabase = get_supabase_client() # Initialize Supabase client
        # Mock database of exercises for now
        self._mock_exercise_db: Dict[str, ExerciseModel] = {
            "Squat": ExerciseModel(name="Squat", description="A compound, full-body exercise...", muscles_targeted=["quads", "glutes"], equipment_needed=["barbell"], precautions="Maintain proper form.", image_url="http://example.com/squat.jpg", video_url="http://example.com/squat.mp4"),
            "Bench Press": ExerciseModel(name="Bench Press", description="An upper body strength training exercise...", muscles_targeted=["chest", "triceps", "shoulders"], equipment_needed=["barbell", "bench"], precautions="Use a spotter for heavy weights.", image_url="http://example.com/bench.jpg", video_url="http://example.com/bench.mp4"),
            "Deadlift": ExerciseModel(name="Deadlift", description="A weight training exercise in which a loaded barbell or bar is lifted off the ground...", muscles_targeted=["back", "hamstrings", "glutes"], equipment_needed=["barbell"], precautions="Keep back straight.", image_url="http://example.com/deadlift.jpg", video_url="http://example.com/deadlift.mp4"),
            "Overhead Press (Dumbbell)": ExerciseModel(name="Overhead Press (Dumbbell)", description="A shoulder exercise...", muscles_targeted=["shoulders", "triceps"], equipment_needed=["dumbbells"], precautions="Avoid if shoulder pain.", image_url="http://example.com/ohp.jpg", video_url="http://example.com/ohp.mp4"),
            "Pull Up": ExerciseModel(name="Pull Up", description="An upper-body compound pulling exercise.", muscles_targeted=["back", "biceps"], equipment_needed=["pull-up bar"], precautions="Full range of motion.", image_url="http://example.com/pullup.jpg", video_url="http://example.com/pullup.mp4"),
            "Plank": ExerciseModel(name="Plank", description="An isometric core strength exercise...", muscles_targeted=["core"], equipment_needed=[], precautions="Keep body straight.", image_url="http://example.com/plank.jpg", video_url="http://example.com/plank.mp4"),
            "Bicep Curl": ExerciseModel(name="Bicep Curl", description="An isolation exercise for the biceps.", muscles_targeted=["biceps"], equipment_needed=["dumbbells"], precautions="Avoid swinging.", image_url="http://example.com/bicepcurl.jpg", video_url="http://example.com/bicepcurl.mp4"),
            "Tricep Extension": ExerciseModel(name="Tricep Extension", description="An isolation exercise for the triceps.", muscles_targeted=["triceps"], equipment_needed=["dumbbells"], precautions="Control the movement.", image_url="http://example.com/tricepext.jpg", video_url="http://example.com/tricepext.mp4"),
            "Leg Press": ExerciseModel(name="Leg Press", description="A compound weight training exercise...", muscles_targeted=["quads", "glutes", "hamstrings"], equipment_needed=["leg press machine"], precautions="Don't lock out knees.", image_url="http://example.com/legpress.jpg", video_url="http://example.com/legpress.mp4"),
            "Lat Pulldown": ExerciseModel(name="Lat Pulldown", description="A strength training exercise to develop the latissimus dorsi muscle.", muscles_targeted=["back", "biceps"], equipment_needed=["lat pulldown machine"], precautions="Pull towards upper chest.", image_url="http://example.com/latpulldown.jpg", video_url="http://example.com/latpulldown.mp4"),
        }
        print("RoutineAssemblyService initialized (mocked DB).")

    async def _get_exercise_details(self, exercise_name: str) -> ExerciseModel | None:
        # Mocked exercise detail fetching
        print(f"RoutineAssemblyService: Fetching details for exercise '{exercise_name}' (mocked)")
        # In real implementation, fetch from Supabase by name:
        # response = self.supabase.table("exercises").select("*").eq("name", exercise_name).single().execute()
        # if response.data:
        #     return ExerciseModel(**response.data)
        # return None
        return self._mock_exercise_db.get(exercise_name)

    async def assemble_full_routine(self, user_id: uuid.UUID, ai_generated_routine: Dict[str, Any]) -> FullRoutineDetail:
        print(f"RoutineAssemblyService: Assembling full routine for user {user_id}")

        detailed_daily_routines: List[DailyRoutine] = []

        for day_data in ai_generated_routine.get("days", []):
            detailed_exercises_in_day: List[ExerciseInRoutine] = []
            for ai_exercise in day_data.get("exercises", []):
                exercise_name = ai_exercise.get("exercise_name")
                if not exercise_name:
                    print(f"Warning: AI routine exercise missing name: {ai_exercise}")
                    continue

                exercise_details = await self._get_exercise_details(exercise_name)

                exercise_in_routine = ExerciseInRoutine(
                    name=exercise_name,
                    sets=ai_exercise.get("sets"),
                    reps=ai_exercise.get("reps"),
                    rest_period=str(ai_exercise.get("rest_period_seconds")) + " seconds" if ai_exercise.get("rest_period_seconds") else None, # Constructing from seconds
                    notes_specifics_ia=ai_exercise.get("notes_specifics_ia"),
                    # Populate with details from our DB
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
            routine_name=ai_generated_routine.get("routine_name", f"AI Routine for {user_id}"), # Example name
            # gemini_response_raw=ai_generated_routine, # Optionally store the raw AI output
            daily_routines=detailed_daily_routines
        )

        print(f"RoutineAssemblyService: Full routine assembled for user {user_id}: {full_routine.dict(exclude_none=True)}")
        return full_routine

# Example usage (for testing purposes)
# if __name__ == "__main__":
#     import asyncio
#     async def main_test():
#         service = RoutineAssemblyService()
#         test_user_id = uuid.uuid4()

#         # Mock AI response (similar to what GeminiService would return)
#         mock_ai_response = {
#             "days": [
#                 {
#                     "day_of_week": "Monday",
#                     "focus": "Test Full Body",
#                     "exercises": [
#                         {"exercise_name": "Squat", "sets": 3, "reps": "10", "rest_period_seconds": 60, "notes_specifics_ia": "Test note for Squat"},
#                         {"exercise_name": "Unknown Exercise", "sets": 2, "reps": "12", "rest_period_seconds": 45, "notes_specifics_ia": "Test note for Unknown"}
#                     ]
#                 }
#             ]
#         }

#         final_routine = await service.assemble_full_routine(test_user_id, mock_ai_response)
#         # print(final_routine.json(indent=2, exclude_none=True))

#     asyncio.run(main_test())
