"""
Local LLM Connector - Interface for Ollama and LM Studio
Provides unified interface for local LLM inference
"""

import aiohttp
import asyncio
import json
from typing import Optional, List, Dict, Any
from enum import Enum


class LocalLLMProvider(Enum):
    """Supported local LLM providers"""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"


class LocalLLMConnector:
    """
    Connector for local LLM providers (Ollama, LM Studio).
    Provides a unified interface for text generation.
    """
    
    def __init__(
        self,
        provider: LocalLLMProvider = LocalLLMProvider.OLLAMA,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Initialize local LLM connector.
        
        Args:
            provider: LLM provider (OLLAMA or LM_STUDIO)
            base_url: Base URL for the provider API
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.provider = provider
        self.timeout = timeout
        
        # Set default URLs and models based on provider
        if provider == LocalLLMProvider.OLLAMA:
            self.base_url = base_url or "http://localhost:11434"
            self.model = model or "llama3.2"
            self.generate_endpoint = f"{self.base_url}/api/generate"
            self.chat_endpoint = f"{self.base_url}/api/chat"
        elif provider == LocalLLMProvider.LM_STUDIO:
            self.base_url = base_url or "http://localhost:1234"
            self.model = model or "local-model"
            self.generate_endpoint = f"{self.base_url}/v1/completions"
            self.chat_endpoint = f"{self.base_url}/v1/chat/completions"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> str:
        """
        Generate text completion from prompt.
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        if self.provider == LocalLLMProvider.OLLAMA:
            return await self._generate_ollama(
                prompt, system_prompt, temperature, max_tokens, stream
            )
        elif self.provider == LocalLLMProvider.LM_STUDIO:
            return await self._generate_lm_studio(
                prompt, system_prompt, temperature, max_tokens, stream
            )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> str:
        """
        Generate chat completion from message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        if self.provider == LocalLLMProvider.OLLAMA:
            return await self._chat_ollama(messages, temperature, max_tokens, stream)
        elif self.provider == LocalLLMProvider.LM_STUDIO:
            return await self._chat_lm_studio(messages, temperature, max_tokens, stream)
    
    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Generate text using Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.generate_endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error ({response.status}): {error_text}")
                    
                    if stream:
                        # Handle streaming response
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if "response" in data:
                                        full_response += data["response"]
                                except json.JSONDecodeError:
                                    continue
                        return full_response
                    else:
                        # Handle non-streaming response
                        data = await response.json()
                        return data.get("response", "")
        
        except asyncio.TimeoutError:
            raise Exception(f"Ollama request timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Ollama generation error: {str(e)}")
    
    async def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Chat using Ollama API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.chat_endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error ({response.status}): {error_text}")
                    
                    if stream:
                        # Handle streaming response
                        full_response = ""
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if "message" in data and "content" in data["message"]:
                                        full_response += data["message"]["content"]
                                except json.JSONDecodeError:
                                    continue
                        return full_response
                    else:
                        # Handle non-streaming response
                        data = await response.json()
                        return data.get("message", {}).get("content", "")
        
        except asyncio.TimeoutError:
            raise Exception(f"Ollama request timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Ollama chat error: {str(e)}")
    
    async def _generate_lm_studio(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Generate text using LM Studio API (OpenAI-compatible)"""
        # LM Studio uses OpenAI-compatible API
        # Convert to chat format for better results
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self._chat_lm_studio(messages, temperature, max_tokens, stream)
    
    async def _chat_lm_studio(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> str:
        """Chat using LM Studio API (OpenAI-compatible)"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.chat_endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"LM Studio API error ({response.status}): {error_text}")
                    
                    if stream:
                        # Handle streaming response (SSE format)
                        full_response = ""
                        async for line in response.content:
                            if line:
                                line_text = line.decode('utf-8').strip()
                                if line_text.startswith("data: "):
                                    data_text = line_text[6:]
                                    if data_text == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(data_text)
                                        if "choices" in data and len(data["choices"]) > 0:
                                            delta = data["choices"][0].get("delta", {})
                                            content = delta.get("content", "")
                                            full_response += content
                                    except json.JSONDecodeError:
                                        continue
                        return full_response
                    else:
                        # Handle non-streaming response
                        data = await response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            return data["choices"][0].get("message", {}).get("content", "")
                        return ""
        
        except asyncio.TimeoutError:
            raise Exception(f"LM Studio request timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"LM Studio chat error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if the local LLM service is available.
        
        Returns:
            True if service is reachable, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Try to connect to the base URL
                async with session.get(
                    self.base_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status in [200, 404]  # 404 is ok, means server is up
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """
        List available models.
        
        Returns:
            List of model names
        """
        if self.provider == LocalLLMProvider.OLLAMA:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/api/tags",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return [model["name"] for model in data.get("models", [])]
            except:
                pass
        elif self.provider == LocalLLMProvider.LM_STUDIO:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/v1/models",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return [model["id"] for model in data.get("data", [])]
            except:
                pass
        
        return []


# Convenience functions for quick usage
async def generate_with_ollama(
    prompt: str,
    model: str = "llama3.2",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Quick function to generate text with Ollama.
    
    Args:
        prompt: Input prompt
        model: Model name
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    connector = LocalLLMConnector(
        provider=LocalLLMProvider.OLLAMA,
        model=model
    )
    return await connector.generate(prompt, system_prompt, temperature, max_tokens)


async def generate_with_lm_studio(
    prompt: str,
    model: str = "local-model",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Quick function to generate text with LM Studio.
    
    Args:
        prompt: Input prompt
        model: Model name
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    connector = LocalLLMConnector(
        provider=LocalLLMProvider.LM_STUDIO,
        model=model
    )
    return await connector.generate(prompt, system_prompt, temperature, max_tokens)
