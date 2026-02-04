from fastapi import APIRouter, HTTPException
from app.models.schemas import PlannerRequest, PlannerResponse
from app.graph.workflow import create_graph

router = APIRouter()

# Instantiate the graph once (or per request if state needs it, but usually the graph definition is static)
graph = create_graph()

@router.post("/chat", response_model=PlannerResponse)
async def chat_with_planner(request: PlannerRequest):
    """
    Interact with the Family Planner Agent.
    """
    try:
        # Initial state for the graph
        initial_state = {
            "messages": [("user", request.message)],
            "user_preferences": {},  # Would load from DB in real app
            "plan": ""
        }
        
        # Invoke the graph
        # Note: In a real async environment, use ainvoke if supported/configured
        result = await graph.ainvoke(initial_state)
        
        # Extract the last message content
        last_message = result["messages"][-1]
        response_content = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        return PlannerResponse(
            response=response_content,
            plan=result.get("plan")
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
