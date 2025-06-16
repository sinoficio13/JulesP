from fastapi import FastAPI

# Import settings (though not directly used in main.py for this basic setup,
# it's good to have it initialized early if other parts of your app structure might need it globally)
from app.core.config import settings

# Import routers
from app.routers import auth, users, doctors # Add other routers as you create them

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Customize OpenAPI URL if needed
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["Users"])
app.include_router(doctors.router, prefix=settings.API_V1_STR + "/doctors", tags=["Doctors"])
# Add other routers here, for example:
# app.include_router(exercises.router, prefix=settings.API_V1_STR + "/exercises", tags=["Exercises"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."}

# Optional: Add any startup/shutdown events if needed
# @app.on_event("startup")
# async def startup_event():
#     # Initialize Supabase client or other resources
#     # from app.core.supabase_client import init_supabase_client
#     # init_supabase_client()
#     print("Application startup complete.")

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Clean up resources
#     print("Application shutdown complete.")

if __name__ == "__main__":
    import uvicorn
    # This is for local development running `python app/main.py`
    # For production, you'd typically use Gunicorn with Uvicorn workers,
    # or another ASGI server setup (e.g., via Render, Fly.io Procfile)
    uvicorn.run(app, host="0.0.0.0", port=8000)
