from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class FamilyPlannerState(TypedDict):
    """
    Family Planner 에이전트의 상태를 나타냅니다.
    
    Attributes:
        messages: 대화 기록 목록입니다.
        plan: 현재 개발 중인 계획입니다.
        user_preferences: 사용자의 저장된 선호도 정보입니다.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    plan: str
    user_preferences: dict
