"""
MCP System Server
FastAPI server exposing system operations through HTTP endpoints.
All sensitive operations require allow=True for security.
"""


from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from connectors.system.system_actions import (
    SystemActions,
    SystemActionsError,
    PermissionDeniedError
)

app = FastAPI(
    title="MCP System Server",
    description="System operations service for the agent",
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

# Initialize SystemActions
system_actions = SystemActions()


# Pydantic models for request validation
class KillProcessRequest(BaseModel):
    """Request model for killing a process."""
    name: str = Field(..., description="Name of the process to kill")
    allow: bool = Field(False, description="Must be True to authorize the action")


class OpenFileRequest(BaseModel):
    """Request model for opening a file."""
    path: str = Field(..., description="Path to the file")
    allow: bool = Field(False, description="Must be True to authorize the action")


class OpenFolderRequest(BaseModel):
    """Request model for opening a folder."""
    path: str = Field(..., description="Path to the folder")
    allow: bool = Field(False, description="Must be True to authorize the action")


class RunProgramRequest(BaseModel):
    """Request model for running a program."""
    path: str = Field(..., description="Path to the program")
    args: Optional[List[str]] = Field(None, description="Optional arguments for the program")
    allow: bool = Field(False, description="Must be True to authorize the action")


class ExistsRequest(BaseModel):
    """Request model for checking if a path exists."""
    path: str = Field(..., description="Path to check")
    allow: bool = Field(False, description="Must be True to authorize the action")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "MCP System Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "list_processes": "GET /system/list_processes",
            "kill_process": "POST /system/kill_process",
            "open_file": "POST /system/open_file",
            "open_folder": "POST /system/open_folder",
            "run_program": "POST /system/run_program",
            "exists": "POST /system/exists"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-system"}


@app.get("/system/list_processes")
async def list_processes():
    """
    List all running processes.
    
    Returns:
        Dict with list of processes including PID, name, username, and memory usage.
    
    Raises:
        HTTPException: If operation fails
    """
    try:
        result = system_actions.list_processes()
        return result
    except SystemActionsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/system/kill_process")
async def kill_process(request: KillProcessRequest):
    """
    Kill a process by name.
    
    Args:
        request: KillProcessRequest with process name and allow flag
    
    Returns:
        Dict with status and number of processes killed
    
    Raises:
        HTTPException: If allow=True is not provided or operation fails
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for security"
        )
    
    try:
        result = system_actions.kill_process(request.name)
        return result
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/system/open_file")
async def open_file(request: OpenFileRequest):
    """
    Open a file with the default application.
    
    Args:
        request: OpenFileRequest with file path and allow flag
    
    Returns:
        Dict with status and file information
    
    Raises:
        HTTPException: If allow=True is not provided or operation fails
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for security"
        )
    
    try:
        result = system_actions.open_file(request.path, allow=request.allow)
        return result
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/system/open_folder")
async def open_folder(request: OpenFolderRequest):
    """
    Open a folder in the file explorer.
    
    Args:
        request: OpenFolderRequest with folder path and allow flag
    
    Returns:
        Dict with status and folder information
    
    Raises:
        HTTPException: If allow=True is not provided or operation fails
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for security"
        )
    
    try:
        result = system_actions.open_folder(request.path, allow=request.allow)
        return result
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/system/run_program")
async def run_program(request: RunProgramRequest):
    """
    Run a program with optional arguments.
    
    Args:
        request: RunProgramRequest with program path, args, and allow flag
    
    Returns:
        Dict with status, program information, and PID
    
    Raises:
        HTTPException: If allow=True is not provided or operation fails
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for security"
        )
    
    try:
        result = system_actions.run_program(request.path, args=request.args)
        return result
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/system/exists")
async def exists(request: ExistsRequest):
    """
    Check if a path (file or folder) exists.
    
    Args:
        request: ExistsRequest with path and allow flag
    
    Returns:
        Dict with existence status and path information
    
    Raises:
        HTTPException: If allow=True is not provided or operation fails
    """
    if not request.allow:
        raise HTTPException(
            status_code=403,
            detail="Permission denied: allow=True required for security"
        )
    
    try:
        result = system_actions.exists(request.path, allow=request.allow)
        return result
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
