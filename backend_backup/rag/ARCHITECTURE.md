# Architecture RAG & Mémoire

## 🎯 Distinction claire entre RAG et Mémoire

### 📚 RAG (Retrieval-Augmented Generation) - Stockage Long Terme
**Fichiers:** `rag_store.py`, `rag_helper.py`

**Objectif:** Stocker et rechercher des documents avec embeddings vectoriels

**Utilisation:**
- Ajouter des documents de référence (documentation, articles, etc.)
- Recherche sémantique dans une base de connaissances
- Génération de réponses basées sur des documents pertinents

**Exemple:**
```python
from backend.rag.rag_helper import rag_helper

# Ajouter un document
result = rag_helper.add_document(
    content="Le chat est un animal domestique...",
    metadata={"source": "wikipedia"}
)

# Rechercher et répondre
response = await rag_helper.query(
    question="Qu'est-ce qu'un chat ?"
)
```

### 💬 Mémoire de Session - Historique Court Terme
**Fichiers:** `rag_engine.py`, `connectors/memory/memory_manager.py`

**Objectif:** Gérer l'historique des conversations

**Utilisation:**
- Stocker les messages d'une conversation
- Maintenir le contexte d'une session
- Récupérer l'historique récent

**Exemple:**
```python
from backend.rag.rag_engine import add_message_to_session, get_session_history

# Ajouter un message
add_message_to_session(
    session_id="user123",
    role="user",
    content="Bonjour !"
)

# Récupérer l'historique
history = get_session_history("user123", limit=10)
```

## 📊 Structure des données

### RAG Store (SQLite)
```
documents/
├── id (TEXT PRIMARY KEY)
├── dataset (TEXT)
├── filename (TEXT)
├── content (TEXT)
├── metadata (TEXT JSON)
└── created_at (TEXT)

chunks/
├── id (TEXT PRIMARY KEY)
├── document_id (TEXT FK)
├── chunk (TEXT)
├── embedding (TEXT JSON - liste de floats)
├── order_index (INTEGER)
└── created_at (TEXT)
```

### Session Memory (JSONL)
```
memory/sessions/{session_id}.jsonl
{
  "ts": "2025-01-18T14:00:00Z",
  "session_id": "user123",
  "role": "user",
  "content": "Message content",
  "meta": {}
}
```

## 🔄 Flux de travail

### Ajout de document RAG
1. Utilisateur envoie un document via `/rag/documents/add`
2. `rag_helper.add_document()` traite le contenu
3. `rag_store.add_document()` découpe en chunks
4. Génération d'embeddings via Gemini API
5. Stockage dans SQLite avec embeddings

### Requête RAG
1. Utilisateur pose une question via `/rag/query`
2. `rag_helper.query()` génère l'embedding de la question
3. `rag_store.query()` calcule la similarité cosinus
4. Retour des chunks les plus pertinents (triés par score)
5. Génération d'une réponse (optionnel avec LLM)

### Gestion de session
1. Message utilisateur arrive
2. `add_message_to_session()` enregistre dans JSONL
3. `get_session_history()` récupère le contexte
4. Utilisation du contexte pour la réponse

## ⚠️ Points importants

1. **NE PAS mélanger RAG et Session Memory**
   - RAG = Documents de référence
   - Memory = Historique de conversation

2. **Embeddings**
   - Format: Liste de floats `[0.123, 0.456, ...]`
   - Stockage: JSON string dans SQLite
   - Désérialisation: `json.loads(embedding_json)`

3. **Colonnes normalisées**
   - `chunks.chunk` (pas `content`)
   - `chunks.order_index` (pas `chunk_index`)

4. **Routes standardisées**
   - `POST /rag/documents/add`
   - `POST /rag/query`
   - `GET /rag/documents`
   - `DELETE /rag/documents/{doc_id}`