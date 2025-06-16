from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import uuid

# Assuming models are in app.models
# Adjust the import path if your structure is different
from app.models.user import MedicalInfo, User, Doctor # Import necessary models

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"] # Tag for API documentation
)

# In-memory storage for demonstration purposes.
# Replace with Supabase interaction later.
db_medical_info: dict[uuid.UUID, MedicalInfo] = {}
db_users: dict[uuid.UUID, User] = {} # Assuming some users exist for association
db_doctors: dict[uuid.UUID, Doctor] = {} # Assuming some doctors exist

# Dependency to "authenticate" doctor (placeholder)
async def get_current_doctor(doctor_id: uuid.UUID) -> Doctor:
    # In a real app, this would involve token validation and fetching doctor from DB
    # For now, we'll simulate by checking if a doctor_id exists in our mock DB
    # doctor = db_doctors.get(doctor_id)
    # if not doctor:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    # For this placeholder, we'll just create a dummy doctor object if not found,
    # or assume any UUID is a valid "authenticated" doctor for now.
    # This part needs proper auth implementation later.
    print(f"Mock authentication for doctor_id: {doctor_id}")
    return Doctor(doctor_id=doctor_id, email=f"{doctor_id}@example.com")


@router.post("/{doctor_id}/users/{user_id}/medical-info", response_model=MedicalInfo, status_code=status.HTTP_201_CREATED)
async def record_user_medical_info(
    doctor_id: uuid.UUID,
    user_id: uuid.UUID,
    medical_info_payload: MedicalInfo,
    # current_doctor: Doctor = Depends(get_current_doctor) # Placeholder for auth
):
    '''
    Allows a doctor to record or update medical information for a specific user.
    - **doctor_id**: The ID of the doctor providing the information.
    - **user_id**: The ID of the user whose medical information is being recorded.
    - **medical_info_payload**: The medical information.
    '''
    print(f"Doctor {doctor_id} attempting to record medical info for user {user_id}")

    # Placeholder: Check if user exists (in a real app, query Supabase)
    # if user_id not in db_users:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found.")

    # In a real implementation, you would:
    # 1. Verify the doctor (current_doctor) is authorized.
    # 2. Verify the user (user_id) exists.
    # 3. Save/update the medical_info_payload in Supabase, associating it with user_id and doctor_id.

    # For now, just store it in the mock DB and ensure IDs match
    if medical_info_payload.user_id != user_id or medical_info_payload.doctor_id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID or Doctor ID in payload does not match path parameters."
        )

    db_medical_info[medical_info_payload.medical_info_id] = medical_info_payload
    print(f"Medical info {medical_info_payload.medical_info_id} recorded for user {user_id} by doctor {doctor_id}")

    return medical_info_payload

@router.get("/{doctor_id}/users/{user_id}/medical-info", response_model=MedicalInfo)
async def get_user_medical_info(
    doctor_id: uuid.UUID,
    user_id: uuid.UUID,
    # current_doctor: Doctor = Depends(get_current_doctor) # Placeholder for auth
):
    '''
    Allows a doctor to retrieve medical information for a specific user.
    - **doctor_id**: The ID of the doctor. (Used for auth/logging, actual data keyed by user_id usually)
    - **user_id**: The ID of the user whose medical information is being retrieved.
    '''
    print(f"Doctor {doctor_id} attempting to retrieve medical info for user {user_id}")

    # In a real implementation, query Supabase for medical info associated with user_id.
    # Ensure doctor has permission.

    # Mock retrieval: find the first record matching user_id
    for info in db_medical_info.values():
        if info.user_id == user_id:
            # Optionally, also check if info.doctor_id matches doctor_id if that's a business rule
            return info

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medical information not found for user {user_id}")
