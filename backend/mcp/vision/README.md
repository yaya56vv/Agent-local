# Vision MCP API

## Outils exposés
- `analyze_image(image_source, prompt)`: Analyser une image (fichier local ou URL) avec un prompt spécifique.
- `describe_image(image_source)`: Obtenir une description générale d'une image.
- `extract_text(image_source)`: Extraire le texte visible (OCR via Vision LLM).

## Schéma d’appel
### Requête
```json
{
  "tool": "analyze_image",
  "params": {
    "image_source": "base64_encoded_string...",
    "prompt": "Que vois-tu sur cette image ?"
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "description": "L'image montre un chat assis sur un canapé...",
    "tags": ["chat", "canapé", "intérieur"]
  }
}
```

## Dépendances requises
- `base64`
- `requests` (pour télécharger images URL)
- Client API compatible Vision (ex: OpenRouter, OpenAI)

## Interaction avec l’orchestrateur
- L'orchestrateur délègue l'analyse visuelle à ce service.
- **Vigilance**: Gestion de la taille des payloads (images base64) et coûts API si utilisation de modèles externes.
