import re
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.graph.workflow import create_graph
from app.core.redis import redis_manager
from app.core.config import settings

# Placeholder function simulating reading 15 DB indicators
def get_latest_market_indicators():
    """
    TODO: 메인 NestJS 서버 API로부터 최신 15개 투자 지표를 가져오는 로직 구현 필요.
    지금은 더미 데이터를 반환.
    """
    return {
        "KOSPI": {"value": 2700.5, "change_rate": -0.5},
        "NASDAQ": {"value": 16400.2, "change_rate": 1.2},
        "USD_KRW": {"value": 1340.5, "change_rate": 0.1},
        "US10Y": {"value": 4.2, "change_rate": -0.05}
    }

async def trigger_agent_analysis(topic: str, instructions: str) -> str:
    """
    'analyst' 에이전트를 호출하여 주어진 주제와 지시사항에 따라 브리핑 텍스트를 생성합니다.
    """
    try:
        # We need a new thread for each background run so it doesn't pollute past history
        import uuid
        thread_id = f"background_analyst_{uuid.uuid4()}"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph = create_graph(checkpointer=redis_manager.checkpointer)
        
        indicators = get_latest_market_indicators()
        
        prompt_message = f"""
        [지시사항]
        {instructions}
        
        [주제]
        {topic}
        
        [현재 보유 중인 최신 지표 데이터 (참고용)]
        {indicators}
        """
        
        new_state_input = {
            "messages": [("user", prompt_message)],
            "user_preferences": {},  
            "plan": "",
            "current_agent": "analyst"
        }
        
        result = await graph.ainvoke(new_state_input, config=config)
        
        last_message = result["messages"][-1]
        raw_content = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        if isinstance(raw_content, list):
            response_content = "".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw_content
            ])
        else:
            response_content = str(raw_content)
            
        # 프론트엔드 출력을 위해 마크다운(bold, headers 등) 완전 제거 (Sanitization)
        sanitized_content = re.sub(r'[*#]', '', response_content)
        return sanitized_content
        
    except Exception as e:
        logger.error(f"Failed to generate analysis from agent: {e}")
        return "브리핑을 생성하는 중 오류가 발생했습니다."

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.RequestError)
)
async def push_to_nestjs(briefing_type: str, title: str, content: str):
    """
    작성 완료된 브리핑을 NestJS 서버에 전송합니다. 실패 시 최대 3번 재시도합니다.
    """
    # NOTE: URL needs to be configured based on NestJS location
    webhook_url = "http://host.docker.internal:3000/api/market-briefing" 
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": settings.APP_API_KEY
    }
    payload = {
        "type": briefing_type,
        "title": title,
        "content": content
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logger.info(f"Successfully pushed {briefing_type} briefing to NestJS.")
            else:
                logger.error(f"NestJS Webhook Failed ({response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"Local request to NestJS failed: {e}")

async def generate_macro_briefing():
    """
    1시간 주기: 매크로 분석
    """
    logger.info("Starting background execution: Macro Briefing")
    instructions = "현재 제공된 지표들(특히 금리, 환율, VIX 등)의 현재 변동 이유를 파악하고, 최신 경제 뉴스를 웹 검색하여 현재 거시경제 매크로 동향을 분석해 주세요."
    content = await trigger_agent_analysis("매크로(거시경제) 동향", instructions)
    await push_to_nestjs("MACRO", "매크로 동향 현황 업데이트", content)

async def generate_market_briefing():
    """
    1일 1회(아침 7시): 시황 분석 (국내 및 뉴욕 증시)
    """
    logger.info("Starting background execution: Market Briefing")
    instructions = "어제 하루 및 오늘 새벽 동안의 뉴욕 증시와 국내 증시의 마감 시황을 웹 검색하여 종합적으로 분석해 주세요."
    content = await trigger_agent_analysis("국내 및 글로벌 증시 시황", instructions)
    await push_to_nestjs("MARKET", "글로벌 증시 시황 업데이트", content)
