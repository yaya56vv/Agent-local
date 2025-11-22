# ============================================================
# SETTINGS — Centralisation des clés API + environnements
# ============================================================

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- API KEYS ---
    OPENROUTER_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    BRAVE_API_KEY: str = ""
    
    # --- AGENT MODELS (Registry) ---
    PROVIDER_ORCHESTRATOR: str | None = "openrouter"
    ORCHESTRATOR_MODEL: str | None = "google/gemini-2.0-flash-001"
    
    PROVIDER_CODE: str | None = "openrouter"
    CODE_AGENT_MODEL: str | None = "google/gemini-2.0-flash-001"
    
    PROVIDER_VISION: str | None = "openrouter"
    VISION_AGENT_MODEL: str | None = "google/gemini-2.0-flash-001"
    
    PROVIDER_LOCAL: str | None = "ollama"
    LOCAL_AGENT_MODEL: str | None = "llama3.2"
    
    PROVIDER_ANALYSE: str | None = "openrouter"
    ANALYSE_AGENT_MODEL: str | None = None

    # --- GLM VISION EXPERT (MCP) ---
    GLM_AGENT_ENABLED: bool = True
    GLM_AGENT_HOST: str = "http://localhost"
    GLM_AGENT_PORT: int = 9001
    GLM_AGENT_MODEL: str = "google/gemini-2.0-flash-thinking-exp-01-21"
    GLM_AGENT_ROLE: str = "glm_vision_expert"

    # --- ROUTING ---
    PRE_PROCESSING_ENABLED: bool = True
    POST_PROCESSING_ENABLED: bool = True
    AUTO_ROUTING_ENABLED: bool = True
    LOCAL_TASKS: str = "intention,summary,postprocess,continuity,light_cleaning"

    # --- MCP TOOLS ---
    MCP_VISION_ENABLED: bool = True
    MCP_CODE_ENABLED: bool = True
    MCP_FILE_SYSTEM_ENABLED: bool = True
    MCP_BROWSER_ENABLED: bool = True
    MCP_SEARCH_ENABLED: bool = True
    MCP_TOOLS_ENABLED: bool = True

    # --- LOCAL LLM ---
    LOCAL_LLM_BASE_URL: str = "http://127.0.0.1:11434"
    LOCAL_LLM_MODEL: str = "llama3.2"

    # --- ENDPOINTS OPENROUTER ---
    OPENROUTER_ENDPOINT: str = "https://openrouter.ai/api/v1/chat/completions"

    # --- RAG ---
    RAG_DB_PATH: str = "rag/rag.db"
    RAG_DOCUMENTS_PATH: str = "rag/documents"
    CHROMA_PATH: str = "C:\\AGENT LOCAL\\rag\\chroma"
    
    # --- LOCAL LLM ---
    LOCAL_LLM_PROVIDER: str = "ollama"  # ollama or lm_studio

    # --- ORCHESTRATOR ---
    ORCHESTRATOR_DEBUG: bool = True

    # --- GLOBAL CONFIG ---
    AGENT_NAME: str = "Agent Local"
    VERSION: str = "0.2.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

