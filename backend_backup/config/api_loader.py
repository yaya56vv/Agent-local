from .settings import settings

def is_openrouter_ready():
    return settings.OPENROUTER_API_KEY not in ["", "A_INSERER"]

