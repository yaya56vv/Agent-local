"""
Context Builder - Fusionne les contextes de tous les modules MCP
"""
from typing import Dict, Any, Optional
from backend.orchestrator.clients.memory_client import MemoryClient
from backend.orchestrator.clients.rag_client import RagClient
from backend.orchestrator.clients.vision_client import VisionClient
from backend.orchestrator.clients.system_client import SystemClient


class ContextBuilder:
    """Construit un super-contexte global à partir de tous les modules"""
    
    def __init__(
        self,
        memory_client: MemoryClient,
        rag_client: RagClient,
        vision_client: VisionClient,
        system_client: SystemClient
    ):
        self.memory = memory_client
        self.rag = rag_client
        self.vision = vision_client
        self.system = system_client
    
    async def build_context(
        self,
        prompt: str,
        session_id: str = "default",
        include_vision: bool = False,
        include_system: bool = False
    ) -> Dict[str, Any]:
        """
        Construit le contexte global fusionné
        
        Args:
            prompt: Requête utilisateur pour recherche sémantique
            session_id: ID de session pour mémoire
            include_vision: Inclure contexte vision
            include_system: Inclure contexte système
            
        Returns:
            Dict avec tous les contextes fusionnés
        """
        context = {
            "memory": {},
            "rag": {},
            "vision": {},
            "system": {},
            "summary": ""
        }
        
        # 1. MÉMOIRE CONVERSATIONNELLE
        try:
            memory_context = await self.memory.get_context(session_id, max_messages=10)
            messages = await self.memory.get_messages(session_id, limit=5)
            context["memory"] = {
                "context": memory_context,
                "recent_messages": messages.get("messages", []),
                "session_id": session_id
            }
        except Exception as e:
            context["memory"]["error"] = str(e)
        
        # 2. RAG - CONNAISSANCES
        try:
            # Agent Core (permanent)
            core_results = await self.rag.query("agent_core", prompt, top_k=3)
            
            # Projects (ongoing)
            project_results = await self.rag.query("projects", prompt, top_k=2)
            
            # Scratchpad (ephemeral)
            scratch_results = await self.rag.query("scratchpad", prompt, top_k=1)
            
            context["rag"] = {
                "core": core_results,
                "projects": project_results,
                "scratchpad": scratch_results
            }
        except Exception as e:
            context["rag"]["error"] = str(e)
        
        # 3. VISION (optionnel)
        if include_vision:
            try:
                # Placeholder - vision context would come from recent analyses
                context["vision"] = {
                    "available": True,
                    "note": "Vision context available on demand"
                }
            except Exception as e:
                context["vision"]["error"] = str(e)
        
        # 4. SYSTÈME (optionnel)
        if include_system:
            try:
                processes = await self.system.list_processes()
                context["system"] = {
                    "processes": processes,
                    "available": True
                }
            except Exception as e:
                context["system"]["error"] = str(e)
        
        # 5. RÉSUMÉ TEXTUEL
        context["summary"] = self._build_summary(context)
        
        return context
    
    def _build_summary(self, context: Dict[str, Any]) -> str:
        """Construit un résumé textuel du contexte"""
        parts = []
        
        # Mémoire
        if context["memory"].get("context"):
            parts.append(f"CONVERSATION:\n{context['memory']['context']}")
        
        # RAG Core
        if context["rag"].get("core"):
            core_texts = [r.get("content", "") for r in context["rag"]["core"]]
            if core_texts:
                parts.append(f"CORE KNOWLEDGE:\n" + "\n".join(core_texts[:2]))
        
        # RAG Projects
        if context["rag"].get("projects"):
            proj_texts = [r.get("content", "") for r in context["rag"]["projects"]]
            if proj_texts:
                parts.append(f"PROJECT CONTEXT:\n" + "\n".join(proj_texts[:2]))
        
        return "\n\n".join(parts) if parts else "No context available"