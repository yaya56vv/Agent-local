from backend.connectors.reasoning.gemini import GeminiOrchestrator

class AgentPipeline:

    def __init__(self):
        self.main_llm = GeminiOrchestrator()

    def process(self, prompt: str, context: str = ""):
        return self.main_llm.ask(prompt, context)