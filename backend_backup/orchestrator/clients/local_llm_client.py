"""
MCP Local LLM Client - HTTP client for local LLM operations
"""
import httpx
from typing import Dict, Any, List, Optional


class LocalLlmClient:
    """Client for MCP Local LLM Service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize the Local LLM MCP client.
        
        Args:
            base_url: Base URL of the MCP Local LLM service
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 120.0  # Longer timeout for LLM operations
    
    async def health(self) -> Dict[str, Any]:
        """
        Check health status of the local LLM service.
        
        Returns:
            Health status information including provider
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/local_llm/health")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "error": f"Health check failed: {str(e)}"
            }
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text completion from a prompt.
        
        Args:
            prompt: The input prompt
            model: Model name (optional, uses default if not specified)
            system_prompt: System prompt to set context (optional)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                }
                
                if model:
                    payload["model"] = model
                if system_prompt:
                    payload["system_prompt"] = system_prompt
                
                response = await client.post(
                    f"{self.base_url}/local_llm/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Generate failed: {str(e)}",
                "response": None
            }
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion from messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model name (optional, uses default if not specified)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated chat response
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                }
                
                if model:
                    payload["model"] = model
                
                response = await client.post(
                    f"{self.base_url}/local_llm/chat",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Chat failed: {str(e)}",
                "response": None
            }
    
    async def list_models(self) -> Dict[str, Any]:
        """
        List available models.
        
        Returns:
            List of available model names
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/local_llm/list_models"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"List models failed: {str(e)}",
                "models": []
            }

