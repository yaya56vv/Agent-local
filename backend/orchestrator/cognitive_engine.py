"""
Cognitive Engine - Synchronisation automatique entre modules
"""
from typing import Dict, Any, Optional
from backend.orchestrator.clients.memory_client import MemoryClient
from backend.orchestrator.clients.rag_client import RagClient
from backend.orchestrator.clients.vision_client import VisionClient


class CognitiveEngine:
    """Synchronise automatiquement mémoire, RAG, vision et documents"""
    
    def __init__(
        self,
        memory_client: MemoryClient,
        rag_client: RagClient,
        vision_client: VisionClient
    ):
        self.memory = memory_client
        self.rag = rag_client
        self.vision = vision_client
    
    async def sync_memory_to_rag(
        self,
        session_id: str,
        dataset: str = "scratchpad"
    ) -> Dict[str, Any]:
        """
        Synchronise la mémoire conversationnelle vers RAG
        
        Args:
            session_id: ID de session
            dataset: Dataset RAG cible
            
        Returns:
            Résultat de la synchronisation
        """
        try:
            # Récupérer les messages récents
            messages_data = await self.memory.get_messages(session_id, limit=20)
            messages = messages_data.get("messages", [])
            
            if not messages:
                return {"status": "success", "synced": 0, "message": "No messages to sync"}
            
            # Construire le contenu à indexer
            content_parts = []
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                content_parts.append(f"{role}: {content}")
            
            full_content = "\n".join(content_parts)
            
            # Ajouter au RAG
            doc_id = f"session_{session_id}_{len(messages)}"
            await self.rag.add_document(
                dataset=dataset,
                document_id=doc_id,
                text=full_content,
                metadata={"session_id": session_id, "message_count": len(messages)}
            )
            
            return {
                "status": "success",
                "synced": len(messages),
                "document_id": doc_id,
                "dataset": dataset
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def sync_vision_to_rag(
        self,
        image_bytes: bytes,
        analysis_result: Dict[str, Any],
        dataset: str = "scratchpad"
    ) -> Dict[str, Any]:
        """
        Synchronise une analyse vision vers RAG
        
        Args:
            image_bytes: Données image
            analysis_result: Résultat de l'analyse vision
            dataset: Dataset RAG cible
            
        Returns:
            Résultat de la synchronisation
        """
        try:
            # Extraire le texte de l'analyse
            description = analysis_result.get("description", "")
            objects = analysis_result.get("objects", [])
            text_content = analysis_result.get("text", "")
            
            # Construire le contenu
            content_parts = []
            if description:
                content_parts.append(f"Description: {description}")
            if objects:
                content_parts.append(f"Objects detected: {', '.join(objects)}")
            if text_content:
                content_parts.append(f"Text extracted: {text_content}")
            
            full_content = "\n".join(content_parts)
            
            if not full_content:
                return {"status": "success", "synced": 0, "message": "No content to sync"}
            
            # Ajouter au RAG
            from datetime import datetime
            doc_id = f"vision_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            await self.rag.add_document(
                dataset=dataset,
                document_id=doc_id,
                text=full_content,
                metadata={"type": "vision_analysis", "timestamp": datetime.utcnow().isoformat()}
            )
            
            return {
                "status": "success",
                "synced": 1,
                "document_id": doc_id,
                "dataset": dataset
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def auto_categorize(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Catégorise automatiquement le contenu vers le bon dataset
        
        Args:
            content: Contenu à catégoriser
            metadata: Métadonnées optionnelles
            
        Returns:
            Nom du dataset recommandé
        """
        content_lower = content.lower()
        
        # Règles de catégorisation
        if any(word in content_lower for word in ["identity", "preference", "rule", "security"]):
            return "agent_core"
        
        if any(word in content_lower for word in ["project", "task", "ongoing", "development"]):
            return "projects"
        
        # Par défaut : scratchpad (éphémère)
        return "scratchpad"
    
    async def cleanup_ephemeral(self, retention_days: int = 1) -> Dict[str, Any]:
        """
        Nettoie les données éphémères
        
        Args:
            retention_days: Jours de rétention
            
        Returns:
            Résultat du nettoyage
        """
        try:
            result = await self.rag.cleanup_memory(retention_days)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def sync_all(self, session_id: str) -> Dict[str, Any]:
        """
        Synchronisation complète de tous les modules
        
        Args:
            session_id: ID de session
            
        Returns:
            Résultats de toutes les synchronisations
        """
        results = {
            "memory_to_rag": await self.sync_memory_to_rag(session_id),
            "timestamp": None
        }
        
        from datetime import datetime
        results["timestamp"] = datetime.utcnow().isoformat()
        
        return results