from typing import Dict, List, Any, Optional
from backend.config.model_registry import model_registry

class AgentRegistry:
    """
    Registry defining agent profiles: role, model, tools, and RAG configuration.
    Decouples agent definitions from implementation details.
    """
    
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._load_agents()
        
    def _load_agents(self):
        """Define agent profiles using models from ModelRegistry."""
        
        # 1. Orchestrator Agent
        # The main brain, has access to everything
        self._register_agent(
            role="orchestrator",
            description="Main orchestrator agent",
            tools=["*"], # All tools
            rag_read=["agent_core", "projects", "context_flow"],
            rag_write=["projects"]
        )
        
        # 2. Code Agent
        # Specialized in coding tasks
        self._register_agent(
            role="code",
            description="Specialist coding agent",
            tools=["file_read", "file_write", "file_list", "code_execute", "code_analyze", "search_web"],
            rag_read=["projects"],
            rag_write=["projects"]
        )
        
        # 3. Vision Agent
        # Specialized in image analysis
        self._register_agent(
            role="vision",
            description="Specialist vision agent",
            tools=["vision_analyze", "vision_extract_text"],
            rag_read=["context_flow"],
            rag_write=[]
        )
        
        # 4. Local Agent
        # Runs on local hardware (Ollama/LM Studio)
        self._register_agent(
            role="local",
            description="Local privacy-focused agent",
            tools=["local_llm_generate", "local_llm_chat"],
            rag_read=["agent_core", "context_flow"],
            rag_write=["context_flow", "agent_memory"]
        )
        
        # 5. Analyse Agent (Optional)
        # For deep research and analysis
        self._register_agent(
            role="analyse",
            description="Deep analysis and research agent",
            tools=["search_web", "rag_query", "file_read"],
            rag_read=["projects", "context_flow"],
            rag_write=["projects"]
        )

    def _register_agent(self, role: str, description: str, tools: List[str], rag_read: List[str], rag_write: List[str]):
        """Register an agent profile."""
        model_config = model_registry.get_model(role)
        
        # Extract provider and model name safely
        provider = model_config.get("provider") if model_config else None
        model_name = model_config.get("model") if model_config else None
        
        self._agents[role] = {
            "role": role,
            "description": description,
            "model": model_name,
            "provider": provider,
            "model_config": model_config, # Keep full config just in case
            "mcp_tools": tools,
            "rag_profile": {
                "read": rag_read,
                "write": rag_write
            },
            "active": model_registry.provider_available(role)
        }

    def get_agent(self, role: str) -> Optional[Dict[str, Any]]:
        """Get full agent profile."""
        return self._agents.get(role)

    def get_tools(self, role: str) -> List[str]:
        """Get allowed tools for an agent."""
        agent = self.get_agent(role)
        return agent.get("mcp_tools", []) if agent else []

    def get_rag_profile(self, role: str) -> Dict[str, List[str]]:
        """Get allowed RAG datasets for an agent (read/write)."""
        agent = self.get_agent(role)
        return agent.get("rag_profile", {"read": [], "write": []}) if agent else {"read": [], "write": []}
        
    def list_active_agents(self) -> List[str]:
        """List roles of currently active agents."""
        return [role for role, agent in self._agents.items() if agent.get("active")]

# Global instance
agent_registry = AgentRegistry()

