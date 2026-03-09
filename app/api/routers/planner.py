from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.schemas import PlannerRequest, PlannerResponse
from app.core.security import verify_api_key
from app.graph.workflow import create_graph
from app.core.redis import redis_manager
from loguru import logger
import uuid
import asyncio

router = APIRouter()

async def apply_ttl_to_thread(thread_id: str, ttl_seconds: int = 3600):
    """
    Background task to apply TTL to all Redis keys associated with a specific LangGraph thread.
    LangGraph typically uses keys starting with 'checkpoint' or containing the thread_id.
    """
    try:
        if not redis_manager.connection:
            logger.warning("Redis connection not available for TTL application.")
            return

        # LangGraph Python Checkpointer uses keys like "checkpoint:<thread_id>:<checkpoint_id>"
        # or hashes where the thread_id is part of the key.
        # Checkpointer write delay mitigation
        await asyncio.sleep(1) # wait for LangGraph to finish all Redis persistence
        
        # In non-decode_responses mode, the pattern should be bytes
        pattern = bytes(f"*{thread_id}*", 'utf-8')
        
        logger.info(f"Starting TTL scan for pattern: {pattern}")
        cursor = 0
        expired_count = 0
        
        while True:
            cursor, keys = await redis_manager.connection.scan(cursor=cursor, match=pattern, count=100)
            logger.info(f"Scan returned cursor: {cursor}, found keys: {len(keys)}")
            for key in keys:
                await redis_manager.connection.expire(key, ttl_seconds)
                expired_count += 1
            if str(cursor) == "0" or cursor == 0:
                break
                
        logger.info(f"Successfully applied TTL of {ttl_seconds}s to {expired_count} keys for thread {thread_id}")
    except Exception as e:
        logger.error(f"Error applying TTL to thread {thread_id}: {e}")

# Graph will be instantiated dynamically per request or cached, considering we need the globally initialized checkpointer.
# Alternatively, since create_graph takes the checkpointer, we can construct the graph locally or lazily.

@router.post("/chat", response_model=PlannerResponse)
async def chat_with_planner(
    request: PlannerRequest, 
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Family Planner 에이전트와 상호작용합니다.
    """
    try:
        # Create or Get the compiled workflow with the Redis checkpointer
        graph = create_graph(checkpointer=redis_manager.checkpointer)
        
        # Room ID 생성 로직 (없으면 UUID 부여)
        current_room_id = request.room_id if request.room_id else str(uuid.uuid4())
        
        # Room ID and User ID combined to form thread uniqueness
        thread_id = f"{request.user_id}_{current_room_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Load existing state if available
        current_state = await graph.aget_state(config)
        
        if current_state.values:
            # We already have a state for this thread, so we only need to append the new message
            # The structure for resuming should just send the list of new messages and the chosen agent
            new_state_input = {
                "messages": [("user", request.message)],
                "current_agent": request.target_agent
            }
        else:
            # First time running this thread, we need to provide the complete initial state schema
            new_state_input = {
                "messages": [("user", request.message)],
                "user_preferences": {},  # 실제 앱에서는 DB에서 불러옵니다.
                "plan": "",
                "current_agent": request.target_agent
            }
        
        # 그래프 실행
        # 참고: 실제 비동기 환경에서는 ainvoke를 사용합니다.
        result = await graph.ainvoke(new_state_input, config=config)
        
        # BackgroundTask를 통해 방금 갱신된(또는 생성된) 데이터에 1시간(3600초) TTL 부여
        background_tasks.add_task(apply_ttl_to_thread, thread_id, 3600)
        
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
            room_id=current_room_id,
            plan=result.get("plan")
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
