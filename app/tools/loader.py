import importlib
from typing import Callable, Any
from langchain_core.tools import StructuredTool
from loguru import logger
from app.core.yaml_config import ToolConfig

def load_tool_from_config(tool_config: ToolConfig) -> StructuredTool:
    """
    Dynamically loads a python function defined in a ToolConfig and wraps it
    into a LangChain StructuredTool.
    """
    try:
        # Dynamically import the module
        module = importlib.import_module(tool_config.module)
        
        # Get the actual python function corresponding to the config
        func: Callable[..., Any] = getattr(module, tool_config.function)
        
        # Build the final description including the prompt if any
        full_description = tool_config.description
        if tool_config.prompt:
            full_description += f"\n\n[지시사항]\n{tool_config.prompt}"
            
        # Create a LangChain tool from the function.
        # It relies on python type hints of the underlying function.
        # Make sure the target functions have concrete type hints!
        langchain_tool = StructuredTool.from_function(
            func=func,
            name=tool_config.name,
            description=full_description,
        )
        
        logger.debug(f"Successfully loaded and wrapped tool: '{tool_config.name}' from {tool_config.module}.{tool_config.function}")
        return langchain_tool
        
    except ImportError as e:
        logger.error(f"Failed to import tool module '{tool_config.module}': {e}")
        raise
    except AttributeError as e:
        logger.error(f"Function '{tool_config.function}' not found in module '{tool_config.module}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading tool '{tool_config.name}': {e}")
        raise
