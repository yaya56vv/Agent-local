import re
import json
from typing import Dict, List, Optional, Any
from backend.connectors.llm.gemini import GeminiLLM
from backend.connectors.search.web_search import WebSearch
from backend.connectors.code.code_executor import CodeExecutor
from backend.connectors.memory.memory_manager import MemoryManager
from backend.connectors.files.file_manager import FileManager
from backend.connectors.system.system_actions import SystemActions
from backend.rag.rag_store import RAGStore


class Orchestrator:
    """
    Advanced agentic orchestrator powered by Gemini 2.0 Flash.
    Analyzes user intent, creates action plans, and coordinates module execution.
    """

    def __init__(self):
        """
        Initialize the orchestrator with all module connectors.
        """
        # Initialize LLM (Gemini by default)
        self.llm = GeminiLLM()
        
        # Initialize module connectors
        self.web_search = WebSearch()
        self.code_executor = CodeExecutor()
        self.memory_manager = MemoryManager()
        self.file_manager = FileManager()
        self.system_actions = SystemActions()
        self.rag = RAGStore()
        
        # Intent patterns for quick detection
        self.intent_patterns = {
            "web_search": [
                r"search|find|look up|google|recherche|cherche",
                r"what is|who is|where is|when is|how to",
                r"latest|news|information about"
            ],
            "vision": [
                r"screenshot|capture|image|visual|voir|regarde",
                r"what do you see|analyze.*screen|check.*display"
            ],
            "code_execution": [
                r"write.*code|create.*function|implement|debug",
                r"fix.*bug|refactor|optimize.*code",
                r"generate.*script|build.*application",
                r"corrige.*code|répare.*code|fix.*code",
                r"exécute.*script|run.*code|execute.*code",
                r"analyse.*code|analyze.*code|review.*code",
                r"optimise|optimize|améliore.*code|improve.*code"
            ],
            "memory": [
                r"remember|recall|what did|previous|history",
                r"save.*information|store.*data|memorize",
                r"rappelle|souviens|historique|reprends.*conversation"
            ],
            "file_operation": [
                r"read.*file|write.*file|create.*file|edit.*file",
                r"open|save|delete.*file"
            ],
            "system_action": [
                r"open.*folder|open.*directory|launch.*program",
                r"list.*process|kill.*process|run.*program",
                r"system|process|application"
            ],
            "rag_query": [
                r"query.*rag|search.*documents|find.*in.*knowledge",
                r"what.*know.*about|retrieve.*from.*memory"
            ],
            "rag_add": [
                r"add.*to.*rag|store.*document|save.*to.*knowledge",
                r"remember.*this|add.*to.*memory"
            ],
            "conversation": [
                r"hello|hi|bonjour|salut|hey",
                r"thank|merci|thanks",
                r"how.*are.*you|comment.*vas"
            ]
        }
        
        # Action routing map
        self.ACTION_MAP = {
            "search_web": self._action_search_web,
            "code_execute": self._action_code_execute,
            "code_analyze": self._action_code_analyze,
            "code_explain": self._action_code_explain,
            "code_optimize": self._action_code_optimize,
            "code_debug": self._action_code_debug,
            "system_open": self._action_system_open,
            "system_run": self._action_system_run,
            "system_list_processes": self._action_system_list_processes,
            "system_kill": self._action_system_kill,
            "file_read": self._action_file_read,
            "file_write": self._action_file_write,
            "file_list": self._action_file_list,
            "file_delete": self._action_file_delete,
            "rag_query": self._action_rag_query,
            "rag_add": self._action_rag_add,
            "memory_recall": self._action_memory_recall,
            "memory_search": self._action_memory_search
        }

    async def think(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Main orchestration method. Analyzes the prompt and creates an action plan.
        
        Args:
            prompt: User's input text
            context: Optional additional context
            
        Returns:
            dict: Structured response with intention, confidence, steps, and response
        """
        # Quick intent detection
        detected_intents = self._detect_intents(prompt)
        
        # Build orchestration prompt
        orchestration_prompt = self._build_orchestration_prompt(prompt, detected_intents)
        
        # Add context if provided
        if context:
            orchestration_prompt = f"{orchestration_prompt}\n\nAdditional Context:\n{context}"
        
        # Get reasoning from LLM
        try:
            reasoning_response = self.llm.ask(orchestration_prompt)
            
            # Parse the response
            parsed_result = self._parse_reasoning_response(reasoning_response, detected_intents)
            
            # Store original prompt for memory management
            parsed_result["original_prompt"] = prompt
            
            return parsed_result
        
        except Exception as e:
            return {
                "intention": "error",
                "confidence": 0.0,
                "steps": [],
                "response": f"Orchestration error: {str(e)}",
                "error": str(e),
                "original_prompt": prompt
            }

    def _detect_intents(self, prompt: str) -> List[str]:
        """
        Quickly detect potential intents using regex patterns.
        
        Args:
            prompt: User's input text
            
        Returns:
            List of detected intent names
        """
        prompt_lower = prompt.lower()
        detected = []
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    detected.append(intent_name)
                    break
        
        return detected if detected else ["fallback"]

    def _build_orchestration_prompt(self, prompt: str, detected_intents: List[str]) -> str:
        """
        Build the orchestration prompt for Gemini.
        
        Args:
            prompt: User's input
            detected_intents: Pre-detected intents
            
        Returns:
            str: Formatted prompt for reasoning
        """
        return f"""You are an advanced AI orchestrator. Analyze the following user request and provide a structured action plan.

User Request: "{prompt}"

Pre-detected intents: {', '.join(detected_intents)}

Available modules and actions:
- WEB_SEARCH: search_web(query, max_results)
- CODE: code_execute(code), code_analyze(code), code_explain(code), code_optimize(code), code_debug(code, error)
- SYSTEM: system_open(path), system_run(path, args), system_list_processes(), system_kill(name)
- FILE: file_read(path), file_write(path, content), file_list(path), file_delete(path)
- RAG: rag_query(dataset, question, top_k), rag_add(dataset, filename, content, metadata)
- MEMORY: memory_recall(session_id, max_messages), memory_search(query, session_id)

Your task:
1. Determine the PRIMARY intention (web_search, code_execution, system_action, file_operation, rag_query, rag_add, conversation, or fallback)
2. Assign a confidence score (0.0 to 1.0)
3. Create a step-by-step action plan with specific action names and parameters
4. Provide a helpful response

Respond in this EXACT JSON format:
```json
{{
  "intention": "primary_intent_name",
  "confidence": 0.95,
  "steps": [
    {{"action": "search_web", "query": "Python FastAPI", "max_results": 5}},
    {{"action": "code_execute", "code": "print(2+2)"}}
  ],
  "response": "Clear explanation of what will be done and why"
}}
```

Be precise and actionable. Use exact action names from the list above."""

    def _parse_reasoning_response(self, response: str, detected_intents: List[str]) -> Dict[str, Any]:
        """
        Parse Gemini's reasoning response into structured format.
        
        Args:
            response: Raw response from Gemini
            detected_intents: Pre-detected intents for fallback
            
        Returns:
            dict: Structured orchestration result
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                # Try to find any JSON object
                json_match = re.search(r'\{.*"intention".*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                else:
                    raise ValueError("No JSON found in response")
            
            # Validate and normalize
            result = {
                "intention": parsed.get("intention", detected_intents[0] if detected_intents else "fallback"),
                "confidence": float(parsed.get("confidence", 0.7)),
                "steps": parsed.get("steps", []),
                "response": parsed.get("response", response)
            }
            
            # Ensure steps have required fields
            for step in result["steps"]:
                if "action" not in step:
                    step["action"] = "unknown"
            
            return result
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: create structured response from raw text
            return {
                "intention": detected_intents[0] if detected_intents else "fallback",
                "confidence": 0.6,
                "steps": [],
                "response": response,
                "parse_warning": f"Could not parse structured response: {str(e)}"
            }

    # ============================================================
    # ACTION METHODS - Individual module actions
    # ============================================================
    
    async def _action_search_web(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Execute web search action."""
        return await self.web_search.search(query, max_results)
    
    async def _action_code_execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """Execute code action."""
        return await self.code_executor.execute(code)
    
    async def _action_code_analyze(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """Analyze code action."""
        return await self.code_executor.analyze(code, language)
    
    async def _action_code_explain(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """Explain code action."""
        return await self.code_executor.explain(code, language)
    
    async def _action_code_optimize(self, code: str, **kwargs) -> Dict[str, Any]:
        """Optimize code action."""
        return await self.code_executor.optimize(code)
    
    async def _action_code_debug(self, code: str, error: str = "", **kwargs) -> Dict[str, Any]:
        """Debug code action."""
        return await self.code_executor.debug(code, error)
    
    async def _action_system_open(self, path: str, **kwargs) -> Dict[str, Any]:
        """Open file or folder action."""
        return self.system_actions.open_path(path)
    
    async def _action_system_run(self, path: str, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Run program action."""
        return self.system_actions.run_program(path, args)
    
    async def _action_system_list_processes(self, **kwargs) -> Dict[str, Any]:
        """List processes action."""
        return self.system_actions.list_processes()
    
    async def _action_system_kill(self, name: str, **kwargs) -> Dict[str, Any]:
        """Kill process action."""
        return self.system_actions.kill_process(name)
    
    async def _action_file_read(self, path: str, **kwargs) -> Dict[str, Any]:
        """Read file action."""
        return self.file_manager.read(path)
    
    async def _action_file_write(self, path: str, content: str, **kwargs) -> Dict[str, Any]:
        """Write file action."""
        return self.file_manager.write(path, content, allow=True)
    
    async def _action_file_list(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        """List directory action."""
        return self.file_manager.list_dir(path)
    
    async def _action_file_delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Delete file action."""
        return self.file_manager.delete(path, allow=True)
    
    async def _action_rag_query(self, dataset: str, question: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Query RAG action."""
        results = await self.rag.query(dataset, question, top_k)
        return {"status": "success", "results": results}
    
    async def _action_rag_add(self, dataset: str, filename: str, content: str, metadata: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Add document to RAG action."""
        doc_id = await self.rag.add_document(dataset, filename, content, metadata)
        return {"status": "success", "document_id": doc_id}
    
    async def _action_memory_recall(self, session_id: str = "default", max_messages: int = 10, **kwargs) -> Dict[str, Any]:
        """Recall memory action."""
        context = self.memory_manager.get_context(session_id, max_messages)
        return {"status": "success", "context": context}
    
    async def _action_memory_search(self, query: str, session_id: str = None, **kwargs) -> Dict[str, Any]:
        """Search memory action."""
        results = self.memory_manager.search(query, session_id)
        return {"status": "success", "results": results}

    # ============================================================
    # PLAN EXECUTION - Sequential multi-step execution
    # ============================================================
    
    async def execute_plan(self, plan: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        """
        Execute the orchestrated plan by calling appropriate modules sequentially.
        Supports multi-step execution with result passing between steps.
        
        Args:
            plan: The orchestration plan from think()
            session_id: Session ID for memory management
            
        Returns:
            dict: Execution results with memory updates
        """
        intention = plan.get("intention", "fallback")
        steps = plan.get("steps", [])
        prompt = plan.get("original_prompt", "")
        
        results = []
        previous_result = None
        memory_updated = False
        
        # Add prompt to memory
        if prompt:
            try:
                self.memory_manager.add(session_id, prompt, role="user")
                memory_updated = True
            except Exception as e:
                print(f"Warning: Could not add prompt to memory: {e}")
        
        try:
            # Execute steps sequentially
            for step in steps:
                action = step.get("action", "")
                
                # Get action handler
                if action in self.ACTION_MAP:
                    # Prepare parameters
                    params = {k: v for k, v in step.items() if k != "action"}
                    
                    # Inject previous result if needed
                    if "input" in params and params["input"] == "$previous" and previous_result:
                        params["data"] = previous_result
                    
                    # Execute action
                    try:
                        result = await self.ACTION_MAP[action](**params)
                        results.append({
                            "action": action,
                            "status": "success",
                            "data": result
                        })
                        previous_result = result
                    except Exception as e:
                        results.append({
                            "action": action,
                            "status": "error",
                            "error": str(e)
                        })
                else:
                    results.append({
                        "action": action,
                        "status": "error",
                        "error": f"Unknown action: {action}"
                    })
            
            # Generate final response
            final_response = plan.get("response", "Task completed")
            
            # Add response to memory
            if final_response:
                try:
                    self.memory_manager.add(session_id, final_response, role="assistant")
                    memory_updated = True
                except Exception as e:
                    print(f"Warning: Could not add response to memory: {e}")
            
            return {
                "status": "executed",
                "intention": intention,
                "confidence": plan.get("confidence", 0.0),
                "steps": steps,
                "response": final_response,
                "execution_results": results,
                "memory_updated": memory_updated
            }
        
        except Exception as e:
            return {
                "status": "error",
                "intention": intention,
                "error": str(e),
                "execution_results": results,
                "memory_updated": memory_updated
            }

    def get_capabilities(self) -> Dict[str, List[str]]:
        """
        Return the orchestrator's current capabilities.
        
        Returns:
            dict: Available modules and their capabilities
        """
        return {
            "web_search": ["search", "information_retrieval"],
            "code_execution": ["execute", "analyze", "explain", "optimize", "debug"],
            "system_action": ["open_path", "run_program", "list_processes", "kill_process"],
            "file_operation": ["read", "write", "list", "delete"],
            "rag": ["query", "add_document"],
            "memory": ["recall", "search"],
            "conversation": ["general_chat", "reasoning"]
        }