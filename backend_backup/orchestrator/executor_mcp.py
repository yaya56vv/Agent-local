"""
MCP Executor - Exécute les plans avec tous les outils MCP
Supporte: audio, vision, documents, RAG, memory, files, system, control, search, LLM
"""
from typing import Dict, Any, List, Optional


class MCPExecutor:
    """Exécuteur de plans MCP avec support complet de tous les outils"""
    
    def __init__(self, orchestrator):
        """
        Initialise l'exécuteur
        
        Args:
            orchestrator: Instance de l'orchestrateur avec tous les clients
        """
        self.orchestrator = orchestrator
    
    async def execute_plan(
        self,
        plan: List[Dict[str, Any]],
        session_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Exécute un plan complet étape par étape
        
        Args:
            plan: Liste d'étapes à exécuter
            session_id: ID de session
            
        Returns:
            Liste des résultats d'exécution
        """
        results = []
        
        for i, step in enumerate(plan):
            # Exécuter l'étape
            result = await self.execute_action(step)
            results.append(result)
            
            # Ajouter à la timeline
            await self.orchestrator.timeline.add(
                event_type="execution",
                data={
                    "step_number": i + 1,
                    "total_steps": len(plan),
                    "step": step,
                    "result": result
                },
                session_id=session_id
            )
            
            # Si erreur critique, arrêter l'exécution
            if result.get("status") == "error" and result.get("critical", False):
                break
        
        return results
    
    async def execute_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une action unique
        
        Args:
            step: Étape avec tool, action, args
            
        Returns:
            Résultat de l'exécution
        """
        tool = step.get("tool", "")
        action = step.get("action", "")
        args = step.get("args", {})
        
        try:
            # Récupérer le client approprié
            client = self._tool_to_client(tool)
            
            # Récupérer la méthode
            if not hasattr(client, action):
                return {
                    "status": "error",
                    "error": f"Action '{action}' not found on tool '{tool}'",
                    "tool": tool,
                    "action": action
                }
            
            method = getattr(client, action)
            
            # Exécuter l'action
            result = await method(**args)
            
            return {
                "status": "success",
                "tool": tool,
                "action": action,
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "tool": tool,
                "action": action,
                "critical": self._is_critical_error(e)
            }
    
    def _tool_to_client(self, tool: str):
        """
        Mappe un nom d'outil vers son client MCP
        
        Args:
            tool: Nom de l'outil
            
        Returns:
            Instance du client
            
        Raises:
            ValueError: Si l'outil n'existe pas
        """
        tool_map = {
            "files": self.orchestrator.files_client,
            "memory": self.orchestrator.memory_client,
            "rag": self.orchestrator.rag_client,
            "vision": self.orchestrator.vision_client,
            "search": self.orchestrator.search_client,
            "system": self.orchestrator.system_client,
            "control": self.orchestrator.control_client,
            "audio": self.orchestrator.audio_client,
            "documents": self.orchestrator.documents_client,
            "llm": self.orchestrator.local_llm_client
        }
        
        if tool not in tool_map:
            raise ValueError(f"Unknown tool: {tool}")
        
        return tool_map[tool]
    
    def _is_critical_error(self, error: Exception) -> bool:
        """
        Détermine si une erreur est critique
        
        Args:
            error: Exception levée
            
        Returns:
            True si l'erreur est critique
        """
        # Erreurs critiques qui doivent arrêter l'exécution
        critical_errors = [
            "ConnectionError",
            "TimeoutError",
            "PermissionError"
        ]
        
        error_type = type(error).__name__
        return error_type in critical_errors
    
    async def execute_with_retry(
        self,
        step: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Exécute une action avec retry automatique
        
        Args:
            step: Étape à exécuter
            max_retries: Nombre maximum de tentatives
            
        Returns:
            Résultat de l'exécution
        """
        last_error = None
        
        for attempt in range(max_retries):
            result = await self.execute_action(step)
            
            if result.get("status") == "success":
                return result
            
            last_error = result.get("error", "Unknown error")
            
            # Ne pas retry si erreur critique
            if result.get("critical", False):
                break
        
        return {
            "status": "error",
            "error": f"Failed after {max_retries} attempts: {last_error}",
            "tool": step.get("tool"),
            "action": step.get("action")
        }
    
    async def execute_parallel(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Exécute plusieurs actions en parallèle
        
        Args:
            steps: Liste d'étapes à exécuter en parallèle
            
        Returns:
            Liste des résultats
        """
        import asyncio
        
        tasks = [self.execute_action(step) for step in steps]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convertir les exceptions en résultats d'erreur
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "status": "error",
                    "error": str(result),
                    "tool": steps[i].get("tool"),
                    "action": steps[i].get("action")
                })
            else:
                formatted_results.append(result)
        
        return formatted_results
    
    def validate_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide une étape avant exécution
        
        Args:
            step: Étape à valider
            
        Returns:
            Résultat de validation avec status et errors
        """
        errors = []
        
        # Vérifier les champs requis
        if "tool" not in step:
            errors.append("Missing required field: tool")
        if "action" not in step:
            errors.append("Missing required field: action")
        
        # Vérifier que l'outil existe
        tool = step.get("tool", "")
        try:
            self._tool_to_client(tool)
        except ValueError as e:
            errors.append(str(e))
        
        # Vérifier les arguments
        args = step.get("args", {})
        if not isinstance(args, dict):
            errors.append("args must be a dictionary")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def dry_run(
        self,
        plan: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simule l'exécution d'un plan sans l'exécuter réellement
        
        Args:
            plan: Plan à simuler
            
        Returns:
            Rapport de simulation
        """
        validations = []
        
        for i, step in enumerate(plan):
            validation = self.validate_step(step)
            validations.append({
                "step_number": i + 1,
                "step": step,
                "validation": validation
            })
        
        total_steps = len(plan)
        valid_steps = sum(1 for v in validations if v["validation"]["valid"])
        
        return {
            "total_steps": total_steps,
            "valid_steps": valid_steps,
            "invalid_steps": total_steps - valid_steps,
            "validations": validations,
            "can_execute": valid_steps == total_steps
        }
