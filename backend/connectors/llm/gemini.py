"""
Gemini LLM Connector
Official Google Gemini API integration
Support multimodal (texte + images) et modèles dynamiques
"""

import requests
import base64
from typing import Optional, List, Dict, Any, Union
from backend.config.settings import settings


class GeminiLLM:
    """
    Gemini connector with dynamic model selection and multimodal support.
    
    Supports:
    - Text-only requests
    - Multimodal requests (text + images)
    - Dynamic model selection
    - Multiple Gemini model variants
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize Gemini connector.
        
        Args:
            model: Model name to use (default: gemini-2.0-flash-exp)
        """
        self.model = model or "gemini-2.0-flash-exp"
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"

    def ask(
        self,
        prompt: str,
        model: Optional[str] = None,
        image_data: Optional[Union[bytes, List[bytes]]] = None,
        mime_type: str = "image/png"
    ) -> str:
        """
        Send a prompt to Gemini and return the response.
        Supports both text-only and multimodal (text + images) requests.
        
        Args:
            prompt: The user prompt/question
            model: Optional model override (uses instance model if not provided)
            image_data: Optional image bytes or list of image bytes for multimodal
            mime_type: MIME type of the image(s) (default: image/png)
            
        Returns:
            The model's response text
        """
        # Use provided model or instance model
        model_name = model or self.model
        url = f"{self.base_url}/{model_name}:generateContent"
        
        headers = {"Content-Type": "application/json"}
        params = {"key": settings.GEMINI_API_KEY}

        # Build request body based on whether we have images
        if image_data:
            body = self._build_multimodal_body(prompt, image_data, mime_type)
        else:
            body = self._build_text_body(prompt)

        print("GEMINI_API_KEY is None:", settings.GEMINI_API_KEY is None)
        print("GEMINI_API_KEY length:", len(settings.GEMINI_API_KEY or ""))

        try:
            r = requests.post(url, json=body, headers=headers, params=params, timeout=60)

            if r.status_code != 200:
                error_detail = r.text
                return f"[ERREUR GEMINI] {r.status_code}: {error_detail}"

            response_data = r.json()
            text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            return text
            
        except requests.exceptions.RequestException as e:
            return f"[ERREUR GEMINI] Erreur de connexion: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"[ERREUR GEMINI] Format de reponse invalide: {str(e)}"

    def _build_text_body(self, prompt: str) -> Dict[str, Any]:
        """
        Build request body for text-only requests.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Request body dict
        """
        return {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

    def _build_multimodal_body(
        self,
        prompt: str,
        image_data: Union[bytes, List[bytes]],
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Build request body for multimodal requests (text + images).
        
        Args:
            prompt: Text prompt
            image_data: Image bytes or list of image bytes
            mime_type: MIME type of images
            
        Returns:
            Request body dict with inline_data format
        """
        # Normalize image_data to list
        if isinstance(image_data, bytes):
            images = [image_data]
        else:
            images = image_data

        # Build parts list: text first, then images
        parts = [{"text": prompt}]
        
        for img_bytes in images:
            # Encode image to base64
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": img_b64
                }
            })

        return {
            "contents": [
                {"parts": parts}
            ]
        }

    def ask_with_image(
        self,
        prompt: str,
        image_bytes: bytes,
        model: Optional[str] = None,
        mime_type: str = "image/png"
    ) -> str:
        """
        Convenience method for single image analysis.
        
        Args:
            prompt: Text prompt/question about the image
            image_bytes: Image data as bytes
            model: Optional model override
            mime_type: MIME type of the image
            
        Returns:
            The model's response text
        """
        return self.ask(
            prompt=prompt,
            model=model,
            image_data=image_bytes,
            mime_type=mime_type
        )

    def ask_with_images(
        self,
        prompt: str,
        images: List[bytes],
        model: Optional[str] = None,
        mime_type: str = "image/png"
    ) -> str:
        """
        Convenience method for multiple images analysis.
        
        Args:
            prompt: Text prompt/question about the images
            images: List of image data as bytes
            model: Optional model override
            mime_type: MIME type of the images
            
        Returns:
            The model's response text
        """
        return self.ask(
            prompt=prompt,
            model=model,
            image_data=images,
            mime_type=mime_type
        )

    def set_model(self, model: str) -> None:
        """
        Change the default model for this instance.
        
        Args:
            model: New model name
        """
        self.model = model

    def get_model(self) -> str:
        """
        Get the current default model.
        
        Returns:
            Current model name
        """
        return self.model
