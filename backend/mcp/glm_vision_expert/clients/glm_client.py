"""
GLM Client - Interface to GLM-4.6 via OpenRouter
Handles all LLM interactions for the GLM Vision Expert MCP server
"""

import os
import aiohttp
import json
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.config.settings import settings


class GLMClient:
    """
    Client for interacting with GLM-4.6 model via OpenRouter API.
    Supports text and vision capabilities.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "zhipuai/glm-4-plus",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Initialize GLM client.
        
        Args:
            api_key: OpenRouter API key (defaults to settings.OPENROUTER_API_KEY)
            model: Model identifier (default: glm-4-plus)
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model
        self.base_url = base_url
        self.endpoint = f"{base_url}/chat/completions"
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY in .env")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from GLM model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            image_base64: Optional base64 encoded image for vision tasks
            
        Returns:
            Dict with response text and metadata
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Build user message
        if image_base64:
            # Vision request with image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            })
        else:
            # Text-only request
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agent-local.com",
            "X-Title": "Agent Local - GLM Vision Expert"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                
                result = await response.json()
                
                # Extract response
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return {
                        "text": content,
                        "model": self.model,
                        "usage": result.get("usage", {}),
                        "status": "success"
                    }
                else:
                    raise Exception("No response from GLM model")
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Chat with GLM model using message history.
        
        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response text and metadata
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agent-local.com",
            "X-Title": "Agent Local - GLM Vision Expert"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                
                result = await response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return {
                        "text": content,
                        "model": self.model,
                        "usage": result.get("usage", {}),
                        "status": "success"
                    }
                else:
                    raise Exception("No response from GLM model")
    
    async def analyze_image(
        self,
        image_base64: str,
        question: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Analyze an image with a specific question.
        
        Args:
            image_base64: Base64 encoded image
            question: Question about the image
            system_prompt: Optional system prompt
            
        Returns:
            Analysis text
        """
        result = await self.generate(
            prompt=question,
            system_prompt=system_prompt,
            image_base64=image_base64,
            temperature=0.3,
            max_tokens=2048
        )
        return result["text"]
    
    async def is_available(self) -> bool:
        """
        Check if the GLM service is available.
        
        Returns:
            True if service is reachable
        """
        try:
            # Simple test request
            result = await self.generate(
                prompt="Hello",
                max_tokens=10
            )
            return result["status"] == "success"
        except Exception:
            return False
