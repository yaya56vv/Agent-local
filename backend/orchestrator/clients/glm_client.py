"""
GLM Vision Expert MCP Client
Client for communicating with the GLM Vision Expert MCP Server
"""
import httpx
from typing import Dict, Any, Optional, List
import logging
from backend.config.settings import settings
from backend.config.model_registry import model_registry

logger = logging.getLogger(__name__)

class GLMClient:
    """Client for GLM Vision Expert MCP Server"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the GLM MCP client.

        Args:
            base_url: Base URL of the GLM MCP service (auto-detected from registry if None)
        """
        # Get configuration from model registry if not provided
        if base_url is None:
            glm_config = model_registry.get_model("glm_vision_expert")
            if glm_config and glm_config.get("enabled"):
                base_url = glm_config.get("base_url", f"{settings.GLM_AGENT_HOST}:{settings.GLM_AGENT_PORT}")
            else:
                base_url = f"{settings.GLM_AGENT_HOST}:{settings.GLM_AGENT_PORT}"

        self.base_url = base_url.rstrip('/')
        self.timeout = 300.0  # Long timeout for complex vision/reasoning tasks

        # Log configuration
        logger.info(f"GLM Client initialized with base_url: {self.base_url}")
    
    async def is_available(self) -> bool:
        """Check if the service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200 and response.json().get("status") == "healthy"
        except Exception:
            return False

    async def solve_problem(self, description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Solve a problem using GLM-4.6 reasoning.
        
        Args:
            description: Problem description
            context: Optional context dictionary
            
        Returns:
            Solution with reasoning steps
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "description": description,
                    "context": context
                }
                response = await client.post(f"{self.base_url}/glm/solve_problem", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"solve_problem failed: {e}")
            return {"error": str(e)}

    async def analyze_code(self, filepath: str, task: str) -> Dict[str, Any]:
        """
        Analyze code file with GLM-4.6.
        
        Args:
            filepath: Path to code file
            task: Analysis task description
            
        Returns:
            Code analysis results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "filepath": filepath,
                    "task": task
                }
                response = await client.post(f"{self.base_url}/glm/analyze_code", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"analyze_code failed: {e}")
            return {"error": str(e)}

    async def analyze_visual_screenshot(self, image_base64: str, question: str) -> Dict[str, Any]:
        """
        Analyze screenshot using GLM-4.6 vision.
        
        Args:
            image_base64: Base64 encoded image
            question: Question about the image
            
        Returns:
            Visual analysis results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "image_base64": image_base64,
                    "question": question
                }
                response = await client.post(f"{self.base_url}/glm/analyze_visual_screenshot", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"analyze_visual_screenshot failed: {e}")
            return {"error": str(e)}

    async def rag_query(self, query: str, dataset: str) -> Dict[str, Any]:
        """
        Query RAG store with GLM-4.6 synthesis.
        
        Args:
            query: Search query
            dataset: Dataset to search in
            
        Returns:
            RAG query results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "query": query,
                    "dataset": dataset
                }
                response = await client.post(f"{self.base_url}/glm/rag_query", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"rag_query failed: {e}")
            return {"error": str(e)}

    async def rag_write(self, content: str, dataset: str, filename: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Write content to RAG store.
        
        Args:
            content: Content to store
            dataset: Target dataset
            filename: Optional filename
            metadata: Optional metadata
            
        Returns:
            Write operation result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "content": content,
                    "dataset": dataset,
                    "filename": filename,
                    "metadata": metadata
                }
                response = await client.post(f"{self.base_url}/glm/rag_write", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"rag_write failed: {e}")
            return {"error": str(e)}

    async def file_read(self, filepath: str) -> Dict[str, Any]:
        """
        Read file content.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"filepath": filepath}
                response = await client.post(f"{self.base_url}/glm/file_read", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"file_read failed: {e}")
            return {"error": str(e)}

    async def file_write(self, filepath: str, content: str, allow: bool = False) -> Dict[str, Any]:
        """
        Write content to file.
        
        Args:
            filepath: Target file path
            content: Content to write
            allow: Must be True to authorize write
            
        Returns:
            Write operation result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "filepath": filepath,
                    "content": content,
                    "allow": allow
                }
                response = await client.post(f"{self.base_url}/glm/file_write", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"file_write failed: {e}")
            return {"error": str(e)}

    async def file_search(self, pattern: str, directory: str = ".") -> Dict[str, Any]:
        """
        Search for files matching pattern.
        
        Args:
            pattern: Search pattern
            directory: Directory to search in
            
        Returns:
            List of matching files
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "pattern": pattern,
                    "directory": directory
                }
                response = await client.post(f"{self.base_url}/glm/file_search", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"file_search failed: {e}")
            return {"error": str(e)}

    async def shell_execute_safe(self, command: str, allow: bool = False) -> Dict[str, Any]:
        """
        Execute shell command with safety checks.
        
        Args:
            command: Command to execute
            allow: Must be True to authorize execution
            
        Returns:
            Command execution result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "command": command,
                    "allow": allow
                }
                response = await client.post(f"{self.base_url}/glm/shell_execute_safe", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"shell_execute_safe failed: {e}")
            return {"error": str(e)}

    async def browser_search(self, query: str) -> Dict[str, Any]:
        """
        Perform web search with GLM-4.6 summary.
        
        Args:
            query: Search query
            
        Returns:
            Search results with summary
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"query": query}
                response = await client.post(f"{self.base_url}/glm/browser_search", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"browser_search failed: {e}")
            return {"error": str(e)}

