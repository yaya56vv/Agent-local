"""
MCP Memory Client - HTTP client for memory/conversation management
"""
import httpx
from typing import Dict, Any, Optional, List


class MemoryClient:
    """Client for MCP Memory Service"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        Initialize the Memory MCP client.
        
        Args:
            base_url: Base URL of the MCP Memory service
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to the session memory.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Success status with message details
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/memory/add_message",
                json={
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get messages from a session.
        
        Args:
            session_id: Session identifier
            limit: Optional maximum number of messages
            
        Returns:
            List of messages
        """
        params = {"session_id": session_id}
        if limit is not None:
            params["limit"] = limit
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/get_messages",
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_context(
        self,
        session_id: str,
        max_messages: int = 10
    ) -> str:
        """
        Get formatted context from recent messages for RAG/prompting.
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages
            
        Returns:
            Formatted context string
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/get_context",
                params={
                    "session_id": session_id,
                    "max_messages": max_messages
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("context", "")
    
    async def search(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query text.
        
        Args:
            query: Search query
            session_id: Optional session to search in
            
        Returns:
            List of matching messages
        """
        params = {"query": query}
        if session_id:
            params["session_id"] = session_id
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/search",
                params=params
            )
            response.raise_for_status()
            result = response.json()
            return result.get("results", [])
    
    async def clear_session(self, session_id: str) -> Dict[str, Any]:
        """
        Clear all messages from a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/memory/clear_session",
                json={"session_id": session_id}
            )
            response.raise_for_status()
            return response.json()
    
    async def list_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/list_sessions"
            )
            response.raise_for_status()
            result = response.json()
            return result.get("sessions", [])
    
    async def get_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary with statistics
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/get_summary",
                params={"session_id": session_id}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("summary", {})
    
    async def get_full_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete session data including metadata.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete session data
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/memory/get_full_session",
                params={"session_id": session_id}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("session", {})
