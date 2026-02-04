from langgraph.graph import StateGraph, START, END
from app.state.state import FamilyPlannerState
from app.agents.planner import planner_agent

def create_graph():
    """
    Constructs the LangGraph workflow for the Family Planner.
    """
    # 1. Initialize the graph with the state schema
    graph_builder = StateGraph(FamilyPlannerState)

    # 2. Add nodes (agents/functions)
    graph_builder.add_node("planner", planner_agent)

    # 3. Define edges (control flow)
    # Start -> Planner
    graph_builder.add_edge(START, "planner")
    
    # Planner -> End (Simple flow for now)
    graph_builder.add_edge("planner", END)

    # 4. Compile the graph
    graph = graph_builder.compile()
    return graph
