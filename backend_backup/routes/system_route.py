"""
System Routes - API endpoints for system operations
Provides endpoints for file/folder operations and process management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.system.system_actions import (
    SystemActions,
    SystemActionsError,
    PermissionDeniedError
)

router = APIRouter()
system_actions = SystemActions()


class PathRequest(BaseModel):
    """Request model for path operations."""
    path: str = Field(..., description="Path to the file/folder")


class RunProcessRequest(BaseModel):
    """Request model for running a process."""
    path: str = Field(..., description="Path to the program")
    args: Optional[List[str]] = Field(None, description="Optional arguments")


class KillProcessRequest(BaseModel):
    """Request model for killing a process."""
    name: str = Field(..., description="Process name to kill")


@router.post("/open_path")
async def open_path(request: PathRequest):
    """
    Open a file or folder with the default application.
    
    Args:
        request: PathRequest with path
        
    Returns:
        dict: Operation result with status, data, and message
    """
    try:
        result = system_actions.open_path(path=request.path)
        
        return {
            "status": "success",
            "data": result,
            "message": f"Opened: {request.path}"
        }
    
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open path: {str(e)}")


@router.post("/run_process")
async def run_process(request: RunProcessRequest):
    """
    Run a program/process.
    
    Args:
        request: RunProcessRequest with path and optional args
        
    Returns:
        dict: Operation result with PID
    """
    try:
        result = system_actions.run_program(
            path=request.path,
            args=request.args
        )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Process started with PID {result.get('pid')}"
        }
    
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run process: {str(e)}")


@router.post("/list_processes")
async def list_processes():
    """
    List all running processes.
    
    Returns:
        dict: List of processes with details
    """
    try:
        result = system_actions.list_processes()
        
        return {
            "status": "success",
            "data": result,
            "message": f"Found {result.get('count', 0)} processes"
        }
    
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list processes: {str(e)}")


@router.post("/kill_process")
async def kill_process(request: KillProcessRequest):
    """
    Kill a process by name.
    
    Args:
        request: KillProcessRequest with process name
        
    Returns:
        dict: Operation result with killed count
    """
    try:
        result = system_actions.kill_process(name=request.name)
        
        return {
            "status": "success",
            "data": result,
            "message": f"Killed {result.get('killed_count', 0)} process(es)"
        }
    
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SystemActionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to kill process: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for system service.
    
    Returns:
        dict: Health status
    """
    try:
        # Check if psutil is available
        try:
            import psutil
            psutil_available = True
        except ImportError:
            psutil_available = False
        
        return {
            "status": "healthy",
            "service": "system",
            "platform": system_actions.platform,
            "is_windows": system_actions.is_windows,
            "psutil_available": psutil_available
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "system",
            "error": str(e)
        }

