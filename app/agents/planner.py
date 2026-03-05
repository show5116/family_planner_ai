from langchain_core.messages import AIMessage
from app.state.state import FamilyPlannerState

def planner_agent(state: FamilyPlannerState) -> dict:
    """
    핵심 기획 에이전트 노드입니다.
    이 함수는 추후 LLM과 상호작용하여 계획을 생성하게 됩니다.
    """
    messages = state.get("messages", [])
    
    # 로직 자리표시자: 실제 구현에서는 여기서 LLM을 호출합니다.
    # response = model.invoke(messages)
    
    # 지금은 모의 응답을 반환합니다.
    response_content = "저는 기획 에이전트입니다. 가족 일정을 정리하는 것을 도와드리겠습니다."
    
    return {"messages": [AIMessage(content=response_content)]}
