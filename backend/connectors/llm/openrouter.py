"""
OpenRouter LLM Connector
OpenRouter API integration for multiple model access
"""

import requests
from backend.config.settings import settings


class OpenRouterLLM:
    """OpenRouter connector for various models"""

    URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "mistralai/mistral-large"  # Default model

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to OpenRouter and return the response
        
        Args:
            prompt: The user prompt/question
            
        Returns:
            The model's response text
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
        }

        body = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            r = requests.post(self.URL, json=body, headers=headers, timeout=30)

            if r.status_code != 200:
                return f"[ERREUR OPENROUTER] {r.status_code}: {r.text}"

            response_data = r.json()
            return response_data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"[ERREUR OPENROUTER] Erreur de connexion: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"[ERREUR OPENROUTER] Format de réponse invalide: {str(e)}"