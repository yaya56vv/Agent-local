# Search MCP API

## Outils exposés
- `web_search(query, max_results)`: Effectuer une recherche sur le web (DuckDuckGo, Google, etc.).
- `get_page_content(url)`: Extraire le contenu textuel principal d'une page web.
- `search_news(query)`: Rechercher des actualités spécifiques.

## Schéma d’appel
### Requête
```json
{
  "tool": "web_search",
  "params": {
    "query": "Météo Paris demain",
    "max_results": 5
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "results": [
      {"title": "Météo Paris...", "link": "https://...", "snippet": "..."},
      {"title": "Prévisions...", "link": "https://...", "snippet": "..."}
    ]
  }
}
```

## Dépendances requises
- `duckduckgo-search` (ou autre wrapper API)
- `requests`
- `beautifulsoup4` (pour le parsing HTML)
- `readability-lxml` (optionnel, pour nettoyer le contenu)

## Interaction avec l’orchestrateur
- Permet à l'agent d'accéder à des informations en temps réel.
- **Vigilance**: Respect des `robots.txt` et gestion des timeouts/erreurs réseau.
