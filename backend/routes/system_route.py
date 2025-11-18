from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.system.system_actions import (
    SystemActions,
    SystemActionsError,
    PermissionDeniedError
)


router = APIRouter()


class OpenFileRequest(BaseModel):
    """Request model for opening a file."""
    path: str = Field(..., description="Path to the file to open")
    allow: bool = Field(False, description="Must be True to allow opening")


class OpenFolderRequest(BaseModel):
    """Request model for opening a folder."""
    path: str = Field(..., description="Path to the folder to open")
    allow: bool = Field(False, description="Must be True to allow opening")


class RunProgramRequest(BaseModel):
    """Request model for running a program."""
    path: str = Field(..., description="Path to the program to run")
    args: Optional[List[str]] = Field(None, description="Optional program arguments")
    allow: bool = Field(False, description="Must be True to allow running")


class ListProcessesRequest(BaseModel):
    """Request model for listing processes."""
    allow: bool = Field(False, description="Must be True to allow listing")


class KillProcessRequest(BaseModel):
    """Request model for killing a process."""
    name: str = Field(..., description="Name of the process to kill")
    allow: bool = Field(False, description="Must be True to allow killing")


class ExistsRequest(BaseModel):
    """Request model for checking path existence."""
    path: str = Field(..., description="Path to check")
    allow: bool = Field(False, description="Must be True to allow checking")


# Initialize system actions
system_actions = SystemActions()


@router.post("/open")
async def open_file_or_folder(request: OpenFileRequest):
    """
    Open a file or folder with the default application.

    Args:
        request: OpenFileRequest with path and allow flag

    Returns:
        dict: Operation result
    """
    try:
        # Try to open as file first
        try:
            result = system_actions.open_file(
                path=request.path,
                allow=request.allow
            )
            return result
        except SystemActionsError as e:
            # If it's not a file, try as folder
            if "not a file" in str(e).lower():
                result = system_actions.open_folder(
                    path=request.path,
                    allow=request.allow
                )
                return result
            else:
                raise

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open: {str(e)}"
        )


@router.post("/open/file")
async def open_file(request: OpenFileRequest):
    """
    Open a file with the default application.

    Args:
        request: OpenFileRequest with path and allow flag

    Returns:
        dict: Operation result
    """
    try:
        result = system_actions.open_file(
            path=request.path,
            allow=request.allow
        )
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open file: {str(e)}"
        )


@router.post("/open/folder")
async def open_folder(request: OpenFolderRequest):
    """
    Open a folder in the file explorer.

    Args:
        request: OpenFolderRequest with path and allow flag

    Returns:
        dict: Operation result
    """
    try:
        result = system_actions.open_folder(
            path=request.path,
            allow=request.allow
        )
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open folder: {str(e)}"
        )


@router.post("/run")
async def run_program(request: RunProgramRequest):
    """
    Run a program.

    Args:
        request: RunProgramRequest with path, optional args, and allow flag

    Returns:
        dict: Operation result with PID
    """
    try:
        result = system_actions.run_program(
            path=request.path,
            args=request.args,
            allow=request.allow
        )
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run program: {str(e)}"
        )


@router.post("/list")
async def list_processes(request: ListProcessesRequest):
    """
    List all running processes.

    Args:
        request: ListProcessesRequest with allow flag

    Returns:
        dict: List of processes with details
    """
    try:
        result = system_actions.list_processes(allow=request.allow)
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list processes: {str(e)}"
        )


@router.post("/kill")
async def kill_process(request: KillProcessRequest):
    """
    Kill a process by name.

    Args:
        request: KillProcessRequest with process name and allow flag

    Returns:
        dict: Operation result with killed count
    """
    try:
        result = system_actions.kill_process(
            name=request.name,
            allow=request.allow
        )
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to kill process: {str(e)}"
        )


@router.post("/exists")
async def check_exists(request: ExistsRequest):
    """
    Check if a path (file or folder) exists.

    Args:
        request: ExistsRequest with path and allow flag

    Returns:
        dict: Existence status and path information
    """
    try:
        result = system_actions.exists(
            path=request.path,
            allow=request.allow
        )
        return result

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except SystemActionsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check existence: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for system service.

    Returns:
        dict: Health status
    """
    try:
        platform_info = {
            "status": "healthy",
            "service": "system",
            "platform": system_actions.platform,
            "is_windows": system_actions.is_windows
        }

        # Check if psutil is available
        try:
            import psutil
            platform_info["psutil_available"] = True
        except ImportError:
            platform_info["psutil_available"] = False
            platform_info["warning"] = "psutil not installed - process management unavailable"

        return platform_info

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "system",
            "error": str(e)
        }


@router.get("/info")
async def system_info():
    """
    Get system information.

    Returns:
        dict: System information
    """
    import platform

    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

    # Add psutil info if available
    try:
        import psutil
        info["psutil_available"] = True
        info["cpu_count"] = psutil.cpu_count()
        info["memory_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        info["psutil_available"] = False

    return {
        "status": "success",
        "info": info
    }
