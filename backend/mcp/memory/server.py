"""
MCP Memory Service - FastAPI Server
Provides HTTP endpoints for memory/conversation management using MemoryManager
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.connectors.memory.memory_manager import MemoryManager

# Initialize FastAPI app
app = FastAPI(
    title="MCP Memory Service",
    description="Memory and conversation management service for MCP protocol",
    version="1.0.0"
)

# Initialize MemoryManager with default configuration
memory_manager = MemoryManager()


# Pydantic models for request bodies
class AddMessageRequest(BaseModel):
    session_id: str
    role: str  # user, assistant, system
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ClearSessionRequest(BaseModel):
    session_id: str


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP Memory",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/memory/add_message")
async def add_message(request: AddMessageRequest):
    """
    Add a message to the session memory.
    
    Args:
        request: AddMessageRequest with session_id, role, content, and optional metadata
        
    Returns:
        Success status with message details
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        memory_manager.add(
            session_id=request.session_id,
            message=request.content,
            role=request.role,
            metadata=request.metadata
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Message added successfully",
            "session_id": request.session_id,
            "role": request.role
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/get_messages")
async def get_messages(
    session_id: str = Query(..., description="Session identifier"),
    limit: Optional[int] = Query(None, description="Maximum number of messages to return")
):
    """
    Get messages from a session.
    
    Args:
        session_id: Session identifier
        limit: Optional maximum number of messages (most recent)
        
    Returns:
        List of messages
    """
    try:
        messages = memory_manager.get(session_id, limit=limit)
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/clear_session")
async def clear_session(request: ClearSessionRequest):
    """
    Clear all messages from a session.
    
    Args:
        request: ClearSessionRequest with session_id
        
    Returns:
        Success status
        
    Raises:
        HTTPException: If session doesn't exist
    """
    try:
        cleared = memory_manager.clear(request.session_id)
        
        if not cleared:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {request.session_id}"
            )
        
        return JSONResponse(content={
            "status": "success",
            "message": "Session cleared successfully",
            "session_id": request.session_id
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/list_sessions")
async def list_sessions():
    """
    List all available session IDs.
    
    Returns:
        List of session IDs
    """
    try:
        sessions = memory_manager.list_sessions()
        
        return JSONResponse(content={
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/get_summary")
async def get_summary(
    session_id: str = Query(..., description="Session identifier")
):
    """
    Get a summary of the session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session summary with statistics
        
    Raises:
        HTTPException: If session doesn't exist
    """
    try:
        summary = memory_manager.get_summary(session_id)
        
        if not summary.get("exists"):
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {session_id}"
            )
        
        return JSONResponse(content={
            "status": "success",
            "summary": summary
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints
@app.get("/memory/get_full_session")
async def get_full_session(
    session_id: str = Query(..., description="Session identifier")
):
    """
    Get complete session data including metadata.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Complete session data
    """
    try:
        session_data = memory_manager.get_full_session(session_id)
        
        return JSONResponse(content={
            "status": "success",
            "session": session_data
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/get_context")
async def get_context(
    session_id: str = Query(..., description="Session identifier"),
    max_messages: int = Query(10, description="Maximum number of messages for context")
):
    """
    Get formatted context from recent messages for RAG/prompting.
    
    Args:
        session_id: Session identifier
        max_messages: Maximum number of recent messages to include
        
    Returns:
        Formatted context string
    """
    try:
        context = memory_manager.get_context(session_id, max_messages=max_messages)
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "context": context
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/search")
async def search_memory(
    query: str = Query(..., description="Search query"),
    session_id: Optional[str] = Query(None, description="Optional session to search in")
):
    """
    Search for messages containing the query text.
    
    Args:
        query: Search query
        session_id: Optional session to search in (searches all if not provided)
        
    Returns:
        List of matching messages
    """
    try:
        results = memory_manager.search(query, session_id=session_id)
        
        return JSONResponse(content={
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)