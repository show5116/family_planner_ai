from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.services.market_service import generate_macro_briefing, generate_market_briefing

# 전역 스케줄러 인스턴스
scheduler = AsyncIOScheduler()

def setup_scheduler():
    """
    백그라운드 스케줄러 초기화 및 Job 등록을 수행합니다.
    - 매크로 지표 분석: 매 1시간 마다 실행
    - 일일 시황 브리핑: 매일 아침 7시 실행 (KST 기준)
    """
    # 1. 매크로 브리핑 (1시간 간격 실행)
    scheduler.add_job(
        generate_macro_briefing,
        'interval',
        hours=1,
        id='macro_briefing_job',
        replace_existing=True
    )
    
    # 2. 일일 전반적 시황 브리핑 (오전 7시 실행)
    scheduler.add_job(
        generate_market_briefing,
        'cron',
        hour=7,
        minute=0,
        id='market_briefing_job',
        replace_existing=True
    )
    
    logger.info("Background Job Scheduler initialized with jobs.")

def start_scheduler():
    """스케줄러 시작"""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started successfully.")

def shutdown_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
