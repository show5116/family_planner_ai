from typing import Callable, Any, Dict
from langchain_core.messages import AIMessage
from loguru import logger
from app.state.state import FamilyPlannerState
from app.core.yaml_config import registry as yaml_registry, AgentConfig

def create_agent_node(agent_config: AgentConfig) -> Callable[[FamilyPlannerState], Dict[str, Any]]:
    """
    Factory function that creates a LangGraph node function for a given agent configuration.
    """
    def dynamic_agent(state: FamilyPlannerState) -> Dict[str, Any]:
        """
        Dynamically generated agent node for {agent_config.name}.
        """
        # In a real implementation, you would initialize the LLM here using agent_config.llm_model,
        # bind tools using agent_config.tools (loading them via yaml_registry.get_tool),
        # and prepend the system prompt to the messages.
        
        # For now, we simulate the LLM response utilizing the dynamic configuration.
        response_content = (
            f"[Dynamic Agent Execution] Name: {agent_config.name}\n"
            f"Desc: {agent_config.description}\n"
            f"Model: {agent_config.llm_model}\n"
            f"System Prompt: {agent_config.system_prompt.strip()}\n"
            f"Tools: {agent_config.tools}\n"
            f"--- State Messages Summary ---\n"
            f"Received {len(state.get('messages', []))} messages in state."
        )
        
        logger.debug(f"Executing dynamic agent node: {agent_config.name}")
        return {"messages": [AIMessage(content=response_content)]}
    
    # Update the dynamic function's metadata for better debugging
    dynamic_agent.__name__ = f"{agent_config.name}_node"
    dynamic_agent.__doc__ = f"Dynamically generated LangGraph node for {agent_config.name}: {agent_config.description}"
    
    return dynamic_agent

def get_all_agent_nodes() -> Dict[str, Callable]:
    """
    Returns a dictionary mapping agent names to their dynamically created node functions.
    """
    nodes = {}
    for agent_name, agent_config in yaml_registry.agents.items():
        try:
            nodes[agent_name] = create_agent_node(agent_config)
            logger.info(f"Successfully created dynamic node for agent: {agent_name}")
        except Exception as e:
            logger.error(f"Failed to create dynamic node for {agent_name}: {e}")
            
    return nodes
