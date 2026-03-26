from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from loguru import logger
from app.core.security import verify_api_key
from pydantic import BaseModel
from typing import Optional
from app.services.market_service import generate_macro_briefing, generate_market_briefing

router = APIRouter()

class TriggerRequest(BaseModel):
    category: str # "macro" or "market" or "all"

@router.post("/trigger")
async def trigger_market_analysis(
    request: TriggerRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    수동으로 백그라운드 스케줄러 대상이었던 시장/매크로 분석 에이전트를 작동시킵니다.
    테스트 및 관리자 용도로 사용됩니다.
    """
    try:
        cat = request.category.lower()
        if cat in ["macro", "all"]:
            logger.info("Manually scheduling Macro Briefing generation.")
            background_tasks.add_task(generate_macro_briefing)
        
        if cat in ["market", "all"]:
            logger.info("Manually scheduling Market Briefing generation.")
            background_tasks.add_task(generate_market_briefing)
            
        if cat not in ["macro", "market", "all"]:
            raise HTTPException(status_code=400, detail="Invalid category. Use 'macro', 'market', or 'all'.")

        return {"status": "accepted", "message": f"Triggered analysis for category: {cat}"}
    except Exception as e:
        logger.error(f"Failed to trigger analysis manually: {e}")
        raise HTTPException(status_code=500, detail=str(e))
