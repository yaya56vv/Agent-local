# Dataset: AGENT_MEMORY (Mémoire d'Auto-Amélioration)

## 📋 Description

Ce dataset contient les **données d'apprentissage et d'auto-amélioration** de l'agent. Ces données incluent :
- Les apprentissages tirés des interactions
- Les feedbacks d'amélioration
- Les optimisations détectées automatiquement
- L'évolution intelligente de l'agent

## 🧠 Caractéristiques

- **Persistence** : Long-terme (conservée entre les sessions)
- **Modification** : Autorisée (apprentissage continu)
- **Priorité** : Haute (après rules, avant context_flow)
- **Accès** : Permanent et cross-session
- **Validation** : Basée sur la confiance et la pertinence

## 📁 Structure

```
agent_memory/
├── learnings/
│   ├── skill_improvements.txt
│   ├── pattern_detections.txt
│   └── optimization_proposals.txt
├── feedbacks/
│   ├── user_feedback.txt
│   └── performance_metrics.txt
├── optimizations/
│   ├── method_improvements.txt
│   └── efficiency_gains.txt
└── README.md
```

## 🔍 Métadonnées

```json
{
  "type": "learning_data",
  "category": "improvement|feedback|optimization",
  "learning_value": "high|medium|low",
  "applicable_to": "core_rules|context_flow|both",
  "confidence": 0.92,
  "source": "user_feedback|performance_analysis|pattern_detection",
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "pending|approved|implemented|rejected"
}
```

## 🚀 Utilisation

### Ajouter un apprentissage
```python
await rag.add_learning_data(
    learning_content="Amélioration détectée: ...",
    category="improvement",
    applicable_to="core_rules",
    confidence=0.85
)
```

### Query d'apprentissage
```python
results = await rag.query(
    dataset="agent_memory",
    question=user_prompt,
    top_k=5,
    filter={"confidence": ">0.8"}
)
```

### Analyser les performances
```python
improvements = await agent_self_improvement.analyze_performance(
    session_id=session_id,
    conversation_history=history
)
```

## 🔄 Cycle de Vie d'un Apprentissage

1. **Détection** : Pattern ou feedback détecté
2. **Analyse** : Évaluation de la pertinence
3. **Stockage** : Ajout à agent_memory avec confiance
4. **Révision** : Révision périodique des apprentissages
5. **Implémentation** : Intégration si confiance > seuil
6. **Validation** : Vérification de l'amélioration

## 📊 Catégories d'Apprentissage

### 1. Skill Improvements (Améliorations de Compétences)
```
Besoin d'amélioration: Mieux gérer les tâches complexes
Confiance: 0.85
Applicable à: core_rules (section 6)
```

### 2. Pattern Detections (Détections de Patterns)
```
Pattern détecté: Utilisateur préfère les réponses courtes
Confiance: 0.92
Applicable à: core_rules (section 2)
```

### 3. Optimization Proposals (Propositions d'Optimisation)
```
Optimisation proposée: Réduire le temps de réponse
Confiance: 0.78
Applicable à: context_flow
```

## ⚠️ Règles de Gestion

- ✅ Lecture/écriture autorisée
- ✅ Modification autorisée
- ✅ Suppression autorisée (avec archivage)
- ✅ Persistence long-terme
- ❌ Modification directe des core_rules (propositions seulement)

## 🎯 Seuils de Confiance

```python
CONFIDENCE_THRESHOLDS = {
    "high": 0.85,      # Implémentation recommandée
    "medium": 0.70,    # Révision nécessaire
    "low": 0.50,       # Observation seulement
    "reject": 0.30     # Rejet automatique
}
```

## 📈 Métriques de Suivi

```python
{
    "total_learnings": 150,
    "high_confidence": 45,
    "implemented": 12,
    "pending_review": 8,
    "rejected": 3,
    "average_confidence": 0.78,
    "improvement_rate": "8% par mois"
}
```

## 🔄 Nettoyage et Archivage

```python
# Archivage des apprentissages anciens
async def archive_old_learnings(days=90):
    await rag.archive_learning_data(
        dataset="agent_memory",
        older_than_days=days
    )
```

## 📝 Notes

- Ce dataset est le **moteur d'évolution** de l'agent
- Les apprentissages ne modifient JAMAIS les core_rules directement
- Les propositions d'amélioration sont stockées avec confiance
- Révision périodique recommandée (hebdomadaire)
- Archivage automatique des données anciennes (>90 jours)

## 🚀 Intégration avec l'Orchestrator

```python
class OrchestratorWithLearning:
    async def process_with_learning(self, prompt: str, session_id: str):
        # 1. Consulter les apprentissages pertinents
        learnings = await self.agent_memory.query_learnings(prompt)
        
        # 2. Enrichir le contexte
        enriched_context = self.apply_learnings(learnings)
        
        # 3. Traiter la requête
        response = await self.process(prompt, enriched_context)
        
        # 4. Analyser les performances
        await self.analyze_and_learn(session_id, response)
        
        return response
```
