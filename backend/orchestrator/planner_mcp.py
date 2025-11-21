"""
Planner MCP - Génère des plans multi-étapes via LLM local
"""
from typing import Dict, Any, List
import json
import re
from backend.orchestrator.clients.local_llm_client import LocalLlmClient


class PlannerMCP:
    """Génère des plans d'action structurés via LLM local"""
    
    def __init__(self, local_llm_client: LocalLlmClient):
        self.llm = local_llm_client
    
    async def create_plan(
        self,
        prompt: str,
        context: Dict[str, Any],
        detected_intents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Crée un plan d'action structuré
        
        Args:
            prompt: Requête utilisateur
            context: Contexte global du context_builder
            detected_intents: Intentions pré-détectées
            
        Returns:
            Plan structuré avec steps
        """
        # Construire le prompt de planification
        planning_prompt = self._build_planning_prompt(prompt, context, detected_intents)
        
        try:
            # Appeler LLM local
            response = await self.llm.generate(planning_prompt, max_tokens=1000)
            
            # Parser la réponse
            plan = self._parse_plan(response.get("text", ""), detected_intents)
            
            return plan
            
        except Exception as e:
            return {
                "intention": detected_intents[0] if detected_intents else "fallback",
                "confidence": 0.5,
                "steps": [],
                "response": f"Planning error: {str(e)}",
                "error": str(e)
            }
    
    def _build_planning_prompt(
        self,
        prompt: str,
        context: Dict[str, Any],
        detected_intents: List[str]
    ) -> str:
        """Construit le prompt de planification"""
        
        context_summary = context.get("summary", "No context")
        intents_str = ", ".join(detected_intents) if detected_intents else "unknown"
        
        return f"""You are an AI planner. Create a structured action plan for the user request.

USER REQUEST: {prompt}

DETECTED INTENTS: {intents_str}

CONTEXT:
{context_summary}

AVAILABLE ACTIONS:
- search_web(query, max_results)
- file_read(path), file_write(path, content), file_list(path)
- system_open(path), system_run(path, args)
- vision_analyze(image_bytes, prompt)
- rag_query(dataset, question, top_k)
- rag_add(dataset, filename, content)
- memory_recall(session_id, max_messages)
- mouse_move(x, y), mouse_click(x, y, button)
- keyboard_type(text), keyboard_press(keys)

RESPOND IN THIS JSON FORMAT:
{{
  "intention": "primary_intent",
  "confidence": 0.95,
  "steps": [
    {{"action": "action_name", "param1": "value1", "param2": "value2"}}
  ],
  "response": "Clear explanation"
}}

Be precise and actionable."""
    
    def _parse_plan(self, response: str, detected_intents: List[str]) -> Dict[str, Any]:
        """Parse la réponse LLM en plan structuré"""
        try:
            # Extraire JSON
            json_match = re.search(r'\{.*"intention".*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found")
            
            return {
                "intention": parsed.get("intention", detected_intents[0] if detected_intents else "fallback"),
                "confidence": float(parsed.get("confidence", 0.7)),
                "steps": parsed.get("steps", []),
                "response": parsed.get("response", response)
            }
            
        except Exception:
            return {
                "intention": detected_intents[0] if detected_intents else "fallback",
                "confidence": 0.6,
                "steps": [],
                "response": response
            }