# RAG Datasets Architecture

## 🏗️ Vue d'ensemble

L'architecture RAG est organisée en **3 datasets séparés** pour gérer les différents types de mémoire de l'agent :

```
backend/rag/datasets/
├── rules/                    # Règles essentielles permanentes
│   ├── agent_core_rules_hybride_v1.txt
│   └── README.md
├── context_flow/             # Flux contextuel temporaire
│   └── README.md
├── agent_memory/             # Mémoire d'auto-amélioration
│   ├── learnings/
│   ├── feedbacks/
│   ├── optimizations/
│   └── README.md
└── README.md                 # Cette documentation
```

## 📊 Comparaison des Datasets

| Aspect | RULES | CONTEXT_FLOW | AGENT_MEMORY |
|--------|-------|--------------|--------------|
| **Type** | Règles essentielles | Données temporaires | Apprentissages |
| **Persistence** | Permanente | Session | Long-terme |
| **Modification** | Protégée (lecture seule) | Autorisée | Autorisée |
| **Priorité** | CRITIQUE (1ère) | Moyenne (3ème) | Haute (2ème) |
| **Accès** | Toujours | Session-spécifique | Cross-session |
| **Durée de vie** | Infinie | Fin de session | Indéfinie |
| **Validation** | Approuvée | Aucune | Basée sur confiance |
| **Nettoyage** | Jamais | Automatique | Archivage >90j |

## 🎯 Cas d'Usage

### RULES (Règles Essentielles)
```
✅ Définir l'identité de l'agent
✅ Établir les comportements fondamentaux
✅ Imposer les contraintes de sécurité
✅ Fixer les protocoles de fonctionnement
❌ Stocker des données temporaires
❌ Enregistrer des apprentissages
```

### CONTEXT_FLOW (Flux Contextuel)
```
✅ Historique de conversation
✅ Documents travaillés récemment
✅ Tâches en cours
✅ Données éphémères de session
❌ Données permanentes
❌ Règles fondamentales
```

### AGENT_MEMORY (Mémoire d'Apprentissage)
```
✅ Apprentissages détectés
✅ Feedbacks d'amélioration
✅ Optimisations proposées
✅ Évolution de l'agent
❌ Données temporaires
❌ Règles core (propositions seulement)
```

## 🔄 Flux de Données

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUÊTE UTILISATEUR                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  1. CONSULTER RULES (PRIORITAIRE)  │
        │  - Identité de l'agent             │
        │  - Comportements fondamentaux      │
        │  - Contraintes de sécurité         │
        └────────────────────┬───────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  2. CONSULTER AGENT_MEMORY         │
        │  - Apprentissages pertinents       │
        │  - Optimisations applicables       │
        │  - Feedbacks d'amélioration        │
        └────────────────────┬───────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  3. CONSULTER CONTEXT_FLOW         │
        │  - Historique de session           │
        │  - Documents récents               │
        │  - Tâches en cours                 │
        └────────────────────┬───────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  GÉNÉRER RÉPONSE ENRICHIE          │
        │  (Avec tous les contextes)         │
        └────────────────────┬───────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  ANALYSER & APPRENDRE              │
        │  - Détecter patterns               │
        │  - Évaluer performance             │
        │  - Stocker apprentissages          │
        └────────────────────┬───────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │  AJOUTER À CONTEXT_FLOW            │
        │  - Réponse générée                 │
        │  - Feedback utilisateur            │
        │  - Métadonnées de session          │
        └────────────────────────────────────┘
```

## 🚀 Implémentation

### Initialisation au Démarrage

```python
class RAGDatasetManager:
    def __init__(self):
        self.datasets = {
            "rules": {
                "path": "backend/rag/datasets/rules",
                "priority": 1,
                "persistence": "permanent",
                "modification": False
            },
            "agent_memory": {
                "path": "backend/rag/datasets/agent_memory",
                "priority": 2,
                "persistence": "long_term",
                "modification": True
            },
            "context_flow": {
                "path": "backend/rag/datasets/context_flow",
                "priority": 3,
                "persistence": "session",
                "modification": True
            }
        }
    
    async def initialize(self):
        """Initialiser tous les datasets"""
        for dataset_name, config in self.datasets.items():
            await self.load_dataset(dataset_name, config)
```

### Query Intelligente

```python
async def query_with_priorities(self, question: str, session_id: str = None):
    """Query avec priorités : Rules > Agent Memory > Context Flow"""
    
    results = {
        "rules": [],
        "agent_memory": [],
        "context_flow": []
    }
    
    # 1. Toujours consulter les rules en premier
    results["rules"] = await self.rag.query(
        dataset="rules",
        question=question,
        top_k=10
    )
    
    # 2. Consulter agent_memory
    results["agent_memory"] = await self.rag.query(
        dataset="agent_memory",
        question=question,
        top_k=5
    )
    
    # 3. Consulter context_flow si session fournie
    if session_id:
        results["context_flow"] = await self.rag.query(
            dataset="context_flow",
            question=question,
            session_id=session_id,
            top_k=5
        )
    
    return results
```

## 📋 Checklist de Déploiement

- [x] Créer structure de répertoires
- [x] Placer agent_core_rules_hybride_v1.txt dans `rules/`
- [x] Documenter chaque dataset
- [ ] Implémenter RAGDatasetManager
- [ ] Intégrer dans l'Orchestrator
- [ ] Tester les queries prioritaires
- [ ] Configurer le nettoyage automatique
- [ ] Mettre en place le monitoring

## 🔗 Références

- [`rules/README.md`](rules/README.md) - Règles essentielles
- [`context_flow/README.md`](context_flow/README.md) - Flux contextuel
- [`agent_memory/README.md`](agent_memory/README.md) - Mémoire d'apprentissage
- [`architecture_rag_memoires.md`](../../architecture_rag_memoires.md) - Architecture complète
- [`integration_core_rules_analyse.md`](../../integration_core_rules_analyse.md) - Analyse d'intégration

## 📝 Notes Importantes

1. **Priorité absolue des RULES** : Toujours consultées en premier
2. **Protection des RULES** : Lecture seule, jamais modifiées
3. **Apprentissage continu** : AGENT_MEMORY accumule les améliorations
4. **Nettoyage automatique** : CONTEXT_FLOW supprimé après session
5. **Séparation claire** : Chaque dataset a un rôle distinct et non-chevauchant
