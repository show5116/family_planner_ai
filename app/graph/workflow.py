from langgraph.graph import StateGraph, START, END
from app.state.state import FamilyPlannerState
from app.agents.registry import get_all_agent_nodes
from loguru import logger

def create_graph():
    """
    Family Planner를 위한 LangGraph 워크플로우를 생성합니다.
    """
    # 1. 상태 스키마로 그래프 초기화
    graph_builder = StateGraph(FamilyPlannerState)

    # 2. 노드 동적 레지스트리에서 로드 및 추가
    agent_nodes = get_all_agent_nodes()
    
    if not agent_nodes:
        logger.error("No agent nodes were dynamically loaded from YAML configuration.")
    else:
        for node_name, node_func in agent_nodes.items():
            graph_builder.add_node(node_name, node_func)
            logger.debug(f"Added node '{node_name}' to graph.")

    # 3. 엣지 정의 (제어 흐름)
    # 현재는 'planner' 에이전트가 존재한다고 가정하고 하드 코딩하지만, 차후 라우팅 로직으로 변경 가능
    if "planner" in agent_nodes:
        # 시작 -> 플래너
        graph_builder.add_edge(START, "planner")
        
        # 플래너 -> 종료 (현재는 단순 흐름)
        graph_builder.add_edge("planner", END)
    else:
        logger.warning("'planner' node not found in yaml. The graph edges were not initialized.")

    # 4. 그래프 컴파일
    graph = graph_builder.compile()
    return graph
