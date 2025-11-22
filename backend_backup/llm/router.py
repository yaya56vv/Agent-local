"""
LLM Router - Sélectionne le bon LLM selon le type de tâche
"""
from typing import Dict, Any, Optional
from backend.config.settings import settings
from backend.connectors.llm.openrouter import OpenRouterLLM
from backend.orchestrator.clients.local_llm_client import LocalLlmClient
from backend.config.model_registry import model_registry


class LLMRouter:
    """Route les requêtes vers le LLM approprié (local/cloud/vision/glm)"""

    def __init__(self):
        # LLM Cloud (OpenRouter) - Load from model_registry
        vision_config = model_registry.get_model("vision")
        code_config = model_registry.get_model("code")
        orchestrator_config = model_registry.get_model("orchestrator")
        glm_config = model_registry.get_model("glm_vision_expert")

        self.llm_vision = OpenRouterLLM(model=vision_config["model"])
        self.llm_code = OpenRouterLLM(model=code_config["model"])
        self.llm_reasoning = OpenRouterLLM(model=orchestrator_config["model"])
        self.llm_conversation = OpenRouterLLM(model=orchestrator_config["model"])
        self.llm_rag = OpenRouterLLM(model=orchestrator_config["model"])
        self.llm_default = OpenRouterLLM(model=orchestrator_config["model"])

        # LLM Local
        self.local_llm = LocalLlmClient(base_url="http://localhost:8008")

        # GLM Vision Expert (MCP)
        from backend.orchestrator.clients.glm_client import GLMClient
        self.glm_client = GLMClient() if glm_config and glm_config.get("enabled") else None

        # Tâches qui doivent utiliser le cloud
        self.cloud_tasks = {
            "vision", "image_analysis", "screenshot_analysis",
            "complex_reasoning", "multi_step_planning"
        }

        # Tâches qui peuvent utiliser GLM (si enabled)
        self.glm_tasks = {
            "solve_problem", "analyze_code", "analyze_visual_screenshot",
            "rag_query_glm", "complex_vision", "expert_analysis"
        }
    
    def pick_model(
        self,
        task_type: str,
        use_local: bool = True,
        multimodal: bool = False,
        use_glm: bool = False
    ) -> Dict[str, Any]:
        """
        Sélectionne le modèle approprié

        Args:
            task_type: Type de tâche
            use_local: Préférer local si possible
            multimodal: Requiert support multimodal
            use_glm: Force utilisation GLM si disponible

        Returns:
            Dict avec model instance et metadata
        """
        # GLM = si explicitement demandé OU tâche GLM-compatible
        if (use_glm or task_type in self.glm_tasks) and self.glm_client:
            glm_config = model_registry.get_model("glm_vision_expert")
            if glm_config and glm_config.get("enabled"):
                return {
                    "instance": self.glm_client,
                    "model": glm_config.get("model", "GLM-4.6"),
                    "specialist": "glm_vision_expert",
                    "provider": "mcp",
                    "type": "mcp",
                    "reason": "GLM Vision Expert for advanced reasoning/vision tasks"
                }

        # Vision = toujours cloud
        if multimodal or task_type in ["vision", "image_analysis", "screenshot_analysis"]:
            vision_config = model_registry.get_model("vision")
            if vision_config and not vision_config.get("disabled", False):
                return {
                    "instance": self.llm_vision,
                    "model": vision_config["model"],
                    "specialist": "vision",
                    "provider": "cloud",
                    "reason": "Multimodal task requires cloud vision model"
                }
        
        # Code = cloud si activé
        if task_type in ["code", "coding", "code_execution", "code_analyze"]:
            code_config = model_registry.get_model("code")
            if code_config and not code_config.get("disabled", False):
                return {
                    "instance": self.llm_code,
                    "model": code_config["model"],
                    "specialist": "code",
                    "provider": "cloud",
                    "reason": "Code task uses specialized model"
                }
        
        # Reasoning complexe = cloud si activé
        if task_type in ["reasoning", "complex_reasoning", "planning"]:
            orchestrator_config = model_registry.get_model("orchestrator")
            if orchestrator_config and not orchestrator_config.get("disabled", False):
                return {
                    "instance": self.llm_reasoning,
                    "model": orchestrator_config["model"],
                    "specialist": "reasoning",
                    "provider": "cloud",
                    "reason": "Complex reasoning task"
                }
        
        # RAG = cloud si activé
        if task_type in ["rag", "rag_query", "knowledge"]:
            orchestrator_config = model_registry.get_model("orchestrator")
            if orchestrator_config and not orchestrator_config.get("disabled", False):
                return {
                    "instance": self.llm_rag,
                    "model": orchestrator_config["model"],
                    "specialist": "rag",
                    "provider": "cloud",
                    "reason": "RAG task uses specialized model"
                }
        
        # Conversation = local par défaut
        if task_type in ["conversation", "chat", "general"]:
            if use_local:
                local_config = model_registry.get_model("local")
                if local_config and not local_config.get("disabled", False):
                    return {
                        "instance": self.local_llm,
                        "model": local_config["model"],
                        "specialist": "conversation",
                        "provider": "local",
                        "reason": "Simple conversation uses local LLM"
                    }
            orchestrator_config = model_registry.get_model("orchestrator")
            if orchestrator_config and not orchestrator_config.get("disabled", False):
                return {
                    "instance": self.llm_conversation,
                    "model": orchestrator_config["model"],
                    "specialist": "conversation",
                    "provider": "cloud",
                    "reason": "Conversation fallback to cloud"
                }
        
        # Défaut = local si demandé, sinon cloud
        if use_local and task_type not in self.cloud_tasks:
            local_config = model_registry.get_model("local")
            if local_config and not local_config.get("disabled", False):
                return {
                    "instance": self.local_llm,
                    "model": local_config["model"],
                    "specialist": "general",
                    "provider": "local",
                    "reason": "Default to local LLM for efficiency"
                }
        
        # Fallback final = cloud default
        orchestrator_config = model_registry.get_model("orchestrator")
        return {
            "instance": self.llm_default,
            "model": orchestrator_config["model"] if orchestrator_config else "unknown",
            "specialist": "general",
            "provider": "cloud",
            "reason": "Default cloud model"
        }
    
    async def generate(
        self,
        prompt: str,
        task_type: str = "general",
        use_local: bool = True,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Génère une réponse avec le bon LLM
        
        Args:
            prompt: Prompt utilisateur
            task_type: Type de tâche
            use_local: Préférer local
            max_tokens: Tokens max
            
        Returns:
            Réponse avec metadata
        """
        model_info = self.pick_model(task_type, use_local)
        instance = model_info["instance"]
        
        try:
            # Local LLM
            if model_info["provider"] == "local":
                response = await instance.generate(prompt, max_tokens=max_tokens)
                return {
                    "text": response.get("text", ""),
                    "model_info": model_info,
                    "status": "success"
                }
            
            # Cloud LLM
            else:
                messages = [{"role": "user", "content": prompt}]
                response = instance.ask(messages)
                return {
                    "text": response,
                    "model_info": model_info,
                    "status": "success"
                }
                
        except Exception as e:
            return {
                "text": "",
                "model_info": model_info,
                "status": "error",
                "error": str(e)
            }
