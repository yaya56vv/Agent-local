import os
from typing import Dict, Optional, Any, List
from backend.config.settings import settings

class ModelRegistry:
    """
    Central registry for model configurations based on .env variables.
    Decouples code from specific model names.
    """
    
    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._load_from_env()
        
    def _load_from_env(self):
        """Load model configurations from environment variables via settings or os.environ."""

        # Define the mapping between roles and environment variables
        role_env_map = {
            "orchestrator": {"model": "ORCHESTRATOR_MODEL", "provider": "PROVIDER_ORCHESTRATOR"},
            "code": {"model": "CODE_AGENT_MODEL", "provider": "PROVIDER_CODE"},
            "vision": {"model": "VISION_AGENT_MODEL", "provider": "PROVIDER_VISION"},
            "local": {"model": "LOCAL_AGENT_MODEL", "provider": "PROVIDER_LOCAL"},
            "analyse": {"model": "ANALYSE_AGENT_MODEL", "provider": "PROVIDER_ANALYSE"},
            "glm_vision_expert": {"model": "GLM_AGENT_MODEL", "provider": None, "type": "mcp"}
        }
        
        for role, env_vars in role_env_map.items():
            model_var = env_vars["model"]
            provider_var = env_vars.get("provider")
            service_type = env_vars.get("type", "llm")

            # Try to get from settings first, then os.environ
            model_str = getattr(settings, model_var, os.getenv(model_var))
            provider_str = getattr(settings, provider_var, os.getenv(provider_var)) if provider_var else None

            # Special handling for MCP services like GLM
            if service_type == "mcp" and role == "glm_vision_expert":
                glm_enabled = getattr(settings, "GLM_AGENT_ENABLED", False)
                if glm_enabled and model_str:
                    self._registry[role] = {
                        "type": "mcp",
                        "server": "glm",
                        "model": model_str,
                        "host": getattr(settings, "GLM_AGENT_HOST", "http://localhost"),
                        "port": getattr(settings, "GLM_AGENT_PORT", 9001),
                        "base_url": f"{getattr(settings, 'GLM_AGENT_HOST', 'http://localhost')}:{getattr(settings, 'GLM_AGENT_PORT', 9001)}",
                        "tools": [
                            "solve_problem",
                            "analyze_code",
                            "analyze_visual_screenshot",
                            "rag_query",
                            "rag_write",
                            "file_read",
                            "file_write",
                            "file_search",
                            "shell_execute_safe",
                            "browser_search"
                        ],
                        "enabled": True
                    }
                else:
                    self._registry[role] = {
                        "type": "mcp",
                        "server": "glm",
                        "enabled": False,
                        "disabled": True
                    }
            elif model_str:
                self._registry[role] = self._parse_model_string(model_str, provider_str)
            else:
                # Handle missing configuration gracefully
                if role == "local":
                    self._registry[role] = {
                        "provider": settings.LOCAL_LLM_PROVIDER,
                        "model": settings.LOCAL_LLM_MODEL,
                        "is_local": True
                    }
                else:
                    # Mark as disabled or missing
                    self._registry[role] = {
                        "provider": None,
                        "model": None,
                        "disabled": True
                    }

    def _parse_model_string(self, model_str: str, default_provider: str = None) -> Dict[str, Any]:
        """
        Parse a model string like 'provider/model_name' or just 'model_name'.
        If provider is not in the string, use default_provider.
        """
        if not model_str:
            return {"provider": None, "model": None}
            
        parts = model_str.split('/', 1)
        
        if len(parts) == 2:
            # Explicit provider in string overrides default_provider
            provider = parts[0].lower()
            model = parts[1]
            
            return {
                "provider": provider,
                "model": model,
                "full_name": model_str
            }
        else:
            # Use default provider from env/settings, or fallback to openrouter
            provider = default_provider if default_provider else "openrouter"
            
            return {
                "provider": provider,
                "model": model_str,
                "full_name": f"{provider}/{model_str}"
            }

    def get_model(self, role: str) -> Optional[Dict[str, Any]]:
        """Get model configuration for a specific role."""
        return self._registry.get(role)

    def list_roles(self) -> List[str]:
        """List all configured roles."""
        return list(self._registry.keys())

    def provider_available(self, role: str) -> bool:
        """Check if the provider for a role is available/configured."""
        config = self.get_model(role)
        if not config:
            return False
        return not config.get("disabled", False) and config.get("model") is not None

# Global instance
model_registry = ModelRegistry()

