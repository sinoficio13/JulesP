# In app/services/gemini_service.py
from typing import Dict, Any, List, Optional # Optional moved here
import json
import os # Keep os for direct getenv if needed, though settings is preferred
import google.generativeai as genai # Import the library
from google.generativeai.types import GenerationConfig # For generation config
from pydantic import BaseModel, ValidationError, Field # Optional removed here
from app.core.config import settings

# --- Pydantic Models for Gemini Response Validation ---
class GeminiExercise(BaseModel):
    exercise_name: str
    sets: Any # Can be int or str like "3" or "As prescribed"
    reps: Any # Can be str like "8-12" or int like 10
    rest_period_seconds: Any # Often int, but AI might return string
    notes_specifics_ia: Optional[str] = None

class GeminiDailyRoutine(BaseModel):
    day_of_week: str
    focus: Optional[str] = None
    exercises: List[GeminiExercise]

class GeminiRoutineResponse(BaseModel):
    days: List[GeminiDailyRoutine]
    # Potentially other top-level fields if requested from Gemini
    # routine_name: Optional[str] = None
# --- End Pydantic Models ---

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        self.generation_config = GenerationConfig(
            # Ensure Gemini attempts to output JSON if the model supports it explicitly
            # For some models, you might specify response_mime_type="application/json"
            # Temperature, top_k, top_p can also be set here.
            # Let's keep it simple for now.
            temperature=0.7 # Example temperature
        )


        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. GeminiService will not be functional for real calls.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name='gemini-1.0-pro', # Changed model name
                    generation_config=self.generation_config
                )
                print("GeminiService initialized successfully with GenerativeModel and generation_config.")
            except Exception as e:
                print(f"Error initializing Gemini GenerativeModel: {e}")

        if not self.model:
             print("GeminiService: Model not initialized. Calls to generate_routine will fail if mock is removed.")

    async def generate_routine(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.model:
            print("GeminiService: Model not available. Cannot make API call.")
            # Depending on desired behavior, either raise an error or return a fallback.
            # For now, let's raise an error if the model isn't configured for a real call.
            raise RuntimeError("GeminiService model is not configured. Check API key and initialization.")

        print(f"GeminiService: Sending prompt to Gemini API. Prompt type: {type(prompt_data)}")
        # The prompt_data is a Python dict. The google-generativeai library typically handles
        # serialization of dicts/lists of Parts. We need to ensure our prompt_data is structured
        # as a valid "Content" part for the API. Usually, just passing the dict works if it's simple text,
        # or a list of parts if it's more complex (e.g. multimodal).
        # Our prompt is a complex JSON structure. We should send it as a single text block that is a JSON string.

        prompt_json_string = json.dumps(prompt_data)

        try:
            print(f"GeminiService: Attempting to generate content with Gemini. Prompt length: {len(prompt_json_string)}")
            # print(f"First 500 chars of prompt sent to Gemini: {prompt_json_string[:500]}") # For debugging

            # response = await self.model.generate_content_async(prompt_data) # If library handles dict directly
            response = await self.model.generate_content_async(prompt_json_string) # Sending JSON string

            # Debug: Print the raw response text
            # print(f"Gemini RAW response text: {response.text}")

            # Gemini's response.text should be the JSON string we asked for.
            # It's crucial that the prompt clearly instructs Gemini to return a JSON.
            if not response.text:
                print("GeminiService Error: Received empty response text from API.")
                raise ValueError("Gemini API returned an empty response.")

            # Parse the JSON string from Gemini's response
            try:
                generated_routine_dict = json.loads(response.text)
            except json.JSONDecodeError as e:
                print(f"GeminiService Error: Failed to decode JSON from Gemini response. Error: {e}")
                print(f"Gemini response text that failed parsing: {response.text}")
                raise ValueError(f"Invalid JSON response from Gemini: {e}")

            # Validate the structure of the parsed dictionary using Pydantic
            try:
                validated_response = GeminiRoutineResponse(**generated_routine_dict)
                print("GeminiService: Successfully generated and validated routine from Gemini.")
                return validated_response.model_dump() # Return as dict
            except ValidationError as e:
                print(f"GeminiService Error: Gemini response failed Pydantic validation. Errors: {e.errors()}")
                print(f"Data that failed validation: {generated_routine_dict}")
                # Optionally, you could try to salvage parts of the data or return a specific error structure
                raise ValueError(f"Gemini response structure validation failed: {e.errors()}")

        except Exception as e:
            # This catches errors from generate_content_async (e.g., API errors, network issues)
            # or errors raised from our handling above.
            print(f"GeminiService Error: An exception occurred during Gemini API call or response processing: {e}")
            # Consider specific error types from google.generativeai.types.generation_types if needed
            # e.g., BlockedPromptException, StopCandidateException
            # from google.generativeai.types import BlockedPromptException (or similar, check specific library version)
            # if isinstance(e, BlockedPromptException):
            #     print(f"Gemini prompt was blocked. Reason: {e}") # Access specific attributes of the exception
            #     raise ValueError(f"Prompt blocked by Gemini: {e}")
            raise RuntimeError(f"Failed to generate routine via Gemini: {str(e)}")
