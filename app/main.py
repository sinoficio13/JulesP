from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users, doctors

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS Configuration ---
# Define allowed origins.
# For development, you might allow localhost if your frontend runs there.
# For production, you should restrict this to your actual frontend domain(s).
# Using ["*"] is permissive and good for initial setup/testing, but update for production.
origins = [
    "http://localhost", # Common for local development (if frontend doesn't specify port)
    "http://localhost:3000", # Example for local React frontend
    "http://localhost:3001", # Example for another local frontend port
    "http://localhost:5173", # Example for local Vite/React frontend
    # "https://your-frontend-domain.com", # TODO: Add your production frontend domain here
    # "https://www.your-frontend-domain.com", # TODO: Add www version if applicable
]

# If you want to be very permissive initially (useful for easy testing, but less secure for production):
# origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make cross-origin requests.
    allow_credentials=True, # Allow cookies to be included in cross-origin requests. Useful if you ever use cookie-based auth.
    allow_methods=["*"],    # Allow all methods (GET, POST, PUT, DELETE, etc.). Or specify like ["GET", "POST"].
    allow_headers=["*"],    # Allow all headers. Or specify like ["Content-Type", "Authorization"].
)
# --- End CORS Configuration ---

# Include routers (as before)
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["Users"])
app.include_router(doctors.router, prefix=settings.API_V1_STR + "/doctors", tags=["Doctors"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."}

# Optional startup/shutdown events (as before)
# @app.on_event("startup")
# async def startup_event():
#     print("Application startup complete.")

# @app.on_event("shutdown")
# async def shutdown_event():
#     print("Application shutdown complete.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
