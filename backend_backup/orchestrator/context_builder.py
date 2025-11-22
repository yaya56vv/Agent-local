"""
Context Builder - Agrège tous les contextes disponibles
Fusionne: mémoire, RAG, vision, audio, documents, état système
"""
from typing import Dict, Any, Optional


class ContextBuilder:
    """Construit un super-contexte global en fusionnant toutes les sources"""
    
    def __init__(self, orchestrator):
        """
        Initialise le context builder
        
        Args:
            orchestrator: Instance de l'orchestrateur avec tous les clients MCP
        """
        self.orchestrator = orchestrator
    
    async def build_super_context(self, user_message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Construit un super-contexte global en agrégeant toutes les sources
        
        Args:
            user_message: Message utilisateur pour recherche sémantique
            session_id: ID de session pour contexte mémoire
            
        Returns:
            Dictionnaire avec tous les contextes fusionnés
        """
        # Récupération parallèle de tous les contextes
        memory = await self._get_memory_context(user_message, session_id)
        rag = await self._get_rag_context(user_message)
        vision = await self._get_vision_context()
        system_state = await self._get_system_state()
        audio_context = await self._get_audio_context()
        documents_context = await self._get_documents_context()
        
        # Fusion des contextes
        return self._merge_contexts(
            memory=memory,
            rag=rag,
            vision=vision,
            system_state=system_state,
            audio=audio_context,
            documents=documents_context
        )
    
    async def _get_memory_context(self, user_message: str, session_id: str) -> Dict[str, Any]:
        """Récupère le contexte mémoire conversationnel"""
        try:
            # Contexte conversationnel récent
            context = await self.orchestrator.memory_client.get_context(session_id, max_messages=5)
            
            # Recherche sémantique dans la mémoire
            search_results = await self.orchestrator.memory_client.search(user_message, session_id)
            
            return {
                "status": "success",
                "recent_context": context,
                "semantic_matches": search_results,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recent_context": "",
                "semantic_matches": []
            }
    
    async def _get_rag_context(self, user_message: str) -> Dict[str, Any]:
        """Récupère le contexte RAG multi-datasets"""
        try:
            rag_results = {}
            
            # A. CORE MEMORY (Permanent: Identity, Rules, PC Structure)
            core_results = await self.orchestrator.rag_client.query("agent_core", user_message, top_k=2)
            if core_results:
                rag_results["core"] = core_results
            
            # B. PROJECT MEMORY (Medium-term: Ongoing work)
            project_results = await self.orchestrator.rag_client.query("projects", user_message, top_k=2)
            if project_results:
                rag_results["projects"] = project_results
            
            # C. SCRATCHPAD (Ephemeral: Temporary info)
            scratch_results = await self.orchestrator.rag_client.query("scratchpad", user_message, top_k=1)
            if scratch_results:
                rag_results["scratchpad"] = scratch_results
            
            # D. RULES (Agent behavior rules)
            rules_results = await self.orchestrator.rag_client.query("rules", user_message, top_k=1)
            if rules_results:
                rag_results["rules"] = rules_results
            
            return {
                "status": "success",
                "datasets": rag_results,
                "total_results": sum(len(v) for v in rag_results.values())
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "datasets": {},
                "total_results": 0
            }
    
    async def _get_vision_context(self) -> Dict[str, Any]:
        """Récupère le contexte vision actif"""
        try:
            # Récupère le contexte vision actif (dernières analyses, etc.)
            context = await self.orchestrator.vision_client.get_active_context()
            return {
                "status": "success",
                "context": context
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "context": {}
            }
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Récupère l'état système actuel"""
        try:
            # Snapshot de l'état système
            snapshot = await self.orchestrator.system_client.snapshot()
            return {
                "status": "success",
                "snapshot": snapshot
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "snapshot": {}
            }
    
    async def _get_audio_context(self) -> Dict[str, Any]:
        """Récupère le contexte audio actif"""
        try:
            # Contexte audio (dernières transcriptions, etc.)
            context = await self.orchestrator.audio_client.get_audio_context()
            return {
                "status": "success",
                "context": context
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "context": {}
            }
    
    async def _get_documents_context(self) -> Dict[str, Any]:
        """Récupère le contexte documents récents"""
        try:
            # Documents récents (à implémenter selon besoins)
            # Pour l'instant, retourne un contexte vide
            return {
                "status": "success",
                "recent_documents": [],
                "active_templates": []
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recent_documents": []
            }
    
    def _merge_contexts(
        self,
        memory: Dict[str, Any],
        rag: Dict[str, Any],
        vision: Dict[str, Any],
        system_state: Dict[str, Any],
        audio: Dict[str, Any],
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fusionne tous les contextes en un super-contexte structuré
        
        Args:
            memory: Contexte mémoire
            rag: Contexte RAG
            vision: Contexte vision
            system_state: État système
            audio: Contexte audio
            documents: Contexte documents
            
        Returns:
            Super-contexte fusionné
        """
        return {
            "memory": memory,
            "rag_docs": rag,
            "vision": vision,
            "system_state": system_state,
            "audio": audio,
            "documents": documents,
            "metadata": {
                "sources_available": [
                    k for k, v in {
                        "memory": memory.get("status") == "success",
                        "rag": rag.get("status") == "success",
                        "vision": vision.get("status") == "success",
                        "system": system_state.get("status") == "success",
                        "audio": audio.get("status") == "success",
                        "documents": documents.get("status") == "success"
                    }.items() if v
                ],
                "total_context_size": self._estimate_context_size(
                    memory, rag, vision, system_state, audio, documents
                )
            }
        }
    
    def _estimate_context_size(self, *contexts) -> int:
        """Estime la taille totale du contexte (approximatif)"""
        import json
        try:
            return len(json.dumps(contexts))
        except:
            return 0
