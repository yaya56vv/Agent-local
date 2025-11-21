# ============================================================
# SETTINGS — Centralisation des clés API + environnements
# ============================================================

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- API KEYS ---
    OPENROUTER_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    BRAVE_API_KEY: str = ""
    
    # --- MODEL CONFIGURATION ---
    MODEL_REASONING: str = "qwen/qwen3-30b-a3b-instruct-2507"
    MODEL_CODING: str = "qwen/qwen3-30b-a3b-instruct-2507"
    MODEL_VISION: str = "qwen/qwen3-30b-a3b-instruct-2507"
    MODEL_SPEECH: str | None = None
    
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

    # --- LLM ROUTER (Mission 10) ---
    # Modèles spécialisés optionnels
    LLM_VISION_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    LLM_CODE_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    LLM_REASONING_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    LLM_CONVERSATION_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    LLM_RAG_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    LLM_DEFAULT_MODEL: str = "qwen/qwen3-30b-a3b-instruct-2507"
    
    # Activation des spécialistes (permet de désactiver certains)
    LLM_ENABLE_VISION: bool = True
    LLM_ENABLE_CODE: bool = True
    LLM_ENABLE_REASONING: bool = True
    LLM_ENABLE_CONVERSATION: bool = True
    LLM_ENABLE_RAG: bool = True

    # --- GLOBAL CONFIG ---
    AGENT_NAME: str = "Agent Local"
    VERSION: str = "0.2.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
