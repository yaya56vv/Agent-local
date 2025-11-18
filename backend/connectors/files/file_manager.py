import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class FileManager:
    """
    Secure file manager for reading, writing, and managing files.
    All dangerous operations require explicit allow=True parameter.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the file manager.
        
        Args:
            base_dir: Base directory for file operations. 
                     Defaults to C:\\AGENT LOCAL
        """
        if base_dir is None:
            # Default to project root
            self.base_dir = Path("C:/AGENT LOCAL")
        else:
            self.base_dir = Path(base_dir)
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, file_path: str) -> Path:
        """
        Resolve and validate a file path.
        
        Args:
            file_path: File path (relative or absolute)
            
        Returns:
            Path: Resolved path object
            
        Raises:
            ValueError: If path is outside base directory
        """
        # Convert to Path object
        path = Path(file_path)
        
        # If relative, make it relative to base_dir
        if not path.is_absolute():
            path = self.base_dir / path
        
        # Resolve to absolute path
        path = path.resolve()
        
        # Security check: ensure path is within base_dir
        try:
            path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"Access denied: Path {path} is outside base directory {self.base_dir}")
        
        return path

    def read(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            dict: Result with status and content
        """
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}",
                    "path": str(path)
                }
            
            if not path.is_file():
                return {
                    "status": "error",
                    "error": f"Not a file: {file_path}",
                    "path": str(path)
                }
            
            # Read file content
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "status": "success",
                "path": str(path),
                "content": content,
                "size": path.stat().st_size,
                "encoding": encoding
            }
        
        except UnicodeDecodeError:
            return {
                "status": "error",
                "error": f"Cannot decode file with {encoding} encoding",
                "path": str(path)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": file_path
            }

    def write(self, file_path: str, content: str, allow: bool = False, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
            allow: Must be True to allow writing (security)
            encoding: File encoding (default: utf-8)
            
        Returns:
            dict: Result with status
        """
        if not allow:
            return {
                "status": "denied",
                "error": "Write operation requires allow=True",
                "path": file_path
            }
        
        try:
            path = self._resolve_path(file_path)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "status": "success",
                "path": str(path),
                "size": path.stat().st_size,
                "message": "File written successfully"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": file_path
            }

    def list_dir(self, dir_path: str = ".") -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            dict: Result with directory contents
        """
        try:
            path = self._resolve_path(dir_path)
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"Directory not found: {dir_path}",
                    "path": str(path)
                }
            
            if not path.is_dir():
                return {
                    "status": "error",
                    "error": f"Not a directory: {dir_path}",
                    "path": str(path)
                }
            
            # List directory contents
            items = []
            for item in path.iterdir():
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item.relative_to(self.base_dir))
                }
                
                if item.is_file():
                    item_info["size"] = item.stat().st_size
                
                items.append(item_info)
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return {
                "status": "success",
                "path": str(path),
                "items": items,
                "count": len(items)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": dir_path
            }

    def make_dir(self, dir_path: str, allow: bool = False) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            dir_path: Path to the directory
            allow: Must be True to allow creation (security)
            
        Returns:
            dict: Result with status
        """
        if not allow:
            return {
                "status": "denied",
                "error": "Directory creation requires allow=True",
                "path": dir_path
            }
        
        try:
            path = self._resolve_path(dir_path)
            
            if path.exists():
                return {
                    "status": "error",
                    "error": f"Path already exists: {dir_path}",
                    "path": str(path)
                }
            
            # Create directory
            path.mkdir(parents=True, exist_ok=False)
            
            return {
                "status": "success",
                "path": str(path),
                "message": "Directory created successfully"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": dir_path
            }

    def delete(self, file_path: str, allow: bool = False) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            allow: Must be True to allow deletion (security)
            
        Returns:
            dict: Result with status
        """
        if not allow:
            return {
                "status": "denied",
                "error": "Delete operation requires allow=True",
                "path": file_path
            }
        
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}",
                    "path": str(path)
                }
            
            if not path.is_file():
                return {
                    "status": "error",
                    "error": f"Not a file (use rmdir for directories): {file_path}",
                    "path": str(path)
                }
            
            # Delete file
            path.unlink()
            
            return {
                "status": "success",
                "path": str(path),
                "message": "File deleted successfully"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": file_path
            }

    def exists(self, file_path: str) -> Dict[str, Any]:
        """
        Check if a file or directory exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            dict: Result with existence status
        """
        try:
            path = self._resolve_path(file_path)
            
            return {
                "status": "success",
                "path": str(path),
                "exists": path.exists(),
                "type": "directory" if path.is_dir() else "file" if path.is_file() else "unknown"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": file_path
            }

    def get_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Args:
            file_path: Path to the file/directory
            
        Returns:
            dict: Detailed information
        """
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"Path not found: {file_path}",
                    "path": str(path)
                }
            
            stat = path.stat()
            
            info = {
                "status": "success",
                "path": str(path),
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime
            }
            
            if path.is_file():
                info["extension"] = path.suffix
            
            return info
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": file_path
            }