"""
MCP Files Client - HTTP client for file operations
"""
import httpx
from typing import Dict, Any, Optional


class FilesClient:
    """Client for MCP Files Service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize the Files MCP client.
        
        Args:
            base_url: Base URL of the MCP Files service
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File content and metadata
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/files/read",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json()
    
    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            Success status and file metadata
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/files/write",
                json={"path": path, "content": content}
            )
            response.raise_for_status()
            return response.json()
    
    async def list_dir(self, path: str = ".") -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of files and directories with metadata
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/files/list",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Success status
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/files/delete",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json()
    
    async def file_exists(self, path: str) -> Dict[str, Any]:
        """
        Check if a file or directory exists.
        
        Args:
            path: Path to check
            
        Returns:
            Existence status and type
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/files/exists",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Args:
            path: Path to the file/directory
            
        Returns:
            Detailed file/directory information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/files/info",
                params={"path": path}
            )
            response.raise_for_status()
            return response.json()

