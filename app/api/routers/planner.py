from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import PlannerRequest, PlannerResponse
from app.core.security import verify_api_key
from app.graph.workflow import create_graph

router = APIRouter()

# 그래프를 한 번 인스턴스화합니다 (상태에 따라 매번 생성해야 할 수도 있지만, 구조가 정적이라면 한 번만 생성).
graph = create_graph()

@router.post("/chat", response_model=PlannerResponse)
async def chat_with_planner(
    request: PlannerRequest, 
    api_key: str = Depends(verify_api_key)
):
    """
    Family Planner 에이전트와 상호작용합니다.
    """
    try:
        # 그래프를 위한 초기 상태
        initial_state = {
            "messages": [("user", request.message)],
            "user_preferences": {},  # 실제 앱에서는 DB에서 불러옵니다.
            "plan": ""
        }
        
        # 그래프 실행
        # 참고: 실제 비동기 환경에서는 ainvoke를 사용합니다.
        result = await graph.ainvoke(initial_state)
        
        # 마지막 메시지 내용 추출
        last_message = result["messages"][-1]
        raw_content = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # LangChain Gemini Integration 종종 문자열 대신 [{'type': 'text', 'text': '...'}] 리스트를 반환함
        if isinstance(raw_content, list):
            response_content = "".join([
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw_content
            ])
        else:
            response_content = str(raw_content)
            
        return PlannerResponse(
            response=response_content,
            plan=result.get("plan")
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
