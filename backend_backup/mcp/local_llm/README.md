# Local LLM MCP API

## Outils exposés
- `completion(prompt, params)`: Génération de texte simple.
- `chat_completion(messages, params)`: Génération en mode conversationnel.
- `get_embeddings(text)`: Génération d'embeddings (si le modèle le supporte).
- `load_model(model_path)`: Charger/Changer de modèle.

## Schéma d’appel
### Requête
```json
{
  "tool": "chat_completion",
  "params": {
    "messages": [{"role": "user", "content": "Bonjour"}],
    "temperature": 0.7,
    "max_tokens": 100
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "content": "Bonjour ! Comment puis-je vous aider ?",
    "usage": {"prompt_tokens": 10, "completion_tokens": 12}
  }
}
```

## Dépendances requises
- `llama-cpp-python` (ou autre backend d'inférence locale)
- `huggingface_hub` (pour télécharger les modèles)

## Interaction avec l’orchestrateur
- Permet d'utiliser un LLM local pour des tâches ne nécessitant pas d'appel API externe (confidentialité, coût, hors-ligne).
- **Vigilance**: Gestion des ressources (VRAM/RAM) et temps de latence. Streaming recommandé pour l'UX.
