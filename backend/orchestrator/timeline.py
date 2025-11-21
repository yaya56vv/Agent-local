"""
Timeline - Enregistre l'historique des actions et résultats
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class Timeline:
    """Gère l'historique chronologique des actions"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.max_events = 1000  # Limite pour éviter surcharge mémoire
    
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
            event_type: Type d'événement (plan, execution, error, etc.)
            data: Données de l'événement
            session_id: ID de session
            metadata: Métadonnées optionnelles
            
        Returns:
            L'événement créé
        """
        event = {
            "id": len(self.events) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "session_id": session_id,
            "data": data,
            "metadata": metadata or {}
        }
        
        self.events.append(event)
        
        # Limiter la taille
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        return event
    
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