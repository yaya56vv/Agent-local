"""
Gemini LLM Connector
Official Google Gemini API integration
"""

import requests
from backend.config.settings import settings


class GeminiLLM:
    """Gemini 2.5 Pro connector"""

    MODEL = "gemini-2.0-flash-exp"
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the response
        
        Args:
            prompt: The user prompt/question
            
        Returns:
            The model's response text
        """
        headers = {"Content-Type": "application/json"}
        params = {"key": settings.GEMINI_API_KEY}

        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        try:
            r = requests.post(self.URL, json=body, headers=headers, params=params, timeout=30)

            if r.status_code != 200:
                return f"[ERREUR GEMINI] {r.status_code}: {r.text}"

            response_data = r.json()
            text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            # Ensure ASCII-safe encoding for Windows console
            return text.encode('ascii', 'replace').decode('ascii')
            
        except requests.exceptions.RequestException as e:
            return f"[ERREUR GEMINI] Erreur de connexion: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"[ERREUR GEMINI] Format de reponse invalide: {str(e)}"