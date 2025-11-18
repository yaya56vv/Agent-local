"""
Session Memory Engine - Gestion de l'historique de conversation court terme
Ce module gère la mémoire de session (historique de conversation).
NE PAS confondre avec RAGStore qui gère le stockage long terme des documents.

Utilisation:
- RAGStore (rag_store.py) = Stockage long terme de documents avec embeddings
- SessionMemory (rag_engine.py) = Historique de conversation court terme
- MemoryManager (connectors/memory/memory_manager.py) = Gestion persistante des sessions
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parents[2]  # C:\AGENT LOCAL
SESSIONS_DIR = BASE_DIR / "memory" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(session_id: str) -> Path:
    """Get the file path for a session"""
    return SESSIONS_DIR / f"{session_id}.jsonl"


def add_message_to_session(
    session_id: str,
    role: str,
    content: str,
    meta: Dict[str, Any] | None = None,
) -> None:
    """
    Add a message to the session history.
    
    Args:
        session_id: Session identifier
        role: Message role (user, assistant, system)
        content: Message content
        meta: Optional metadata
    """
    meta = meta or {}
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "role": role,
        "content": content,
        "meta": meta,
    }
    path = _session_path(session_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get the conversation history for a session.
    
    Args:
        session_id: Session identifier
        limit: Maximum number of messages to return (most recent)
        
    Returns:
        List of message records
    """
    path = _session_path(session_id)
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    # Keep only the most recent messages
    lines = lines[-limit:]

    out: List[Dict[str, Any]] = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
