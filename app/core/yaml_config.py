import os
import glob
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

# --- Pydantic Models for Configuration Validation ---

class ToolConfig(BaseModel):
    name: str
    description: str
    prompt: Optional[str] = None
    module: str
    function: str

class ToolDomainConfig(BaseModel):
    domain: str
    tools: List[ToolConfig]

class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    llm_model: str
    tools: List[str]  # format: "domain.tool_name"


# --- Loaders ---

def load_yaml_configs(directory: str) -> Dict[str, Any]:
    """Helper to load all yaml files from a directory."""
    configs = {}
    if not os.path.exists(directory):
        logger.warning(f"Configuration directory {directory} does not exist.")
        return configs

    search_pattern = os.path.join(directory, "**", "*.yaml")
    for filepath in glob.glob(search_pattern, recursive=True):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    filename = os.path.basename(filepath).replace(".yaml", "")
                    # Either use explicitly defined domain/name, or fallback to file name
                    key = data.get("domain", data.get("name", filename))
                    configs[key] = data
        except Exception as e:
            logger.error(f"Failed to load yaml config from {filepath}: {e}")
            
    return configs

class Registry:
    """Registry to hold loaded agents and tools configurations."""
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.agents: Dict[str, AgentConfig] = {}
        self.tools: Dict[str, ToolConfig] = {} # Keyed by "domain.tool_name"
        self._load_all()

    def _load_all(self):
        logger.info("Loading agent and tool configurations from YAML...")
        self._load_tools()
        self._load_agents()

    def _load_tools(self):
        tools_dir = os.path.join(self.config_dir, "tools")
        raw_tool_domains = load_yaml_configs(tools_dir)
        
        for domain_name, domain_data in raw_tool_domains.items():
            try:
                domain_config = ToolDomainConfig(**domain_data)
                for tool in domain_config.tools:
                    tool_key = f"{domain_config.domain}.{tool.name}"
                    self.tools[tool_key] = tool
            except Exception as e:
                logger.error(f"Validation failed for tool domain '{domain_name}': {e}")
                
        logger.info(f"Loaded {len(self.tools)} tools from config.")

    def _load_agents(self):
        agents_dir = os.path.join(self.config_dir, "agents")
        raw_agents = load_yaml_configs(agents_dir)
        
        for agent_name, agent_data in raw_agents.items():
            try:
                agent_config = AgentConfig(**agent_data)
                self.agents[agent_config.name] = agent_config
            except Exception as e:
                logger.error(f"Validation failed for agent '{agent_name}': {e}")
                
        logger.info(f"Loaded {len(self.agents)} agents from config.")

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        return self.agents.get(name)

    def get_tool(self, key: str) -> Optional[ToolConfig]:
        """Get tool by "domain.tool_name" """
        return self.tools.get(key)

# Global registry instance
registry = Registry()
