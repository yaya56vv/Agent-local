"""
Timeline Routes - API pour accéder à l'historique
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.orchestrator.timeline import Timeline

router = APIRouter(prefix="/timeline", tags=["timeline"])

# Instance globale de timeline (sera injectée par l'orchestrateur)
timeline_instance = Timeline()


@router.get("/events")
async def get_events(
    session_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50
):
    """
    Récupère les événements de la timeline
    
    Args:
        session_id: Filtrer par session
        event_type: Filtrer par type
        limit: Nombre max d'événements
        
    Returns:
        Liste des événements
    """
    try:
        events = timeline_instance.get_events(session_id, event_type, limit)
        return {
            "status": "success",
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """
    Résumé d'une session
    
    Args:
        session_id: ID de session
        
    Returns:
        Statistiques de la session
    """
    try:
        summary = timeline_instance.get_session_summary(session_id)
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_actions(limit: int = 10):
    """
    Actions récentes
    
    Args:
        limit: Nombre max d'actions
        
    Returns:
        Liste des actions récentes
    """
    try:
        actions = timeline_instance.get_recent_actions(limit)
        return {
            "status": "success",
            "count": len(actions),
            "actions": actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_timeline(session_id: Optional[str] = None):
    """
    Exporte la timeline en JSON
    
    Args:
        session_id: Optionnel, filtrer par session
        
    Returns:
        Timeline en JSON
    """
    try:
        json_data = timeline_instance.export_timeline(session_id)
        return {
            "status": "success",
            "data": json_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Efface les événements d'une session
    
    Args:
        session_id: ID de session
        
    Returns:
        Nombre d'événements supprimés
    """
    try:
        deleted = timeline_instance.clear_session(session_id)
        return {
            "status": "success",
            "deleted": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))