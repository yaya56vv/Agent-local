"""
GLM Vision Expert MCP Server
FastAPI server exposing GLM-4.6 capabilities through MCP protocol
Port: 9001 (configurable)
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.mcp.glm_vision_expert.tools.tool_handlers import ToolHandlers
from backend.mcp.glm_vision_expert.clients.glm_client import GLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GLM Vision Expert MCP Server",
    description="MCP Server for GLM-4.6 model with comprehensive tool support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
tool_handlers = ToolHandlers()
glm_client = GLMClient()


# ============================================================
# REQUEST MODELS
# ============================================================

class SolveProblemRequest(BaseModel):
    """Request model for solve_problem tool."""
    description: str = Field(..., description="Problem description")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class AnalyzeCodeRequest(BaseModel):
    """Request model for analyze_code tool."""
    filepath: str = Field(..., description="Path to code file")
    task: str = Field(..., description="Analysis task description")


class AnalyzeVisualRequest(BaseModel):
    """Request model for analyze_visual_screenshot tool."""
    image_base64: str = Field(..., description="Base64 encoded image")
    question: str = Field(..., description="Question about the image")


class RAGQueryRequest(BaseModel):
    """Request model for rag_query tool."""
    query: str = Field(..., description="Search query")
    dataset: str = Field(..., description="Dataset to search in")


class RAGWriteRequest(BaseModel):
    """Request model for rag_write tool."""
    content: str = Field(..., description="Content to store")
    dataset: str = Field(..., description="Target dataset")
    filename: Optional[str] = Field(None, description="Optional filename")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class FileReadRequest(BaseModel):
    """Request model for file_read tool."""
    filepath: str = Field(..., description="Path to file")


class FileWriteRequest(BaseModel):
    """Request model for file_write tool."""
    filepath: str = Field(..., description="Target file path")
    content: str = Field(..., description="Content to write")
    allow: bool = Field(False, description="Must be True to authorize write")


class FileSearchRequest(BaseModel):
    """Request model for file_search tool."""
    pattern: str = Field(..., description="Search pattern")
    directory: str = Field(".", description="Directory to search in")


class ShellExecuteRequest(BaseModel):
    """Request model for shell_execute_safe tool."""
    command: str = Field(..., description="Command to execute")
    allow: bool = Field(False, description="Must be True to authorize execution")


class BrowserSearchRequest(BaseModel):
    """Request model for browser_search tool."""
    query: str = Field(..., description="Search query")


# ============================================================
# HEALTH & INFO ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "GLM Vision Expert MCP Server",
        "version": "1.0.0",
        "status": "running",
        "model": "GLM-4.6 via OpenRouter",
        "tools": [
            "solve_problem",
            "analyze_code",
            "analyze_visual_screenshot",
            "rag_query",
            "rag_write",
            "file_read",
            "file_write",
            "file_search",
            "shell_execute_safe",
            "browser_search"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        is_available = await glm_client.is_available()
        return {
            "status": "healthy" if is_available else "degraded",
            "service": "glm-vision-expert",
            "glm_available": is_available
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "glm-vision-expert",
            "error": str(e)
        }


@app.get("/mcp/tools/list")
async def list_tools():
    """
    MCP endpoint: List all available tools.
    
    Returns:
        List of tool definitions with schemas
    """
    tools = [
        {
            "name": "solve_problem",
            "description": "Solve a problem using GLM-4.6 reasoning capabilities",
            "parameters": {
                "description": {"type": "string", "required": True},
                "context": {"type": "object", "required": False}
            }
        },
        {
            "name": "analyze_code",
            "description": "Analyze code file with GLM-4.6",
            "parameters": {
                "filepath": {"type": "string", "required": True},
                "task": {"type": "string", "required": True}
            }
        },
        {
            "name": "analyze_visual_screenshot",
            "description": "Analyze screenshot using GLM-4.6 vision capabilities",
            "parameters": {
                "image_base64": {"type": "string", "required": True},
                "question": {"type": "string", "required": True}
            }
        },
        {
            "name": "rag_query",
            "description": "Query RAG store and synthesize answer with GLM-4.6",
            "parameters": {
                "query": {"type": "string", "required": True},
                "dataset": {"type": "string", "required": True}
            }
        },
        {
            "name": "rag_write",
            "description": "Write content to RAG store with validation",
            "parameters": {
                "content": {"type": "string", "required": True},
                "dataset": {"type": "string", "required": True},
                "filename": {"type": "string", "required": False},
                "metadata": {"type": "object", "required": False}
            }
        },
        {
            "name": "file_read",
            "description": "Read file content",
            "parameters": {
                "filepath": {"type": "string", "required": True}
            }
        },
        {
            "name": "file_write",
            "description": "Write content to file with validation",
            "parameters": {
                "filepath": {"type": "string", "required": True},
                "content": {"type": "string", "required": True},
                "allow": {"type": "boolean", "required": True}
            }
        },
        {
            "name": "file_search",
            "description": "Search for files matching pattern",
            "parameters": {
                "pattern": {"type": "string", "required": True},
                "directory": {"type": "string", "required": False}
            }
        },
        {
            "name": "shell_execute_safe",
            "description": "Execute shell command with safety checks",
            "parameters": {
                "command": {"type": "string", "required": True},
                "allow": {"type": "boolean", "required": True}
            }
        },
        {
            "name": "browser_search",
            "description": "Perform web search and summarize results with GLM-4.6",
            "parameters": {
                "query": {"type": "string", "required": True}
            }
        }
    ]
    
    return {
        "tools": tools,
        "count": len(tools)
    }


# ============================================================
# TOOL ENDPOINTS
# ============================================================

@app.post("/glm/solve_problem")
async def solve_problem(request: SolveProblemRequest):
    """
    Solve a problem using GLM-4.6 reasoning.
    
    Args:
        request: Problem description and context
        
    Returns:
        Solution with reasoning steps
    """
    logger.info(f"solve_problem: {request.description[:100]}...")
    try:
        result = await tool_handlers.solve_problem(
            description=request.description,
            context=request.context
        )
        return result
    except Exception as e:
        logger.error(f"solve_problem error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/analyze_code")
async def analyze_code(request: AnalyzeCodeRequest):
    """
    Analyze code file with GLM-4.6.
    
    Args:
        request: Filepath and analysis task
        
    Returns:
        Code analysis results
    """
    logger.info(f"analyze_code: {request.filepath}")
    try:
        result = await tool_handlers.analyze_code(
            filepath=request.filepath,
            task=request.task
        )
        return result
    except Exception as e:
        logger.error(f"analyze_code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/analyze_visual_screenshot")
async def analyze_visual_screenshot(request: AnalyzeVisualRequest):
    """
    Analyze screenshot using GLM-4.6 vision.
    
    Args:
        request: Base64 image and question
        
    Returns:
        Visual analysis results
    """
    logger.info(f"analyze_visual_screenshot: {request.question[:100]}...")
    try:
        result = await tool_handlers.analyze_visual_screenshot(
            image_base64=request.image_base64,
            question=request.question
        )
        return result
    except Exception as e:
        logger.error(f"analyze_visual_screenshot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/rag_query")
async def rag_query(request: RAGQueryRequest):
    """
    Query RAG store with GLM-4.6 synthesis.
    
    Args:
        request: Query and dataset
        
    Returns:
        RAG query results with synthesized answer
    """
    logger.info(f"rag_query: {request.query[:100]}... in {request.dataset}")
    try:
        result = await tool_handlers.rag_query(
            query=request.query,
            dataset=request.dataset
        )
        return result
    except Exception as e:
        logger.error(f"rag_query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/rag_write")
async def rag_write(request: RAGWriteRequest):
    """
    Write content to RAG store.
    
    Args:
        request: Content, dataset, and metadata
        
    Returns:
        Write operation result
    """
    logger.info(f"rag_write: {len(request.content)} chars to {request.dataset}")
    try:
        result = await tool_handlers.rag_write(
            content=request.content,
            dataset=request.dataset,
            filename=request.filename,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"rag_write error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/file_read")
async def file_read(request: FileReadRequest):
    """
    Read file content.
    
    Args:
        request: Filepath
        
    Returns:
        File content
    """
    logger.info(f"file_read: {request.filepath}")
    try:
        result = await tool_handlers.file_read(filepath=request.filepath)
        return result
    except Exception as e:
        logger.error(f"file_read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/file_write")
async def file_write(request: FileWriteRequest):
    """
    Write content to file.
    
    Args:
        request: Filepath, content, and allow flag
        
    Returns:
        Write operation result
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for file write"
        )
    
    logger.info(f"file_write: {request.filepath}")
    try:
        result = await tool_handlers.file_write(
            filepath=request.filepath,
            content=request.content,
            allow=request.allow
        )
        return result
    except Exception as e:
        logger.error(f"file_write error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/file_search")
async def file_search(request: FileSearchRequest):
    """
    Search for files matching pattern.
    
    Args:
        request: Pattern and directory
        
    Returns:
        List of matching files
    """
    logger.info(f"file_search: {request.pattern} in {request.directory}")
    try:
        result = await tool_handlers.file_search(
            pattern=request.pattern,
            directory=request.directory
        )
        return result
    except Exception as e:
        logger.error(f"file_search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/shell_execute_safe")
async def shell_execute_safe(request: ShellExecuteRequest):
    """
    Execute shell command with safety checks.
    
    Args:
        request: Command and allow flag
        
    Returns:
        Command execution result
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for command execution"
        )
    
    logger.info(f"shell_execute_safe: {request.command}")
    try:
        result = await tool_handlers.shell_execute_safe(
            command=request.command,
            allow=request.allow
        )
        return result
    except Exception as e:
        logger.error(f"shell_execute_safe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/glm/browser_search")
async def browser_search(request: BrowserSearchRequest):
    """
    Perform web search with GLM-4.6 summary.
    
    Args:
        request: Search query
        
    Returns:
        Search results with summary
    """
    logger.info(f"browser_search: {request.query}")
    try:
        result = await tool_handlers.browser_search(query=request.query)
        return result
    except Exception as e:
        logger.error(f"browser_search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting GLM Vision Expert MCP Server on port 9001...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9001,
        log_level="info"
    )
