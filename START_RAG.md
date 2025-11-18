# 🚀 SYSTÈME RAG - READY TO USE

## ✅ Implémentation complète terminée !

Le système RAG (Retrieval-Augmented Generation) est maintenant entièrement fonctionnel avec :
- ✅ Stockage vectoriel SQLite + Gemini embeddings
- ✅ LLM local (Ollama / LM Studio)
- ✅ API REST FastAPI complète
- ✅ Interface web moderne
- ✅ Scripts utilitaires
- ✅ Documentation complète

---

## 🎯 DÉMARRAGE IMMÉDIAT (3 étapes)

### Étape 1 : Installer Ollama (2 minutes)

**Windows :**
1. Télécharger : https://ollama.ai/download
2. Installer et lancer
3. Ouvrir PowerShell :
```powershell
ollama pull llama3.2
```

**Vérifier :**
```powershell
ollama list
```

### Étape 2 : Configurer l'API Gemini (1 minute)

1. Obtenir clé gratuite : https://ai.google.dev/
2. Créer fichier `.env` à la racine du projet :
```env
GEMINI_API_KEY=votre_clé_ici
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434
LOCAL_LLM_MODEL=llama3.2
```

### Étape 3 : Tester (30 secondes)

```powershell
python test_rag.py
```

✅ Si tout est OK, vous verrez :
- LLM local disponible ✅
- Document ajouté ✅
- Recherche fonctionnelle ✅
- Réponse générée ✅

---

## 🌐 UTILISATION

### Interface Web (le plus simple)

1. **Lancer le serveur :**
```powershell
.\run_agent.ps1
```

2. **Ouvrir dans le navigateur :**
```
http://localhost:8000/ui/rag.html
```

3. **Utiliser :**
   - Entrer un nom de dataset
   - Coller du texte
   - Cliquer "Ajouter au RAG"
   - Poser une question
   - Voir la réponse + sources

### Scripts (pour automatiser)

**Ajouter un fichier :**
```powershell
python add_to_rag.py --file README.md --dataset docs
```

**Ajouter un répertoire complet :**
```powershell
python add_to_rag.py --dir ./backend --dataset code
```

**Exemples avancés :**
```powershell
python examples_rag.py
```

### Python (pour intégrer)

```python
import asyncio
from backend.rag.rag_helper import answer_question_with_rag

async def main():
    answer = await answer_question_with_rag(
        dataset="docs",
        question="Comment ça marche ?"
    )
    print(answer)

asyncio.run(main())
```

---

## 📚 DOCUMENTATION

| Fichier | Description |
|---------|-------------|
| **QUICKSTART_RAG.md** | Guide de démarrage rapide (5 min) |
| **RAG_README.md** | Documentation complète (tout) |
| **RAG_IMPLEMENTATION.md** | Détails de l'implémentation |
| Ce fichier | Instructions immédiates |

---

## 🔧 ENDPOINTS API

Base URL : `http://localhost:8000`

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/rag/documents/add` | POST | Ajouter un document |
| `/rag/query` | POST | Rechercher + générer réponse |
| `/rag/datasets` | GET | Lister les datasets |
| `/rag/datasets/{name}` | GET | Info d'un dataset |
| `/rag/datasets/{name}` | DELETE | Supprimer un dataset |
| `/rag/llm/status` | GET | Status du LLM local |
| `/ui/rag.html` | GET | Interface web |
| `/docs` | GET | Documentation API |

---

## 🎓 EXEMPLES RAPIDES

### Créer une base de docs projet
```powershell
# Indexer le code
python add_to_rag.py --dir ./backend --dataset backend_code --ext .py

# Indexer la doc
python add_to_rag.py --dir . --dataset project_docs --ext .md .txt

# Poser une question via l'interface web
```

### API cURL
```bash
# Ajouter document
curl -X POST http://localhost:8000/rag/documents/add \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "test",
    "filename": "doc.txt",
    "content": "Python est un langage..."
  }'

# Poser question
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "test",
    "question": "Qu est-ce que Python ?",
    "use_llm": true
  }'
```

---

## 🐛 DÉPANNAGE RAPIDE

### ❌ "LLM local non disponible"
```powershell
# Vérifier Ollama
ollama list
ollama serve  # Si pas lancé

# Tester
curl http://localhost:11434/api/tags
```

### ❌ "Erreur embedding Gemini"
- Vérifier `GEMINI_API_KEY` dans `.env`
- Tester la clé : https://ai.google.dev/

### ❌ "Module not found"
```powershell
pip install -r requirements.txt
```

### ❌ "CORS error"
- Vérifier que le backend tourne sur port 8000
- Utiliser : http://localhost:8000/ui/rag.html (pas file://)

---

## 📊 ARCHITECTURE SIMPLIFIÉE

```
┌──────────────────┐
│  Interface Web   │  ← Vous utilisez ça
│   rag.html       │
└────────┬─────────┘
         │
┌────────▼─────────┐
│   API Routes     │  ← FastAPI REST API
│  rag_routes.py   │
└────┬─────────┬───┘
     │         │
┌────▼────┐  ┌▼──────────┐
│ RAG     │  │ Local LLM │
│ Store   │  │ Connector │
│ (SQLite)│  │ (Ollama)  │
└─────────┘  └───────────┘
```

---

## ✅ CHECKLIST DE VÉRIFICATION

Avant de commencer, vérifiez :

- [ ] Python 3.11+ installé
- [ ] Ollama installé et lancé (`ollama list`)
- [ ] Modèle téléchargé (`llama3.2` ou autre)
- [ ] Clé Gemini API obtenue
- [ ] Fichier `.env` créé avec `GEMINI_API_KEY`
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Test réussi (`python test_rag.py`)

Si tout est ✅, vous êtes prêt !

---

## 🎯 PROCHAINES ÉTAPES

### Maintenant
1. ✅ Lancer le test : `python test_rag.py`
2. ✅ Démarrer le serveur : `.\run_agent.ps1`
3. ✅ Ouvrir l'interface : http://localhost:8000/ui/rag.html

### Ensuite
4. Ajouter vos premiers documents
5. Tester différentes questions
6. Créer plusieurs datasets thématiques

### Plus tard
7. Intégrer dans l'orchestrator
8. Créer des agents spécialisés
9. Optimiser pour vos cas d'usage

---

## 💡 CONSEILS

### Modèles LLM recommandés

**Pour démarrer (rapide) :**
```powershell
ollama pull llama3.2  # 2GB, très rapide
```

**Pour la qualité :**
```powershell
ollama pull qwen2.5:14b  # 8GB, meilleure qualité
ollama pull mistral:7b   # 4GB, bon compromis
```

### Changer de modèle
Dans `.env` :
```env
LOCAL_LLM_MODEL=qwen2.5:14b
```
Puis redémarrer le serveur.

### Performances
- Plus de chunks (`top_k`) = plus de contexte mais plus lent
- Temperature élevée = réponses créatives
- Temperature basse = réponses précises

---

## 📞 SUPPORT

### Si ça ne marche pas :

1. **Vérifier les logs :**
   - Console du serveur
   - Console du navigateur (F12)

2. **Tester les composants :**
   ```powershell
   # Test Ollama
   curl http://localhost:11434/api/tags
   
   # Test backend
   curl http://localhost:8000/health
   
   # Test RAG
   python test_rag.py
   ```

3. **Documentation :**
   - `QUICKSTART_RAG.md` pour démarrage
   - `RAG_README.md` pour tout le reste
   - `/docs` endpoint pour API reference

---

## 🎉 PRÊT !

Vous avez maintenant un système RAG complet et fonctionnel.

**Pour commencer immédiatement :**

```powershell
# 1. Test rapide
python test_rag.py

# 2. Lancer le serveur
.\run_agent.ps1

# 3. Ouvrir le navigateur
start http://localhost:8000/ui/rag.html
```

**Bon développement ! 🚀**
