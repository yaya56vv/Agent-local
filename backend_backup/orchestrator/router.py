"""
Multi-Agent Router with Automatic PRE/POST Processing
Handles intelligent routing with local agent pre/post processing
"""
from typing import Dict, Any, Optional, List
from backend.config.settings import settings
from backend.orchestrator.clients.local_llm_client import LocalLlmClient
from backend.config.model_registry import model_registry


class AgentRegistry:
    """Registry of available agents and their capabilities"""
    
    @staticmethod
    def get_agents() -> Dict[str, Dict[str, Any]]:
        """
        Get all available agents from environment configuration.
        NO HARDCODED VALUES - All from settings.
        
        Returns:
            Dict mapping agent names to their configurations
        """
        return {
            "local": {
                "name": "Local Agent",
                "model": settings.LOCAL_AGENT_MODEL,
                "capabilities": ["summary", "intention", "clean", "fast_analysis", 
                               "postprocess", "continuity", "shorten", "clarify"],
                "priority": "high",
                "description": "Fast local processing for pre/post operations"
            },
            "orchestrator": {
                "name": "Orchestrator Agent",
                "model": settings.ORCHESTRATOR_MODEL,
                "capabilities": ["planning", "coordination", "general_tasks"],
                "priority": "medium",
                "description": "Main orchestration and general task handling"
            },
            "code": {
                "name": "Code Agent",
                "model": settings.CODE_AGENT_MODEL,
                "capabilities": ["code", "bugfix", "code_analysis", "refactor", 
                               "debug", "optimize"],
                "priority": "high",
                "description": "Specialized in code-related tasks"
            },
            "vision": {
                "name": "Vision Agent",
                "model": settings.VISION_AGENT_MODEL,
                "capabilities": ["image_analysis", "screenshot", "visual_inspection"],
                "priority": "high",
                "description": "Specialized in visual analysis"
            },
            "analyse": {
                "name": "Analysis Agent",
                "model": settings.ANALYSE_AGENT_MODEL or settings.ORCHESTRATOR_MODEL,
                "capabilities": ["complex_analysis", "deep_reasoning", "research"],
                "priority": "medium",
                "description": "Deep analysis and complex reasoning"
            },
            "glm": {
                "name": "GLM Vision Expert",
                "model": settings.GLM_AGENT_MODEL,
                "capabilities": ["vision_expert", "complex_reasoning", "glm_tools", "visual_inspection"],
                "priority": "high",
                "description": "Expert GLM-4.6 agent with vision and tools"
            }
        }
    
    @staticmethod
    def get_agent_by_capability(capability: str) -> Optional[str]:
        """
        Find the best agent for a given capability.
        
        Args:
            capability: The capability needed
            
        Returns:
            Agent name or None if not found
        """
        agents = AgentRegistry.get_agents()
        
        # Sort by priority (high first)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_agents = sorted(
            agents.items(),
            key=lambda x: priority_order.get(x[1].get("priority", "low"), 2)
        )
        
        for agent_name, agent_config in sorted_agents:
            if capability in agent_config.get("capabilities", []):
                return agent_name
        
        return None


class ModelRegistry:
    """Registry of available models - Uses centralized model_registry"""
    
    @staticmethod
    def get_models() -> Dict[str, Dict[str, Any]]:
        """
        Get all available models from centralized model_registry.
        
        Returns:
            Dict mapping model types to their configurations
        """
        orchestrator_config = model_registry.get_model("orchestrator")
        code_config = model_registry.get_model("code")
        vision_config = model_registry.get_model("vision")
        local_config = model_registry.get_model("local")
        
        return {
            "reasoning": {
                "model": orchestrator_config["model"] if orchestrator_config else "unknown",
                "provider": orchestrator_config.get("provider", "openrouter") if orchestrator_config else "openrouter",
                "description": "General reasoning and planning"
            },
            "coding": {
                "model": code_config["model"] if code_config else "unknown",
                "provider": code_config.get("provider", "openrouter") if code_config else "openrouter",
                "description": "Code generation and analysis"
            },
            "vision": {
                "model": vision_config["model"] if vision_config else "unknown",
                "provider": vision_config.get("provider", "openrouter") if vision_config else "openrouter",
                "description": "Visual analysis and understanding"
            },
            "local": {
                "model": local_config["model"] if local_config else settings.LOCAL_LLM_MODEL,
                "provider": settings.LOCAL_LLM_PROVIDER,
                "base_url": settings.LOCAL_LLM_BASE_URL,
                "description": "Fast local processing"
            }
        }
    
    @staticmethod
    def get_model_for_agent(agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the model configuration for a specific agent using centralized registry.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Model configuration or None
        """
        # Map agent names to registry roles
        role_map = {
            "orchestrator": "orchestrator",
            "code": "code",
            "vision": "vision",
            "local": "local",
            "analyse": "orchestrator",  # Fallback to orchestrator for analyse
            "glm": "glm"
        }
        
        role = role_map.get(agent_name)
        if not role:
            return None
            
        if role == "glm":
             return {
                "model": settings.GLM_AGENT_MODEL,
                "provider": "openrouter", # Assuming openrouter for now as per settings
                "description": "GLM Vision Expert Model"
            }

        config = model_registry.get_model(role)
        if not config:
            return None
        
        return {
            "model": config["model"],
            "provider": config.get("provider", "openrouter"),
            "description": f"Model for {agent_name} agent"
        }


class MultiAgentRouter:
    """
    Intelligent router that manages PRE/POST processing with local agent
    and routes to appropriate specialized agents
    """
    
    # Local agent tasks for PRE-processing
    LOCAL_PRE_TASKS = {
        "summary", "intention", "clean", "fast_analysis"
    }
    
    # Local agent tasks for POST-processing
    LOCAL_POST_TASKS = {
        "postprocess", "continuity", "shorten", "clarify"
    }
    
    def __init__(self, orchestrator=None):
        """
        Initialize the router.
        
        Args:
            orchestrator: Optional orchestrator instance for access to clients
        """
        self.orchestrator = orchestrator
        self.local_client = LocalLlmClient(base_url=settings.LOCAL_LLM_BASE_URL)
        self.agent_registry = AgentRegistry()
        self.model_registry = ModelRegistry()
    
    async def pre_process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        PRE-PROCESS step: Use local agent for fast initial processing.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Pre-processed result with intention, cleaned message, etc.
        """
        try:
            # Determine which pre-processing tasks are needed
            tasks_needed = self._detect_pre_tasks(message)
            
            if not tasks_needed:
                # No pre-processing needed
                return {
                    "status": "skipped",
                    "original_message": message,
                    "processed_message": message,
                    "tasks": []
                }
            
            # Build pre-processing prompt
            prompt = self._build_pre_prompt(message, tasks_needed)
            
            # Call local agent
            result = await self.local_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse result
            processed = self._parse_pre_result(result, message)
            
            return {
                "status": "success",
                "original_message": message,
                "processed_message": processed.get("cleaned_message", message),
                "intention": processed.get("intention", "general"),
                "summary": processed.get("summary"),
                "tasks": list(tasks_needed),
                "agent_used": "local",
                "model_used": settings.LOCAL_LLM_MODEL
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "original_message": message,
                "processed_message": message
            }
    
    async def route(self, message: str, pre_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        ROUTING step: Select the appropriate agent based on message analysis.
        
        Args:
            message: User message (possibly pre-processed)
            pre_result: Optional pre-processing result
            
        Returns:
            Routing decision with selected agent and model
        """
        try:
            # Use pre-processed intention if available
            intention = None
            if pre_result and pre_result.get("status") == "success":
                intention = pre_result.get("intention")
                message = pre_result.get("processed_message", message)
            
            # Detect routing criteria
            routing_info = self._analyze_routing(message, intention)
            
            # Select agent
            selected_agent = self._select_agent(routing_info)
            
            # Get model for selected agent
            model_config = self.model_registry.get_model_for_agent(selected_agent)
            
            return {
                "status": "success",
                "selected_agent": selected_agent,
                "model_config": model_config,
                "routing_reason": routing_info.get("reason"),
                "confidence": routing_info.get("confidence", 0.8),
                "message": message
            }
            
        except Exception as e:
            # Fallback to orchestrator
            return {
                "status": "fallback",
                "selected_agent": "orchestrator",
                "model_config": self.model_registry.get_model_for_agent("orchestrator"),
                "routing_reason": f"Error in routing: {str(e)}",
                "confidence": 0.5,
                "message": message
            }
    
    async def post_process(self, result: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """
        POST-PROCESS step: Use local agent to refine and format the result.
        
        Args:
            result: Result from the main agent
            original_message: Original user message
            
        Returns:
            Post-processed result
        """
        try:
            # Determine which post-processing tasks are needed
            tasks_needed = self._detect_post_tasks(result, original_message)
            
            if not tasks_needed:
                # No post-processing needed
                return {
                    "status": "skipped",
                    "final_output": result,
                    "tasks": []
                }
            
            # Build post-processing prompt
            prompt = self._build_post_prompt(result, original_message, tasks_needed)
            
            # Call local agent
            processed = await self.local_client.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "status": "success",
                "original_output": result,
                "final_output": processed.get("text", str(result)),
                "tasks": list(tasks_needed),
                "agent_used": "local",
                "model_used": settings.LOCAL_LLM_MODEL
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "final_output": result
            }
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete processing pipeline: PRE -> ROUTE -> EXECUTE -> POST.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Complete processing result
        """
        # Step 1: PRE-PROCESS
        pre_result = await self.pre_process(message, context)
        
        # Step 2: ROUTE
        routing = await self.route(
            message=pre_result.get("processed_message", message),
            pre_result=pre_result
        )
        
        # Step 3: EXECUTE (delegated to orchestrator or specific agent)
        # This would be handled by the orchestrator based on routing decision
        execution_result = {
            "agent": routing.get("selected_agent"),
            "model": routing.get("model_config", {}).get("model"),
            "message": routing.get("message")
        }
        
        # Step 4: POST-PROCESS
        post_result = await self.post_process(execution_result, message)
        
        # Return complete result
        return {
            "pre_processing": pre_result,
            "routing": routing,
            "execution": execution_result,
            "post_processing": post_result,
            "agent_used": routing.get("selected_agent"),
            "model_used": routing.get("model_config", {}).get("model"),
            "final_output": post_result.get("final_output")
        }
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _detect_pre_tasks(self, message: str) -> set:
        """Detect which pre-processing tasks are needed"""
        tasks = set()
        
        message_lower = message.lower()
        
        # Always do intention detection
        tasks.add("intention")
        
        # Check if message needs cleaning
        if len(message) > 200 or "\n" in message:
            tasks.add("clean")
        
        # Check if fast analysis is needed
        if any(word in message_lower for word in ["analyze", "analyse", "check", "review"]):
            tasks.add("fast_analysis")
        
        return tasks
    
    def _detect_post_tasks(self, result: Dict[str, Any], original_message: str) -> set:
        """Detect which post-processing tasks are needed"""
        tasks = set()
        
        # Always do basic post-processing
        tasks.add("postprocess")
        
        # Check if result needs shortening
        result_str = str(result)
        if len(result_str) > 1000:
            tasks.add("shorten")
        
        # Check if clarification is needed
        if "error" in result or "warning" in result:
            tasks.add("clarify")
        
        return tasks
    
    def _build_pre_prompt(self, message: str, tasks: set) -> str:
        """Build prompt for pre-processing"""
        prompt = f"Analyze this user message and perform the following tasks: {', '.join(tasks)}\n\n"
        prompt += f"User message: {message}\n\n"
        prompt += "Provide:\n"
        
        if "intention" in tasks:
            prompt += "- intention: (code/vision/analysis/general)\n"
        if "clean" in tasks:
            prompt += "- cleaned_message: (concise version)\n"
        if "summary" in tasks:
            prompt += "- summary: (brief summary)\n"
        if "fast_analysis" in tasks:
            prompt += "- quick_analysis: (initial thoughts)\n"
        
        return prompt
    
    def _build_post_prompt(self, result: Dict[str, Any], original_message: str, tasks: set) -> str:
        """Build prompt for post-processing"""
        prompt = f"Post-process this result for the user. Tasks: {', '.join(tasks)}\n\n"
        prompt += f"Original message: {original_message}\n\n"
        prompt += f"Result to process: {result}\n\n"
        prompt += "Provide a clear, concise, and user-friendly response."
        
        return prompt
    
    def _parse_pre_result(self, result: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """Parse pre-processing result"""
        text = result.get("text", "")
        
        parsed = {
            "cleaned_message": original_message,
            "intention": "general"
        }
        
        # Simple parsing (could be enhanced with structured output)
        if "intention:" in text.lower():
            lines = text.split("\n")
            for line in lines:
                if "intention:" in line.lower():
                    parsed["intention"] = line.split(":", 1)[1].strip()
                elif "cleaned_message:" in line.lower():
                    parsed["cleaned_message"] = line.split(":", 1)[1].strip()
                elif "summary:" in line.lower():
                    parsed["summary"] = line.split(":", 1)[1].strip()
        
        return parsed
    
    def _analyze_routing(self, message: str, intention: Optional[str] = None) -> Dict[str, Any]:
        """Analyze message to determine routing"""
        message_lower = message.lower()
        
        # Check for GLM/Expert keywords
        if any(word in message_lower for word in ["glm", "expert vision", "vision expert", "glm-4"]):
             return {
                "target": "glm",
                "reason": "Explicit request for GLM Vision Expert",
                "confidence": 0.95
            }

        # Check for image/vision keywords
        if any(word in message_lower for word in ["image", "screenshot", "regarde", "voir", "visual"]):
            return {
                "target": "vision",
                "reason": "Visual analysis required",
                "confidence": 0.9
            }
        
        # Check for code keywords or intention
        if intention in ["code", "bugfix", "debug"] or any(word in message_lower for word in ["code", "bug", "debug", "function", "class"]):
            return {
                "target": "code",
                "reason": "Code-related task detected",
                "confidence": 0.85
            }
        
        # Check for complex analysis
        if any(word in message_lower for word in ["analyze deeply", "research", "complex", "detailed analysis"]):
            return {
                "target": "analyse",
                "reason": "Complex analysis required",
                "confidence": 0.8
            }
        
        # Default to orchestrator
        return {
            "target": "orchestrator",
            "reason": "General task handling",
            "confidence": 0.7
        }
    
    def _select_agent(self, routing_info: Dict[str, Any]) -> str:
        """Select agent based on routing analysis"""
        target = routing_info.get("target", "orchestrator")
        
        # Verify agent exists
        agents = self.agent_registry.get_agents()
        if target in agents:
            return target
        
        # Fallback to orchestrator
        return "orchestrator"
