import re
import json
from typing import Dict, List, Optional, Any
from backend.connectors.llm.openrouter import OpenRouterLLM
# from backend.connectors.llm.llm_router import pick_model
from backend.connectors.search.web_search import WebSearch
# from backend.connectors.code.code_executor import CodeExecutor
from backend.connectors.memory.memory_manager import MemoryManager
from backend.connectors.files.file_manager import FileManager
from backend.connectors.system.system_actions import SystemActions
# from backend.connectors.control.input_controller import InputController  # DEPRECATED - Use MCP Control Client
from backend.connectors.vision.vision_analyzer import VisionAnalyzer
from backend.rag.rag_store import RAGStore
from backend.config.settings import settings
from backend.config.agent_registry import agent_registry
from backend.config.model_registry import model_registry

# Import MCP clients
from backend.orchestrator.clients.files_client import FilesClient
from backend.orchestrator.clients.memory_client import MemoryClient
from backend.orchestrator.clients.rag_client import RagClient
from backend.orchestrator.clients.vision_client import VisionClient
from backend.orchestrator.clients.search_client import SearchClient
from backend.orchestrator.clients.system_client import SystemClient
from backend.orchestrator.clients.control_client import ControlClient
from backend.orchestrator.clients.local_llm_client import LocalLlmClient
from backend.orchestrator.clients.audio_client import AudioClient
from backend.orchestrator.clients.documents_client import DocumentsClient
from backend.orchestrator.clients.glm_client import GLMClient

# Import Phase 5 components
from backend.orchestrator.context_builder import ContextBuilder
from backend.orchestrator.planner_mcp import MCPPlanner
from backend.orchestrator.executor_mcp import MCPExecutor
from backend.orchestrator.timeline import Timeline
from backend.orchestrator.cognitive_engine import CognitiveEngine


class Orchestrator:
    """
    Advanced agentic orchestrator powered by OpenRouter with Nemotron.
    Analyzes user intent, creates action plans, and coordinates module execution.
    """

    def __init__(self):
        """
        Initialize the orchestrator with all module connectors.
        NO HARDCODED MODELS - All models loaded from model_registry.
        """
        # Initialize three specialized LLM instances from model_registry
        orchestrator_config = model_registry.get_model("orchestrator")
        code_config = model_registry.get_model("code")
        vision_config = model_registry.get_model("vision")
        
        self.llm_reasoning = OpenRouterLLM(model=orchestrator_config["model"])
        self.llm_coding = OpenRouterLLM(model=code_config["model"])
        self.llm_vision = OpenRouterLLM(model=vision_config["model"])
        
        # Track current model info for logging
        self.current_model_info = None
        
        # Initialize MCP clients (Phase 1-4: Files, Memory, RAG, Vision, Search, System, Control, Local LLM)
        self.files_client = FilesClient(base_url="http://localhost:8001")
        self.memory_client = MemoryClient(base_url="http://localhost:8002")
        self.rag_client = RagClient(base_url="http://localhost:8003")
        self.vision_client = VisionClient(base_url="http://localhost:8004")
        self.search_client = SearchClient(base_url="http://localhost:8005")
        self.system_client = SystemClient(base_url="http://localhost:8006")
        self.control_client = ControlClient(base_url="http://localhost:8007")
        self.local_llm_client = LocalLlmClient(base_url="http://localhost:8008")
        self.audio_client = AudioClient(base_url="http://localhost:8010")
        self.documents_client = DocumentsClient(base_url="http://localhost:8009")

        # GLM Client - configured dynamically from model_registry
        glm_config = model_registry.get_model("glm_vision_expert")
        if glm_config and glm_config.get("enabled"):
            self.glm_client = GLMClient()  # Auto-configured from registry
        else:
            self.glm_client = None  # Disabled
        
        # Initialize Phase 5 components
        self.context_builder = ContextBuilder(self)
        self.planner = MCPPlanner(self)
        self.executor = MCPExecutor(self)
        self.timeline = Timeline()
        self.cognitive_engine = CognitiveEngine(self)
        
        # Initialize module connectors (legacy - will be migrated in phases)
        self.web_search = WebSearch()  # Keep for backward compatibility during migration
        # self.code_executor = CodeExecutor()
        self.memory_manager = MemoryManager()  # Keep for backward compatibility during migration
        self.file_manager = FileManager()  # Keep for backward compatibility during migration
        self.system_actions = SystemActions()  # Keep for backward compatibility during migration
        # self.input_controller = InputController()  # DEPRECATED - Use control_client instead
        self.vision_analyzer = VisionAnalyzer()  # Keep for backward compatibility during migration
        self.rag = RAGStore()  # Keep for backward compatibility during migration
        
        # Intent patterns for quick detection
        self.intent_patterns = {
            "web_search": [
                r"search|find|look up|google|recherche|cherche",
                r"what is|who is|where is|when is|how to",
                r"latest|news|information about"
            ],
            "vision_analysis": [
                r"analyse.*image|analyze.*image|regarde.*image",
                r"qu'est-ce.*capture|what.*screenshot|explique.*capture",
                r"que vois-tu|what do you see|check.*display",
                r"explique.*qui.*va.*pas.*écran|explain.*bug.*screen",
                r"screenshot|capture d'écran|screen capture"
            ],
            # "code_execution": [
            #     r"write.*code|create.*function|implement|debug",
            #     r"fix.*bug|refactor|optimize.*code",
            #     r"generate.*script|build.*application",
            #     r"corrige.*code|repare.*code|fix.*code",
            #     r"execute.*script|run.*code|execute.*code",
            #     r"analyse.*code|analyze.*code|review.*code",
            #     r"optimise|optimize|ameliore.*code|improve.*code"
            # ],
            "memory": [
                r"remember|recall|what did|previous|history",
                r"save.*information|store.*data|memorize",
                r"rappelle|souviens|historique|reprends.*conversation"
            ],
            "file_operation": [
                r"read.*file|write.*file|create.*file|edit.*file",
                r"open|save|delete.*file",
                r"move.*file|copy.*file|rename.*file",
                r"trier|ranger|classer|sort|organize"
            ],
            "input_control": [
                r"mouse|souris|click|clique|scroll|defile",
                r"keyboard|clavier|type|ecris|press|appuie",
                r"control.*mouse|control.*keyboard|prends.*controle"
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
            "memory_cleanup": [
                r"clean.*memory|forget.*project|delete.*dataset",
                r"oublie.*projet|nettoie.*memoire|supprime.*dataset"
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
            # "code_execute": self._action_code_execute,
            # "code_analyze": self._action_code_analyze,
            # "code_explain": self._action_code_explain,
            # "code_optimize": self._action_code_optimize,
            # "code_debug": self._action_code_debug,
            "system_open": self._action_system_open,
            "system_run": self._action_system_run,
            "system_list_processes": self._action_system_list_processes,
            "system_kill": self._action_system_kill,
            "file_read": self._action_file_read,
            "file_write": self._action_file_write,
            "file_list": self._action_file_list,
            "file_delete": self._action_file_delete,
            "file_move": self._action_file_move,
            "file_copy": self._action_file_copy,
            "vision_analyze": self._action_vision_analyze,
            "rag_query": self._action_rag_query,
            "rag_add": self._action_rag_add,
            "memory_cleanup": self._action_memory_cleanup,
            "memory_recall": self._action_memory_recall,
            "memory_search": self._action_memory_search,
            "mouse_move": self._action_mouse_move,
            "mouse_click": self._action_mouse_click,
            "mouse_scroll": self._action_mouse_scroll,
            "keyboard_type": self._action_keyboard_type,
            "keyboard_press": self._action_keyboard_press
        }
        
        # Sensitive actions that require confirmation
        self.SENSITIVE_ACTIONS = {
            "system_open", "system_run", "system_kill",
            "file_write", "file_delete", "file_move", "file_copy",
            # "code_execute", 
            "rag_add", "memory_cleanup",
            "mouse_move", "mouse_click", "mouse_scroll",
            "keyboard_type", "keyboard_press"
        }
        
        # Safe actions that can be executed directly
        self.SAFE_ACTIONS = {
            "search_web", "conversation",
            "rag_query", 
            # "code_analyze", "code_explain",
            "memory_recall", "memory_search", "file_read", "file_list"
        }

    def _log(self, message: str):
        """Log message if debug mode is enabled."""
        if settings.ORCHESTRATOR_DEBUG:
            print(message)
    
    def pick_model(self, task_type: str) -> OpenRouterLLM:
        """
        Pick the appropriate LLM based on task type.
        
        Args:
            task_type: Type of task (coding, vision, reasoning, etc.)
            
        Returns:
            OpenRouterLLM instance for the task
        """
        if task_type in ["code_execution", "code_analyze", "code_explain", "code_optimize", "code_debug", "coding"]:
            return self.llm_coding
        elif task_type in ["vision_analysis", "image_analysis", "screenshot_analysis", "vision"]:
            return self.llm_vision
        else:
            # Default to reasoning for everything else
            return self.llm_reasoning
    
    async def _inject_rag_context(self, messages: List[Dict[str, str]], prompt: str, session_id: str = "default") -> List[Dict[str, str]]:
        """
        Inject RAG context into messages before LLM call.
        Queries both conversation memory AND RAG store.
        
        Args:
            messages: Original messages list
            prompt: Current user prompt for semantic search
            session_id: Session ID for context retrieval
            
        Returns:
            Messages with RAG context injected
        """
        context_parts = []
        
        # 1. Conversation History (Short-term)
        try:
            # Get recent conversation history from memory via MCP
            context = await self.memory_client.get_context(session_id, max_messages=5)
            
            if context:
                context_parts.append(f"=== RECENT CONVERSATION ===\n{context}")
        except Exception as e:
            self._log(f"[ORCH] Memory injection warning: {str(e)}")

        # 2. RAG Context (Long-term / Knowledge)
        try:
            # Query multiple datasets based on priority
            rag_context_parts = []
            
            # A. CORE MEMORY (Permanent: Identity, Rules, PC Structure)
            core_results = await self.rag_client.query("agent_core", prompt, top_k=2)
            if core_results:
                core_text = "\n".join([f"- {r['content']}" for r in core_results])
                rag_context_parts.append(f"--- CORE KNOWLEDGE (Permanent) ---\n{core_text}")
            
            # B. PROJECT MEMORY (Medium-term: Ongoing work)
            # We search in all project datasets (starting with 'project_')
            # For now, we just search a generic 'current_projects' dataset or infer from prompt
            # Simplified: Search in 'projects' dataset
            project_results = await self.rag_client.query("projects", prompt, top_k=2)
            if project_results:
                proj_text = "\n".join([f"- {r['content']} (Source: {r['filename']})" for r in project_results])
                rag_context_parts.append(f"--- PROJECT CONTEXT (Ongoing) ---\n{proj_text}")
                
            # C. SCRATCHPAD (Ephemeral: Temporary info)
            scratch_results = await self.rag_client.query("scratchpad", prompt, top_k=1)
            if scratch_results:
                scratch_text = "\n".join([f"- {r['content']}" for r in scratch_results])
                rag_context_parts.append(f"--- TEMPORARY NOTES (Ephemeral) ---\n{scratch_text}")
            
            if rag_context_parts:
                full_rag_text = "\n\n".join(rag_context_parts)
                context_parts.append(f"=== KNOWLEDGE BASE (RAG) ===\n{full_rag_text}")
            else:
                self._log("[ORCH] RAG: No relevant context found")
                
        except Exception as e:
            self._log(f"[ORCH] RAG injection warning: {str(e)}")
        
        if context_parts:
            full_context = "\n\n".join(context_parts)
            # Inject context as system message at the beginning
            rag_message = {
                "role": "system",
                "content": f"CONTEXT INFORMATION:\n{full_context}"
            }
            return [rag_message] + messages
        
        return messages

    def _is_plan_sensitive(self, steps: List[Dict[str, Any]]) -> bool:
        """
        Determine if a plan contains sensitive actions or is long.
        
        Args:
            steps: List of action steps
            
        Returns:
            bool: True if plan requires confirmation
        """
        # Multiple steps = long plan = requires confirmation
        if len(steps) > 1:
            return True
        
        # Check for sensitive actions
        for step in steps:
            action = step.get("action", "")
            if action in self.SENSITIVE_ACTIONS:
                return True
        
        return False

    async def run(
        self,
        prompt: str,
        context: Optional[str] = None,
        session_id: str = "default",
        execution_mode: str = "auto",
        image_data: Optional[bytes] = None,
        agent_id: Optional[str] = None,
        auto_routing: bool = True
    ) -> Dict[str, Any]:
        """
        Main orchestration method with execution modes and permission system.
        Supports multimodal input (text + images).
        
        Args:
            prompt: User's input text
            context: Optional additional context
            session_id: Session ID for memory management
            execution_mode: Execution mode (auto, plan_only, step_by_step)
            image_data: Optional image bytes for multimodal analysis
            agent_id: Optional specific agent to use
            auto_routing: Whether to use auto-routing (default True)
            
        Returns:
            dict: Structured response with execution results, permissions, and llm_used
        """
        self._log(f"[ORCH] Nouveau prompt recu : {prompt}")
        self._log(f"[ORCH] Mode d'execution : {execution_mode}")
        if agent_id:
            self._log(f"[ORCH] Agent force : {agent_id} (Auto-routing: {auto_routing})")
        
        if image_data:
            self._log(f"[ORCH] Mode multimodal active (image fournie)")
        
        # Step 1: Analyze and create plan (with optional image)
        plan = await self.think(prompt, context, image_data, agent_id, auto_routing)
        
        intention = plan.get("intention", "fallback")
        confidence = plan.get("confidence", 0.0)
        steps = plan.get("steps", [])
        response = plan.get("response", "")
        
        self._log(f"[ORCH] Intention detectee : {intention} (confiance={confidence:.2f})")
        self._log(f"[ORCH] Plan genere : {len(steps)} etape(s)")
        
        # Step 2: Determine if plan requires confirmation
        requires_confirmation = self._is_plan_sensitive(steps)
        
        if requires_confirmation:
            self._log("[ORCH] Plan sensible ou long - validation requise")
        else:
            self._log("[ORCH] Plan court et sur - execution possible")
        
        # Step 3: Execute based on mode
        execution_results = []
        
        if execution_mode == "plan_only":
            # Mode 1: plan_only - Never execute, just return plan
            self._log("[ORCH] Mode plan_only - aucune execution")
            requires_confirmation = True
            
        elif execution_mode == "step_by_step":
            # Mode 2: step_by_step - Execute only first step
            self._log("[ORCH] Mode step_by_step - execution de la premiere etape uniquement")
            if steps:
                execution_results = await self._execute_steps(steps[:1], session_id)
                requires_confirmation = len(steps) > 1  # More steps remaining?
            
        elif execution_mode == "auto":
            # Mode 3: auto - Execute only if safe and short
            if not requires_confirmation:
                self._log("[ORCH] Mode auto - execution directe autorisee")
                execution_results = await self._execute_steps(steps, session_id)
            else:
                self._log("[ORCH] Mode auto - plan necessite validation, aucune execution")
        
        # Add prompt to memory via MCP
        try:
            await self.memory_client.add_message(session_id, "user", prompt)
            if response:
                await self.memory_client.add_message(session_id, "assistant", response)
        except Exception as e:
            self._log(f"[ORCH ERROR] Erreur memoire : {str(e)}")
        
        self._log(f"[ORCH] Execution terminee. Nombre de steps executees : {len(execution_results)}")
        
        return {
            "intention": intention,
            "confidence": confidence,
            "steps": steps,
            "response": response,
            "execution_results": execution_results,
            "requires_confirmation": requires_confirmation,
            "execution_mode_used": execution_mode,
            "llm_used": plan.get("llm_used", "unknown"),
            "llm_specialist": plan.get("llm_specialist", "unknown")
        }

    async def _execute_steps(
        self,
        steps: List[Dict[str, Any]],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of steps sequentially with logging.
        Uses LLM Router for steps that require LLM calls.
        
        Args:
            steps: List of action steps to execute
            session_id: Session ID for context
            
        Returns:
            List of execution results
        """
        results = []
        previous_result = None
        
        for i, step in enumerate(steps):
            action = step.get("action", "")
            params = {k: v for k, v in step.items() if k != "action"}
            
            self._log(f"[ORCH] Execution etape {i+1}/{len(steps)} : {action}")
            self._log(f"[ORCH] Parametres : {params}")
            
            # Detect if this step needs multimodal support
            multimodal = "image_bytes" in params or "image_data" in params
            
            # Select model for this specific action if it involves LLM
            if action in ["code_analyze", "code_explain", "code_optimize", "rag_query"]:
                # model_info = self.pick_model(action, multimodal=multimodal) # TODO: Update pick_model signature to support multimodal arg if needed, or just pass task_type
                # For now, simple call as defined in class
                llm_instance = self.pick_model(action)
                model_info = {"model": llm_instance.model, "specialist": "unknown"} # Reconstruct basic info
                self._log(f"[ORCH] Modele pour action {action} : {model_info['model']}")
                params["_model_info"] = model_info
            
            # Get action handler
            if action in self.ACTION_MAP:
                try:
                    # Inject previous result if needed
                    if "input" in params and params["input"] == "$previous" and previous_result:
                        params["data"] = previous_result
                    
                    # Execute action
                    result = await self.ACTION_MAP[action](**params)
                    
                    self._log(f"[ORCH] Resultat etape {i+1} : {result}")
                    
                    results.append({
                        "action": action,
                        "status": "success",
                        "data": result
                    })
                    previous_result = result
                    
                except Exception as e:
                    self._log(f"[ORCH ERROR] Action echouee : {action}")
                    self._log(f"[ORCH ERROR] Raison : {str(e)}")
                    
                    results.append({
                        "action": action,
                        "status": "error",
                        "error": str(e)
                    })
            else:
                self._log(f"[ORCH ERROR] Action inconnue : {action}")
                results.append({
                    "action": action,
                    "status": "error",
                    "error": f"Unknown action: {action}"
                })
        
        return results

    async def think(
        self,
        prompt: str,
        context: Optional[str] = None,
        image_data: Optional[bytes] = None,
        agent_id: Optional[str] = None,
        auto_routing: bool = True
    ) -> Dict[str, Any]:
        """
        Main orchestration method. Analyzes the prompt and creates an action plan.
        Uses LLM Router to select the appropriate specialist model.
        
        Args:
            prompt: User's input text
            context: Optional additional context
            image_data: Optional image bytes for multimodal analysis
            agent_id: Optional specific agent to use
            auto_routing: Whether to use auto-routing
            
        Returns:
            dict: Structured response with intention, confidence, steps, response, and llm_used
        """
        # Quick intent detection
        detected_intents = self._detect_intents(prompt)
        
        # Determine if multimodal is needed
        multimodal = image_data is not None
        
        # Select appropriate model
        llm = None
        model_info = {}
        
        # Logic for model selection
        if not auto_routing and agent_id:
            # Manual selection
            if agent_id == "code":
                llm = self.llm_coding
                model_info = {"model": llm.model, "specialist": "coding", "reason": "Manual selection"}
            elif agent_id == "vision":
                llm = self.llm_vision
                model_info = {"model": llm.model, "specialist": "vision", "reason": "Manual selection"}
            elif agent_id == "local":
                # Special case for local agent - might need different handling
                # For now, we don't have a direct LocalLLM wrapper that matches OpenRouterLLM interface exactly
                # We'll fallback to reasoning model but log it, or implement a wrapper
                # TODO: Implement LocalLLM wrapper for direct use here
                llm = self.llm_reasoning 
                model_info = {"model": "local-fallback", "specialist": "local", "reason": "Manual selection (Local not fully implemented in think)"}
            else:
                # Default / Orchestrator
                llm = self.llm_reasoning
                model_info = {"model": llm.model, "specialist": "reasoning", "reason": "Manual selection"}
        else:
            # Auto-routing
            primary_intention = detected_intents[0] if detected_intents else "fallback"
            llm = self.pick_model(primary_intention)
            
            specialist = "reasoning"
            if primary_intention in ["vision_analysis", "image_analysis", "screenshot_analysis", "vision"]:
                 specialist = "vision"
            elif primary_intention in ["code_execution", "code_analyze", "code_explain", "code_optimize", "code_debug", "coding"]:
                 specialist = "coding"
            
            model_info = {
                "model": llm.model,
                "specialist": specialist,
                "reason": f"Auto-routing (Intent: {primary_intention})"
            }

        self.current_model_info = model_info
        self._log(f"[ORCH] Modele selectionne : {model_info['model']} (specialiste: {model_info['specialist']})")
        self._log(f"[ORCH] Raison : {model_info.get('reason', 'N/A')}")
        
        # Build orchestration prompt
        orchestration_prompt = self._build_orchestration_prompt(prompt, detected_intents)
        
        # Add context if provided
        if context:
            orchestration_prompt = f"{orchestration_prompt}\n\nAdditional Context:\n{context}"
        
        # Get reasoning from LLM with selected model
        try:
            # Prepare messages
            messages = [{"role": "user", "content": orchestration_prompt}]
            
            # Inject RAG context before LLM call
            messages = await self._inject_rag_context(messages, prompt)
            
            # Call LLM
            if multimodal and image_data:
                # For multimodal, use vision model directly (override selection if needed)
                llm = self.llm_vision
                reasoning_response = llm.ask_with_image(
                    prompt=orchestration_prompt,
                    image_bytes=image_data
                )
            else:
                reasoning_response = llm.ask(messages)
            
            # Parse the response
            parsed_result = self._parse_reasoning_response(reasoning_response, detected_intents)
            
            # Store original prompt for memory management
            parsed_result["original_prompt"] = prompt
            
            # Add LLM info to result
            parsed_result["llm_used"] = model_info["model"]
            parsed_result["llm_specialist"] = model_info["specialist"]
            
            return parsed_result
        
        except Exception as e:
            return {
                "intention": "error",
                "confidence": 0.0,
                "steps": [],
                "response": f"Orchestration error: {str(e)}",
                "error": str(e),
                "original_prompt": prompt,
                "llm_used": model_info.get("model", "unknown"),
                "llm_specialist": model_info.get("specialist", "unknown")
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
        Build the orchestration prompt for the LLM.
        
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
- FILE: file_read(path), file_write(path, content), file_list(path), file_delete(path), file_move(src, dest), file_copy(src, dest)
- INPUT: mouse_move(x, y), mouse_click(x, y, button), keyboard_type(text), keyboard_press(keys)
- VISION: vision_analyze(image_bytes, prompt)
- RAG: rag_query(dataset, question, top_k), rag_add(dataset, filename, content, metadata), memory_cleanup(retention_days)

IMPORTANT - MEMORY MANAGEMENT RULES:
1. Use dataset='agent_core' for PERMANENT info (Identity, User Preferences, PC Structure, Security Rules). NEVER delete this.
2. Use dataset='projects' for ONGOING work (Multi-day tasks, Project documentation).
3. Use dataset='scratchpad' for EPHEMERAL info (One-off analysis, temporary notes).
4. Use 'memory_cleanup(retention_days=1)' to clear old ephemeral data when asked to "forget" or "clean up".

Your task:
1. Determine the PRIMARY intention (web_search, code_execution, system_action, file_operation, vision_analysis, rag_query, rag_add, conversation, or fallback)
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
        Parse LLM's reasoning response into structured format.
        
        Args:
            response: Raw response from LLM
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
        """Execute web search action via MCP Search Client."""
        # Use MCP Search Client - defaults to search_all for comprehensive results
        return await self.search_client.search_all(query)
    
    # async def _action_code_execute(self, code: str, **kwargs) -> Dict[str, Any]:
    #     """Execute code action."""
    #     return await self.code_executor.execute(code)
    
    # async def _action_code_analyze(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
    #     """Analyze code action."""
    #     return await self.code_executor.analyze(code, language)
    
    # async def _action_code_explain(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
    #     """Explain code action."""
    #     return await self.code_executor.explain(code, language)
    
    # async def _action_code_optimize(self, code: str, **kwargs) -> Dict[str, Any]:
    #     """Optimize code action."""
    #     return await self.code_executor.optimize(code)
    
    # async def _action_code_debug(self, code: str, error: str = "", **kwargs) -> Dict[str, Any]:
    #     """Debug code action."""
    #     return await self.code_executor.debug(code, error)
    
    async def _action_system_open(self, path: str, **kwargs) -> Dict[str, Any]:
        """Open file or folder action via MCP System Client."""
        # Determine if it's a file or folder and call appropriate MCP method
        import os
        if os.path.isfile(path):
            return await self.system_client.open_file(path)
        else:
            return await self.system_client.open_folder(path)
    
    async def _action_system_run(self, path: str, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Run program action via MCP System Client."""
        return await self.system_client.run_program(path, args)
    
    async def _action_system_list_processes(self, **kwargs) -> Dict[str, Any]:
        """List processes action via MCP System Client."""
        return await self.system_client.list_processes()
    
    async def _action_system_kill(self, name: str, **kwargs) -> Dict[str, Any]:
        """Kill process action via MCP System Client."""
        # Note: MCP System Client uses PID, but we receive name
        # For now, we'll need to list processes first to get PID
        # This is a simplified implementation - may need enhancement
        processes = await self.system_client.list_processes()
        # Find process by name and get PID
        # TODO: Implement proper name-to-PID resolution
        # For now, assume 'name' might be a PID
        try:
            pid = int(name)
            return await self.system_client.kill_process(pid)
        except ValueError:
            return {"status": "error", "message": "Process name resolution not yet implemented. Please provide PID."}
    
    async def _action_file_read(self, path: str, **kwargs) -> Dict[str, Any]:
        """Read file action via MCP."""
        return await self.files_client.read_file(path)
    
    async def _action_file_write(self, path: str, content: str, **kwargs) -> Dict[str, Any]:
        """Write file action via MCP."""
        return await self.files_client.write_file(path, content)
    
    async def _action_file_move(self, src: str, dest: str, **kwargs) -> Dict[str, Any]:
        """Move file action - not yet implemented in MCP, using legacy."""
        return self.file_manager.move(src, dest, allow=True)

    async def _action_file_copy(self, src: str, dest: str, **kwargs) -> Dict[str, Any]:
        """Copy file action - not yet implemented in MCP, using legacy."""
        return self.file_manager.copy(src, dest, allow=True)

    async def _action_vision_analyze(self, image_bytes: bytes, prompt: str = "", **kwargs) -> Dict[str, Any]:
        """
        Analyze image action via MCP Vision Client.
        """
        self._log(f"[ORCH] Vision analysis via MCP Vision Client")
        
        # Use MCP Vision Client for image analysis
        if prompt:
            # If there's a specific prompt, use analyze_image
            return await self.vision_client.analyze_image(image_bytes)
        else:
            # Default to analyze_screenshot for general analysis
            return await self.vision_client.analyze_screenshot(image_bytes)
    async def _action_file_list(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        """List directory action via MCP."""
        return await self.files_client.list_dir(path)
    
    async def _action_file_delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Delete file action via MCP."""
        return await self.files_client.delete_file(path)
    
    async def _action_rag_query(self, dataset: str, question: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Query RAG action via MCP."""
        results = await self.rag_client.query(dataset, question, top_k)
        return {"status": "success", "results": results}
    
    async def _action_rag_add(self, dataset: str, filename: str, content: str, metadata: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Add document to RAG action via MCP."""
        doc_id = await self.rag_client.add_document(dataset, filename, content, metadata)
        return {"status": "success", "document_id": doc_id}
    
    async def _action_memory_recall(self, session_id: str = "default", max_messages: int = 10, **kwargs) -> Dict[str, Any]:
        """Recall memory action via MCP."""
        context = await self.memory_client.get_context(session_id, max_messages)
        return {"status": "success", "context": context}
    
    async def _action_memory_search(self, query: str, session_id: str = None, **kwargs) -> Dict[str, Any]:
        """Search memory action via MCP."""
        results = await self.memory_client.search(query, session_id)
        return {"status": "success", "results": results}
    
    async def _action_memory_cleanup(self, retention_days: int = 1, **kwargs) -> Dict[str, Any]:
        """Clean up old memory action via MCP."""
        return await self.rag_client.cleanup_memory(retention_days)

    async def _action_mouse_move(self, x: int, y: int, duration: float = 0.5, **kwargs) -> Dict[str, Any]:
        """Move mouse action via MCP Control Client."""
        return await self.control_client.move_mouse(x, y, duration)

    async def _action_mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1, **kwargs) -> Dict[str, Any]:
        """Click mouse action via MCP Control Client."""
        # Map button name to button number for MCP client
        button_map = {"left": 1, "right": 2, "middle": 3}
        button_num = button_map.get(button, 1)
        return await self.control_client.click_mouse(button=button_num, x=x, y=y, clicks=clicks)

    async def _action_mouse_scroll(self, clicks: int, **kwargs) -> Dict[str, Any]:
        """Scroll mouse action via MCP Control Client."""
        return await self.control_client.scroll(scroll_y=clicks)

    async def _action_keyboard_type(self, text: str, interval: float = 0.05, **kwargs) -> Dict[str, Any]:
        """Type text action via MCP Control Client."""
        return await self.control_client.type(text, interval)

    async def _action_keyboard_press(self, keys: List[str], **kwargs) -> Dict[str, Any]:
        """Press keys action via MCP Control Client."""
        return await self.control_client.keypress(keys)

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
        
        # Add prompt to memory via MCP
        if prompt:
            try:
                await self.memory_client.add_message(session_id, "user", prompt)
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
            
            # Add response to memory via MCP
            if final_response:
                try:
                    await self.memory_client.add_message(session_id, "assistant", final_response)
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
            "file_operation": ["read", "write", "list", "delete", "move", "copy"],
            "input_control": ["mouse_move", "mouse_click", "keyboard_type", "keyboard_press"],
            "vision": ["analyze_image", "analyze_screenshot", "extract_text"],
            "rag": ["query", "add_document"],
            "memory": ["recall", "search"],
            "conversation": ["general_chat", "reasoning"]
        }
