"""
MCP Files Service - FastAPI Server
Provides HTTP endpoints for file operations using FileManager
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.connectors.files.file_manager import FileManager

# Initialize FastAPI app
app = FastAPI(
    title="MCP Files Service",
    description="File operations service for MCP protocol",
    version="1.0.0"
)

# Initialize FileManager with default configuration
file_manager = FileManager()


# Pydantic models for request bodies
class WriteFileRequest(BaseModel):
    path: str
    content: str


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP Files",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/files/read")
async def read_file(path: str = Query(..., description="Path to the file to read")):
    """
    Read content from a file.
    
    Args:
        path: Path to the file (relative or absolute)
        
    Returns:
        File content and metadata
        
    Raises:
        HTTPException: If file not found or cannot be read
    """
    result = file_manager.read(path)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    
    return JSONResponse(content=result)


@app.get("/files/list")
async def list_directory(path: str = Query(".", description="Path to the directory to list")):
    """
    List contents of a directory.
    
    Args:
        path: Path to the directory (default: current directory)
        
    Returns:
        List of files and directories with metadata
        
    Raises:
        HTTPException: If directory not found or cannot be listed
    """
    result = file_manager.list_dir(path)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    
    return JSONResponse(content=result)


@app.post("/files/write")
async def write_file(request: WriteFileRequest):
    """
    Write content to a file.
    
    Args:
        request: WriteFileRequest with path and content
        
    Returns:
        Success status and file metadata
        
    Raises:
        HTTPException: If write operation fails
    """
    result = file_manager.write(request.path, request.content, allow=True)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    if result["status"] == "denied":
        raise HTTPException(status_code=403, detail=result["error"])
    
    return JSONResponse(content=result)


@app.delete("/files/delete")
async def delete_file(path: str = Query(..., description="Path to the file to delete")):
    """
    Delete a file.
    
    Args:
        path: Path to the file to delete
        
    Returns:
        Success status
        
    Raises:
        HTTPException: If file not found or cannot be deleted
    """
    result = file_manager.delete(path, allow=True)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    
    if result["status"] == "denied":
        raise HTTPException(status_code=403, detail=result["error"])
    
    return JSONResponse(content=result)


# Additional utility endpoints
@app.get("/files/exists")
async def check_exists(path: str = Query(..., description="Path to check")):
    """
    Check if a file or directory exists.
    
    Args:
        path: Path to check
        
    Returns:
        Existence status and type
    """
    result = file_manager.exists(path)
    return JSONResponse(content=result)


@app.get("/files/info")
async def get_file_info(path: str = Query(..., description="Path to get info for")):
    """
    Get detailed information about a file or directory.
    
    Args:
        path: Path to the file/directory
        
    Returns:
        Detailed file/directory information
        
    Raises:
        HTTPException: If path not found
    """
    result = file_manager.get_info(path)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)