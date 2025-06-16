from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import uuid

class Exercise(BaseModel):
    exercise_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., example="Squat")
    description: Optional[str] = Field(None, example="A compound, full-body exercise...") # Made optional as per some DBs
    muscles_targeted: Optional[List[str]] = Field(None, example=["quadriceps", "glutes"])
    equipment_needed: Optional[List[str]] = Field(None, example=["barbell"])
    precautions: Optional[str] = Field(None, example="Maintain proper form to avoid back injury. Consult a doctor if you have knee issues.")
    image_url: Optional[HttpUrl] = Field(None, example="http://example.com/images/squat.jpg")
    video_url: Optional[HttpUrl] = Field(None, example="http://example.com/videos/squat.mp4")

    class Config:
        orm_mode = True
