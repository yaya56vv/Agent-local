class LocalLlmClient:
    def __init__(self, base_url: str):
        """Initialise le client MCP pour le service LLM local."""
        self.base_url = base_url

    # TODO: implémenter completion(self, prompt, params),
    # chat_completion(self, messages, params), get_embeddings(self, text),
    # load_model(self, model_path)
