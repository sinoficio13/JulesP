from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid # For User ID, Doctor ID if not handled by Supabase directly in model

class ProfileBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    # Common fields for both User and Doctor, if any
    # name: Optional[str] = Field(None, example="John Doe")

class User(ProfileBase):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    objectives: Optional[List[str]] = Field(None, example=["gain muscle", "lose weight"])
    experience_level: Optional[str] = Field(None, example="intermediate")
    preferences: Optional[dict] = Field(None, example={"preferred_gym_days": ["Mon", "Wed", "Fri"]})

    class Config:
        orm_mode = True

class Doctor(ProfileBase):
    doctor_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    # Specific fields for Doctor, if any
    # medical_license_id: Optional[str] = Field(None, example="MD12345")

    class Config:
        orm_mode = True

class MedicalInfo(BaseModel):
    medical_info_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    doctor_id: uuid.UUID # Or some reference to the doctor who provided the info
    conditions: Optional[List[str]] = Field(None, example=["hypertension", "past knee injury"])
    limitations: Optional[List[str]] = Field(None, example=["avoid high-impact exercises"])
    recommendations: Optional[str] = Field(None, example="Focus on low-impact cardio and strength training.")
    # relevant_medical_history: Optional[str] = None # Example of other fields

    class Config:
        orm_mode = True
