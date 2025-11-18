# 🤖 Module RAG - Agent Local

## Vue d'ensemble

Module RAG (Retrieval-Augmented Generation) complet avec support pour LLM local (Ollama / LM Studio).

### Fonctionnalités

✅ **Stockage vectoriel** - Embeddings via Gemini API + SQLite
✅ **Recherche sémantique** - Similarité cosinus sur les embeddings
✅ **LLM local** - Support Ollama et LM Studio
✅ **API REST complète** - Endpoints FastAPI
✅ **Interface web** - UI moderne et responsive
✅ **Multi-datasets** - Gestion de collections séparées

---

## 🚀 Installation

### 1. Dépendances Python

```bash
pip install -r requirements.txt
```

### 2. LLM Local (choisir un)

#### Option A : Ollama (recommandé)
```bash
# Installer Ollama
# Télécharger depuis: https://ollama.ai

# Télécharger un modèle
ollama pull llama3.2
# ou
ollama pull qwen2.5:14b
```

#### Option B : LM Studio
```bash
# Télécharger LM Studio
# https://lmstudio.ai

# Lancer un modèle dans LM Studio
# Default port: 1234
```

### 3. Variables d'environnement

Créer un fichier `.env` :

```env
# Gemini API pour embeddings
GEMINI_API_KEY=votre_clé_api

# LLM Local (Ollama)
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434
LOCAL_LLM_MODEL=llama3.2

# Ou LM Studio
# LOCAL_LLM_BASE_URL=http://127.0.0.1:1234
# LOCAL_LLM_MODEL=local-model
```

---

## 📖 Utilisation

### Démarrer le serveur

```bash
# Via script PowerShell
.\run_agent.ps1

# Ou directement
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Interface Web

Ouvrir dans le navigateur :
```
http://localhost:8000/ui/rag.html
```

### API REST

#### Ajouter un document
```bash
POST http://localhost:8000/rag/documents/add
Content-Type: application/json

{
  "dataset": "mon_projet",
  "filename": "doc.txt",
  "content": "Contenu du document...",
  "metadata": {"source": "manual"}
}
```

#### Poser une question
```bash
POST http://localhost:8000/rag/query
Content-Type: application/json

{
  "dataset": "mon_projet",
  "question": "Quelle est la fonction principale ?",
  "top_k": 5,
  "use_llm": true
}
```

#### Lister les datasets
```bash
GET http://localhost:8000/rag/datasets
```

#### Supprimer un dataset
```bash
DELETE http://localhost:8000/rag/datasets/mon_projet
```

#### Vérifier le statut LLM
```bash
GET http://localhost:8000/rag/llm/status
```

---

## 🔧 Intégration avec l'orchestrator

### Utilisation simple

```python
from backend.rag.rag_helper import answer_question_with_rag

# Répondre à une question
answer = await answer_question_with_rag(
    dataset="mon_projet",
    question="Comment fonctionne le système ?"
)
print(answer)
```

### Utilisation avancée

```python
from backend.rag.rag_helper import rag_helper

# Réponse complète avec sources
result = await rag_helper.answer_with_rag(
    dataset="mon_projet",
    question="Comment fonctionne le système ?",
    top_k=5,
    temperature=0.7
)

print(result["answer"])
print(f"Sources: {len(result['sources'])}")
for source in result["sources"]:
    print(f"- {source['filename']}: {source['similarity']:.2%}")
```

### Ajouter des documents

```python
from backend.rag.rag_helper import rag_helper

# Ajouter un document
doc_id = rag_helper.add_document_sync(
    dataset="mon_projet",
    filename="readme.md",
    content="# Mon Projet\n\nDescription...",
    metadata={"type": "documentation"}
)
```

---

## 📁 Structure des fichiers

```
backend/
├── rag/
│   ├── rag_store.py       # Stockage vectoriel SQLite + Gemini
│   ├── rag_helper.py      # Helper pour orchestrator
│   └── rag_engine.py      # (existant)
├── routes/
│   └── rag_routes.py      # API REST endpoints
├── connectors/
│   └── local_llm/
│       ├── local_llm_connector.py  # Connecteur Ollama/LM Studio
│       └── __init__.py
└── main.py                # Application FastAPI

frontend/
└── ui/
    ├── rag.html           # Interface web
    └── rag.js             # Logique frontend

rag/                       # Données RAG
├── rag.db                 # Base SQLite
└── documents/             # (optionnel)
```

---

## 🧪 Tests

### Test rapide

```python
import asyncio
from backend.rag.rag_helper import rag_helper

async def test_rag():
    # Ajouter un document
    doc_id = rag_helper.add_document_sync(
        dataset="test",
        filename="test.txt",
        content="Python est un langage de programmation interprété."
    )
    print(f"Document ajouté: {doc_id}")
    
    # Vérifier LLM
    llm_ok = await rag_helper.check_llm_available()
    print(f"LLM disponible: {llm_ok}")
    
    # Poser une question
    result = await rag_helper.answer_with_rag(
        dataset="test",
        question="Qu'est-ce que Python ?"
    )
    print(f"Réponse: {result['answer']}")

asyncio.run(test_rag())
```

---

## 🔍 Endpoints API complets

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/rag/documents/add` | Ajouter un document |
| POST | `/rag/documents/upload` | Upload fichier |
| POST | `/rag/query` | Recherche + génération LLM |
| GET | `/rag/datasets` | Liste des datasets |
| GET | `/rag/datasets/{dataset}` | Info d'un dataset |
| DELETE | `/rag/datasets/{dataset}` | Supprimer dataset |
| GET | `/rag/llm/status` | Statut du LLM |
| POST | `/rag/llm/configure` | Configurer LLM |
| GET | `/rag/health` | Health check |

---

## ⚙️ Configuration avancée

### Changer de modèle Ollama

```bash
# Lister les modèles disponibles
ollama list

# Télécharger un nouveau modèle
ollama pull qwen2.5:14b

# Mettre à jour .env
LOCAL_LLM_MODEL=qwen2.5:14b
```

### Utiliser LM Studio

1. Lancer LM Studio
2. Charger un modèle
3. Démarrer le serveur local
4. Configurer dans `.env` :

```env
LOCAL_LLM_BASE_URL=http://127.0.0.1:1234
LOCAL_LLM_MODEL=local-model
```

### Personnaliser les embeddings

Modifier dans `backend/rag/rag_store.py` :

```python
self.embedding_model = "models/text-embedding-004"  # Modèle Gemini
```

### Ajuster le chunking

```python
chunks = self._chunk_text(
    content, 
    chunk_size=1000,    # Taille des chunks
    overlap=200         # Overlap entre chunks
)
```

---

## 🐛 Dépannage

### LLM non disponible

```bash
# Vérifier Ollama
ollama list
curl http://localhost:11434/api/tags

# Vérifier LM Studio
curl http://localhost:1234/v1/models
```

### Erreur d'embeddings

- Vérifier `GEMINI_API_KEY` dans `.env`
- Tester la clé : https://ai.google.dev/

### Base de données corrompue

```bash
# Supprimer et recréer
rm rag/rag.db
# La base sera recréée au prochain lancement
```

### CORS errors

Vérifier que le backend autorise CORS :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Exemples d'utilisation

### Exemple 1 : Documentation de projet

```python
# Ajouter toute la doc
docs = [
    ("readme.md", readme_content),
    ("api.md", api_content),
    ("guide.md", guide_content)
]

for filename, content in docs:
    rag_helper.add_document_sync(
        dataset="project_docs",
        filename=filename,
        content=content
    )

# Interroger
answer = await answer_question_with_rag(
    dataset="project_docs",
    question="Comment utiliser l'API ?"
)
```

### Exemple 2 : Base de connaissances

```python
# Créer plusieurs datasets thématiques
datasets = {
    "python": ["python_basics.txt", "python_advanced.txt"],
    "javascript": ["js_guide.txt", "react_intro.txt"],
    "devops": ["docker.txt", "kubernetes.txt"]
}

# Poser une question ciblée
answer = await answer_question_with_rag(
    dataset="python",
    question="Comment créer un décorateur ?"
)
```

---

## 🎯 Prochaines étapes

1. **Lancer Ollama** et télécharger un modèle
2. **Configurer** les variables d'environnement
3. **Tester** l'interface web : http://localhost:8000/ui/rag.html
4. **Ajouter** vos premiers documents
5. **Intégrer** avec l'orchestrator

---

## 📝 Notes

- **Embeddings** : Utilise Gemini API (gratuit avec quotas)
- **Stockage** : SQLite (pas besoin de serveur externe)
- **LLM** : 100% local (pas de coûts API)
- **Performance** : Dépend du modèle LLM choisi
- **Sécurité** : Données stockées localement

---

## 🤝 Support

Pour toute question ou problème :
1. Vérifier les logs du backend
2. Tester les endpoints avec curl/Postman
3. Vérifier que Ollama/LM Studio est lancé
4. Consulter la documentation Ollama : https://ollama.ai/docs
