"""
MCP Documents Service - Génération et export de documents
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import io

app = FastAPI(title="MCP Documents Service")


class DocumentRequest(BaseModel):
    """Requête de génération de document"""
    content: str
    title: Optional[str] = "Document"
    format: str = "txt"  # txt, md, html
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Réponse de génération"""
    status: str
    document_id: str
    content: Optional[str] = None
    format: str
    size: int


@app.get("/")
async def root():
    """Info service"""
    return {
        "service": "MCP Documents",
        "version": "1.0.0",
        "formats": ["txt", "md", "html"]
    }


@app.post("/documents/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """
    Génère un document
    
    Args:
        request: Requête avec contenu et format
        
    Returns:
        Document généré
    """
    try:
        content = request.content
        doc_format = request.format.lower()
        
        # Générer selon le format
        if doc_format == "md":
            formatted_content = f"# {request.title}\n\n{content}"
        elif doc_format == "html":
            formatted_content = f"<html><head><title>{request.title}</title></head><body><h1>{request.title}</h1><p>{content}</p></body></html>"
        else:  # txt
            formatted_content = f"{request.title}\n{'=' * len(request.title)}\n\n{content}"
        
        doc_id = f"doc_{hash(content) % 10000}"
        
        return DocumentResponse(
            status="success",
            document_id=doc_id,
            content=formatted_content,
            format=doc_format,
            size=len(formatted_content)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/fill")
async def fill_template(template: str, data: Dict[str, Any]):
    """
    Remplit un template avec des données
    
    Args:
        template: Template avec placeholders {key}
        data: Données à insérer
        
    Returns:
        Document rempli
    """
    try:
        filled = template
        for key, value in data.items():
            filled = filled.replace(f"{{{key}}}", str(value))
        
        return {
            "status": "success",
            "content": filled,
            "size": len(filled)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "mcp-documents"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
