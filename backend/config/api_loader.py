from .settings import settings

def is_gemini_ready():
    return settings.GEMINI_API_KEY not in ["", "A_INSERER"]

def is_kimi_ready():
    return settings.KIMI_API_KEY not in ["", "A_INSERER"]

def is_openrouter_ready():
    return settings.OPENROUTER_API_KEY not in ["", "A_INSERER"]
