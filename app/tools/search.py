import os
import asyncio
from functools import partial
from loguru import logger
from tavily import TavilyClient

async def web_search(query: str, category: str = "general") -> str:
    """
    Tavily API를 이용하여 웹에서 최신 뉴스와 정보를 검색합니다.
    category에 따라 신뢰할 수 있는 특정 사이트로 검색 범위를 좁힙니다.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("TAVILY_API_KEY is not set in the environment variables.")
        return "Error: TAVILY_API_KEY 환경 변수가 설정되지 않았습니다. 검색을 수행할 수 없습니다."
        
    # 카테고리별 대상 도메인 설정
    include_domains = []
    if category == "macro":
        include_domains = ["investing.com", "stlouisfed.org"]
    elif category == "global":
        include_domains = ["finance.yahoo.com", "cnbc.com"]
    elif category == "domestic":
        include_domains = ["finance.naver.com", "hankyung.com", "yna.co.kr"]

    try:
        tavily = TavilyClient(api_key=api_key)
        logger.info(f"Performing web search for: '{query}' in category: '{category}' (domains: {include_domains})")
        
        # Search for context, focusing on news
        # Run synchronous blocking operation in a background thread
        search_func = partial(
            tavily.search,
            query=query, 
            search_depth="advanced",
            include_answer=True,
            include_domains=include_domains if include_domains else None,
            max_results=3
        )
        response = await asyncio.to_thread(search_func)
        
        # We can return the AI generated answer directly or a compilation of the results
        if response.get("answer"):
            result = f"[Search Answer]: {response['answer']}\n\n[Sources]:\n"
        else:
            result = "[Search Results]:\n"
            
        for idx, res in enumerate(response.get("results", [])):
            result += f"{idx+1}. {res.get('title', 'No Title')} - {res.get('url', '')}\n"
            result += f"   {res.get('content', '')[:200]}...\n"
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to perform web search using Tavily: {e}")
        return f"Error: 웹 검색 중 오류가 발생했습니다. ({str(e)})"
