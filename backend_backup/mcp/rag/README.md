# RAG MCP API

## Outils exposés
- `add_document(content, metadata, dataset)`: Ingérer un document, le découper et générer ses embeddings.
- `query_rag(question, dataset, top_k)`: Rechercher les fragments les plus pertinents pour une question.
- `list_documents(dataset)`: Lister les documents indexés.
- `delete_document(doc_id)`: Supprimer un document et ses vecteurs associés.
- `list_datasets()`: Lister les collections disponibles.

## Schéma d’appel
### Requête
```json
{
  "tool": "query_rag",
  "params": {
    "question": "Comment configurer le serveur ?",
    "dataset": "default",
    "top_k": 3
  }
}
```

### Réponse
```json
{
  "status": "success",
  "data": {
    "results": [
      {"content": "...", "score": 0.89, "source": "doc1.md"},
      {"content": "...", "score": 0.75, "source": "doc2.txt"}
    ]
  }
}
```

## Dépendances requises
- `sentence-transformers` (pour embeddings locaux)
- `sqlite3` (stockage vecteurs/métadonnées)
- `numpy`
- `hashlib`

## Interaction avec l’orchestrateur
- L'orchestrateur utilise ce service pour enrichir le contexte avant d'appeler le LLM (Retrieval Augmented Generation).
- **Vigilance**: Performance de l'inférence des embeddings (peut être lente sur CPU).
