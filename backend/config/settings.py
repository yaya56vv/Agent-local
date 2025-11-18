# ============================================================
# SETTINGS — Centralisation des clés API + environnements
# ============================================================

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- API KEYS ---
    GEMINI_API_KEY: str = ""
    KIMI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    BRAVE_API_KEY: str = ""
    
    # --- LOCAL LLM ---
    LOCAL_LLM_BASE_URL: str = "http://127.0.0.1:11434"
    LOCAL_LLM_MODEL: str = "llama3.2"

    # --- ENDPOINTS GEMINI ---
    GEMINI_ENDPOINT: str = "https://generativelanguage.googleapis.com/v1beta/models"

    # --- ENDPOINTS KIMI ---
    KIMI_ENDPOINT: str = "https://api.moonshot.cn/v1"

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

settings = Settings()
