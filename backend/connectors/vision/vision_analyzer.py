import os
import base64
import asyncio
from typing import Optional, Dict, Any
import aiohttp


class VisionAnalyzer:
    """
    Vision multimodal analyzer using Gemini 2.0 Flash.
    Capable of analyzing images, extracting text, and providing detailed descriptions.
    """

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.timeout = 60  # seconds
        self.max_retries = 3

    async def analyze_image(self, image_bytes: bytes, prompt: str = "") -> dict:
        """
        Analyze an image using Gemini multimodal.
        
        Args:
            image_bytes: Raw image bytes (PNG, JPG, etc.)
            prompt: Optional prompt to guide the analysis
            
        Returns:
            dict: Structured JSON with:
                - description: General description of the image
                - detected_text: Any text found in the image
                - objects: List of detected objects
                - reasoning: Analysis and interpretation
                - suggested_actions: Recommended next steps
                - raw_response: Full model response
        """
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(prompt)
        
        # Prepare API payload
        payload = {
            "contents": [{
                "parts": [
                    {"text": analysis_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",  # Gemini accepts jpeg/png
                            "data": image_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }

        params = {"key": self.api_key}

        # Execute with retries
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
                            raw_text = self._extract_text(data)
                            return self._parse_vision_response(raw_text)
                        else:
                            error_text = await response.text()
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            raise Exception(f"Gemini Vision API error (status {response.status}): {error_text}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Gemini Vision API timeout after {self.timeout}s")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Gemini Vision API error: {str(e)}")

        raise Exception("Max retries exceeded for Gemini Vision API")

    def _build_analysis_prompt(self, user_prompt: str = "") -> str:
        """
        Build a comprehensive analysis prompt for vision tasks.
        
        Args:
            user_prompt: Optional user-provided prompt
            
        Returns:
            str: Formatted prompt for Gemini
        """
        base_prompt = """Analyze this image in detail and provide a structured response in JSON format.

Your analysis should include:
1. **description**: A clear, detailed description of what you see in the image
2. **detected_text**: Any text visible in the image (OCR)
3. **objects**: List of main objects, UI elements, or components visible
4. **reasoning**: Your interpretation and analysis of the image content
5. **suggested_actions**: Recommended actions based on what you see

"""
        
        if user_prompt:
            base_prompt += f"\nUser's specific question: {user_prompt}\n"
        
        base_prompt += """
Respond in this EXACT JSON format:
```json
{
  "description": "Detailed description of the image",
  "detected_text": "Any text found in the image",
  "objects": ["object1", "object2", "object3"],
  "reasoning": "Your analysis and interpretation",
  "suggested_actions": ["action1", "action2"]
}
```

Be precise, technical, and actionable in your analysis."""
        
        return base_prompt

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

    def _parse_vision_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse the vision analysis response into structured format.
        
        Args:
            raw_response: Raw text response from Gemini
            
        Returns:
            dict: Structured vision analysis result
        """
        import json
        import re
        
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                # Try to find any JSON object
                json_match = re.search(r'\{.*"description".*\}', raw_response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                else:
                    # Fallback: create structured response from raw text
                    return {
                        "description": raw_response[:500],
                        "detected_text": "",
                        "objects": [],
                        "reasoning": raw_response,
                        "suggested_actions": [],
                        "raw_response": raw_response,
                        "parse_warning": "Could not parse structured JSON, returning raw response"
                    }
            
            # Ensure all required fields exist
            result = {
                "description": parsed.get("description", ""),
                "detected_text": parsed.get("detected_text", ""),
                "objects": parsed.get("objects", []),
                "reasoning": parsed.get("reasoning", ""),
                "suggested_actions": parsed.get("suggested_actions", []),
                "raw_response": raw_response
            }
            
            return result
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback response
            return {
                "description": raw_response[:500] if len(raw_response) > 500 else raw_response,
                "detected_text": "",
                "objects": [],
                "reasoning": raw_response,
                "suggested_actions": [],
                "raw_response": raw_response,
                "error": f"Parse error: {str(e)}"
            }

    async def analyze_screenshot(self, image_bytes: bytes, context: str = "") -> dict:
        """
        Specialized method for analyzing screenshots.
        
        Args:
            image_bytes: Screenshot image bytes
            context: Optional context about what to look for
            
        Returns:
            dict: Analysis result focused on UI/UX elements
        """
        prompt = f"""This is a screenshot. Analyze it focusing on:
- UI elements and layout
- Any errors or issues visible
- Text content and readability
- User experience aspects

{context if context else ''}"""
        
        return await self.analyze_image(image_bytes, prompt)

    async def extract_text(self, image_bytes: bytes) -> dict:
        """
        Extract text from an image (OCR).
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            dict: Extracted text and confidence
        """
        prompt = "Extract ALL text visible in this image. Be precise and maintain formatting."
        result = await self.analyze_image(image_bytes, prompt)
        
        return {
            "text": result.get("detected_text", ""),
            "full_analysis": result
        }