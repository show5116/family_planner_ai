from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logging
from loguru import logger
from app.api.routers import planner

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Family Planner AI 에이전트에 오신 것을 환영합니다", "status": "running"}

# 라우터 포함
app.include_router(planner.router, prefix="/api/v1/planner", tags=["planner"])

if __name__ == "__main__":
    import uvicorn
    # 개발을 위한 리로드 설정
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
