# Module RAG - Documentation

## Vue d'ensemble

Module RAG (Retrieval-Augmented Generation) complet avec stockage local, utilisant :
- **Gemini** pour les embeddings (vectorisation des documents)
- **LLM local** (Ollama ou LM Studio) pour la génération de réponses
- **SQLite** pour le stockage des documents et embeddings

## Architecture

```
backend/rag/
├── rag_store.py          # Gestion du stockage et recherche vectorielle
├── rag_engine.py         # Moteur de mémoire de session (existant)
└── README.md             # Cette documentation

backend/connectors/local_llm/
├── local_llm_connector.py  # Connecteur pour Ollama/LM Studio
└── __init__.py

backend/routes/
└── rag_routes.py         # API endpoints pour le RAG

rag/
├── rag.db                # Base de données SQLite (créée automatiquement)
└── documents/            # Dossier pour stocker les documents
```

## Configuration

### Variables d'environnement

Ajoutez ces variables dans votre fichier `.env` :

```env
# Gemini API (pour les embeddings)
GEMINI_API_KEY=votre_clé_api_gemini

# Configuration LLM local (optionnel)
LOCAL_LLM_PROVIDER=ollama          # ou "lm_studio"
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.2
```

### Installation d'Ollama (recommandé)

1. Téléchargez Ollama : https://ollama.ai/
2. Installez un modèle :
   ```bash
   ollama pull llama3.2
   ```
3. Le serveur démarre automatiquement sur `http://localhost:11434`

### Alternative : LM Studio

1. Téléchargez LM Studio : https://lmstudio.ai/
2. Chargez un modèle
3. Démarrez le serveur local (port 1234 par défaut)
4. Configurez : `LOCAL_LLM_PROVIDER=lm_studio`

## API Endpoints

### 1. Ajouter un document

**POST** `/rag/documents/add`

```json
{
  "dataset": "documentation",
  "filename": "guide.txt",
  "content": "Contenu du document...",
  "metadata": {
    "author": "John Doe",
    "date": "2024-01-15"
  }
}
```

**Réponse :**
```json
{
  "status": "success",
  "document_id": "abc123...",
  "dataset": "documentation",
  "filename": "guide.txt"
}
```

### 2. Upload un fichier

**POST** `/rag/documents/upload`

Form-data :
- `dataset`: nom du dataset
- `file`: fichier texte à uploader
- `metadata`: JSON optionnel

### 3. Interroger le RAG

**POST** `/rag/query`

```json
{
  "dataset": "documentation",
  "question": "Comment configurer le système ?",
  "top_k": 5,
  "use_llm": true,
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Réponse :**
```json
{
  "answer": "Pour configurer le système, vous devez...",
  "sources": [
    {
      "chunk_id": "doc1_0",
      "content": "Extrait pertinent du document...",
      "filename": "guide.txt",
      "metadata": {},
      "similarity": 0.89
    }
  ],
  "dataset": "documentation"
}
```

### 4. Lister les datasets

**GET** `/rag/datasets`

**Réponse :**
```json
["documentation", "faq", "technical"]
```

### 5. Informations sur un dataset

**GET** `/rag/datasets/{dataset}`

**Réponse :**
```json
{
  "dataset": "documentation",
  "document_count": 15,
  "chunk_count": 87,
  "documents": [
    {
      "filename": "guide.txt",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 6. Supprimer un dataset

**DELETE** `/rag/datasets/{dataset}`

### 7. Vérifier le statut du LLM

**GET** `/rag/llm/status`

**Réponse :**
```json
{
  "available": true,
  "provider": "ollama",
  "base_url": "http://localhost:11434",
  "current_model": "llama3.2",
  "available_models": ["llama3.2", "mistral", "codellama"]
}
```

### 8. Configurer le LLM

**POST** `/rag/llm/configure`

Form-data :
- `provider`: "ollama" ou "lm_studio"
- `base_url`: URL du serveur (optionnel)
- `model`: nom du modèle (optionnel)

### 9. Health check

**GET** `/rag/health`

## Utilisation en Python

### Exemple 1 : Ajouter des documents

```python
from backend.rag.rag_store import RAGStore

# Initialiser le store
rag = RAGStore()

# Ajouter un document
doc_id = rag.add_document(
    dataset="documentation",
    filename="guide.txt",
    content="Voici le contenu de mon guide...",
    metadata={"author": "John", "version": "1.0"}
)

print(f"Document ajouté : {doc_id}")
```

### Exemple 2 : Recherche vectorielle

```python
# Rechercher des documents pertinents
results = rag.query(
    dataset="documentation",
    question="Comment installer le système ?",
    top_k=5
)

for result in results:
    print(f"Score: {result['similarity']:.2f}")
    print(f"Fichier: {result['filename']}")
    print(f"Contenu: {result['content'][:200]}...")
    print("---")
```

### Exemple 3 : Utiliser le LLM local

```python
from backend.connectors.local_llm import LocalLLMConnector, LocalLLMProvider
import asyncio

async def generate_answer():
    # Initialiser le connecteur
    llm = LocalLLMConnector(
        provider=LocalLLMProvider.OLLAMA,
        model="llama3.2"
    )
    
    # Générer une réponse
    answer = await llm.generate(
        prompt="Explique-moi le RAG en une phrase",
        temperature=0.7
    )
    
    print(answer)

# Exécuter
asyncio.run(generate_answer())
```

### Exemple 4 : RAG complet (recherche + génération)

```python
import asyncio
from backend.rag.rag_store import RAGStore
from backend.connectors.local_llm import LocalLLMConnector, LocalLLMProvider

async def rag_query(question: str, dataset: str = "documentation"):
    # Initialiser
    rag = RAGStore()
    llm = LocalLLMConnector(provider=LocalLLMProvider.OLLAMA)
    
    # 1. Rechercher les documents pertinents
    sources = rag.query(dataset=dataset, question=question, top_k=3)
    
    if not sources:
        return "Aucun document pertinent trouvé."
    
    # 2. Construire le contexte
    context = "\n\n".join([
        f"Source {i+1}:\n{src['content']}"
        for i, src in enumerate(sources)
    ])
    
    # 3. Générer la réponse avec le LLM
    prompt = f"""Contexte:
{context}

Question: {question}

Réponds en te basant uniquement sur le contexte fourni."""
    
    answer = await llm.generate(
        prompt=prompt,
        system_prompt="Tu es un assistant qui répond aux questions en te basant sur le contexte fourni.",
        temperature=0.7
    )
    
    return answer

# Utilisation
answer = asyncio.run(rag_query("Comment configurer le système ?"))
print(answer)
```

## Fonctionnalités

### RAGStore

- ✅ Stockage SQLite local
- ✅ Embeddings via Gemini API
- ✅ Découpage automatique en chunks (500-800 tokens)
- ✅ Recherche par similarité cosinus
- ✅ Gestion de datasets multiples
- ✅ Métadonnées personnalisables

### LocalLLMConnector

- ✅ Support Ollama
- ✅ Support LM Studio
- ✅ API unifiée
- ✅ Mode streaming (optionnel)
- ✅ Configuration dynamique
- ✅ Détection automatique des modèles

### API Routes

- ✅ Upload de fichiers
- ✅ Gestion de datasets
- ✅ Requêtes RAG avec LLM
- ✅ Configuration du LLM
- ✅ Health checks

## Dépendances

Assurez-vous d'avoir installé :

```bash
pip install fastapi aiohttp numpy
```

## Troubleshooting

### Erreur : "GEMINI_API_KEY not set"
- Vérifiez que la clé API Gemini est dans votre `.env`
- Rechargez les variables d'environnement

### Erreur : "LLM not available"
- Vérifiez qu'Ollama ou LM Studio est démarré
- Testez avec : `curl http://localhost:11434` (Ollama)
- Vérifiez le port configuré

### Erreur : "No embedding returned"
- Vérifiez votre connexion internet
- Vérifiez la validité de votre clé API Gemini
- Vérifiez les quotas de l'API

### Performance lente
- Réduisez `top_k` pour moins de résultats
- Utilisez des chunks plus petits
- Optimisez la taille du contexte envoyé au LLM

## Prochaines améliorations

- [ ] Support de fichiers PDF, DOCX
- [ ] Cache des embeddings
- [ ] Réindexation incrémentale
- [ ] Support de modèles d'embeddings alternatifs
- [ ] Interface web pour la gestion des documents
- [ ] Statistiques et analytics

## Support

Pour toute question ou problème, consultez la documentation ou créez une issue.