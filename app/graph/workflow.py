from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.state.state import FamilyPlannerState
from app.agents.registry import get_all_agent_nodes
from app.core.yaml_config import registry as yaml_registry
from app.tools.loader import load_tool_from_config
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Optional
from loguru import logger

def route_start(state: FamilyPlannerState):
    """결정된 초기 에이전트(current_agent)로 라우팅합니다."""
    # 만약 지정되지 않았다면 supervisor로 기본 처리
    return state.get("current_agent", "supervisor")

def route_tools(state: FamilyPlannerState):
    """도구 실행 후 원래 호출했던 에이전트로 되돌아갑니다."""
    return state.get("current_agent", "supervisor")

def create_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
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
    
    # 시작 -> 동적 에이전트 분기
    graph_builder.add_conditional_edges(START, route_start)
    
    # 각 에이전트 노드 -> 도구 호출 여부 판단 / END
    for agent_name in agent_nodes.keys():
        if all_loaded_tools:
            graph_builder.add_conditional_edges(
                agent_name,
                tools_condition,
            )
        else:
            # 도구가 아예 없다면 다이렉트로 END
            graph_builder.add_edge(agent_name, END)

    # 도구 노드 실행 후 -> 원래 불렀던 에이전트 노드로 복귀
    if all_loaded_tools:
        graph_builder.add_conditional_edges("tools", route_tools)

    # 5. 그래프 컴파일
    if checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        logger.info("Graph compiled with checkpointer.")
    else:
        graph = graph_builder.compile()
        logger.info("Graph compiled WITHOUT checkpointer.")
        
    return graph
