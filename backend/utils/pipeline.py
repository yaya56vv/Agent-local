from backend.connectors.llm.openrouter import OpenRouterLLM

class AgentPipeline:
    """
    Simple pipeline using OpenRouterLLM directly.
    For advanced orchestration, use backend.orchestrator.orchestrator.Orchestrator instead.
    """

    def __init__(self):
        self.main_llm = OpenRouterLLM()

    def process(self, prompt: str, context: str = ""):
        """Process a prompt with optional context."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        return self.main_llm.ask(full_prompt)