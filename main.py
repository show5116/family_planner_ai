from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.handlers import setup_exception_handlers
from app.core.exceptions import BadRequestException
from app.core.middleware import RequestTracingMiddleware
from loguru import logger
from app.api.routers import planner, market
from app.core.redis import redis_manager
from app.core.scheduler import setup_scheduler, start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    
    # Redis 연결 시작
    logger.info("Initializing Application...")
    await redis_manager.connect()
    
    # 스케줄러 초기화 및 시작
    setup_scheduler()
    start_scheduler()
    
    yield
    
    # 앱 종료 시 스케줄러 및 Redis 연결 해제
    logger.info("Shutting down Application...")
    shutdown_scheduler()
    await redis_manager.disconnect()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Add Middlewares
app.add_middleware(RequestTracingMiddleware)

# Register all global exception handlers
setup_exception_handlers(app)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Family Planner AI 에이전트에 오신 것을 환영합니다", "status": "running"}

@app.get("/health")
def health_check():
    """Endpoint for infrastructure and external services to check health status."""
    return {"status": "ok"}

@app.get("/error-test")
def test_error():
    """Temporary endpoint to test AppException response format and logging."""
    raise BadRequestException(message="This is a test bad request error", details={"field": "test_field"})

# 라우터 포함
app.include_router(planner.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])

if __name__ == "__main__":
    import uvicorn
    # 개발을 위한 리로드 설정
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
