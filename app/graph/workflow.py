from langgraph.graph import StateGraph, START, END
from app.state.state import FamilyPlannerState
from app.agents.planner import planner_agent

def create_graph():
    """
    Family Planner를 위한 LangGraph 워크플로우를 생성합니다.
    """
    # 1. 상태 스키마로 그래프 초기화
    graph_builder = StateGraph(FamilyPlannerState)

    # 2. 노드 추가 (에이전트/함수)
    graph_builder.add_node("planner", planner_agent)

    # 3. 엣지 정의 (제어 흐름)
    # 시작 -> 플래너
    graph_builder.add_edge(START, "planner")
    
    # 플래너 -> 종료 (현재는 단순 흐름)
    graph_builder.add_edge("planner", END)

    # 4. 그래프 컴파일
    graph = graph_builder.compile()
    return graph
