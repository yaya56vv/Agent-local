from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import sys
import os

# Add backend to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.connectors.local_llm.local_llm_connector import LocalLLMConnector, LocalLLMProvider

app = FastAPI(title="Local LLM MCP Service")

# Initialize connector (default to Ollama)
# You can change this to LocalLLMProvider.LM_STUDIO if needed
connector = LocalLLMConnector(provider=LocalLLMProvider.OLLAMA)

class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

@app.post("/local_llm/generate")
async def generate(request: GenerateRequest):
    try:
        # Update model if provided
        if request.model:
            connector.model = request.model
            
        response = await connector.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/local_llm/chat")
async def chat(request: ChatRequest):
    try:
        # Update model if provided
        if request.model:
            connector.model = request.model
            
        response = await connector.chat(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/local_llm/list_models")
async def list_models():
    try:
        models = await connector.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/local_llm/health")
async def health():
    is_available = await connector.is_available()
    if is_available:
        return {"status": "healthy", "provider": connector.provider.value}
    else:
        return {"status": "unhealthy", "provider": connector.provider.value, "detail": "Service unreachable"}

if __name__ == "__main__":
    # Run on port 8001 to avoid conflict with main backend
    uvicorn.run(app, host="0.0.0.0", port=8001)

