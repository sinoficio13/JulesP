from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from .exercise import Exercise # Assuming Exercise model is in exercise.py

class ExerciseInRoutine(BaseModel):
    # exercise_id: uuid.UUID # Reference to the Exercise model
    name: str # Name of the exercise, as returned by Gemini
    sets: Optional[int] = Field(None, example=3)
    reps: Optional[str] = Field(None, example="8-12") # Can be a range or specific number
    rest_period: Optional[str] = Field(None, example="60-90 seconds")
    notes_specifics_ia: Optional[str] = Field(None, example="Perform with controlled movement, focusing on form.")
    # These will be populated by the backend after fetching from DB
    description_detailed: Optional[str] = None
    precautions: Optional[str] = None
    image_url: Optional[str] = None # Using str as HttpUrl might be too strict if URLs are not always perfect
    video_url: Optional[str] = None

class DailyRoutine(BaseModel):
    day: str = Field(..., example="Monday")
    focus: Optional[str] = Field(None, example="Full Body Strength")
    exercises: List[ExerciseInRoutine] = []

class Routine(BaseModel):
    routine_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    routine_name: Optional[str] = Field(None, example="Beginner Strength Plan - Week 1")
    generated_by_ia: bool = Field(True)
    # The raw JSON response from Gemini might be stored for debugging or history
    # gemini_prompt: Optional[Dict[str, Any]] = None
    # gemini_response_raw: Optional[Dict[str, Any]] = None
    daily_routines: List[DailyRoutine] = []

    class Config:
        orm_mode = True

# This is the model that will be sent to the frontend,
# combining AI routine with DB exercise details.
class FullRoutineDetail(Routine):
    # daily_routines will contain ExerciseInRoutine which now includes details from DB
    pass
