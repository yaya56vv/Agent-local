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
        Initialize the orchestrator with Gemini LLM by default.
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
            
            return parsed_result
        
        except Exception as e:
            return {
                "intention": "error",
                "confidence": 0.0,
                "steps": [],
                "response": f"Orchestration error: {str(e)}",
                "error": str(e)
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
        
        return detected if detected else ["general"]

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

Available modules:
- SEARCH: Web search and information retrieval
- VISION: Screenshot analysis and visual understanding
- CODE: Code generation, debugging, and execution
- MEMORY: Session memory and context retrieval
- FILE: File operations (read, write, edit)

Your task:
1. Determine the PRIMARY intention (search, vision, code, memory, file, or general)
2. Assign a confidence score (0.0 to 1.0)
3. Create a step-by-step action plan
4. Provide a helpful response

Respond in this EXACT JSON format:
```json
{{
  "intention": "primary_intent_name",
  "confidence": 0.95,
  "steps": [
    {{"action": "module_name", "description": "what to do", "priority": 1}},
    {{"action": "module_name", "description": "what to do", "priority": 2}}
  ],
  "response": "Clear explanation of what will be done and why"
}}
```

Be precise and actionable. If the request is simple, keep steps minimal."""

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
                "intention": parsed.get("intention", detected_intents[0] if detected_intents else "general"),
                "confidence": float(parsed.get("confidence", 0.7)),
                "steps": parsed.get("steps", []),
                "response": parsed.get("response", response)
            }
            
            # Ensure steps have required fields
            for step in result["steps"]:
                if "action" not in step:
                    step["action"] = "unknown"
                if "description" not in step:
                    step["description"] = "No description"
                if "priority" not in step:
                    step["priority"] = 1
            
            return result
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: create structured response from raw text
            return {
                "intention": detected_intents[0] if detected_intents else "general",
                "confidence": 0.6,
                "steps": [
                    {
                        "action": detected_intents[0] if detected_intents else "general",
                        "description": "Process user request",
                        "priority": 1
                    }
                ],
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
    
    async def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the orchestrated plan by calling appropriate modules.
        
        Args:
            plan: The orchestration plan from think()
            
        Returns:
            dict: Execution results
        """
        intention = plan.get("intention", "general")
        steps = plan.get("steps", [])
        
        results = []
        
        try:
            # Execute based on intention
            if intention == "search":
                # Extract search query from the plan
                query = self._extract_search_query(plan)
                if query:
                    search_result = await self.web_search.search_with_summary(query, max_results=5)
                    results.append({
                        "module": "search",
                        "status": "success",
                        "data": search_result
                    })
                else:
                    results.append({
                        "module": "search",
                        "status": "error",
                        "error": "Could not extract search query from plan"
                    })
            
            # Other modules will be implemented here
            elif intention == "vision":
                results.append({
                    "module": "vision",
                    "status": "not_implemented",
                    "message": "Vision module to be implemented"
                })
            
            elif intention == "code":
                # Extract code and action type from plan
                code_info = self._extract_code_info(plan)
                
                if code_info.get("action") == "execute":
                    code_result = await self.code_executor.execute(code_info.get("code", ""))
                    results.append({
                        "module": "code",
                        "status": "success",
                        "action": "execute",
                        "data": code_result
                    })
                elif code_info.get("action") == "analyze":
                    code_result = await self.code_executor.analyze(code_info.get("code", ""))
                    results.append({
                        "module": "code",
                        "status": "success",
                        "action": "analyze",
                        "data": code_result
                    })
                elif code_info.get("action") == "optimize":
                    code_result = await self.code_executor.optimize(code_info.get("code", ""))
                    results.append({
                        "module": "code",
                        "status": "success",
                        "action": "optimize",
                        "data": code_result
                    })
                elif code_info.get("action") == "debug":
                    code_result = await self.code_executor.debug(
                        code_info.get("code", ""),
                        code_info.get("error", "")
                    )
                    results.append({
                        "module": "code",
                        "status": "success",
                        "action": "debug",
                        "data": code_result
                    })
                else:
                    results.append({
                        "module": "code",
                        "status": "error",
                        "error": "Could not determine code action from plan"
                    })
            
            elif intention == "memory":
                # Extract session_id and operation from the plan
                session_info = self._extract_memory_info(plan)
                session_id = session_info.get("session_id", "default")
                operation = session_info.get("operation", "recall")
                
                if operation == "recall":
                    # Get context from memory
                    context = self.memory_manager.get_context(session_id, max_messages=10)
                    results.append({
                        "module": "memory",
                        "status": "success",
                        "operation": "recall",
                        "data": {
                            "session_id": session_id,
                            "context": context
                        }
                    })
                elif operation == "search":
                    # Search in memory
                    query = session_info.get("query", "")
                    search_results = self.memory_manager.search(query, session_id)
                    results.append({
                        "module": "memory",
                        "status": "success",
                        "operation": "search",
                        "data": {
                            "query": query,
                            "results": search_results
                        }
                    })
                else:
                    # Get summary
                    summary = self.memory_manager.get_summary(session_id)
                    results.append({
                        "module": "memory",
                        "status": "success",
                        "operation": "summary",
                        "data": summary
                    })
            
            elif intention == "file":
                # Extract file operation info from the plan
                file_info = self._extract_file_info(plan)
                operation = file_info.get("operation", "read")
                file_path = file_info.get("file_path", "")
                
                if operation == "read":
                    file_result = self.file_manager.read(file_path)
                    results.append({
                        "module": "file",
                        "status": "success",
                        "operation": "read",
                        "data": file_result
                    })
                elif operation == "write":
                    content = file_info.get("content", "")
                    file_result = self.file_manager.write(file_path, content, allow=True)
                    results.append({
                        "module": "file",
                        "status": "success",
                        "operation": "write",
                        "data": file_result
                    })
                elif operation == "list":
                    file_result = self.file_manager.list_dir(file_path or ".")
                    results.append({
                        "module": "file",
                        "status": "success",
                        "operation": "list",
                        "data": file_result
                    })
                elif operation == "delete":
                    file_result = self.file_manager.delete(file_path, allow=True)
                    results.append({
                        "module": "file",
                        "status": "success",
                        "operation": "delete",
                        "data": file_result
                    })
                else:
                    results.append({
                        "module": "file",
                        "status": "error",
                        "error": "Unknown file operation"
                    })
            
            else:
                results.append({
                    "module": "general",
                    "status": "completed",
                    "message": "General conversation handled by orchestrator"
                })
            
            return {
                "status": "executed",
                "intention": intention,
                "results": results,
                "plan": plan
            }
        
        except Exception as e:
            return {
                "status": "error",
                "intention": intention,
                "error": str(e),
                "plan": plan
            }
    
    def _extract_code_info(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract code and action type from the orchestration plan.
        
        Args:
            plan: The orchestration plan
            
        Returns:
            dict: Code info with 'code', 'action', and optional 'error'
        """
        code_info = {"code": "", "action": "analyze"}
        
        # Try to get from steps
        for step in plan.get("steps", []):
            desc = step.get("description", "").lower()
            
            # Determine action type
            if "execute" in desc or "run" in desc or "exécute" in desc:
                code_info["action"] = "execute"
            elif "optimize" in desc or "optimise" in desc or "improve" in desc:
                code_info["action"] = "optimize"
            elif "debug" in desc or "fix" in desc or "répare" in desc or "corrige" in desc:
                code_info["action"] = "debug"
            elif "analyze" in desc or "analyse" in desc or "review" in desc:
                code_info["action"] = "analyze"
            
            # Try to extract code from description
            if "```" in step.get("description", ""):
                code_start = step["description"].find("```") + 3
                # Skip language identifier if present
                if step["description"][code_start:code_start+10].strip().split()[0] in ["python", "py", "javascript", "js"]:
                    code_start = step["description"].find("\n", code_start) + 1
                code_end = step["description"].find("```", code_start)
                if code_end > code_start:
                    code_info["code"] = step["description"][code_start:code_end].strip()
        
        # Fallback: try to get code from response
        response = plan.get("response", "")
        if not code_info["code"] and "```" in response:
            code_start = response.find("```") + 3
            if response[code_start:code_start+10].strip().split()[0] in ["python", "py"]:
                code_start = response.find("\n", code_start) + 1
            code_end = response.find("```", code_start)
            if code_end > code_start:
                code_info["code"] = response[code_start:code_end].strip()
        
        return code_info
    
    def _extract_search_query(self, plan: Dict[str, Any]) -> Optional[str]:
        """
        Extract search query from the orchestration plan.
        
        Args:
            plan: The orchestration plan
            
        Returns:
            str: Extracted search query or None
        """
        # Try to get from steps
        for step in plan.get("steps", []):
            if step.get("action") == "search":
                desc = step.get("description", "")
                # Try to extract query from description
                if "search for" in desc.lower():
                    query = desc.lower().split("search for")[-1].strip()
                    return query
                elif "query:" in desc.lower():
                    query = desc.lower().split("query:")[-1].strip()
                    return query
                else:
                    return desc
        
        # Fallback: use the response text
        response = plan.get("response", "")
        if response:
            return response[:100]  # Use first 100 chars as query
        
        return None
    
    def _extract_memory_info(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract memory operation info from the orchestration plan.
        
        Args:
            plan: The orchestration plan
            
        Returns:
            dict: Memory operation information
        """
        info = {
            "session_id": "default",
            "operation": "recall",
            "query": ""
        }
        
        # Try to get from steps
        for step in plan.get("steps", []):
            if step.get("action") == "memory":
                desc = step.get("description", "").lower()
                
                # Determine operation type
                if "search" in desc or "find" in desc:
                    info["operation"] = "search"
                    # Extract query
                    if "for" in desc:
                        info["query"] = desc.split("for")[-1].strip()
                elif "summary" in desc or "overview" in desc:
                    info["operation"] = "summary"
                else:
                    info["operation"] = "recall"
                
                # Try to extract session_id if mentioned
                if "session" in desc:
                    parts = desc.split("session")
                    if len(parts) > 1:
                        session_part = parts[1].strip().split()[0]
                        if session_part:
                            info["session_id"] = session_part
        
        return info
    
    def _extract_file_info(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract file operation info from the orchestration plan.
        
        Args:
            plan: The orchestration plan
            
        Returns:
            dict: File operation information
        """
        info = {
            "operation": "read",
            "file_path": "",
            "content": ""
        }
        
        # Try to get from steps
        for step in plan.get("steps", []):
            if step.get("action") == "file":
                desc = step.get("description", "").lower()
                
                # Determine operation type
                if "write" in desc or "create" in desc or "save" in desc:
                    info["operation"] = "write"
                elif "delete" in desc or "remove" in desc:
                    info["operation"] = "delete"
                elif "list" in desc or "show" in desc:
                    info["operation"] = "list"
                else:
                    info["operation"] = "read"
                
                # Try to extract file path
                if "file:" in desc:
                    info["file_path"] = desc.split("file:")[-1].strip().split()[0]
                elif "path:" in desc:
                    info["file_path"] = desc.split("path:")[-1].strip().split()[0]
                
                # Try to extract content for write operations
                if info["operation"] == "write" and "content:" in desc:
                    info["content"] = desc.split("content:")[-1].strip()
        
        return info

    def get_capabilities(self) -> Dict[str, List[str]]:
        """
        Return the orchestrator's current capabilities.
        
        Returns:
            dict: Available modules and their capabilities
        """
        return {
            "search": ["web_search", "information_retrieval", "fact_checking"],
            "vision": ["screenshot_analysis", "image_understanding", "visual_qa"],
            "code": ["code_generation", "debugging", "refactoring", "execution"],
            "memory": ["context_retrieval", "session_history", "knowledge_storage"],
            "file": ["read_file", "write_file", "edit_file", "file_operations"],
            "general": ["conversation", "reasoning", "planning", "coordination"]
        }