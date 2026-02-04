from typing import TypedDict, Annotated, List, Union
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class FamilyPlannerState(TypedDict):
    """
    Represents the state of the Family Planner agent.
    
    Attributes:
        messages: A list of messages in the conversation history.
        plan: The current plan being developed.
        user_preferences: Stored preferences for the user.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    plan: str
    user_preferences: dict
