from typing import Callable, Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger
from app.state.state import FamilyPlannerState
from app.core.yaml_config import registry as yaml_registry, AgentConfig
from app.tools.loader import load_tool_from_config

def create_agent_node(agent_config: AgentConfig) -> Callable[[FamilyPlannerState], Dict[str, Any]]:
    """
    Factory function that creates a LangGraph node function for a given agent configuration.
    """
    def dynamic_agent(state: FamilyPlannerState) -> Dict[str, Any]:
        """
        Dynamically generated agent node for {agent_config.name}.
        """
        # LLM Initialization
        if "gemini" in agent_config.llm_model.lower():
            llm = ChatGoogleGenerativeAI(model=agent_config.llm_model)
        else:
            # Fallback or generic initialization could go here. 
            # For now, if not gemini, raise an error or fallback to mock.
            logger.error(f"Unsupported LLM model: {agent_config.llm_model}")
            return {"messages": [AIMessage(content="에러: 지원하지 않는 LLM 모델입니다.")]}
            
        # Tool Loading and Binding
        loaded_tools = []
        for tool_key in agent_config.tools:
            t_config = yaml_registry.get_tool(tool_key)
            if t_config:
                try:
                    loaded_tools.append(load_tool_from_config(t_config))
                except Exception as e:
                    logger.error(f"Could not load tool '{tool_key}' for agent '{agent_config.name}': {e}")
            else:
                logger.warning(f"Tool '{tool_key}' not found in registry for agent '{agent_config.name}'.")
                
        if loaded_tools:
            bound_llm = llm.bind_tools(loaded_tools)
        else:
            bound_llm = llm
        
        # Prepare messages: Prepend SystemPrompt
        messages = state.get("messages", [])
        system_message = SystemMessage(content=agent_config.system_prompt)
        
        # We invoke the LLM with the system prompt followed by the conversation history
        invoke_messages = [system_message] + messages
        
        logger.debug(f"Executing dynamic agent node '{agent_config.name}' with model '{agent_config.llm_model}'")
        
        try:
            # Invoke the LLM with bound tools
            response = bound_llm.invoke(invoke_messages)
            return {"messages": [response]}
        except Exception as e:
            logger.exception(f"Failed to invoke LLM in agent '{agent_config.name}': {e}")
            return {"messages": [AIMessage(content="죄송합니다. 요청을 처리하는 중에 문제가 발생했습니다.")]}
    
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
