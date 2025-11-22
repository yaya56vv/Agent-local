"""
MCP Planner - Planification multi-étapes avec sélection de LLM
Choisit: quel outil (MCP), quel modèle (LLM), quel mode
"""
from typing import Dict, Any, List, Optional
import json
import re


class MCPPlanner:
    """Planificateur intelligent avec sélection de LLM et d'outils MCP"""
    
    def __init__(self, orchestrator):
        """
        Initialise le planificateur
        
        Args:
            orchestrator: Instance de l'orchestrateur avec tous les clients
        """
        self.orchestrator = orchestrator
    
    async def plan(self, user_message: str, session_id: str = "default") -> List[Dict[str, Any]]:
        """
        Génère un plan multi-étapes avec sélection de LLM
        
        Args:
            user_message: Message utilisateur
            session_id: ID de session
            
        Returns:
            Liste d'étapes avec tool, action, args, preferred_llm
        """
        # 1. Construire le super-contexte
        super_context = await self.orchestrator.context_builder.build_super_context(
            user_message, session_id
        )
        
        # 2. Générer le plan via LLM
        plan = await self._llm_generate_plan(
            user_message=user_message,
            super_context=super_context
        )
        
        return plan
    
    async def _llm_generate_plan(
        self,
        user_message: str,
        super_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Utilise un LLM pour générer un plan structuré
        
        Args:
            user_message: Message utilisateur
            super_context: Super-contexte agrégé
            
        Returns:
            Plan structuré avec étapes
        """
        # Construire le prompt de planification
        planning_prompt = self._build_planning_prompt(user_message, super_context)
        
        # Utiliser le LLM de raisonnement pour la planification
        try:
            llm = self.orchestrator.llm_reasoning
            
            messages = [{"role": "user", "content": planning_prompt}]
            response = llm.ask(messages)
            
            # Parser la réponse
            plan = self._parse_plan_response(response)
            
            return plan
            
        except Exception as e:
            # Plan de secours en cas d'erreur
            return [{
                "tool": "llm",
                "action": "generate",
                "args": {"prompt": user_message},
                "preferred_llm": "reasoning",
                "error": str(e)
            }]
    
    def _build_planning_prompt(
        self,
        user_message: str,
        super_context: Dict[str, Any]
    ) -> str:
        """
        Construit le prompt de planification avec contexte
        
        Args:
            user_message: Message utilisateur
            super_context: Super-contexte
            
        Returns:
            Prompt formaté
        """
        # Extraire les informations clés du contexte
        context_summary = self._summarize_context(super_context)
        
        return f"""You are an advanced AI planner. Generate a structured multi-step execution plan.

User Request: "{user_message}"

Available Context:
{context_summary}

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

Available LLM Models:
- reasoning: Best for planning, analysis, decision-making
- coding: Best for code generation, debugging, technical tasks
- vision: Best for image analysis, visual understanding

Your task:
1. Analyze the user request and available context
2. Break down the task into sequential steps
3. For each step, specify:
   - tool: Which MCP tool to use
   - action: Which action to call
   - args: Arguments for the action
   - preferred_llm: Which LLM model is best (reasoning/coding/vision)

Respond in this EXACT JSON format:
```json
{{
  "steps": [
    {{
      "tool": "search",
      "action": "search_web",
      "args": {{"query": "Python FastAPI"}},
      "preferred_llm": "reasoning"
    }},
    {{
      "tool": "llm",
      "action": "generate",
      "args": {{"prompt": "Summarize the search results"}},
      "preferred_llm": "reasoning"
    }}
  ],
  "reasoning": "Explanation of the plan"
}}
```

Be precise and actionable. Use exact tool and action names from the list above."""
    
    def _summarize_context(self, super_context: Dict[str, Any]) -> str:
        """
        Résume le super-contexte pour le prompt
        
        Args:
            super_context: Super-contexte complet
            
        Returns:
            Résumé textuel
        """
        summary_parts = []
        
        # Mémoire
        memory = super_context.get("memory", {})
        if memory.get("status") == "success":
            recent = memory.get("recent_context", "")
            if recent:
                summary_parts.append(f"Recent Conversation:\n{recent[:500]}...")
        
        # RAG
        rag = super_context.get("rag_docs", {})
        if rag.get("status") == "success":
            datasets = rag.get("datasets", {})
            if datasets:
                summary_parts.append(f"Knowledge Base: {len(datasets)} datasets with {rag.get('total_results', 0)} relevant docs")
        
        # Vision
        vision = super_context.get("vision", {})
        if vision.get("status") == "success":
            summary_parts.append("Vision: Active context available")
        
        # Audio
        audio = super_context.get("audio", {})
        if audio.get("status") == "success":
            summary_parts.append("Audio: Context available")
        
        # System
        system = super_context.get("system_state", {})
        if system.get("status") == "success":
            summary_parts.append("System: State snapshot available")
        
        return "\n".join(summary_parts) if summary_parts else "No additional context available"
    
    def _parse_plan_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse la réponse LLM en plan structuré
        
        Args:
            response: Réponse brute du LLM
            
        Returns:
            Liste d'étapes
        """
        try:
            # Extraire le JSON de la réponse
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                # Chercher n'importe quel objet JSON
                json_match = re.search(r'\{.*"steps".*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                else:
                    raise ValueError("No JSON found in response")
            
            steps = parsed.get("steps", [])
            
            # Valider et normaliser les étapes
            validated_steps = []
            for step in steps:
                if "tool" in step and "action" in step:
                    validated_step = {
                        "tool": step["tool"],
                        "action": step["action"],
                        "args": step.get("args", {}),
                        "preferred_llm": step.get("preferred_llm", "reasoning")
                    }
                    validated_steps.append(validated_step)
            
            return validated_steps if validated_steps else self._fallback_plan()
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Plan de secours
            return self._fallback_plan()
    
    def _fallback_plan(self) -> List[Dict[str, Any]]:
        """
        Plan de secours simple
        
        Returns:
            Plan minimal
        """
        return [{
            "tool": "llm",
            "action": "generate",
            "args": {},
            "preferred_llm": "reasoning"
        }]
    
    def select_llm_for_step(self, step: Dict[str, Any]) -> str:
        """
        Sélectionne le meilleur LLM pour une étape
        
        Args:
            step: Étape du plan
            
        Returns:
            Nom du modèle LLM
        """
        preferred = step.get("preferred_llm", "reasoning")
        tool = step.get("tool", "")
        action = step.get("action", "")
        
        # Règles de sélection
        if tool == "vision" or "image" in action or "screenshot" in action:
            return "vision"
        elif tool in ["files", "system"] and "code" in str(step.get("args", {})).lower():
            return "coding"
        elif preferred in ["coding", "vision", "reasoning"]:
            return preferred
        else:
            return "reasoning"
