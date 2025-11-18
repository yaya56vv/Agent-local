from fastapi import APIRouter
from pydantic import BaseModel
from backend.connectors.reasoning.gemini import GeminiOrchestrator

router = APIRouter()
orchestrator = GeminiOrchestrator()

class Query(BaseModel):
    prompt: str
    context: str | None = ""

@router.post("/orchestrate")
def orchestrate(query: Query):
    response = orchestrator.ask(query.prompt, query.context)
    return {"response": response}