"""
RAG Routes - API endpoints for RAG operations
Provides endpoints for document management and RAG queries
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

from backend.rag.rag_store import RAGStore
from backend.connectors.local_llm.local_llm_connector import LocalLLMConnector, LocalLLMProvider

router = APIRouter()

# Initialize RAG store
rag_store = RAGStore()

# Initialize local LLM connector (default to Ollama)
local_llm = LocalLLMConnector(
    provider=LocalLLMProvider.OLLAMA,
    model=os.getenv("LOCAL_LLM_MODEL", "llama3.2")
)


class AddDocumentRequest(BaseModel):
    """Request model for adding a document"""
    dataset: str
    filename: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    dataset: str
    question: str
    top_k: int = 5
    use_llm: bool = True
    temperature: float = 0.7
    max_tokens: int = 2048


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str
    sources: List[Dict[str, Any]]
    dataset: str


class DatasetInfo(BaseModel):
    """Response model for dataset information"""
    dataset: str
    document_count: int
    chunk_count: int
    documents: List[Dict[str, Any]]


@router.post("/documents/add", response_model=Dict[str, str])
async def add_document(request: AddDocumentRequest):
    """
    Add a document to the RAG store.
    
    Args:
        request: Document details (dataset, filename, content, metadata)
        
    Returns:
        Document ID and status
    """
    try:
        doc_id = rag_store.add_document(
            dataset=request.dataset,
            filename=request.filename,
            content=request.content,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "document_id": doc_id,
            "dataset": request.dataset,
            "filename": request.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@router.post("/documents/upload")
async def upload_document(
    dataset: str = Form(...),
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload a document file to the RAG store.
    
    Args:
        dataset: Dataset name
        file: File to upload
        metadata: Optional JSON metadata string
        
    Returns:
        Document ID and status
    """
    try:
        # Read file content
        content = await file.read()
        content_text = content.decode('utf-8')
        
        # Parse metadata if provided
        import json
        metadata_dict = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Add to RAG store
        doc_id = rag_store.add_document(
            dataset=dataset,
            filename=file.filename,
            content=content_text,
            metadata=metadata_dict
        )
        
        return {
            "status": "success",
            "document_id": doc_id,
            "dataset": dataset,
            "filename": file.filename
        }
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based (UTF-8)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG store and optionally generate an answer using local LLM.
    
    Args:
        request: Query details (dataset, question, top_k, use_llm)
        
    Returns:
        Answer and relevant sources
    """
    try:
        # Get relevant chunks from RAG store
        sources = rag_store.query(
            dataset=request.dataset,
            question=request.question,
            top_k=request.top_k
        )
        
        if not sources:
            return QueryResponse(
                answer="No relevant documents found in the dataset.",
                sources=[],
                dataset=request.dataset
            )
        
        # If use_llm is True, generate answer using local LLM
        if request.use_llm:
            # Build context from sources
            context = "\n\n".join([
                f"Source {i+1} (from {src['filename']}):\n{src['content']}"
                for i, src in enumerate(sources)
            ])
            
            # Build prompt for LLM
            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer the question.
If the context doesn't contain enough information, say so clearly.
Be concise and accurate."""
            
            prompt = f"""Context:
{context}

Question: {request.question}

Answer:"""
            
            # Generate answer using local LLM
            try:
                answer = await local_llm.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            except Exception as llm_error:
                # If LLM fails, return sources only
                answer = f"[LLM Error: {str(llm_error)}]\n\nRelevant sources found but could not generate answer. Please check if your local LLM is running."
        else:
            # Return sources only without LLM generation
            answer = "Sources retrieved successfully. Set use_llm=true to generate an answer."
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            dataset=request.dataset
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/datasets", response_model=List[str])
async def list_datasets():
    """
    List all available datasets.
    
    Returns:
        List of dataset names
    """
    try:
        datasets = rag_store.list_datasets()
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")


@router.get("/datasets/{dataset}", response_model=DatasetInfo)
async def get_dataset_info(dataset: str):
    """
    Get information about a specific dataset.
    
    Args:
        dataset: Dataset name
        
    Returns:
        Dataset information including document count and list
    """
    try:
        info = rag_store.get_dataset_info(dataset)
        return DatasetInfo(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset info: {str(e)}")


@router.delete("/datasets/{dataset}")
async def delete_dataset(dataset: str):
    """
    Delete a dataset and all its documents.
    
    Args:
        dataset: Dataset name to delete
        
    Returns:
        Status message
    """
    try:
        rag_store.delete_dataset(dataset)
        return {
            "status": "success",
            "message": f"Dataset '{dataset}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")


@router.get("/llm/status")
async def check_llm_status():
    """
    Check if the local LLM is available.
    
    Returns:
        LLM availability status
    """
    try:
        is_available = await local_llm.is_available()
        models = []
        
        if is_available:
            try:
                models = await local_llm.list_models()
            except:
                pass
        
        return {
            "available": is_available,
            "provider": local_llm.provider.value,
            "base_url": local_llm.base_url,
            "current_model": local_llm.model,
            "available_models": models
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


@router.post("/llm/configure")
async def configure_llm(
    provider: str = Form(...),
    base_url: Optional[str] = Form(None),
    model: Optional[str] = Form(None)
):
    """
    Configure the local LLM connector.
    
    Args:
        provider: LLM provider (ollama or lm_studio)
        base_url: Optional base URL
        model: Optional model name
        
    Returns:
        Configuration status
    """
    global local_llm
    
    try:
        # Map provider string to enum
        if provider.lower() == "ollama":
            provider_enum = LocalLLMProvider.OLLAMA
        elif provider.lower() in ["lm_studio", "lmstudio"]:
            provider_enum = LocalLLMProvider.LM_STUDIO
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Create new connector
        local_llm = LocalLLMConnector(
            provider=provider_enum,
            base_url=base_url,
            model=model
        )
        
        # Check if available
        is_available = await local_llm.is_available()
        
        return {
            "status": "success",
            "provider": local_llm.provider.value,
            "base_url": local_llm.base_url,
            "model": local_llm.model,
            "available": is_available
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Configuration failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for RAG service.
    
    Returns:
        Service status
    """
    try:
        datasets = rag_store.list_datasets()
        llm_available = await local_llm.is_available()
        
        return {
            "status": "healthy",
            "rag_store": "operational",
            "datasets_count": len(datasets),
            "local_llm": "available" if llm_available else "unavailable"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }