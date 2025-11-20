from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
import sys
import socket

from backend.routes.orchestrate_route import router as orchestrate_router
from backend.routes.search_route import router as search_router
# from backend.routes.code_route import router as code_router
from backend.routes.files_route import router as files_router
from backend.routes.rag_routes import router as rag_router
from backend.routes.system_route import router as system_router
from backend.routes.vision_route import router as vision_router
from backend.routes.voice_route import router as voice_router

app = FastAPI(title="Agent Local")

# Include routers
app.include_router(orchestrate_router, prefix="/orchestrate", tags=["orchestration"])
app.include_router(search_router, prefix="/search", tags=["search"])
# app.include_router(code_router, prefix="/code", tags=["code"])
app.include_router(files_router, prefix="/files", tags=["files"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(system_router, prefix="/system", tags=["system"])
app.include_router(vision_router, prefix="/vision", tags=["vision"])
app.include_router(voice_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shutdown")
async def shutdown():
    """Endpoint pour arrêter proprement le serveur FastAPI"""
    import asyncio
    
    def stop_server():
        # Attendre un peu pour que la réponse soit envoyée
        import time
        time.sleep(0.5)
        # Arrêt propre du serveur
        os._exit(0)
    
    # Lancer l'arrêt dans un thread séparé
    import threading
    threading.Thread(target=stop_server, daemon=True).start()
    
    return {
        "status": "shutdown_initiated",
        "message": "Le serveur s'arrête dans quelques instants..."
    }


def check_port_available(port: int = 8000) -> bool:
    """Vérifie si le port est disponible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
        sock.close()
        return True
    except OSError:
        return False


def check_existing_session():
    """Vérifie s'il y a déjà une session active sur le port 8000"""
    if not check_port_available(8000):
        print("\n" + "="*60)
        print("⚠️  ATTENTION: Port 8000 déjà occupé!")
        print("="*60)
        print("Une session de l'agent semble déjà active.")
        print("Veuillez:")
        print("  1. Fermer l'autre instance via l'interface UI (bouton Stop)")
        print("  2. Ou fermer manuellement le processus Python")
        print("="*60 + "\n")
        sys.exit(1)


@app.get("/", include_in_schema=False)
async def serve_root():
    """Serve main UI interface"""
    return FileResponse(frontend_path / "index.html")


@app.get("/ui/rag", include_in_schema=False)
async def serve_rag():
    """Serve RAG interface"""
    rag_html = frontend_path / "static" / "rag.html"
    if rag_html.exists():
        return FileResponse(str(rag_html))
    return {"error": "RAG interface not found"}


 
