# MCP Planner - Planificateur Multi-LLM et Multi-Outils

## Mission Accomplie ✅

Le module **MCP Planner** est operationnel et integre dans l'orchestrateur. Il genere des plans multi-etapes structures avec selection intelligente de LLM.

## Fichiers Crees/Verifies

### 1. Module Principal
- **`backend/orchestrator/planner_mcp.py`** ✅ (Deja existant et complet)
  - Classe `MCPPlanner` avec methode `plan()`
  - Generation de plans via LLM avec super-contexte
  - Selection intelligente de LLM pour chaque etape
  - Parsing robuste des reponses LLM

### 2. Integration
- **`backend/orchestrator/orchestrator.py`** ✅
  - Import a la ligne 32: `from backend.orchestrator.planner_mcp import MCPPlanner`
  - Initialisation a la ligne 75: `self.planner = MCPPlanner(self)`

### 3. Fichier de Test
- **`test_planner_mcp.py`** ✅
  - Tests complets du MCP Planner
  - Verification de l'integration
  - Tests de selection de LLM

## Architecture du MCP Planner

```
MCPPlanner
├── plan()                          # Point d'entree principal
│   ├── build_super_context()      # Via context_builder
│   └── _llm_generate_plan()       # Generation via LLM
│       ├── _build_planning_prompt()
│       ├── llm.ask()              # Appel LLM
│       └── _parse_plan_response()
├── select_llm_for_step()          # Selection de LLM
├── _summarize_context()           # Resume du contexte
└── _fallback_plan()               # Plan de secours
```

## Fonctionnalites

### 1. Generation de Plans Multi-Etapes

Le planner genere des plans structures avec:
- **tool**: Quel outil MCP utiliser (files, memory, rag, vision, search, system, control, audio, documents, llm)
- **action**: Quelle action appeler (read_file, search_web, analyze_image, etc.)
- **args**: Arguments pour l'action
- **preferred_llm**: Quel LLM utiliser (reasoning, coding, vision)

### 2. Utilisation du Super-Contexte

Le planner utilise le Context Builder pour obtenir:
- Memoire conversationnelle recente
- Documents RAG pertinents (core, projects, scratchpad, rules)
- Contexte vision actif
- Etat systeme
- Contexte audio
- Documents recents

### 3. Selection Intelligente de LLM

Regles de selection:
- **Vision**: Pour actions vision, image, screenshot
- **Coding**: Pour actions files/system avec code
- **Reasoning**: Pour tout le reste (par defaut)

### 4. Outils MCP Disponibles

```python
Available Tools (MCP):
- files: read_file, write_file, list_dir, delete_file
- memory: add_message, get_context, search
- rag: query, add_document, cleanup_memory
- vision: analyze_screenshot, analyze_image, detect_objects
- search: search_all, search_web, search_news
- system: snapshot, open_file, open_folder, run_program, list_processes, kill_process
- control: move_mouse, click_mouse, scroll, type, keypress
- audio: transcribe, text_to_speech, analyze
- documents: generate_document, fill_template
- llm: generate (for text generation tasks)
```

## Format du Plan

### Structure JSON Generee

```json
{
  "steps": [
    {
      "tool": "search",
      "action": "search_web",
      "args": {"query": "Python FastAPI"},
      "preferred_llm": "reasoning"
    },
    {
      "tool": "files",
      "action": "write_file",
      "args": {
        "path": "resume.txt",
        "content": "Summary of search results"
      },
      "preferred_llm": "coding"
    }
  ],
  "reasoning": "Explanation of the plan"
}
```

### Exemple de Plan Genere

Pour la requete: "Recherche des informations sur Python FastAPI et cree un fichier resume.txt"

```python
[
  {
    "tool": "search",
    "action": "search_web",
    "args": {"query": "Python FastAPI"},
    "preferred_llm": "reasoning"
  },
  {
    "tool": "llm",
    "action": "generate",
    "args": {"prompt": "Summarize the search results"},
    "preferred_llm": "reasoning"
  },
  {
    "tool": "files",
    "action": "write_file",
    "args": {
      "path": "resume.txt",
      "content": "$previous"
    },
    "preferred_llm": "coding"
  }
]
```

## Utilisation

### Exemple Simple

```python
from backend.orchestrator.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Generer un plan
plan = await orchestrator.planner.plan(
    user_message="Recherche Python FastAPI et cree un resume",
    session_id="user_123"
)

# Analyser le plan
for step in plan:
    print(f"Tool: {step['tool']}")
    print(f"Action: {step['action']}")
    print(f"Args: {step['args']}")
    print(f"LLM: {step['preferred_llm']}")
```

### Exemple avec Selection de LLM

```python
# Selectionner le meilleur LLM pour une etape
step = {
    "tool": "vision",
    "action": "analyze_screenshot",
    "args": {},
    "preferred_llm": "vision"
}

selected_llm = orchestrator.planner.select_llm_for_step(step)
print(f"LLM selectionne: {selected_llm}")  # Output: "vision"
```

## Prompt de Planification

Le planner utilise un prompt structure qui inclut:

1. **Requete utilisateur**: Message original
2. **Contexte disponible**: Resume du super-contexte
3. **Outils disponibles**: Liste complete des outils MCP
4. **Modeles LLM**: reasoning, coding, vision
5. **Instructions**: Format JSON exact attendu

### Exemple de Prompt

```
You are an advanced AI planner. Generate a structured multi-step execution plan.

User Request: "Recherche Python FastAPI et cree un resume"

Available Context:
Recent Conversation: ...
Knowledge Base: 4 datasets with 8 relevant docs
Vision: Active context available
System: State snapshot available

Available Tools (MCP):
- files: read_file, write_file, list_dir, delete_file
- memory: add_message, get_context, search
- rag: query, add_document, cleanup_memory
...

Available LLM Models:
- reasoning: Best for planning, analysis, decision-making
- coding: Best for code generation, debugging, technical tasks
- vision: Best for image analysis, visual understanding

Your task:
1. Analyze the user request and available context
2. Break down the task into sequential steps
3. For each step, specify: tool, action, args, preferred_llm

Respond in this EXACT JSON format:
{
  "steps": [...],
  "reasoning": "Explanation"
}
```

## Gestion des Erreurs

### Plan de Secours

Si le parsing echoue, le planner retourne un plan minimal:

```python
[{
    "tool": "llm",
    "action": "generate",
    "args": {},
    "preferred_llm": "reasoning"
}]
```

### Validation des Etapes

Chaque etape est validee pour s'assurer qu'elle contient:
- `tool` (requis)
- `action` (requis)
- `args` (optionnel, defaut: {})
- `preferred_llm` (optionnel, defaut: "reasoning")

## Tests

Pour tester le MCP Planner:

```bash
python test_planner_mcp.py
```

Le script de test verifie:
1. ✅ Generation de plans multi-etapes
2. ✅ Utilisation du super-contexte
3. ✅ Integration dans l'orchestrateur
4. ✅ Selection de LLM pour differentes etapes
5. ✅ Parsing robuste des reponses

## Performance

### Metriques Estimees
- **Temps de generation**: ~1-2s (avec appel LLM)
- **Taille du plan**: 1-10 etapes typiquement
- **Taux de reussite parsing**: >95% avec prompt structure

### Optimisations Implementees
1. **Resume de contexte**: Contexte condense pour economiser tokens
2. **Prompt structure**: Format JSON strict pour parsing fiable
3. **Fallback gracieux**: Plan minimal si parsing echoue
4. **Validation robuste**: Verification de chaque etape

## Integration avec Autres Composants

### Context Builder
```python
# Le planner utilise le context builder
super_context = await self.orchestrator.context_builder.build_super_context(
    user_message, session_id
)
```

### Executor MCP
```python
# Le plan genere peut etre execute par l'executor
plan = await orchestrator.planner.plan(user_message)
results = await orchestrator.executor.execute(plan)
```

### LLM Router
```python
# Selection automatique du meilleur LLM
llm_name = orchestrator.planner.select_llm_for_step(step)
llm_instance = orchestrator.pick_model(llm_name)
```

## Prochaines Etapes

### Ameliorations Possibles
1. **Cache de plans**: Mettre en cache les plans similaires
2. **Apprentissage**: Ameliorer la selection de LLM avec feedback
3. **Plans conditionnels**: Support de branches if/else
4. **Plans paralleles**: Execution parallele d'etapes independantes
5. **Validation pre-execution**: Verifier la faisabilite avant execution

### Integration Future
- Utiliser dans le **Cognitive Engine** pour planification avancee
- Integrer avec **Timeline** pour historique des plans
- Ajouter support de **plans adaptatifs** (modification en cours d'execution)

## Conclusion

✅ **Mission accomplie!** Le MCP Planner est operationnel et pret a etre utilise.

Le module genere avec succes des plans multi-etapes structures:
- Utilisation du super-contexte ✅
- Selection intelligente de LLM ✅
- Support de tous les outils MCP ✅
- Parsing robuste des reponses ✅
- Integration complete dans l'orchestrateur ✅

Le planner est maintenant disponible pour generer des plans d'execution intelligents qui seront executes par le **MCP Executor**.

---

**Date**: 2025-11-21
**Status**: ✅ COMPLET
**Fichiers verifies**: 2
**Tests**: ✅ REUSSIS