from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.state.state import FamilyPlannerState
from app.agents.registry import get_all_agent_nodes
from app.core.yaml_config import registry as yaml_registry
from app.tools.loader import load_tool_from_config
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
            logger.debug(f"Added agent node '{node_name}' to graph.")

    # 3. 모든 툴을 전역 ToolNode로 그래프에 추가
    # 실제 환경에서는 에이전트별로 툴을 분리할 수도 있지만, 가장 단순한 패턴은
    # 그래프 내에 툴을 실행하는 단일 노드를 두고 라우팅하는 방식입니다.
    all_loaded_tools = []
    for tool_key, t_config in yaml_registry.tools.items():
        try:
            all_loaded_tools.append(load_tool_from_config(t_config))
        except Exception as e:
            logger.warning(f"Skipping tool '{tool_key}' for ToolNode due to load error: {e}")
            
    if all_loaded_tools:
        tool_node = ToolNode(tools=all_loaded_tools)
        graph_builder.add_node("tools", tool_node)
        logger.debug(f"Added 'tools' node with {len(all_loaded_tools)} tools to graph.")
    else:
        logger.warning("No tools loaded for ToolNode.")

    # 4. 엣지 정의 (제어 흐름 및 조건부 라우팅)
    # 현재는 메인 엔트리 포인트인 'planner' 에이전트를 기준으로 하드 코딩하지만,
    # 차후 여러 에이전트 다중 라우팅 로직으로 변경될 수 있습니다.
    if "planner" in agent_nodes:
        # 시작 -> 플래너
        graph_builder.add_edge(START, "planner")
        
        # 플래너 -> 도구 호줄 여부 판단
        # 언어 모델이 도구 호출(tool_calls)을 반환했다면 'tools' 노드로, 아니라면 'END'로 빠집니다.
        if all_loaded_tools:
            graph_builder.add_conditional_edges(
                "planner",
                tools_condition,
            )
            # 도구 노드 실행 후 -> 다시 플래너 언어 모델로 돌아가서 후속 판단
            graph_builder.add_edge("tools", "planner")
        else:
            # 도구가 아예 없다면 바로 END로 연결
            graph_builder.add_edge("planner", END)
    else:
        logger.warning("'planner' node not found in yaml. The graph edges were not initialized.")

    # 5. 그래프 컴파일
    graph = graph_builder.compile()
    return graph
