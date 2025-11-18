from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pathlib import Path

from backend.rag.rag_engine import add_message_to_session, get_session_history
from backend.routers import orchestrator
from backend.routes.orchestrate_route import router as orchestrate_router
from backend.routes.search_route import router as search_router
from backend.routes.memory_route import router as memory_router
from backend.routes.code_route import router as code_router
from backend.routes.files_route import router as files_router
from backend.routes.rag_routes import router as rag_router
from backend.routes.rag_routes import router as rag_router

app = FastAPI(title="Agent Local")

app.include_router(orchestrator.router)
app.include_router(orchestrate_router, prefix="/orchestrate", tags=["orchestration"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])
app.include_router(code_router, prefix="/code", tags=["code"])
app.include_router(files_router, prefix="/files", tags=["files"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/ui", StaticFiles(directory=str(frontend_path), html=True), name="ui")


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatReply(BaseModel):
    reply: str
    session_id: str
    history: List[Dict[str, Any]]


class MemoryAddRequest(BaseModel):
    session_id: str
    role: str = "user"
    content: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ui", include_in_schema=False)
async def serve_ui():
    """Serve main UI interface"""
    return FileResponse(frontend_path / "index.html")


@app.get("/ui/rag", include_in_schema=False)
async def serve_rag():
    """Serve RAG interface"""
    rag_html = frontend_path / "static" / "rag.html"
    if rag_html.exists():
        return FileResponse(str(rag_html))
    return {"error": "RAG interface not found"}


@app.post("/chat", response_model=ChatReply)
def chat(req: ChatRequest):
    """
    Chat minimal :
    - crée un session_id si absent
    - enregistre le message dans la mémoire
    - répond juste en écho (pour l’instant)
    """
    session_id = req.session_id or str(uuid4())

    add_message_to_session(
        session_id=session_id,
        role="user",
        content=req.message,
        meta={"source": "chat"},
    )

    # Plus tard : appel à une API de reasoning + RAG
    reply_text = f"[backend OK] Tu as dit : {req.message}"

    add_message_to_session(
        session_id=session_id,
        role="assistant",
        content=reply_text,
        meta={"source": "chat"},
    )

    history = get_session_history(session_id, limit=50)

    return ChatReply(
        reply=reply_text,
        session_id=session_id,
        history=history,
    )


@app.post("/memory/add")
def memory_add(req: MemoryAddRequest):
    add_message_to_session(
        session_id=req.session_id,
        role=req.role,
        content=req.content,
        meta={"source": "manual"},
    )
    return {"status": "ok"}


@app.get("/memory/{session_id}")
def memory_get(session_id: str, limit: int = 50):
    history = get_session_history(session_id, limit=limit)
    return {"session_id": session_id, "history": history}


# Endpoints “bouchons” pour la suite (actions / vision / search)
@app.post("/actions/plan")
def plan_action(payload: Dict[str, Any]):
    """
    Bouchon : renvoie juste le plan reçu.
    Plus tard : utilisera backend.local_agent.actions.
    """
    return {
        "received": payload,
        "note": "Endpoint en place, logique d’actions à implémenter ensuite.",
    }


@app.post("/vision/analyse")
def analyse_vision(payload: Dict[str, Any]):
    """
    Bouchon : endpoint de vision.
    Plus tard : appel modèle vision + analyse de capture.
    """
    return {
        "note": "Endpoint vision en place. À connecter à un modèle vision plus tard.",
        "received": list(payload.keys()),
    }


@app.post("/search/web")
def search_web(payload: Dict[str, Any]):
    """
    Bouchon : endpoint de recherche web.
    Plus tard : utilisera une API de type Perplexity / Tavily / autre.
    """
    return {
        "note": "Endpoint recherche en place. À connecter à une API web plus tard.",
        "query": payload.get("query", ""),
    }
