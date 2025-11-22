# AUDIT COMPLET : SYSTÈMES RAG & MEMORY

**Date:** 21 Novembre 2025
**Auditeur:** Claude Agent
**Scope:** Organisation, stockage, flux et règles des systèmes RAG et Memory
**Objectif:** Comprendre l'état actuel et proposer des améliorations architecturales

---

## TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Système RAG - Architecture Actuelle](#système-rag---architecture-actuelle)
3. [Système Memory - Architecture Actuelle](#système-memory---architecture-actuelle)
4. [Flux de Données](#flux-de-données)
5. [Règles de Tri et Rangement](#règles-de-tri-et-rangement)
6. [Problèmes Identifiés](#problèmes-identifiés)
7. [Propositions d'Amélioration](#propositions-damélioration)
8. [Plan d'Action Recommandé](#plan-daction-recommandé)

---

## VUE D'ENSEMBLE

### Architecture Générale

Le système dispose de **deux systèmes de mémoire distincts** :

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌────────────────┐           │
│  │  RAG SYSTEM  │              │ MEMORY SYSTEM  │           │
│  │  (Long-term) │              │  (Short-term)  │           │
│  │              │              │                │           │
│  │  Documents   │              │  Conversations │           │
│  │  Embeddings  │              │  Sessions      │           │
│  │  Semantic    │              │  Text Search   │           │
│  └──────────────┘              └────────────────┘           │
│         ↓                              ↓                     │
│  ┌──────────────┐              ┌────────────────┐           │
│  │  SQLite DB   │              │   JSON Files   │           │
│  │  rag.db      │              │  memory_data/  │           │
│  └──────────────┘              └────────────────┘           │
│                                                               │
│  ┌─────────────────────────────────────────────┐            │
│  │         CONTEXT BUILDER                      │            │
│  │  (Agrège RAG + Memory + Vision + System)    │            │
│  └─────────────────────────────────────────────┘            │
│                                                               │
│  ┌─────────────────────────────────────────────┐            │
│  │              TIMELINE                        │            │
│  │  (Historique chronologique des actions)     │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Composants Analysés

**Fichiers Audités:**
- `backend/rag/rag_store.py` - Stockage RAG avec embeddings
- `backend/connectors/memory/memory_manager.py` - Gestionnaire mémoire persistante
- `backend/rag/rag_engine.py` - Sessions conversation courte durée
- `backend/orchestrator/context_builder.py` - Agrégation contextes
- `backend/orchestrator/timeline.py` - Historique événements
- `backend/orchestrator/clients/rag_client.py` - Client RAG MCP
- `backend/orchestrator/clients/memory_client.py` - Client Memory MCP
- `backend/routes/rag_routes.py` - API RAG
- `backend/routes/memory_route.py` - API Memory

---

## SYSTÈME RAG - ARCHITECTURE ACTUELLE

### 1. Structure de Stockage

#### Base de Données SQLite

**Localisation:** `C:\AGENT LOCAL\rag\rag.db`
**Taille:** 60 KB
**Technologie:** SQLite + Sentence-Transformers (all-MiniLM-L6-v2)

#### Schéma de Tables

```sql
-- Table: documents
CREATE TABLE documents (
    id TEXT PRIMARY KEY,              -- SHA256 hash
    dataset TEXT NOT NULL,            -- Nom du dataset
    filename TEXT NOT NULL,           -- Nom du fichier
    content TEXT NOT NULL,            -- Contenu complet
    metadata TEXT,                    -- JSON metadata
    created_at TEXT NOT NULL,         -- ISO timestamp
    updated_at TEXT NOT NULL          -- ISO timestamp
);

-- Table: chunks
CREATE TABLE chunks (
    id TEXT PRIMARY KEY,              -- document_id_index
    document_id TEXT NOT NULL,        -- FK vers documents
    chunk TEXT NOT NULL,              -- Texte du chunk
    embedding TEXT,                   -- JSON array embeddings (384 dims)
    order_index INTEGER NOT NULL,    -- Position dans le document
    created_at TEXT NOT NULL,         -- ISO timestamp
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_documents_dataset ON documents(dataset);
CREATE INDEX idx_chunks_document ON chunks(document_id);
```

### 2. Datasets Définis

Le système définit **5 datasets conceptuels** :

```python
VALID_DATASETS = {
    "agent_core",    # Règles permanentes, identité, structure PC
    "context_flow",  # Résumés pré/post, flux conversationnel
    "agent_memory",  # Feedbacks, leçons apprises
    "projects",      # Code, documentation analytique
    "scratchpad"     # Temporaire (legacy)
}
```

#### Mapping d'Alias

```python
mapping = {
    "core": "agent_core",
    "rules": "agent_core",
    "memory": "agent_memory",
    "feedback": "agent_memory",
    "lessons": "agent_memory",
    "context": "context_flow",
    "summary": "context_flow",
    "flow": "context_flow",
    "project": "projects",
    "code": "projects",
    "docs": "projects",
    "temp": "scratchpad"
}
```

### 3. État Actuel de la Base

**Données présentes:**
- **Datasets:** `test_dataset` (2 docs), `uploads` (1 doc)
- **Total chunks:** 3
- **Total documents:** 3

⚠️ **OBSERVATION CRITIQUE:** Les datasets conceptuels définis dans le code (`agent_core`, `context_flow`, etc.) **ne sont pas utilisés** dans la base actuelle. Les données sont stockées dans des datasets génériques.

### 4. Traitement des Documents

#### Chunking
```python
def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200)
```
- **Taille chunk:** 1000 caractères
- **Overlap:** 200 caractères
- **Méthode:** Découpage simple sans respect des limites sémantiques

#### Embeddings
- **Modèle:** `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Dimensions:** 384
- **Type:** Local (pas d'API externe)
- **Stockage:** JSON string dans SQLite

#### Recherche Sémantique
```python
def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float
```
- **Méthode:** Cosine similarity
- **Algorithme:** NumPy dot product + norms
- **Tri:** Par score de similarité décroissant

### 5. Flux d'Ajout de Documents

```
User Request
    ↓
add_document(dataset, filename, content, metadata)
    ↓
1. Génère document_id (SHA256 hash)
2. Stocke document dans table documents
3. Chunke le contenu (1000 chars, overlap 200)
4. Pour chaque chunk:
    - Génère embedding (384 dims)
    - Stocke chunk + embedding dans table chunks
    ↓
Retourne document_id
```

### 6. Flux de Requête

```
User Query
    ↓
query(dataset, question, top_k=5)
    ↓
1. Génère embedding de la question
2. Récupère tous les chunks du dataset
3. Calcule cosine similarity pour chaque chunk
4. Trie par similarité décroissante
5. Retourne top_k chunks
    ↓
Retourne [{chunk_id, content, filename, metadata, similarity}]
```

### 7. Opérations Supportées

| Opération | Description | Endpoint |
|-----------|-------------|----------|
| `add_document` | Ajouter un document | POST /rag/add_document |
| `query` | Recherche sémantique | POST /rag/query |
| `list_documents` | Lister tous les docs | GET /rag/list_documents |
| `list_datasets` | Lister les datasets | GET /rag/list_datasets |
| `get_dataset_info` | Info sur un dataset | GET /rag/get_dataset_info |
| `delete_document` | Supprimer un doc | DELETE /rag/delete_document |
| `delete_dataset` | Supprimer un dataset | DELETE /rag/delete_dataset |
| `get_document_chunks` | Chunks d'un doc | GET /rag/get_document_chunks |
| `cleanup_memory` | Nettoyage scratchpad | POST /rag/cleanup_memory |

### 8. Métadonnées

```python
def parse_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    # Types valides
    valid_types = {"core_rule", "context_data", "learning_data", "project_doc", "general"}

    # Priorités valides
    valid_priorities = {"high", "medium", "low"}
```

**Structure metadata:**
```json
{
  "type": "core_rule|context_data|learning_data|project_doc|general",
  "priority": "high|medium|low",
  "dataset": "agent_core|context_flow|...",
  "filename": "nom_fichier.txt",
  "...": "champs personnalisés"
}
```

---

## SYSTÈME MEMORY - ARCHITECTURE ACTUELLE

### 1. Structure de Stockage

#### Fichiers JSON

**Localisation:** `C:\AGENT LOCAL\memory_data/`
**Format:** Un fichier JSON par session
**Naming:** `{session_id}.json`

**Nombre actuel:** 33 sessions enregistrées

#### Structure d'un Fichier Session

```json
{
  "session_id": "default",
  "created_at": "2025-11-21T03:09:00.123456",
  "updated_at": "2025-11-21T05:21:00.789012",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "Contenu du message",
      "timestamp": "2025-11-21T03:09:01.234567",
      "metadata": {
        // Champs optionnels
      }
    }
  ]
}
```

### 2. Double Système de Sessions

⚠️ **DUPLICATION CRITIQUE DÉTECTÉE**

Il existe **DEUX systèmes de gestion de sessions** :

#### A. MemoryManager (`backend/connectors/memory/memory_manager.py`)
- **Stockage:** `C:\AGENT LOCAL\memory_data/`
- **Format:** JSON (un fichier par session)
- **Utilisation:** API Memory principale
- **Endpoints:** `/memory/*`

#### B. SessionMemory (`backend/rag/rag_engine.py`)
- **Stockage:** `C:\AGENT LOCAL\memory/sessions/`
- **Format:** JSONL (append-only log)
- **Utilisation:** Sessions RAG court terme
- **État:** Répertoire **vide** (non utilisé)

### 3. Flux d'Ajout de Message

```
User Message
    ↓
add_message(session_id, role, content, metadata)
    ↓
1. Charge ou crée le fichier {session_id}.json
2. Ajoute le message avec timestamp
3. Met à jour updated_at
4. Sauvegarde le fichier
    ↓
Retourne success
```

### 4. Opérations Supportées

| Opération | Description | Endpoint |
|-----------|-------------|----------|
| `add` | Ajouter un message | POST /memory/add |
| `get` | Récupérer messages | POST /memory/get |
| `get_context` | Contexte formaté | GET /memory/session/{id}/context |
| `search` | Recherche textuelle | POST /memory/search |
| `clear` | Effacer session | POST /memory/clear |
| `list_sessions` | Lister sessions | GET /memory/sessions |
| `get_summary` | Résumé session | GET /memory/session/{id}/summary |
| `get_full_session` | Session complète | GET /memory/session/{id} |

### 5. Recherche

**Type:** Recherche textuelle simple (substring matching)
**Méthode:** `query.lower() in content.lower()`
**Scope:** Une session OU toutes les sessions

⚠️ **LIMITATION:** Pas d'embeddings, pas de recherche sémantique dans Memory

### 6. Contexte Formaté

```python
def get_context(session_id: str, max_messages: int = 10) -> str:
    # Format:
    # Previous conversation:
    # [user] Message user
    # [assistant] Réponse assistant
    # ...
```

---

## FLUX DE DONNÉES

### 1. Architecture des Flux

```
┌──────────────────────────────────────────────────────────┐
│                    USER REQUEST                          │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ↓
     ┌────────────────────────────┐
     │  FastAPI Main (main.py)    │
     └────────────┬───────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ↓                   ↓
┌───────────────┐   ┌──────────────────┐
│  RAG Routes   │   │  Memory Routes   │
│  /rag/*       │   │  /memory/*       │
└───────┬───────┘   └────────┬─────────┘
        │                    │
        ↓                    ↓
┌───────────────┐   ┌──────────────────┐
│  RAGStore     │   │  MemoryManager   │
│  (rag.db)     │   │  (JSON files)    │
└───────────────┘   └──────────────────┘
        │                    │
        └────────┬───────────┘
                 │
                 ↓
        ┌────────────────┐
        │  Orchestrator  │
        │  + Clients     │
        └────────┬───────┘
                 │
                 ↓
        ┌────────────────┐
        │ Context Builder│
        │  (Agrégation)  │
        └────────────────┘
```

### 2. Sources de Données

#### A. RAG (Documents Long-Terme)

**Alimentation:**
1. **Manuellement** via API `/rag/add_document`
2. **Par l'orchestrateur** via `rag_client.add_document()`
3. **Non automatique** - requiert action explicite

**Contenu attendu:**
- Règles de l'agent
- Documentation projet
- Code analysé
- Connaissances persistantes
- Leçons apprises

#### B. Memory (Conversations Court-Terme)

**Alimentation:**
1. **Automatique** - chaque message user/assistant
2. **Via orchestrateur** - `memory_client.add_message()`
3. **Temps réel** - append à chaque interaction

**Contenu attendu:**
- Historique conversationnel
- Messages user/assistant/system
- Contexte de session
- État dialogue

#### C. Timeline (Événements)

**Alimentation:**
1. **Automatique** - chaque action de l'orchestrateur
2. **En mémoire** - pas de persistance
3. **Limité** - max 1000 événements

**Contenu:**
- Plans générés
- Exécutions d'outils
- Erreurs
- Événements multimodaux (audio, vision)

#### D. Context Builder (Agrégation)

**Sources consolidées:**
```python
async def build_super_context(user_message, session_id):
    return {
        "memory": await _get_memory_context(),      # Memory + search
        "rag_docs": await _get_rag_context(),       # RAG multi-datasets
        "vision": await _get_vision_context(),       # Vision active
        "system_state": await _get_system_state(),   # Snapshot système
        "audio": await _get_audio_context(),         # Audio récent
        "documents": await _get_documents_context()  # Docs récents
    }
```

### 3. Flux de Requête Utilisateur

```
1. User message arrive
    ↓
2. Orchestrator reçoit la requête
    ↓
3. Context Builder agrège:
    - Memory: get_context(session_id, max=5) + search(user_message)
    - RAG: query multiple datasets
        * agent_core (top_k=2)
        * projects (top_k=2)
        * scratchpad (top_k=1)
        * rules (top_k=1)
    - Vision: contexte actif
    - System: snapshot état
    - Audio: contexte récent
    - Documents: documents récents
    ↓
4. Super-context construit
    ↓
5. LLM Planner génère plan avec contexte
    ↓
6. Executor exécute actions
    ↓
7. Réponse finale user
    ↓
8. Memory stocke interaction (add_message)
9. Timeline enregistre événements
```

---

## RÈGLES DE TRI ET RANGEMENT

### 1. RAG - Règles de Datasets

#### Mapping Conceptuel

```python
# Définition théorique (EnhancedRAGStore)
VALID_DATASETS = {
    "agent_core",    # Permanent: Identity, Rules, PC Structure
    "context_flow",  # Pre/Post summaries, conversational flow
    "agent_memory",  # Feedbacks, lessons learned
    "projects",      # Code, analytical docs, medium-term work
    "scratchpad"     # Ephemeral, temporary info
}
```

#### Auto-Routing

La classe `EnhancedRAGStore` implémente un **auto-routing** :

```python
async def auto_route(self, dataset_choice: str) -> str:
    # Alias → dataset canonique
    if dataset_choice in VALID_DATASETS:
        return dataset_choice
    return mapping.get(dataset_choice.lower(), "scratchpad")
```

⚠️ **PROBLÈME:** Cette logique existe mais **n'est PAS appliquée** systématiquement.

#### Règles de Priorité

```python
valid_types = {"core_rule", "context_data", "learning_data", "project_doc", "general"}
valid_priorities = {"high", "medium", "low"}
```

**Mapping type → dataset (logique attendue):**
- `core_rule` → `agent_core`
- `context_data` → `context_flow`
- `learning_data` → `agent_memory`
- `project_doc` → `projects`
- `general` → `scratchpad`

⚠️ **PROBLÈME:** Cette logique n'est **pas implémentée** dans `parse_metadata()`.

### 2. Memory - Règles de Sessions

#### Naming Convention

```python
# Sanitized session_id
safe_session_id = "".join(c for c in session_id if c.isalnum() or c in ('-', '_'))
filename = f"{safe_session_id}.json"
```

**Pattern observé:**
- `default.json` - Session par défaut
- `session_{timestamp}_{random}.json` - Sessions générées
- `test_*.json` - Sessions de test
- `{custom_name}.json` - Sessions nommées

#### Pas de Tri Hiérarchique

⚠️ **OBSERVATION:** Tous les fichiers sont au même niveau dans `memory_data/`. Aucune organisation par :
- Date
- Utilisateur
- Projet
- Type d'interaction

#### Pas de Rétention

⚠️ **OBSERVATION:** Aucune règle de rétention automatique. Les sessions s'accumulent indéfiniment.

### 3. Timeline - Règles d'Événements

#### Détection Automatique de Modalité

```python
def _detect_modality(event_type: str, data: Dict[str, Any]) -> str:
    # Règles de détection:
    if "audio" in event_type.lower():
        return "audio"
    elif "vision" in event_type.lower() or "image" in event_type.lower():
        return "vision"
    elif "document" in event_type.lower():
        return "documents"
    elif "system" in event_type.lower():
        return "system"
    # Vérifier tool dans data
    return "text"  # default
```

#### Limitation de Taille

```python
self.max_events = 1000  # Limite mémoire
if len(self.events) > self.max_events:
    self.events = self.events[-self.max_events:]  # Garde les plus récents
```

⚠️ **PROBLÈME:** Pas de persistance. En cas de redémarrage, toute la timeline est perdue.

### 4. Context Builder - Règles d'Agrégation

#### Requêtes RAG Multi-Datasets

```python
# A. CORE MEMORY (top_k=2)
core_results = await rag_client.query("agent_core", user_message, top_k=2)

# B. PROJECT MEMORY (top_k=2)
project_results = await rag_client.query("projects", user_message, top_k=2)

# C. SCRATCHPAD (top_k=1)
scratch_results = await rag_client.query("scratchpad", user_message, top_k=1)

# D. RULES (top_k=1)
rules_results = await rag_client.query("rules", user_message, top_k=1)
```

**Total chunks récupérés:** Max 6 chunks par requête

#### Requête Memory

```python
# Contexte récent: 5 derniers messages
context = await memory_client.get_context(session_id, max_messages=5)

# Recherche sémantique (textuelle)
search_results = await memory_client.search(user_message, session_id)
```

---

## PROBLÈMES IDENTIFIÉS

### 🔴 CRITIQUES

#### 1. Datasets RAG Non Utilisés

**Problème:** Le code définit 5 datasets conceptuels (`agent_core`, `context_flow`, `agent_memory`, `projects`, `scratchpad`) mais la base de données contient des datasets génériques (`test_dataset`, `uploads`).

**Impact:**
- ❌ Perte de la structure sémantique
- ❌ Pas de séparation mémoire permanente vs temporaire
- ❌ Confusion sur où ranger les documents
- ❌ Auto-routing non effectif

**Cause:** Absence d'utilisation cohérente de `EnhancedRAGStore` et son `auto_route()`.

#### 2. Double Système de Sessions

**Problème:** Deux systèmes de gestion de sessions coexistent :
- `MemoryManager` (JSON, utilisé)
- `SessionMemory` (JSONL, non utilisé)

**Impact:**
- ❌ Confusion architecturale
- ❌ Code mort (`rag_engine.py` sessions)
- ❌ Risque d'utilisation incohérente
- ❌ Maintenance compliquée

#### 3. Memory Sans Recherche Sémantique

**Problème:** La recherche dans Memory est purement textuelle (substring matching), contrairement au RAG qui a des embeddings.

**Impact:**
- ❌ Impossible de retrouver des conversations par sens
- ❌ Recherche très limitée
- ❌ Pas d'exploitation de la sémantique des échanges

**Exemple:** Rechercher "comment configurer l'audio" ne trouvera pas "setup microphone" ou "paramétrer le son".

#### 4. Timeline Non Persistante

**Problème:** La Timeline est en mémoire (liste Python), limitée à 1000 événements, et perdue au redémarrage.

**Impact:**
- ❌ Perte de l'historique des actions au redémarrage
- ❌ Impossible d'auditer les actions passées
- ❌ Limite de 1000 événements arbitraire
- ❌ Pas de traçabilité long terme

### 🟠 MAJEURS

#### 5. Métadonnées Non Exploitées

**Problème:** Le système définit `parse_metadata()` avec types et priorités, mais ne les utilise pas pour :
- Router automatiquement vers le bon dataset
- Prioriser les résultats de recherche
- Organiser les documents

**Impact:**
- ⚠️ Métadonnées inutilisées
- ⚠️ Pas de filtrage par type
- ⚠️ Pas de tri par priorité

#### 6. Chunking Naïf

**Problème:** Le découpage est fixe (1000 chars, overlap 200), sans respect des:
- Paragraphes
- Phrases
- Sections logiques

**Impact:**
- ⚠️ Chunks coupés au milieu de phrases
- ⚠️ Perte de contexte sémantique
- ⚠️ Qualité de recherche dégradée

#### 7. Pas de Cleanup Automatique

**Problème:** Aucun système de rétention automatique pour :
- `scratchpad` dans RAG
- Sessions anciennes dans Memory
- Timeline (mais en mémoire donc reset au reboot)

**Impact:**
- ⚠️ Accumulation de données obsolètes
- ⚠️ Croissance continue de la base
- ⚠️ Pollution des résultats de recherche

#### 8. Absence de Versioning

**Problème:** Les documents dans RAG peuvent être mis à jour (INSERT OR REPLACE) mais sans historique de versions.

**Impact:**
- ⚠️ Impossible de revenir en arrière
- ⚠️ Perte de l'évolution des documents
- ⚠️ Pas d'audit des modifications

### 🟡 MINEURS

#### 9. Context Builder Trop Générique

**Problème:** Le Context Builder récupère toujours les mêmes datasets RAG, sans adaptation au type de requête.

**Impact:**
- ⚙️ Surcharge inutile pour requêtes simples
- ⚙️ Pas d'optimisation par contexte

#### 10. Embeddings en JSON

**Problème:** Les embeddings (384 dimensions) sont stockés en JSON text dans SQLite, pas en BLOB binaire.

**Impact:**
- ⚙️ Taille de stockage 4-5x plus grande
- ⚙️ Parsing JSON à chaque requête
- ⚙️ Performance dégradée

#### 11. Recherche Non Optimisée

**Problème:** Pour chaque requête, TOUS les chunks du dataset sont chargés en mémoire pour calculer les similarités.

**Impact:**
- ⚙️ Scalabilité limitée
- ⚙️ Performance O(n) où n = nombre de chunks
- ⚙️ Pas d'indexation vectorielle

#### 12. Sessions Memory Non Structurées

**Problème:** Toutes les sessions sont au même niveau dans `memory_data/`, sans organisation hiérarchique.

**Impact:**
- ⚙️ Difficile de naviguer avec 33+ sessions
- ⚙️ Pas de groupement par projet/utilisateur/date
- ⚙️ Backup/archivage compliqué

---

## PROPOSITIONS D'AMÉLIORATION

### 🚀 PRIORITÉ 1 - CRITIQUE (Court Terme)

#### A1. Implémenter Datasets RAG Correctement

**Objectif:** Utiliser systématiquement les 5 datasets conceptuels

**Actions:**
1. Migrer les données existantes vers les bons datasets
2. Forcer l'utilisation de `EnhancedRAGStore` partout
3. Documenter le mapping dataset → usage
4. Ajouter validation à l'API

**Implémentation:**
```python
# Dans routes/rag_routes.py - ajouter validation
ALLOWED_DATASETS = {"agent_core", "context_flow", "agent_memory", "projects", "scratchpad"}

@router.post("/rag/add_document")
async def add_document(request: AddDocumentRequest):
    dataset = request.dataset
    if dataset not in ALLOWED_DATASETS:
        raise HTTPException(400, f"Invalid dataset. Use: {ALLOWED_DATASETS}")
    # Auto-route si alias fourni
    dataset = await rag_store.auto_route(dataset)
    ...
```

**Script de migration:**
```python
# migration_datasets.py
import sqlite3

conn = sqlite3.connect('rag/rag.db')
cursor = conn.cursor()

# Mapper test_dataset → projects (exemple)
cursor.execute("UPDATE documents SET dataset='projects' WHERE dataset='test_dataset'")
cursor.execute("UPDATE documents SET dataset='scratchpad' WHERE dataset='uploads'")

conn.commit()
conn.close()
```

#### A2. Supprimer le Double Système de Sessions

**Objectif:** Garder uniquement `MemoryManager`, supprimer `SessionMemory`

**Actions:**
1. Supprimer les fonctions dans `rag_engine.py`
2. Supprimer le répertoire `memory/sessions/`
3. Mettre à jour les imports
4. Clarifier la documentation

**Fichiers à modifier:**
- `backend/rag/rag_engine.py` - Supprimer `add_message_to_session`, `get_session_history`
- `backend/memory/sessions/` - Supprimer répertoire

#### A3. Ajouter Embeddings à Memory

**Objectif:** Permettre recherche sémantique dans les conversations

**Implémentation:**
```python
# Dans MemoryManager
class MemoryManager:
    def __init__(self, storage_dir: Optional[str] = None):
        # ...
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def add(self, session_id, message, role, metadata):
        # Générer embedding du message
        embedding = self.embedding_model.encode(message).tolist()

        message_entry = {
            "role": role,
            "content": message,
            "embedding": embedding,  # NOUVEAU
            "timestamp": datetime.now().isoformat()
        }
        # ...

    async def semantic_search(self, query: str, session_id: Optional[str] = None, top_k: int = 5):
        """Recherche sémantique dans les conversations"""
        query_embedding = self.embedding_model.encode(query).tolist()

        # Charger toutes les sessions concernées
        # Calculer similarités
        # Retourner top_k
```

#### A4. Persister la Timeline

**Objectif:** Sauvegarder la timeline en base de données

**Structure:**
```sql
CREATE TABLE timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON
    metadata TEXT,        -- JSON
    modality TEXT
);

CREATE INDEX idx_timeline_session ON timeline_events(session_id);
CREATE INDEX idx_timeline_type ON timeline_events(event_type);
CREATE INDEX idx_timeline_modality ON timeline_events(modality);
```

**Implémentation:**
```python
class PersistentTimeline(Timeline):
    def __init__(self, db_path="timeline.db"):
        super().__init__()
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS ...""")
        conn.commit()
        conn.close()

    def add_event(self, event_type, data, session_id, metadata):
        # Ajouter à self.events (mémoire)
        event = super().add_event(event_type, data, session_id, metadata)

        # Persister en DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO timeline_events ...")
        conn.commit()
        conn.close()

        return event
```

### 🔧 PRIORITÉ 2 - MAJEURE (Moyen Terme)

#### B1. Métadonnées Intelligentes

**Objectif:** Utiliser les métadonnées pour router et filtrer

**Implémentation:**
```python
class SmartRAGStore(EnhancedRAGStore):
    async def add_document(self, dataset, filename, content, metadata):
        # Auto-déterminer le dataset basé sur metadata.type
        if metadata and "type" in metadata:
            doc_type = metadata["type"]
            type_to_dataset = {
                "core_rule": "agent_core",
                "context_data": "context_flow",
                "learning_data": "agent_memory",
                "project_doc": "projects",
                "general": "scratchpad"
            }
            dataset = type_to_dataset.get(doc_type, dataset)

        # Valider et parser metadata
        enhanced_metadata = self.parse_metadata(metadata)

        # Ajouter dataset auto-déterminé
        enhanced_metadata["auto_dataset"] = dataset

        return await super().add_document(dataset, filename, content, enhanced_metadata)

    async def query(self, dataset, question, top_k=5, filters: Dict[str, Any] = None):
        """Query avec filtres metadata"""
        results = await super().query(dataset, question, top_k)

        if filters:
            # Filtrer par type
            if "type" in filters:
                results = [r for r in results if r["metadata"].get("type") == filters["type"]]

            # Filtrer par priorité
            if "min_priority" in filters:
                priority_order = {"high": 3, "medium": 2, "low": 1}
                min_val = priority_order.get(filters["min_priority"], 0)
                results = [r for r in results
                          if priority_order.get(r["metadata"].get("priority", "low"), 1) >= min_val]

        return results
```

#### B2. Chunking Intelligent

**Objectif:** Respecter les limites sémantiques

**Implémentation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SmartChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",  # Paragraphes
                "\n",    # Lignes
                ". ",    # Phrases
                " ",     # Mots
                ""       # Caractères
            ]
        )

    def chunk_text(self, text: str) -> List[str]:
        return self.splitter.split_text(text)
```

#### B3. Cleanup Automatique

**Objectif:** Nettoyer automatiquement les données obsolètes

**Implémentation:**
```python
class RAGStoreWithCleanup(RAGStore):
    async def cleanup_scratchpad(self, retention_days: int = 7):
        """Supprimer les docs du scratchpad plus vieux que N jours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.utcnow() - timedelta(days=retention_days)).isoformat()

        cursor.execute("""
            SELECT id FROM documents
            WHERE dataset = 'scratchpad'
            AND created_at < ?
        """, (cutoff_date,))

        doc_ids = [row[0] for row in cursor.fetchall()]

        for doc_id in doc_ids:
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

        conn.commit()
        conn.close()

        return {"deleted": len(doc_ids), "retention_days": retention_days}

class MemoryManagerWithCleanup(MemoryManager):
    async def cleanup_old_sessions(self, retention_days: int = 30):
        """Archiver sessions plus vieilles que N jours"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        archived_count = 0
        for session_file in self.storage_dir.glob("*.json"):
            if session_file.stat().st_mtime < cutoff_date.timestamp():
                # Archiver dans un sous-répertoire
                archive_dir = self.storage_dir / "archive"
                archive_dir.mkdir(exist_ok=True)
                session_file.rename(archive_dir / session_file.name)
                archived_count += 1

        return {"archived": archived_count, "retention_days": retention_days}
```

**Tâche cron:**
```python
# Dans orchestrator ou main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)  # 2h du matin chaque jour
async def daily_cleanup():
    # Cleanup scratchpad (7 jours)
    await rag_store.cleanup_scratchpad(retention_days=7)

    # Cleanup sessions (30 jours)
    await memory_manager.cleanup_old_sessions(retention_days=30)

    print(f"[CLEANUP] Daily cleanup completed at {datetime.now()}")

scheduler.start()
```

#### B4. Versioning Documents

**Objectif:** Historiser les modifications de documents

**Structure:**
```sql
CREATE TABLE document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT,
    change_reason TEXT,
    UNIQUE(document_id, version)
);

CREATE INDEX idx_versions_doc ON document_versions(document_id);
```

**Implémentation:**
```python
class VersionedRAGStore(RAGStore):
    async def add_document(self, dataset, filename, content, metadata):
        # Vérifier si le document existe déjà
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        doc_id = hashlib.sha256(f"{dataset}:{filename}:{content[:100]}".encode()).hexdigest()

        cursor.execute("SELECT COUNT(*) FROM documents WHERE id = ?", (doc_id,))
        exists = cursor.fetchone()[0] > 0

        if exists:
            # Archiver la version actuelle
            cursor.execute("SELECT content, metadata FROM documents WHERE id = ?", (doc_id,))
            old_content, old_metadata = cursor.fetchone()

            # Compter les versions existantes
            cursor.execute("SELECT COALESCE(MAX(version), 0) FROM document_versions WHERE document_id = ?", (doc_id,))
            last_version = cursor.fetchone()[0]
            new_version = last_version + 1

            # Sauvegarder l'ancienne version
            cursor.execute("""
                INSERT INTO document_versions (document_id, version, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, new_version, old_content, old_metadata, datetime.utcnow().isoformat()))

            conn.commit()

        conn.close()

        # Ajouter/mettre à jour le document
        return await super().add_document(dataset, filename, content, metadata)

    def get_document_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """Récupérer l'historique des versions d'un document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT version, content, metadata, created_at
            FROM document_versions
            WHERE document_id = ?
            ORDER BY version DESC
        """, (doc_id,))

        versions = []
        for row in cursor.fetchall():
            versions.append({
                "version": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            })

        conn.close()
        return versions
```

### ⚡ PRIORITÉ 3 - OPTIMISATION (Long Terme)

#### C1. Context Builder Adaptatif

**Objectif:** Adapter les requêtes RAG selon le type de demande

**Implémentation:**
```python
class AdaptiveContextBuilder(ContextBuilder):
    async def build_super_context(self, user_message: str, session_id: str = "default"):
        # Classifier l'intent du message
        intent = await self._classify_intent(user_message)

        # Adapter les datasets RAG selon l'intent
        rag_config = self._get_rag_config_for_intent(intent)

        # Construire le contexte adapté
        memory = await self._get_memory_context(user_message, session_id)
        rag = await self._get_adaptive_rag_context(user_message, rag_config)

        # Contextee vision/audio seulement si pertinent
        vision = None
        audio = None
        if intent in ["vision_analysis", "multimodal"]:
            vision = await self._get_vision_context()
        if intent in ["audio_processing", "multimodal"]:
            audio = await self._get_audio_context()

        system_state = await self._get_system_state()
        documents = await self._get_documents_context()

        return self._merge_contexts(
            memory=memory,
            rag=rag,
            vision=vision,
            system_state=system_state,
            audio=audio,
            documents=documents
        )

    async def _classify_intent(self, message: str) -> str:
        """Classifier l'intent du message"""
        # Simple keyword-based pour commencer
        message_lower = message.lower()

        if any(kw in message_lower for kw in ["règle", "rule", "policy", "principe"]):
            return "rules_query"
        elif any(kw in message_lower for kw in ["projet", "code", "function", "class"]):
            return "project_query"
        elif any(kw in message_lower for kw in ["rappelle", "remember", "conversation précédente"]):
            return "memory_query"
        elif any(kw in message_lower for kw in ["image", "voir", "analyser", "vision"]):
            return "vision_analysis"
        elif any(kw in message_lower for kw in ["audio", "son", "voix", "écoute"]):
            return "audio_processing"
        else:
            return "general"

    def _get_rag_config_for_intent(self, intent: str) -> Dict[str, int]:
        """Configuration RAG selon l'intent"""
        configs = {
            "rules_query": {
                "agent_core": 5,
                "rules": 3,
                "projects": 0,
                "scratchpad": 0
            },
            "project_query": {
                "projects": 5,
                "agent_core": 1,
                "scratchpad": 2
            },
            "memory_query": {
                "agent_memory": 5,
                "context_flow": 3,
                "scratchpad": 0
            },
            "general": {
                "agent_core": 2,
                "projects": 2,
                "scratchpad": 1,
                "rules": 1
            }
        }
        return configs.get(intent, configs["general"])

    async def _get_adaptive_rag_context(self, user_message: str, config: Dict[str, int]) -> Dict[str, Any]:
        """Requête RAG adaptée selon config"""
        rag_results = {}

        for dataset, top_k in config.items():
            if top_k > 0:
                results = await self.orchestrator.rag_client.query(dataset, user_message, top_k=top_k)
                if results:
                    rag_results[dataset] = results

        return {
            "status": "success",
            "datasets": rag_results,
            "total_results": sum(len(v) for v in rag_results.values())
        }
```

#### C2. Optimiser Embeddings Storage

**Objectif:** Stocker embeddings en binaire, pas en JSON

**Migration:**
```sql
-- Ajouter colonne binaire
ALTER TABLE chunks ADD COLUMN embedding_bin BLOB;

-- Script de migration
UPDATE chunks
SET embedding_bin = (
    -- Convertir JSON → liste → bytes numpy → blob
    -- À faire en Python
);

-- Supprimer ancienne colonne (après migration)
-- ALTER TABLE chunks DROP COLUMN embedding;
```

**Code:**
```python
import struct

class OptimizedRAGStore(RAGStore):
    def _embedding_to_bytes(self, embedding: List[float]) -> bytes:
        """Convertir embedding en bytes binaires"""
        return struct.pack(f'{len(embedding)}f', *embedding)

    def _bytes_to_embedding(self, data: bytes) -> List[float]:
        """Convertir bytes en embedding"""
        n = len(data) // 4  # 4 bytes par float
        return list(struct.unpack(f'{n}f', data))

    async def add_document(self, dataset, filename, content, metadata):
        # ...
        for idx, chunk in enumerate(chunks):
            embedding = await self._get_embedding(chunk)
            embedding_bytes = self._embedding_to_bytes(embedding)

            cursor.execute("""
                INSERT OR REPLACE INTO chunks
                (id, document_id, chunk, embedding_bin, order_index, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (chunk_id, doc_id, chunk, embedding_bytes, idx, now))
```

**Gain:** Taille réduite de 70-80%, parsing 10x plus rapide.

#### C3. Indexation Vectorielle (FAISS)

**Objectif:** Utiliser FAISS pour recherche vectorielle rapide

**Implémentation:**
```python
import faiss
import numpy as np

class FAISSRAGStore(RAGStore):
    def __init__(self, db_path: str = "rag/rag.db"):
        super().__init__(db_path)
        self.index = None
        self.chunk_ids = []
        self._load_index()

    def _load_index(self):
        """Charger tous les embeddings en index FAISS"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, embedding FROM chunks WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            # Index vide
            self.index = faiss.IndexFlatL2(384)  # 384 dimensions
            return

        # Construire l'index
        chunk_ids = []
        embeddings = []

        for chunk_id, embedding_json in rows:
            chunk_ids.append(chunk_id)
            embeddings.append(json.loads(embedding_json))

        self.chunk_ids = chunk_ids
        embeddings_np = np.array(embeddings, dtype=np.float32)

        # Créer index FAISS
        self.index = faiss.IndexFlatL2(embeddings_np.shape[1])
        self.index.add(embeddings_np)

    async def query(self, dataset: str, question: str, top_k: int = 5):
        """Recherche ultra-rapide avec FAISS"""
        # Générer embedding de la question
        question_embedding = await self._get_embedding(question)
        query_vec = np.array([question_embedding], dtype=np.float32)

        # Recherche FAISS
        distances, indices = self.index.search(query_vec, top_k)

        # Récupérer les chunks correspondants
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            chunk_id = self.chunk_ids[idx]

            cursor.execute("""
                SELECT c.chunk, d.filename, d.metadata, d.dataset
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.id = ?
            """, (chunk_id,))

            row = cursor.fetchone()
            if row and row[3] == dataset:  # Filtrer par dataset
                content, filename, metadata_json, _ = row
                similarity = 1 / (1 + distance)  # Convertir distance → similarité

                results.append({
                    "chunk_id": chunk_id,
                    "content": content,
                    "filename": filename,
                    "metadata": json.loads(metadata_json) if metadata_json else {},
                    "similarity": float(similarity)
                })

        conn.close()

        # Trier par similarité
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
```

**Gain:** Recherche 100x plus rapide sur gros volumes (>10k chunks).

#### C4. Structurer Memory Hiérarchiquement

**Objectif:** Organiser sessions par projet/date

**Structure:**
```
memory_data/
├── active/              # Sessions actives (< 7 jours)
│   ├── default.json
│   └── session_xxx.json
├── archive/             # Sessions anciennes (7-90 jours)
│   ├── 2025-11/
│   │   └── session_xxx.json
│   └── 2025-10/
├── projects/            # Sessions par projet
│   ├── project_alpha/
│   │   └── session_xxx.json
│   └── project_beta/
└── tests/               # Sessions de test
    └── test_xxx.json
```

**Implémentation:**
```python
class HierarchicalMemoryManager(MemoryManager):
    def __init__(self, storage_dir: Optional[str] = None):
        super().__init__(storage_dir)
        self.active_dir = self.storage_dir / "active"
        self.archive_dir = self.storage_dir / "archive"
        self.projects_dir = self.storage_dir / "projects"
        self.tests_dir = self.storage_dir / "tests"

        # Créer sous-répertoires
        for directory in [self.active_dir, self.archive_dir, self.projects_dir, self.tests_dir]:
            directory.mkdir(exist_ok=True)

    def _get_session_file(self, session_id: str, metadata: Dict[str, Any] = None) -> Path:
        """Déterminer le chemin du fichier selon metadata"""
        safe_session_id = "".join(c for c in session_id if c.isalnum() or c in ('-', '_'))

        # Test sessions
        if session_id.startswith("test_"):
            return self.tests_dir / f"{safe_session_id}.json"

        # Project sessions
        if metadata and "project" in metadata:
            project_dir = self.projects_dir / metadata["project"]
            project_dir.mkdir(exist_ok=True)
            return project_dir / f"{safe_session_id}.json"

        # Active sessions (default)
        return self.active_dir / f"{safe_session_id}.json"

    async def auto_archive_old_sessions(self, days_threshold: int = 7):
        """Archiver automatiquement les sessions anciennes"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        archived_count = 0

        for session_file in self.active_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)

            if mtime < cutoff_date:
                # Archiver dans archive/{year-month}/
                year_month = mtime.strftime("%Y-%m")
                archive_month_dir = self.archive_dir / year_month
                archive_month_dir.mkdir(exist_ok=True)

                session_file.rename(archive_month_dir / session_file.name)
                archived_count += 1

        return {"archived": archived_count, "threshold_days": days_threshold}
```

---

## PLAN D'ACTION RECOMMANDÉ

### Phase 1 : Stabilisation (Semaine 1-2)

**Objectif:** Corriger les problèmes critiques

✅ **Actions:**
1. **Migrer les datasets RAG**
   - Script de migration `test_dataset` → `projects`, `uploads` → `scratchpad`
   - Valider que tous les docs sont dans les bons datasets
   - Ajouter validation stricte à l'API

2. **Supprimer double système sessions**
   - Supprimer code `SessionMemory` dans `rag_engine.py`
   - Supprimer répertoire `memory/sessions/`
   - Mettre à jour documentation

3. **Implémenter Timeline persistante**
   - Créer table SQLite `timeline_events`
   - Migrer `Timeline` → `PersistentTimeline`
   - Tester sauvegarde/restauration

4. **Documentation architecture**
   - Documenter les 5 datasets et leurs usages
   - Documenter Memory vs RAG
   - Créer schémas d'architecture

📊 **KPI de succès:**
- ✅ 100% des docs dans datasets corrects
- ✅ Zéro duplication système sessions
- ✅ Timeline survit aux redémarrages
- ✅ Documentation à jour

### Phase 2 : Enrichissement (Semaine 3-4)

**Objectif:** Améliorer fonctionnalités existantes

✅ **Actions:**
1. **Embeddings dans Memory**
   - Ajouter `embedding_model` à `MemoryManager`
   - Générer embeddings pour chaque message
   - Implémenter `semantic_search()`

2. **Métadonnées intelligentes**
   - Implémenter auto-routing par type
   - Ajouter filtres metadata aux requêtes
   - Documenter metadata schema

3. **Chunking intelligent**
   - Intégrer `RecursiveCharacterTextSplitter`
   - Tester avec docs longs
   - Comparer qualité vs chunking naïf

4. **Cleanup automatique**
   - Implémenter `cleanup_scratchpad(retention_days=7)`
   - Implémenter `cleanup_old_sessions(retention_days=30)`
   - Configurer tâche cron quotidienne

📊 **KPI de succès:**
- ✅ Recherche sémantique opérationnelle dans Memory
- ✅ Auto-routing fonctionne pour 100% des ajouts
- ✅ Qualité chunks améliorée (mesure humaine)
- ✅ Cleanup automatique tourne quotidiennement

### Phase 3 : Optimisation (Semaine 5-6)

**Objectif:** Performance et scalabilité

✅ **Actions:**
1. **Embeddings binaires**
   - Migrer embeddings JSON → BLOB
   - Mesurer gain taille/performance
   - Valider résultats identiques

2. **Context Builder adaptatif**
   - Implémenter classification intent
   - Configurer RAG adaptatif
   - Mesurer réduction tokens

3. **Memory hiérarchique**
   - Restructurer `memory_data/` en `active/archive/projects/tests/`
   - Migrer sessions existantes
   - Auto-archivage quotidien

4. **Versioning documents (optionnel)**
   - Créer table `document_versions`
   - Implémenter historique
   - Interface pour voir versions

📊 **KPI de succès:**
- ✅ Taille DB réduite de 70%
- ✅ Parsing embeddings 10x plus rapide
- ✅ Context tokens réduits de 30-50% selon intent
- ✅ Sessions organisées logiquement

### Phase 4 : Scalabilité (Semaine 7-8+)

**Objectif:** Supporter gros volumes

✅ **Actions (optionnelles):**
1. **FAISS indexation**
   - Intégrer FAISS pour recherche vectorielle
   - Benchmark vs SQLite native
   - Migration progressive

2. **Pagination avancée**
   - Implémenter pagination API
   - Cursor-based pagination
   - Limites raisonnables par défaut

3. **Monitoring & métriques**
   - Ajouter métriques Prometheus
   - Dashboard Grafana
   - Alertes sur anomalies

📊 **KPI de succès:**
- ✅ Support >100k chunks sans dégradation
- ✅ Recherche <100ms même sur gros volumes
- ✅ Métriques temps réel disponibles

---

## CONCLUSION

### Résumé Exécutif

Le système RAG & Memory actuel est **fonctionnel mais sous-optimisé**. Les fondations sont solides (SQLite + embeddings locaux pour RAG, JSON pour Memory), mais plusieurs problèmes architecturaux limitent l'efficacité :

**Points Forts:**
✅ Séparation claire RAG (long-terme) vs Memory (court-terme)
✅ Embeddings locaux (pas de dépendance API)
✅ Architecture modulaire (clients MCP)
✅ Context Builder pour agrégation

**Points Faibles:**
❌ Datasets conceptuels non utilisés
❌ Double système sessions
❌ Memory sans recherche sémantique
❌ Timeline non persistante
❌ Métadonnées non exploitées

### Impact des Améliorations

**Court terme (Phase 1):**
- 🎯 Clarté architecturale
- 🎯 Traçabilité complète (timeline)
- 🎯 Organisation logique des données

**Moyen terme (Phases 2-3):**
- 🎯 Recherche sémantique partout
- 🎯 Auto-organisation intelligente
- 🎯 Performance optimisée
- 🎯 Maintenance automatisée

**Long terme (Phase 4+):**
- 🎯 Scalabilité illimitée
- 🎯 Observabilité complète
- 🎯 Production-ready

### Recommandation Finale

**Priorité:** Commencer par la **Phase 1** immédiatement. Les corrections des problèmes critiques sont essentielles pour éviter :
- Confusion sur l'organisation des données
- Perte de traçabilité
- Duplication code/données
- Tech debt croissante

**Timeline recommandée:** 8 semaines pour compléter Phases 1-3, Phase 4 optionnelle selon besoins.

**Ressources nécessaires:**
- 1 développeur à temps plein
- Environnement de test
- Backup complet avant migration

---

## ANNEXES

### A. Schéma Base de Données Actuel

```sql
-- rag.db (SQLite)
documents (
    id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)

chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk TEXT NOT NULL,
    embedding TEXT,  -- JSON [384 floats]
    order_index INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
)
```

### B. Schéma Proposé Complet

```sql
-- rag.db (SQLite) - Version améliorée
documents (
    id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL CHECK(dataset IN ('agent_core', 'context_flow', 'agent_memory', 'projects', 'scratchpad')),
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT,
    current_version INTEGER DEFAULT 1
)

chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk TEXT NOT NULL,
    embedding_bin BLOB,  -- Binaire optimisé
    order_index INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
)

document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT,
    change_reason TEXT,
    UNIQUE(document_id, version)
)

timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON
    metadata TEXT,  -- JSON
    modality TEXT
)

-- Indexes
CREATE INDEX idx_documents_dataset ON documents(dataset);
CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_versions_doc ON document_versions(document_id);
CREATE INDEX idx_timeline_session ON timeline_events(session_id);
CREATE INDEX idx_timeline_type ON timeline_events(event_type);
CREATE INDEX idx_timeline_modality ON timeline_events(modality);
```

### C. Structure Memory Hiérarchique

```
memory_data/
├── active/
│   ├── default.json
│   └── session_*.json
├── archive/
│   ├── 2025-11/
│   │   └── session_*.json
│   └── 2025-10/
│       └── session_*.json
├── projects/
│   ├── agent_local/
│   │   └── session_*.json
│   ├── mcp_documents/
│   │   └── session_*.json
│   └── rag_audit/
│       └── session_*.json
└── tests/
    ├── integration_test.json
    └── end_to_end_test.json
```

### D. Datasets RAG - Guide d'Utilisation

| Dataset | Usage | Rétention | Exemples |
|---------|-------|-----------|----------|
| `agent_core` | Identité, règles permanentes, structure PC | Permanent | Capacités agent, règles comportement, config système |
| `context_flow` | Résumés conversations, flux contexte | 90 jours | Résumé session précédente, contexte projet actif |
| `agent_memory` | Feedbacks, leçons, apprentissages | Permanent | "User préfère format JSON", "Éviter lib X" |
| `projects` | Code, docs analytiques, travail en cours | 180 jours | Documentation code, architecture, specs |
| `scratchpad` | Données temporaires, tests | 7 jours | Notes temporaires, résultats tests, brouillons |

### E. Métriques de Monitoring Recommandées

```python
# Prometheus metrics
rag_documents_total = Counter('rag_documents_total', 'Total documents', ['dataset'])
rag_chunks_total = Counter('rag_chunks_total', 'Total chunks', ['dataset'])
rag_query_duration_seconds = Histogram('rag_query_duration_seconds', 'Query duration')
rag_query_results = Histogram('rag_query_results', 'Number of results returned')

memory_sessions_total = Counter('memory_sessions_total', 'Total sessions')
memory_messages_total = Counter('memory_messages_total', 'Total messages', ['role'])
memory_search_duration_seconds = Histogram('memory_search_duration_seconds', 'Search duration')

timeline_events_total = Counter('timeline_events_total', 'Total events', ['event_type', 'modality'])
```

---

**Fin du Rapport d'Audit**

*Rapport généré le 21 Novembre 2025*
*Version: 1.0*
*Auditeur: Claude Agent*
