from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import PlannerRequest, PlannerResponse
from app.core.security import verify_api_key
from app.graph.workflow import create_graph
from app.core.redis import redis_manager

router = APIRouter()

# Graph will be instantiated dynamically per request or cached, considering we need the globally initialized checkpointer.
# Alternatively, since create_graph takes the checkpointer, we can construct the graph locally or lazily.

@router.post("/chat", response_model=PlannerResponse)
async def chat_with_planner(
    request: PlannerRequest, 
    api_key: str = Depends(verify_api_key)
):
    """
    Family Planner 에이전트와 상호작용합니다.
    """
    try:
        # Create or Get the compiled workflow with the Redis checkpointer
        graph = create_graph(checkpointer=redis_manager.checkpointer)
        
        # Room ID and User ID combined to form thread uniqueness
        thread_id = f"{request.user_id}_{request.room_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Load existing state if available
        # But we only need to pass messages for a new turn. 
        # The checkpointer automatically loads previous history and merges the new input.
        # However, for a user's first query in a thread, `user_preferences` and `plan` may need initializing.
        
        current_state = await graph.aget_state(config)
        
        if current_state.values:
            # We already have a state for this thread, so we only need to append the new message
            # The structure for resuming should just send the list of new messages
            new_state_input = {
                "messages": [("user", request.message)]
            }
        else:
            # First time running this thread, we need to provide the complete initial state schema
            new_state_input = {
                "messages": [("user", request.message)],
                "user_preferences": {},  # 실제 앱에서는 DB에서 불러옵니다.
                "plan": ""
            }
        
        # 그래프 실행
        # 참고: 실제 비동기 환경에서는 ainvoke를 사용합니다.
        result = await graph.ainvoke(new_state_input, config=config)
        
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
