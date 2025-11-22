# GLM Vision Expert MCP Server

MCP Server pour le modèle GLM-4.6 via OpenRouter, offrant des capacités avancées de raisonnement, vision et traitement de données.

## 🚀 Démarrage Rapide

```bash
# Démarrer le serveur
python backend/mcp/glm_vision_expert/server.py
```

Le serveur démarre sur le port **9001** par défaut.

## 🔧 Configuration

### Variables d'environnement (.env)

```env
OPENROUTER_API_KEY=your_api_key_here
```

### Modèle par défaut

- **Modèle**: `zhipuai/glm-4-plus` (GLM-4.6)
- **Provider**: OpenRouter
- **Capacités**: Texte + Vision

## 📋 Outils Disponibles

### 1. solve_problem
Résout un problème en utilisant les capacités de raisonnement de GLM-4.6.

**Endpoint**: `POST /glm/solve_problem`

**Paramètres**:
- `description` (string, requis): Description du problème
- `context` (object, optionnel): Contexte additionnel

**Exemple**:
```json
{
  "description": "Comment optimiser une requête SQL lente?",
  "context": {
    "database": "PostgreSQL",
    "table_size": "10M rows"
  }
}
```

### 2. analyze_code
Analyse un fichier de code avec GLM-4.6.

**Endpoint**: `POST /glm/analyze_code`

**Paramètres**:
- `filepath` (string, requis): Chemin vers le fichier
- `task` (string, requis): Description de l'analyse

**Exemple**:
```json
{
  "filepath": "backend/main.py",
  "task": "Identifier les problèmes de performance"
}
```

### 3. analyze_visual_screenshot
Analyse une capture d'écran avec les capacités vision de GLM-4.6.

**Endpoint**: `POST /glm/analyze_visual_screenshot`

**Paramètres**:
- `image_base64` (string, requis): Image encodée en base64
- `question` (string, requis): Question sur l'image

**Exemple**:
```json
{
  "image_base64": "iVBORw0KGgoAAAANS...",
  "question": "Quels sont les éléments UI visibles?"
}
```

### 4. rag_query
Interroge le RAG store et synthétise une réponse avec GLM-4.6.

**Endpoint**: `POST /glm/rag_query`

**Paramètres**:
- `query` (string, requis): Question
- `dataset` (string, requis): Dataset à interroger

**Datasets valides**:
- `agent_core`: Règles permanentes
- `context_flow`: Résumés pré/post
- `agent_memory`: Feedbacks, leçons
- `projects`: Code & docs analytiques
- `scratchpad`: Temporaire

**Exemple**:
```json
{
  "query": "Quelles sont les règles de gestion mémoire?",
  "dataset": "agent_core"
}
```

### 5. rag_write
Écrit du contenu dans le RAG store avec validation.

**Endpoint**: `POST /glm/rag_write`

**Paramètres**:
- `content` (string, requis): Contenu à stocker
- `dataset` (string, requis): Dataset cible
- `filename` (string, optionnel): Nom du fichier
- `metadata` (object, optionnel): Métadonnées

**Exemple**:
```json
{
  "content": "Nouvelle règle: toujours valider les entrées utilisateur",
  "dataset": "agent_core",
  "filename": "security_rule_001.txt",
  "metadata": {
    "type": "core_rule",
    "priority": "high"
  }
}
```

### 6. file_read
Lit le contenu d'un fichier.

**Endpoint**: `POST /glm/file_read`

**Paramètres**:
- `filepath` (string, requis): Chemin du fichier

### 7. file_write
Écrit du contenu dans un fichier (avec validation).

**Endpoint**: `POST /glm/file_write`

**Paramètres**:
- `filepath` (string, requis): Chemin du fichier
- `content` (string, requis): Contenu à écrire
- `allow` (boolean, requis): Doit être `true` pour autoriser

### 8. file_search
Recherche des fichiers correspondant à un pattern.

**Endpoint**: `POST /glm/file_search`

**Paramètres**:
- `pattern` (string, requis): Pattern de recherche (glob)
- `directory` (string, optionnel): Répertoire (défaut: ".")

**Exemple**:
```json
{
  "pattern": "*.py",
  "directory": "backend/mcp"
}
```

### 9. shell_execute_safe
Exécute une commande shell avec vérifications de sécurité.

**Endpoint**: `POST /glm/shell_execute_safe`

**Paramètres**:
- `command` (string, requis): Commande à exécuter
- `allow` (boolean, requis): Doit être `true` pour autoriser

**Commandes autorisées**:
- `ls`, `dir`, `pwd`, `cd`, `echo`, `cat`, `type`
- `git`, `npm`, `pip`, `python`, `node`
- `mkdir`, `touch`, `rm`, `cp`, `mv`

### 10. browser_search
Effectue une recherche web et résume les résultats avec GLM-4.6.

**Endpoint**: `POST /glm/browser_search`

**Paramètres**:
- `query` (string, requis): Requête de recherche

## 🔒 Sécurité

### Validation des opérations sensibles

Les opérations suivantes nécessitent `allow=true`:
- `file_write`: Écriture de fichiers
- `rag_write`: Écriture dans le RAG (validation de dataset)
- `shell_execute_safe`: Exécution de commandes (whitelist)

### Whitelist de commandes

Seules les commandes suivantes sont autorisées pour `shell_execute_safe`:
```python
SAFE_COMMANDS = {
    "ls", "dir", "pwd", "cd", "echo", "cat", "type",
    "git", "npm", "pip", "python", "node",
    "mkdir", "touch", "rm", "cp", "mv"
}
```

## 📊 Endpoints MCP Standard

### GET /
Informations sur le service

### GET /health
Health check avec vérification de disponibilité GLM

### GET /mcp/tools/list
Liste tous les outils disponibles avec leurs schémas

## 🧪 Tests

```bash
# Test de santé
curl http://localhost:9001/health

# Liste des outils
curl http://localhost:9001/mcp/tools/list

# Test solve_problem
curl -X POST http://localhost:9001/glm/solve_problem \
  -H "Content-Type: application/json" \
  -d '{"description": "Test problem", "context": {}}'
```

## 📝 Logs

Le serveur log toutes les requêtes avec le format:
```
[2025-01-21 21:00:00] INFO - solve_problem: Test problem...
```

## 🏗️ Architecture

```
backend/mcp/glm_vision_expert/
├── __init__.py
├── server.py              # Serveur FastAPI principal
├── README.md             # Cette documentation
├── clients/
│   ├── __init__.py
│   └── glm_client.py     # Client OpenRouter/GLM-4.6
└── tools/
    ├── __init__.py
    └── tool_handlers.py  # Implémentation des outils
```

## 🔗 Intégration

Le serveur s'intègre avec:
- **RAG Store**: Pour la gestion de la mémoire
- **OpenRouter**: Pour l'accès à GLM-4.6
- **Système de fichiers**: Opérations sécurisées
- **DuckDuckGo**: Recherche web

## 📦 Dépendances

Voir `requirements.txt` du projet principal:
- `fastapi`
- `uvicorn`
- `aiohttp`
- `pydantic`
- `duckduckgo-search`
- `sentence-transformers` (pour RAG)

## 🚨 Troubleshooting

### Erreur: "OpenRouter API key not found"
Vérifiez que `OPENROUTER_API_KEY` est défini dans `.env`

### Erreur: "Port 9001 already in use"
Changez le port dans `server.py` ligne 509

### Erreur: "File not found"
Vérifiez que les chemins sont relatifs à `c:/AGENT LOCAL`

## 📄 Licence

Partie du projet Agent Local