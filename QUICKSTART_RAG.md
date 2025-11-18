# 🚀 Guide de Démarrage Rapide - RAG

## Installation en 5 minutes

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Installer et lancer Ollama

**Windows:**
- Télécharger : https://ollama.ai/download
- Installer et lancer
- Télécharger un modèle :
```bash
ollama pull llama3.2
```

**Vérifier que ça marche :**
```bash
ollama list
curl http://localhost:11434/api/tags
```

### 3. Configurer l'API Gemini (pour embeddings)

- Obtenir une clé gratuite : https://ai.google.dev/
- Créer `.env` à la racine :
```env
GEMINI_API_KEY=votre_clé_ici
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434
LOCAL_LLM_MODEL=llama3.2
```

### 4. Tester le système

```bash
python test_rag.py
```

### 5. Lancer le serveur

```bash
# Via script
.\run_agent.ps1

# Ou directement
cd backend
uvicorn main:app --reload --port 8000
```

### 6. Ouvrir l'interface

Navigateur : http://localhost:8000/ui/rag.html

---

## Premier test en 3 étapes

### Étape 1 : Ajouter un document

Dans l'interface web :
1. Entrer un nom de dataset : `test`
2. Nom du fichier : `info.txt`
3. Coller du texte dans "Contenu"
4. Cliquer "Ajouter au RAG"

### Étape 2 : Poser une question

1. Le dataset `test` est sélectionné
2. Taper une question en rapport avec le document
3. Cliquer "Rechercher"

### Étape 3 : Voir la réponse

- La réponse du LLM s'affiche
- Les passages utilisés sont listés avec leur score de pertinence

---

## Utilisation via script

### Ajouter un fichier

```bash
python add_to_rag.py --file README.md --dataset docs
```

### Ajouter un répertoire complet

```bash
python add_to_rag.py --dir ./backend --dataset code
```

### Ajouter seulement certains types de fichiers

```bash
python add_to_rag.py --dir ./docs --dataset documentation --ext .md .txt
```

---

## Utilisation en Python

```python
import asyncio
from backend.rag.rag_helper import answer_question_with_rag, rag_helper

async def main():
    # Ajouter un document
    rag_helper.add_document_sync(
        dataset="project",
        filename="guide.txt",
        content="Python est un langage de programmation..."
    )
    
    # Poser une question
    answer = await answer_question_with_rag(
        dataset="project",
        question="Qu'est-ce que Python ?"
    )
    print(answer)

asyncio.run(main())
```

---

## Endpoints API essentiels

### Ajouter un document
```bash
curl -X POST http://localhost:8000/rag/documents/add \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "test",
    "filename": "doc.txt",
    "content": "Contenu..."
  }'
```

### Poser une question
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "test",
    "question": "Ma question ?",
    "use_llm": true
  }'
```

### Lister les datasets
```bash
curl http://localhost:8000/rag/datasets
```

---

## Dépannage express

### ❌ "LLM local non disponible"
```bash
# Vérifier Ollama
ollama list
ollama serve  # Si pas lancé
```

### ❌ "Erreur embedding"
- Vérifier `GEMINI_API_KEY` dans `.env`
- Tester : https://ai.google.dev/

### ❌ "CORS error" dans le navigateur
- Vérifier que le backend tourne sur port 8000
- Ouvrir l'interface via http://localhost:8000/ui/rag.html

### ❌ "Module not found"
```bash
pip install -r requirements.txt
```

---

## Modèles recommandés

### Pour démarrer (rapide)
```bash
ollama pull llama3.2        # 2GB - Très rapide
```

### Pour la qualité (plus lent)
```bash
ollama pull qwen2.5:14b     # 8GB - Meilleure qualité
ollama pull mistral:7b      # 4GB - Bon compromis
```

### Changer de modèle
Dans `.env` :
```env
LOCAL_LLM_MODEL=qwen2.5:14b
```

---

## 🎯 Next Steps

1. ✅ Test avec `test_rag.py`
2. ✅ Ajouter vos documents
3. ✅ Tester l'interface web
4. 📖 Lire `RAG_README.md` pour plus de détails
5. 🔧 Intégrer dans votre code

---

## Exemples pratiques

### Créer une base de connaissances de code
```bash
python add_to_rag.py --dir ./backend --dataset backend_code --ext .py
python add_to_rag.py --dir ./frontend --dataset frontend_code --ext .js .html .css
```

### Indexer de la documentation
```bash
python add_to_rag.py --dir ./docs --dataset documentation --ext .md .txt
```

### Poser des questions via API
```python
import requests

response = requests.post(
    "http://localhost:8000/rag/query",
    json={
        "dataset": "backend_code",
        "question": "Comment fonctionne le système de routing ?",
        "top_k": 5,
        "use_llm": True
    }
)

print(response.json()["answer"])
```

---

## Support

- 📖 Documentation complète : `RAG_README.md`
- 🧪 Tests : `python test_rag.py`
- 🌐 Interface : http://localhost:8000/ui/rag.html
- 📊 API Docs : http://localhost:8000/docs

**Prêt à démarrer !** 🚀
