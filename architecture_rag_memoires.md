# Architecture RAG avec Mémoires Séparées

## 🎯 Objectif
Créer une architecture RAG qui sépare :
- **Règles essentielles permanentes** (auto-amélioration de l'agent)
- **Flux contextuel** (conversation temporelle)
- **Mémoire interne** (évolution de l'agent)

## ✅ OUI, c'est techniquement possible !

L'architecture actuelle le permet grâce aux **datasets** et **métadonnées**.

## 📋 Architecture Proposée

### 1. Structure des Datasets

```python
DATASETS = {
    "agent_core": {
        "description": "Règles essentielles permanentes",
        "persistence": "permanente",
        "auto_update": False,
        "examples": [
            "personnalite_agent",
            "regles_ethiques", 
            "methodes_travail",
            "competences_noyau"
        ]
    },
    "context_flow": {
        "description": "Flux contextuel temporaire",
        "persistence": "session",
        "auto_update": True,
        "examples": [
            "historique_conversation",
            "documents_travailles",
            "taches_en_cours"
        ]
    },
    "agent_memory": {
        "description": "Mémoire d'auto-amélioration",
        "persistence": "long_terme",
        "auto_update": True,
        "examples": [
            "apprentissages",
            "feedbacks",
            "optimisations"
        ]
    }
}
```

### 2. Métadonnées pour Classification

```python
METADATA_SCHEMA = {
    "agent_core": {
        "type": "core_rule",
        "category": "personality|ethics|methods|skills",
        "priority": "high|medium|low",
        "version": "1.0",
        "last_updated": "2024-01-15",
        "validation_status": "approved|pending|deprecated"
    },
    "context_flow": {
        "type": "context_data",
        "session_id": "session_xxx",
        "timestamp": "2024-01-15T10:30:00Z",
        "source": "user|agent|system",
        "relevance_score": 0.85
    },
    "agent_memory": {
        "type": "learning_data", 
        "category": "improvement|feedback|optimization",
        "learning_value": "high|medium|low",
        "applicable_to": "core_rules|context_flow",
        "confidence": 0.92
    }
}
```

### 3. Implémentation du Système

#### A. Extension du RAGStore existant

```python
class EnhancedRAGStore(RAGStore):
    def __init__(self):
        super().__init__()
        self.memory_types = {
            "CORE_RULES": "agent_core",
            "CONTEXT_FLOW": "context_flow", 
            "AGENT_MEMORY": "agent_memory"
        }
    
    async def add_core_rule(self, rule_content: str, category: str, priority: str = "high"):
        """Ajouter une règle essentielle permanente"""
        metadata = {
            "type": "core_rule",
            "category": category,
            "priority": priority,
            "validation_status": "approved"
        }
        return await self.add_document(
            dataset=self.memory_types["CORE_RULES"],
            filename=f"core_rule_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=rule_content,
            metadata=metadata
        )
    
    async def add_context_data(self, content: str, session_id: str, source: str):
        """Ajouter des données au flux contextuel"""
        metadata = {
            "type": "context_data",
            "session_id": session_id,
            "source": source
        }
        return await self.add_document(
            dataset=self.memory_types["CONTEXT_FLOW"],
            filename=f"context_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=content,
            metadata=metadata
        )
    
    async def add_learning_data(self, learning_content: str, category: str, applicable_to: str):
        """Ajouter des données d'apprentissage"""
        metadata = {
            "type": "learning_data",
            "category": category,
            "applicable_to": applicable_to
        }
        return await self.add_document(
            dataset=self.memory_types["AGENT_MEMORY"],
            filename=f"learning_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=learning_content,
            metadata=metadata
        )
```

#### B. Système de Query Intelligent

```python
class IntelligentQuery:
    def __init__(self, rag_store):
        self.rag = rag_store
    
    async def query_with_priorities(self, question: str, context_session: str = None):
        """Query avec priorités : Core Rules > Agent Memory > Context Flow"""
        
        # 1. Toujours chercher dans les core rules d'abord
        core_results = await self.rag.query(
            dataset=self.rag.memory_types["CORE_RULES"],
            question=question,
            top_k=3
        )
        
        # 2. Chercher dans la mémoire d'agent
        memory_results = await self.rag.query(
            dataset=self.rag.memory_types["AGENT_MEMORY"],
            question=question,
            top_k=2
        )
        
        # 3. Chercher dans le flux contextuel (si session fournie)
        context_results = []
        if context_session:
            context_results = await self.rag.query(
                dataset=self.rag.memory_types["CONTEXT_FLOW"],
                question=question,
                top_k=5
            )
        
        return {
            "core_rules": core_results,
            "agent_memory": memory_results,
            "context_flow": context_results,
            "priority_order": ["core_rules", "agent_memory", "context_flow"]
        }
```

#### C. Moteur d'Auto-Amélioration

```python
class AgentSelfImprovement:
    def __init__(self, rag_store, memory_manager):
        self.rag = rag_store
        self.memory = memory_manager
        
    async def analyze_performance(self, session_id: str, conversation_history: list):
        """Analyser les performances pour améliorer l'agent"""
        
        # Analyser les patterns dans la conversation
        improvements = []
        
        for exchange in conversation_history:
            if "difficulty" in exchange.get("user_feedback", "").lower():
                # Pattern d'amélioration détecté
                improvement = {
                    "type": "skill_gap",
                    "content": f"Besoin d'amélioration: {exchange['user_feedback']}",
                    "applicable_to": "core_rules",
                    "confidence": 0.8
                }
                improvements.append(improvement)
        
        # Stocker les apprentissages
        for improvement in improvements:
            await self.rag.add_learning_data(
                learning_content=improvement["content"],
                category=improvement["type"],
                applicable_to=improvement["applicable_to"]
            )
        
        return improvements
    
    async def propose_core_rule_update(self, learning_data: list):
        """Proposer des mises à jour des règles core"""
        
        proposals = []
        for learning in learning_data:
            if learning["confidence"] > 0.9:
                proposal = {
                    "action": "create_or_update_core_rule",
                    "content": learning["content"],
                    "category": "improved_method",
                    "priority": "high"
                }
                proposals.append(proposal)
        
        return proposals
```

### 4. Intégration avec l'Orchestrator

```python
class OrchestratorWithMemory:
    def __init__(self):
        self.enhanced_rag = EnhancedRAGStore()
        self.memory_manager = MemoryManager()
        
    async def process_with_memory(self, user_prompt: str, session_id: str):
        """Traitement avec mémoire multicouche"""
        
        # 1. Ajouter au flux contextuel
        await self.enhanced_rag.add_context_data(
            content=user_prompt,
            session_id=session_id,
            source="user"
        )
        
        # 2. Query intelligente avec priorités
        context = await self.enhanced_rag.query_with_priorities(
            question=user_prompt,
            context_session=session_id
        )
        
        # 3. Générer réponse avec contexte enrichi
        prompt_with_context = self.build_context_prompt(user_prompt, context)
        
        # 4. Analyser les performances pour apprentissage
        # (En arrière-plan)
        asyncio.create_task(
            self.self_improvement.analyze_performance(session_id, [user_prompt])
        )
        
        return response
```

## 🚀 Avantages de cette Architecture

### ✅ Séparation Claire
- **Core Rules** : Règles permanentes, validées, stables
- **Context Flow** : Données temporaires, session-spécifiques  
- **Agent Memory** : Apprentissage et évolution

### ✅ Auto-Amélioration
- Analyse automatique des performances
- Détection des gaps de compétences
- Propositions d'amélioration des règles core

### ✅ Performance Optimisée
- Queries prioritaires (Core > Memory > Context)
- Métadonnées riches pour filtrage rapide
- Cache intelligent par type de données

### ✅ Contrôle Granulaire
- Validation des règles core avant activation
- Cycle de vie des données contextuelles
- Métriques de confiance pour les apprentissages

## 🛠️ Implémentation Étapes

1. **Phase 1** : Étendre RAGStore avec les nouveaux datasets
2. **Phase 2** : Créer IntelligentQuery avec priorités
3. **Phase 3** : Intégrer AgentSelfImprovement
4. **Phase 4** : Connecter avec l'Orchestrator existant
5. **Phase 5** : Interface frontend pour visualiser les 3 types de mémoire

Cette architecture permet une vraie **évolution intelligente de l'agent** tout en gardant les règles essentielles stables et bien séparées du flux contextuel.