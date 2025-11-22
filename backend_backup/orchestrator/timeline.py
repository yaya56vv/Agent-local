"""
Timeline - Enregistre l'historique des actions et résultats
Support complet: audio, vision, documents, RAG, memory, system
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class Timeline:
    """Gère l'historique chronologique des actions avec support multimodal"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.max_events = 1000  # Limite pour éviter surcharge mémoire
        self.modalities = ["text", "audio", "vision", "documents", "system"]
    
    async def add(
        self,
        event_type: str,
        data: Dict[str, Any],
        session_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ajoute un événement à la timeline (async pour compatibilité)
        
        Args:
            event_type: Type d'événement (plan, execution, error, audio, vision, etc.)
            data: Données de l'événement
            session_id: ID de session
            metadata: Métadonnées optionnelles (modality, tool, action, etc.)
            
        Returns:
            L'événement créé
        """
        return self.add_event(event_type, data, session_id, metadata)
    
    def add_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        session_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ajoute un événement à la timeline
        
        Args:
            event_type: Type d'événement (plan, execution, error, audio, vision, etc.)
            data: Données de l'événement
            session_id: ID de session
            metadata: Métadonnées optionnelles (modality, tool, action, etc.)
            
        Returns:
            L'événement créé
        """
        # Détecter la modalité automatiquement si non spécifiée
        if metadata is None:
            metadata = {}
        
        if "modality" not in metadata:
            metadata["modality"] = self._detect_modality(event_type, data)
        
        event = {
            "id": len(self.events) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "session_id": session_id,
            "data": data,
            "metadata": metadata
        }
        
        self.events.append(event)
        
        # Limiter la taille
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        return event
    
    def _detect_modality(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Détecte automatiquement la modalité d'un événement
        
        Args:
            event_type: Type d'événement
            data: Données de l'événement
            
        Returns:
            Modalité détectée
        """
        # Vérifier le type d'événement
        if "audio" in event_type.lower():
            return "audio"
        elif "vision" in event_type.lower() or "image" in event_type.lower():
            return "vision"
        elif "document" in event_type.lower():
            return "documents"
        elif "system" in event_type.lower():
            return "system"
        
        # Vérifier les données
        if isinstance(data, dict):
            tool = data.get("tool", "")
            if tool == "audio":
                return "audio"
            elif tool == "vision":
                return "vision"
            elif tool == "documents":
                return "documents"
            elif tool == "system":
                return "system"
        
        return "text"
    
    def get_events(
        self,
        session_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupère les événements filtrés
        
        Args:
            session_id: Filtrer par session
            event_type: Filtrer par type
            limit: Nombre max d'événements
            
        Returns:
            Liste des événements
        """
        filtered = self.events
        
        if session_id:
            filtered = [e for e in filtered if e["session_id"] == session_id]
        
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]
        
        return filtered[-limit:]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Résumé d'une session
        
        Args:
            session_id: ID de session
            
        Returns:
            Statistiques de la session
        """
        session_events = [e for e in self.events if e["session_id"] == session_id]
        
        if not session_events:
            return {
                "session_id": session_id,
                "total_events": 0,
                "first_event": None,
                "last_event": None,
                "event_types": {}
            }
        
        event_types = {}
        for event in session_events:
            event_type = event["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "session_id": session_id,
            "total_events": len(session_events),
            "first_event": session_events[0]["timestamp"],
            "last_event": session_events[-1]["timestamp"],
            "event_types": event_types
        }
    
    def clear_session(self, session_id: str) -> int:
        """
        Efface les événements d'une session
        
        Args:
            session_id: ID de session
            
        Returns:
            Nombre d'événements supprimés
        """
        initial_count = len(self.events)
        self.events = [e for e in self.events if e["session_id"] != session_id]
        return initial_count - len(self.events)
    
    def export_timeline(self, session_id: Optional[str] = None) -> str:
        """
        Exporte la timeline en JSON
        
        Args:
            session_id: Optionnel, filtrer par session
            
        Returns:
            JSON string
        """
        if session_id:
            events = [e for e in self.events if e["session_id"] == session_id]
        else:
            events = self.events
        
        return json.dumps(events, indent=2, ensure_ascii=False)
    
    def get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les actions récentes (type=execution)
        
        Args:
            limit: Nombre max d'actions
            
        Returns:
            Liste des actions récentes
        """
        executions = [e for e in self.events if e["type"] == "execution"]
        return executions[-limit:]
    
    def get_by_modality(
        self,
        modality: str,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Récupère les événements par modalité
        
        Args:
            modality: Modalité (text, audio, vision, documents, system)
            session_id: Filtrer par session (optionnel)
            limit: Nombre max d'événements
            
        Returns:
            Liste des événements
        """
        filtered = [
            e for e in self.events
            if e.get("metadata", {}).get("modality") == modality
        ]
        
        if session_id:
            filtered = [e for e in filtered if e["session_id"] == session_id]
        
        return filtered[-limit:]
    
    def get_audio_events(
        self,
        session_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Récupère les événements audio
        
        Args:
            session_id: Filtrer par session (optionnel)
            limit: Nombre max d'événements
            
        Returns:
            Liste des événements audio
        """
        return self.get_by_modality("audio", session_id, limit)
    
    def get_vision_events(
        self,
        session_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Récupère les événements vision
        
        Args:
            session_id: Filtrer par session (optionnel)
            limit: Nombre max d'événements
            
        Returns:
            Liste des événements vision
        """
        return self.get_by_modality("vision", session_id, limit)
    
    def get_multimodal_summary(
        self,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Résumé multimodal d'une session
        
        Args:
            session_id: ID de session (optionnel)
            
        Returns:
            Statistiques par modalité
        """
        events = self.events
        if session_id:
            events = [e for e in events if e["session_id"] == session_id]
        
        modality_counts = {}
        for modality in self.modalities:
            count = sum(
                1 for e in events
                if e.get("metadata", {}).get("modality") == modality
            )
            modality_counts[modality] = count
        
        return {
            "session_id": session_id or "all",
            "total_events": len(events),
            "modality_breakdown": modality_counts,
            "modalities_used": [m for m, c in modality_counts.items() if c > 0]
        }
