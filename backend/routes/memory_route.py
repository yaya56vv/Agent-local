from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.memory.memory_manager import MemoryManager


router = APIRouter()


class AddMemoryRequest(BaseModel):
    """Request model for adding a memory."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Message content", min_length=1)
    role: Optional[str] = Field("user", description="Message role (user, assistant, system)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class GetMemoryRequest(BaseModel):
    """Request model for getting memories."""
    session_id: str = Field(..., description="Session identifier")
    limit: Optional[int] = Field(None, description="Maximum number of messages to return", ge=1)


class ClearMemoryRequest(BaseModel):
    """Request model for clearing memory."""
    session_id: str = Field(..., description="Session identifier")


class SearchMemoryRequest(BaseModel):
    """Request model for searching memories."""
    query: str = Field(..., description="Search query", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session to search in")


class MemoryResponse(BaseModel):
    """Response model for memory operations."""
    status: str
    session_id: str
    message: Optional[str] = None
    data: Optional[Any] = None


# Initialize memory manager
memory_manager = MemoryManager()


@router.post("/add", response_model=MemoryResponse)
async def add_memory(request: AddMemoryRequest):
    """
    Add a message to session memory.
    
    Args:
        request: AddMemoryRequest with session_id, message, role, and metadata
        
    Returns:
        MemoryResponse: Operation result
    """
    try:
        memory_manager.add(
            session_id=request.session_id,
            message=request.message,
            role=request.role,
            metadata=request.metadata
        )
        
        return MemoryResponse(
            status="success",
            session_id=request.session_id,
            message="Memory added successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add memory: {str(e)}"
        )


@router.post("/get", response_model=MemoryResponse)
async def get_memory(request: GetMemoryRequest):
    """
    Get messages from session memory.
    
    Args:
        request: GetMemoryRequest with session_id and optional limit
        
    Returns:
        MemoryResponse: Messages from the session
    """
    try:
        messages = memory_manager.get(
            session_id=request.session_id,
            limit=request.limit
        )
        
        return MemoryResponse(
            status="success",
            session_id=request.session_id,
            data={
                "messages": messages,
                "count": len(messages)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get memory: {str(e)}"
        )


@router.post("/clear", response_model=MemoryResponse)
async def clear_memory(request: ClearMemoryRequest):
    """
    Clear all messages from a session.
    
    Args:
        request: ClearMemoryRequest with session_id
        
    Returns:
        MemoryResponse: Operation result
    """
    try:
        cleared = memory_manager.clear(request.session_id)
        
        if cleared:
            return MemoryResponse(
                status="success",
                session_id=request.session_id,
                message="Memory cleared successfully"
            )
        else:
            return MemoryResponse(
                status="not_found",
                session_id=request.session_id,
                message="Session not found or already empty"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear memory: {str(e)}"
        )


@router.post("/search")
async def search_memory(request: SearchMemoryRequest):
    """
    Search for messages containing the query text.
    
    Args:
        request: SearchMemoryRequest with query and optional session_id
        
    Returns:
        dict: Search results
    """
    try:
        results = memory_manager.search(
            query=request.query,
            session_id=request.session_id
        )
        
        return {
            "status": "success",
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/sessions")
async def list_sessions():
    """
    List all available session IDs.
    
    Returns:
        dict: List of session IDs
    """
    try:
        sessions = memory_manager.list_sessions()
        
        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get detailed information about a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        dict: Session information
    """
    try:
        session_data = memory_manager.get_full_session(session_id)
        
        return {
            "status": "success",
            "data": session_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """
    Get a summary of the session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        dict: Session summary
    """
    try:
        summary = memory_manager.get_summary(session_id)
        
        return {
            "status": "success",
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session summary: {str(e)}"
        )


@router.get("/session/{session_id}/context")
async def get_session_context(session_id: str, max_messages: int = 10):
    """
    Get formatted context from recent messages for RAG/prompting.
    
    Args:
        session_id: Session identifier
        max_messages: Maximum number of recent messages
        
    Returns:
        dict: Formatted context
    """
    try:
        context = memory_manager.get_context(session_id, max_messages)
        
        return {
            "status": "success",
            "session_id": session_id,
            "context": context,
            "max_messages": max_messages
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for memory service.
    
    Returns:
        dict: Health status
    """
    try:
        # Check if storage directory exists and is writable
        storage_dir = memory_manager.storage_dir
        
        if storage_dir.exists() and storage_dir.is_dir():
            # Try to list sessions
            sessions = memory_manager.list_sessions()
            
            return {
                "status": "healthy",
                "service": "memory",
                "storage_dir": str(storage_dir),
                "session_count": len(sessions)
            }
        else:
            return {
                "status": "unhealthy",
                "service": "memory",
                "error": "Storage directory not accessible"
            }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "memory",
            "error": str(e)
        }