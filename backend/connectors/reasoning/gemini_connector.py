import os
import asyncio
import json
from typing import Optional
import aiohttp


class GeminiReasoner:
    """
    Advanced Gemini 2.5 Pro connector for orchestration.
    Acts as the main reasoning brain of the agent.
    """

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.timeout = 60  # seconds
        self.max_retries = 3

    async def run(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Execute a reasoning query with Gemini 2.5 Pro.
        
        Args:
            prompt: The main query/instruction
            context: Optional context to provide additional information
            
        Returns:
            str: The model's response text
            
        Raises:
            Exception: If the API call fails after retries
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuery:\n{prompt}"

        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }

        params = {"key": self.api_key}

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        json=payload,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._extract_text(data)
                        else:
                            error_text = await response.text()
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise Exception(f"Gemini API error (status {response.status}): {error_text}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Gemini API timeout after {self.timeout}s")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Gemini API error: {str(e)}")

        raise Exception("Max retries exceeded for Gemini API")

    def _extract_text(self, response_data: dict) -> str:
        """
        Extract text from Gemini API response.
        
        Args:
            response_data: The JSON response from Gemini API
            
        Returns:
            str: Extracted text content
        """
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                return "[ERROR] No candidates in Gemini response"
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return "[ERROR] No parts in Gemini response"
            
            return parts[0].get("text", "[ERROR] No text in response")
        
        except (KeyError, IndexError, TypeError) as e:
            return f"[ERROR] Failed to parse Gemini response: {str(e)}"

    async def run_with_json(self, prompt: str, context: Optional[str] = None) -> dict:
        """
        Execute a query and attempt to parse the response as JSON.
        Useful for structured outputs.
        
        Args:
            prompt: The main query/instruction
            context: Optional context
            
        Returns:
            dict: Parsed JSON response or error dict
        """
        response_text = await self.run(prompt, context)
        
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            else:
                # Try to parse the entire response as JSON
                return json.loads(response_text)
        
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON",
                "raw_response": response_text
            }