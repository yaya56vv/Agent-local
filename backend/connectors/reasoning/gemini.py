import requests
import json
from backend.config.settings import settings

class GeminiOrchestrator:

    def __init__(self):
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.key = settings.GEMINI_API_KEY

    def ask(self, prompt: str, context: str = "") -> str:
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"Contexte:\n{context}\n\nQuestion:\n{prompt}"}
                ]
            }]
        }

        params = {"key": self.key}

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            params=params,
            timeout=50
        )

        if response.status_code != 200:
            return f"[ERREUR GEMINI] {response.text}"

        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "[ERREUR GEMINI] Format inattendu dans la réponse."