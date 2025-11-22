import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class MemoryManager:
    """
    Long-term memory manager for storing and retrieving conversation history.
    Uses JSON file storage organized by session_id.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the memory manager.
        
        Args:
            storage_dir: Directory for storing memory files.
                        Defaults to C:\\AGENT LOCAL\\memory_data
        """
        if storage_dir is None:
            # Default to memory_data in project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.storage_dir = project_root / "memory_data"
        else:
            self.storage_dir = Path(storage_dir)
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_file(self, session_id: str) -> Path:
        """
        Get the file path for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path: Path to the session file
        """
        # Sanitize session_id to be filesystem-safe
        safe_session_id = "".join(c for c in session_id if c.isalnum() or c in ('-', '_'))
        return self.storage_dir / f"{safe_session_id}.json"

    def add(self, session_id: str, message: str, role: str = "user", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the session memory.
        
        Args:
            session_id: Session identifier
            message: Message content
            role: Message role (user, assistant, system)
            metadata: Optional metadata dictionary
        """
        session_file = self._get_session_file(session_id)
        
        # Load existing data or create new
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        # Add new message
        message_entry = {
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            message_entry["metadata"] = metadata
        
        data["messages"].append(message_entry)
        data["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (most recent first)
            
        Returns:
            List of message dictionaries
        """
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            return []
        
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get("messages", [])
        
        if limit:
            messages = messages[-limit:]
        
        return messages

    def get_full_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete session data including metadata.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete session dictionary
        """
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            return {
                "session_id": session_id,
                "messages": [],
                "exists": False
            }
        
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data["exists"] = True
        return data

    def clear(self, session_id: str) -> bool:
        """
        Clear all messages from a session (deletes the file).
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was cleared, False if it didn't exist
        """
        session_file = self._get_session_file(session_id)
        
        if session_file.exists():
            session_file.unlink()
            return True
        
        return False

    def list_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        session_files = self.storage_dir.glob("*.json")
        return [f.stem for f in session_files]

    def search(self, query: str, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query text.
        Simple text-based search (no semantic vectors for now).
        
        Args:
            query: Search query
            session_id: Optional session to search in. If None, searches all sessions.
            
        Returns:
            List of matching messages with session context
        """
        query_lower = query.lower()
        results = []
        
        # Determine which sessions to search
        if session_id:
            sessions_to_search = [session_id]
        else:
            sessions_to_search = self.list_sessions()
        
        for sid in sessions_to_search:
            messages = self.get(sid)
            
            for msg in messages:
                if query_lower in msg.get("content", "").lower():
                    results.append({
                        "session_id": sid,
                        "message": msg,
                        "match_type": "content"
                    })
        
        return results

    def get_context(self, session_id: str, max_messages: int = 10) -> str:
        """
        Get formatted context from recent messages for RAG/prompting.
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        messages = self.get(session_id, limit=max_messages)
        
        if not messages:
            return "No previous conversation history."
        
        context_lines = ["Previous conversation:"]
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            context_lines.append(f"[{role}] {content}")
        
        return "\n".join(context_lines)

    def get_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary dictionary
        """
        session_data = self.get_full_session(session_id)
        
        if not session_data.get("exists"):
            return {
                "session_id": session_id,
                "exists": False,
                "message_count": 0
            }
        
        messages = session_data.get("messages", [])
        
        # Count by role
        role_counts = {}
        for msg in messages:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "session_id": session_id,
            "exists": True,
            "message_count": len(messages),
            "role_counts": role_counts,
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at"),
            "first_message": messages[0] if messages else None,
            "last_message": messages[-1] if messages else None
        }
