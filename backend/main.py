from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routes.orchestrate_route import router as orchestrate_router
from backend.routes.search_route import router as search_router
from backend.routes.code_route import router as code_router
from backend.routes.files_route import router as files_router
from backend.routes.rag_routes import router as rag_router
from backend.routes.system_route import router as system_router
from backend.routes.vision_route import router as vision_router

app = FastAPI(title="Agent Local")

# Include routers
app.include_router(orchestrate_router, prefix="/orchestrate", tags=["orchestration"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(code_router, prefix="/code", tags=["code"])
app.include_router(files_router, prefix="/files", tags=["files"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(system_router, prefix="/system", tags=["system"])
app.include_router(vision_router, prefix="/vision", tags=["vision"])

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


 
