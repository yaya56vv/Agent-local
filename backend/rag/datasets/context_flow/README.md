# Dataset: CONTEXT_FLOW (Flux Contextuel Temporaire)

## 📋 Description

Ce dataset contient les **données contextuelles temporaires** de chaque session. Ces données incluent :
- L'historique de conversation
- Les documents travaillés récemment
- Les tâches en cours
- Les données éphémères de session

## 🌊 Caractéristiques

- **Persistence** : Temporaire (session-spécifique)
- **Modification** : Autorisée (lecture/écriture)
- **Priorité** : Moyenne (après rules et agent_memory)
- **Accès** : Limité à la session active
- **Durée de vie** : Durée de la session + nettoyage automatique

## 📁 Structure

```
context_flow/
├── session_xxx_conversation.txt
├── session_xxx_documents.txt
├── session_xxx_tasks.txt
└── README.md
```

## 🔍 Métadonnées

```json
{
  "type": "context_data",
  "session_id": "session_xxx",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "user|agent|system",
  "relevance_score": 0.85,
  "expiry": "session_end"
}
```

## 🚀 Utilisation

### Ajouter des données contextuelles
```python
await rag.add_context_data(
    content="Utilisateur demande: ...",
    session_id=session_id,
    source="user"
)
```

### Query contextuelle
```python
results = await rag.query(
    dataset="context_flow",
    question=user_prompt,
    session_id=session_id,
    top_k=5
)
```

## ⚠️ Règles de Gestion

- ✅ Lecture/écriture autorisée
- ✅ Modification autorisée
- ✅ Suppression autorisée
- ✅ Nettoyage automatique après session
- ❌ Pas de persistence long-terme

## 🧹 Nettoyage Automatique

```python
# Nettoyage après fin de session
async def cleanup_session_context(session_id: str):
    await rag.delete_session_data(
        dataset="context_flow",
        session_id=session_id
    )
```

## 📊 Statistiques

- **Durée de vie** : Durée de la session
- **Taille moyenne** : 50-500 KB par session
- **Nombre de documents** : Variable (1-100+)
- **Accès** : Fréquent (à chaque requête)

## 🔄 Cycle de Vie

1. **Création** : Début de session
2. **Accumulation** : Ajout de données au fil de la conversation
3. **Utilisation** : Consulté pour le contexte immédiat
4. **Nettoyage** : Suppression à la fin de la session
5. **Archivage** : Optionnel (copie vers agent_memory si pertinent)

## 📝 Notes

- Ce dataset est **éphémère** et **session-spécifique**
- Les données importantes doivent être copiées vers `agent_memory`
- Pas de persistence automatique entre les sessions
- Optimisé pour la performance (accès rapide)
