import requests
from typing import List, Dict, Any
from backend.config.settings import settings


class OpenRouterLLM:

    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str):
        if not model:
            raise ValueError("Model must be specified")
        self.model = model

    def ask(self, messages: List[Dict[str, str]]) -> str:

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Local-Agent"
        }

        payload = {
            "model": self.model,
            "messages": messages
        }

        try:
            r = requests.post(self.URL, json=payload, headers=headers, timeout=60)

            if r.status_code != 200:
                return f"[ERREUR OPENROUTER] {r.status_code}: {r.text}"

            return r.json()["choices"][0]["message"]["content"]

        except Exception as e:
            return f"[ERREUR OPENROUTER] {str(e)}"

    def ask_simple(self, prompt: str) -> str:
        return self.ask([{"role": "user", "content": prompt}])

