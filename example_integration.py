"""
Exemple d'intégration complète du module System Actions
Montre comment intégrer dans une application FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routes
from backend.routes import system_route

# Créer l'application FastAPI
app = FastAPI(
    title="Agent API",
    description="API pour l'agent avec actions système",
    version="1.0.0"
)

# Configuration CORS (optionnel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes système
app.include_router(
    system_route.router,
    prefix="/system",
    tags=["system"]
)

# Route racine
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Agent API with System Actions",
        "version": "1.0.0",
        "endpoints": {
            "system": "/system",
            "docs": "/docs",
            "health": "/system/health"
        }
    }

# Health check global
@app.get("/health")
async def global_health():
    """Vérification globale de santé"""
    return {
        "status": "healthy",
        "service": "agent-api",
        "modules": {
            "system": "/system/health"
        }
    }


# Point d'entrée pour le développement
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Agent API - System Actions Module")
    print("=" * 60)
    print()
    print("Server starting on http://localhost:8000")
    print()
    print("Available endpoints:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("  - Health:     http://localhost:8000/health")
    print("  - System:     http://localhost:8000/system/health")
    print()
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

