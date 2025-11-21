"""
LLM Router - Sélectionne le bon LLM selon le type de tâche
"""
from typing import Dict, Any, Optional
from backend.config.settings import settings
from backend.connectors.llm.openrouter import OpenRouterLLM
from backend.orchestrator.clients.local_llm_client import LocalLlmClient


class LLMRouter:
    """Route les requêtes vers le LLM approprié (local/cloud/vision)"""
    
    def __init__(self):
        # LLM Cloud (OpenRouter)
        self.llm_vision = OpenRouterLLM(model=settings.LLM_VISION_MODEL)
        self.llm_code = OpenRouterLLM(model=settings.LLM_CODE_MODEL)
        self.llm_reasoning = OpenRouterLLM(model=settings.LLM_REASONING_MODEL)
        self.llm_conversation = OpenRouterLLM(model=settings.LLM_CONVERSATION_MODEL)
        self.llm_rag = OpenRouterLLM(model=settings.LLM_RAG_MODEL)
        self.llm_default = OpenRouterLLM(model=settings.LLM_DEFAULT_MODEL)
        
        # LLM Local
        self.local_llm = LocalLlmClient(base_url="http://localhost:8008")
        
        # Tâches qui doivent utiliser le cloud
        self.cloud_tasks = {
            "vision", "image_analysis", "screenshot_analysis",
            "complex_reasoning", "multi_step_planning"
        }
    
    def pick_model(
        self,
        task_type: str,
        use_local: bool = True,
        multimodal: bool = False
    ) -> Dict[str, Any]:
        """
        Sélectionne le modèle approprié
        
        Args:
            task_type: Type de tâche
            use_local: Préférer local si possible
            multimodal: Requiert support multimodal
            
        Returns:
            Dict avec model instance et metadata
        """
        # Vision = toujours cloud
        if multimodal or task_type in ["vision", "image_analysis", "screenshot_analysis"]:
            if settings.LLM_ENABLE_VISION:
                return {
                    "instance": self.llm_vision,
                    "model": settings.LLM_VISION_MODEL,
                    "specialist": "vision",
                    "provider": "cloud",
                    "reason": "Multimodal task requires cloud vision model"
                }
        
        # Code = cloud si activé
        if task_type in ["code", "coding", "code_execution", "code_analyze"]:
            if settings.LLM_ENABLE_CODE:
                return {
                    "instance": self.llm_code,
                    "model": settings.LLM_CODE_MODEL,
                    "specialist": "code",
                    "provider": "cloud",
                    "reason": "Code task uses specialized model"
                }
        
        # Reasoning complexe = cloud si activé
        if task_type in ["reasoning", "complex_reasoning", "planning"]:
            if settings.LLM_ENABLE_REASONING:
                return {
                    "instance": self.llm_reasoning,
                    "model": settings.LLM_REASONING_MODEL,
                    "specialist": "reasoning",
                    "provider": "cloud",
                    "reason": "Complex reasoning task"
                }
        
        # RAG = cloud si activé
        if task_type in ["rag", "rag_query", "knowledge"]:
            if settings.LLM_ENABLE_RAG:
                return {
                    "instance": self.llm_rag,
                    "model": settings.LLM_RAG_MODEL,
                    "specialist": "rag",
                    "provider": "cloud",
                    "reason": "RAG task uses specialized model"
                }
        
        # Conversation = local par défaut
        if task_type in ["conversation", "chat", "general"]:
            if use_local and settings.LLM_ENABLE_CONVERSATION:
                return {
                    "instance": self.local_llm,
                    "model": settings.LOCAL_LLM_MODEL,
                    "specialist": "conversation",
                    "provider": "local",
                    "reason": "Simple conversation uses local LLM"
                }
            elif settings.LLM_ENABLE_CONVERSATION:
                return {
                    "instance": self.llm_conversation,
                    "model": settings.LLM_CONVERSATION_MODEL,
                    "specialist": "conversation",
                    "provider": "cloud",
                    "reason": "Conversation fallback to cloud"
                }
        
        # Défaut = local si demandé, sinon cloud
        if use_local and task_type not in self.cloud_tasks:
            return {
                "instance": self.local_llm,
                "model": settings.LOCAL_LLM_MODEL,
                "specialist": "general",
                "provider": "local",
                "reason": "Default to local LLM for efficiency"
            }
        
        # Fallback final = cloud default
        return {
            "instance": self.llm_default,
            "model": settings.LLM_DEFAULT_MODEL,
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