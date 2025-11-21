# Dataset: RULES (Règles Essentielles Permanentes)

## 📋 Description

Ce dataset contient les **règles essentielles permanentes** de l'agent. Ces règles définissent :
- L'identité et la personnalité de l'agent
- Les comportements fondamentaux
- Les contraintes de sécurité
- Les protocoles de fonctionnement

## 🏛️ Caractéristiques

- **Persistence** : Permanente (jamais supprimée)
- **Modification** : Protégée (lecture seule)
- **Priorité** : CRITIQUE (toujours consultée en premier)
- **Accès** : Permanent et prioritaire
- **Validation** : Approuvée et figée

## 📁 Fichiers

### `agent_core_rules_hybride_v1.txt`
Document maître contenant les 10 sections fondamentales :

1. **IDENTITÉ** - Rôle, objectifs, style
2. **RÈGLES LINGUISTIQUES** - Langue, longueur, registres
3. **RÈGLES COMPORTEMENTALES** - Cohérence, continuité
4. **MÉMOIRE & RAG** - Structure, utilité
5. **RAISONNEMENT INTERNE** - Procédure en 7 étapes
6. **GESTION DES TÂCHES** - Découpage, validation
7. **CONTRAINTES & SÉCURITÉ** - Sources, refus
8. **PROTOCOLE GLOBAL** - Urgence, registres
9. **COMPORTEMENT ÉMOTIONNEL** - Stable, bienveillant
10. **CONTINUITÉ** - Mémoire, style, objectifs

## 🔍 Métadonnées

```json
{
  "type": "core_rule",
  "rule_version": "hybride_v1",
  "category": "identity|linguistics|behavior|memory|reasoning|tasks|security|protocol|emotional|continuity",
  "priority": "critical",
  "validation_status": "approved",
  "modification_allowed": false,
  "access_level": "always",
  "content_type": "behavioral_rule"
}
```

## 🚀 Utilisation

### Query Prioritaire
```python
# Les règles core sont TOUJOURS consultées en premier
results = await rag.query(
    dataset="rules",
    question=user_prompt,
    top_k=10,
    priority="critical"
)
```

### Intégration dans l'Orchestrator
```python
# Enrichir chaque prompt avec les règles core
enriched_prompt = f"""
RÈGLES CORE DE L'AGENT:
{core_rules_context}

DEMANDE UTILISATEUR:
{user_prompt}

Réponds en respectant TOUTES les règles core ci-dessus.
"""
```

## ⚠️ Règles de Gestion

- ✅ Lecture autorisée à tout moment
- ❌ Modification interdite (protégée)
- ✅ Consultation prioritaire dans les queries
- ❌ Suppression interdite
- ✅ Accessible à tous les modules

## 📊 Statistiques

- **Documents** : 1 (agent_core_rules_hybride_v1.txt)
- **Sections** : 10
- **Lignes** : 75
- **Taille** : ~2.5 KB
- **Version** : hybride_v1
- **Statut** : Approuvé et figé

## 🔄 Cycle de Vie

1. **Création** : Document initial approuvé
2. **Déploiement** : Chargé au démarrage de l'agent
3. **Utilisation** : Consulté à chaque requête
4. **Maintenance** : Lecture seule, aucune modification
5. **Évolution** : Nouvelle version = nouveau fichier (v2, v3, etc.)

## 📝 Notes

- Ce dataset est le **fondement immuable** de l'agent
- Les améliorations vont dans `agent_memory`, pas ici
- Les données temporaires vont dans `context_flow`, pas ici
- Les règles core sont **toujours prioritaires** sur les autres données
