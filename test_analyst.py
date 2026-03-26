import asyncio
from app.services.market_service import trigger_agent_analysis
from app.core.redis import redis_manager

async def test_analyst():
    await redis_manager.connect()
    
    print("------- AI MARKET ANALYST START -------")
    content = await trigger_agent_analysis(
        topic="매크로(거시경제) 동향", 
        instructions="제공된 지표의 특징을 잡아서 짧고 명확하게 뉴스 헤드라인처럼 3줄 요약해 줘."
    )
    print("\n------- RESULT -------")
    print(content)
    
    await redis_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_analyst())
