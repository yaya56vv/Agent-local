# Memory MCP API

## Outils exposés
- `store_memory(session_id, role, content, metadata)`: Stocker un message ou une information dans la mémoire à court/long terme.
- `retrieve_history(session_id, limit)`: Récupérer l'historique récent d'une session.
- `search_memory(query, session_id, limit)`: Recherche sémantique ou par mots-clés dans la mémoire.
- `clear_session(session_id)`: Effacer la mémoire d'une session.
- `get_stats()`: Obtenir des statistiques sur l'utilisation de la mémoire.

## Schéma d’appel
### Requête
```json
{
  "tool": "store_memory",
  "params": {
    "session_id": "session_123",
    "role": "user",
    "content": "Je m'appelle Alice.",
    "metadata": {"timestamp": "2023-10-27T10:00:00Z"}
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "memory_id": "mem_456",
    "stored_at": "2023-10-27T10:00:01Z"
  }
}
```

## Dépendances requises
- `sqlite3` (ou autre DB locale)
- `json`
- `datetime`

## Interaction avec l’orchestrateur
- Appelé à chaque tour de conversation pour sauvegarder le contexte et récupérer l'historique.
- **Vigilance**: Gestion de la confidentialité des données et nettoyage périodique des sessions inactives.
