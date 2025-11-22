from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.files.file_manager import FileManager


router = APIRouter()


class ReadFileRequest(BaseModel):
    """Request model for reading a file."""
    file_path: str = Field(..., description="Path to the file")
    encoding: Optional[str] = Field("utf-8", description="File encoding")


class WriteFileRequest(BaseModel):
    """Request model for writing a file."""
    file_path: str = Field(..., description="Path to the file")
    content: str = Field(..., description="Content to write")
    allow: bool = Field(False, description="Must be True to allow writing")
    encoding: Optional[str] = Field("utf-8", description="File encoding")


class ListDirRequest(BaseModel):
    """Request model for listing a directory."""
    dir_path: Optional[str] = Field(".", description="Path to the directory")


class MakeDirRequest(BaseModel):
    """Request model for creating a directory."""
    dir_path: str = Field(..., description="Path to the directory")
    allow: bool = Field(False, description="Must be True to allow creation")


class DeleteFileRequest(BaseModel):
    """Request model for deleting a file."""
    file_path: str = Field(..., description="Path to the file")
    allow: bool = Field(False, description="Must be True to allow deletion")


class FileExistsRequest(BaseModel):
    """Request model for checking file existence."""
    file_path: str = Field(..., description="Path to check")


class FileInfoRequest(BaseModel):
    """Request model for getting file info."""
    file_path: str = Field(..., description="Path to the file")


# Initialize file manager
file_manager = FileManager()


@router.post("/read")
async def read_file(request: ReadFileRequest):
    """
    Read content from a file.
    
    Args:
        request: ReadFileRequest with file_path and encoding
        
    Returns:
        dict: File content and metadata
    """
    try:
        result = file_manager.read(
            file_path=request.file_path,
            encoding=request.encoding
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file: {str(e)}"
        )


@router.post("/write")
async def write_file(request: WriteFileRequest):
    """
    Write content to a file.
    
    Args:
        request: WriteFileRequest with file_path, content, allow, and encoding
        
    Returns:
        dict: Operation result
    """
    try:
        result = file_manager.write(
            file_path=request.file_path,
            content=request.content,
            allow=request.allow,
            encoding=request.encoding
        )
        
        if result["status"] == "denied":
            raise HTTPException(status_code=403, detail=result["error"])
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write file: {str(e)}"
        )


@router.post("/list")
async def list_directory(request: ListDirRequest):
    """
    List contents of a directory.
    
    Args:
        request: ListDirRequest with dir_path
        
    Returns:
        dict: Directory contents
    """
    try:
        result = file_manager.list_dir(dir_path=request.dir_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list directory: {str(e)}"
        )


@router.post("/mkdir")
async def make_directory(request: MakeDirRequest):
    """
    Create a directory.
    
    Args:
        request: MakeDirRequest with dir_path and allow
        
    Returns:
        dict: Operation result
    """
    try:
        result = file_manager.make_dir(
            dir_path=request.dir_path,
            allow=request.allow
        )
        
        if result["status"] == "denied":
            raise HTTPException(status_code=403, detail=result["error"])
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create directory: {str(e)}"
        )


@router.post("/delete")
async def delete_file(request: DeleteFileRequest):
    """
    Delete a file.
    
    Args:
        request: DeleteFileRequest with file_path and allow
        
    Returns:
        dict: Operation result
    """
    try:
        result = file_manager.delete(
            file_path=request.file_path,
            allow=request.allow
        )
        
        if result["status"] == "denied":
            raise HTTPException(status_code=403, detail=result["error"])
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.post("/exists")
async def check_exists(request: FileExistsRequest):
    """
    Check if a file or directory exists.
    
    Args:
        request: FileExistsRequest with file_path
        
    Returns:
        dict: Existence status
    """
    try:
        result = file_manager.exists(file_path=request.file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check existence: {str(e)}"
        )


@router.post("/info")
async def get_file_info(request: FileInfoRequest):
    """
    Get detailed information about a file or directory.
    
    Args:
        request: FileInfoRequest with file_path
        
    Returns:
        dict: File/directory information
    """
    try:
        result = file_manager.get_info(file_path=request.file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for files service.
    
    Returns:
        dict: Health status
    """
    try:
        # Check if base directory is accessible
        base_dir = file_manager.base_dir
        
        if base_dir.exists() and base_dir.is_dir():
            return {
                "status": "healthy",
                "service": "files",
                "base_dir": str(base_dir)
            }
        else:
            return {
                "status": "unhealthy",
                "service": "files",
                "error": "Base directory not accessible"
            }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "files",
            "error": str(e)
        }
