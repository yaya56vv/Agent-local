"""
Kimi LLM Connector
Official Moonshot AI (Kimi) API integration
"""

import requests
from backend.config.settings import settings


class KimiLLM:
    """Kimi K2 (Moonshot) connector"""

    URL = "https://api.moonshot.cn/v1/chat/completions"
    MODEL = "moonshot-v1-8k"

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to Kimi and return the response
        
        Args:
            prompt: The user prompt/question
            
        Returns:
            The model's response text
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.KIMI_API_KEY}"
        }

        body = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            r = requests.post(self.URL, json=body, headers=headers, timeout=30)

            if r.status_code != 200:
                return f"[ERREUR KIMI] {r.status_code}: {r.text}"

            response_data = r.json()
            return response_data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"[ERREUR KIMI] Erreur de connexion: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"[ERREUR KIMI] Format de réponse invalide: {str(e)}"