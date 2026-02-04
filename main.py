from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import planner

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def read_root():
    return {"message": "Welcome to Family Planner AI", "status": "running"}

# Include routers
app.include_router(planner.router, prefix="/api/v1/planner", tags=["planner"])

if __name__ == "__main__":
    import uvicorn
    # Reload for development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
