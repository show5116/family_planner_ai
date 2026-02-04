from langchain_core.messages import AIMessage
from app.state.state import FamilyPlannerState

def planner_agent(state: FamilyPlannerState) -> dict:
    """
    Core planner agent node.
    This function will eventually interact with the LLM to generate plans.
    """
    messages = state.get("messages", [])
    
    # Placeholder logic: In a real implementation, you would call an LLM here.
    # response = model.invoke(messages)
    
    # Returning a mock response for now
    response_content = "I am the planner agent. I will help you organize your family schedule."
    
    return {"messages": [AIMessage(content=response_content)]}
