"""
MCP RAG Service - FastAPI Server
Provides HTTP endpoints for RAG (Retrieval Augmented Generation) operations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.rag.rag_store import RAGStore
from backend.rag.rag_helper import RAGHelper

# Initialize FastAPI app
app = FastAPI(
    title="MCP RAG Service",
    description="RAG (Retrieval Augmented Generation) service for MCP protocol",
    version="1.0.0"
)

# Initialize RAG components
rag_store = RAGStore()
rag_helper = RAGHelper()


# Pydantic models for request bodies
class AddDocumentRequest(BaseModel):
    dataset: str
    document_id: str  # This will be used as filename
    text: str
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    dataset: str
    query: str
    top_k: int = 5


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP RAG",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/rag/add_document")
async def add_document(request: AddDocumentRequest):
    """
    Add a document to the RAG store with embeddings.
    
    Args:
        request: AddDocumentRequest with dataset, document_id, text, and optional metadata
        
    Returns:
        Document ID and chunk information
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Prepare metadata
        metadata = request.metadata or {}
        metadata["dataset"] = request.dataset
        metadata["source"] = request.document_id
        
        # Add document to RAG store
        doc_id = await rag_store.add_document(
            dataset=request.dataset,
            filename=request.document_id,
            content=request.text,
            metadata=metadata
        )
        
        # Get chunks for this document
        chunks = rag_store.get_document_chunks(doc_id)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Document added successfully",
            "document_id": doc_id,
            "dataset": request.dataset,
            "chunk_count": len(chunks)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query")
async def query_rag(request: QueryRequest):
    """
    Query the RAG store for relevant documents.
    
    Args:
        request: QueryRequest with dataset, query, and top_k
        
    Returns:
        Relevant chunks with similarity scores
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Query the RAG store
        results = await rag_store.query(
            dataset=request.dataset,
            question=request.query,
            top_k=request.top_k
        )
        
        return JSONResponse(content={
            "status": "success",
            "query": request.query,
            "dataset": request.dataset,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/list_documents")
async def list_documents(
    dataset: Optional[str] = Query(None, description="Optional dataset to filter by")
):
    """
    List documents in the RAG store.
    
    Args:
        dataset: Optional dataset name to filter by
        
    Returns:
        List of documents
    """
    try:
        if dataset:
            # Get documents for specific dataset
            dataset_info = rag_store.get_dataset_info(dataset)
            documents = dataset_info.get("documents", [])
            
            return JSONResponse(content={
                "status": "success",
                "dataset": dataset,
                "documents": documents,
                "count": len(documents)
            })
        else:
            # Get all documents
            documents = rag_store.list_all_documents()
            
            return JSONResponse(content={
                "status": "success",
                "documents": documents,
                "count": len(documents)
            })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/get_dataset_info")
async def get_dataset_info(
    dataset: str = Query(..., description="Dataset name")
):
    """
    Get information about a dataset.
    
    Args:
        dataset: Dataset name
        
    Returns:
        Dataset statistics and information
        
    Raises:
        HTTPException: If dataset doesn't exist
    """
    try:
        info = rag_store.get_dataset_info(dataset)
        
        if info["document_count"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found or empty: {dataset}"
            )
        
        return JSONResponse(content={
            "status": "success",
            "info": info
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints
@app.get("/rag/list_datasets")
async def list_datasets():
    """
    List all available datasets.
    
    Returns:
        List of dataset names
    """
    try:
        datasets = rag_store.list_datasets()
        
        return JSONResponse(content={
            "status": "success",
            "datasets": datasets,
            "count": len(datasets)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/rag/delete_document")
async def delete_document(
    document_id: str = Query(..., description="Document ID to delete")
):
    """
    Delete a document from the RAG store.
    
    Args:
        document_id: Document ID to delete
        
    Returns:
        Success status
        
    Raises:
        HTTPException: If document doesn't exist
    """
    try:
        rag_store.delete_document(document_id)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Document deleted successfully",
            "document_id": document_id
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/rag/delete_dataset")
async def delete_dataset(
    dataset: str = Query(..., description="Dataset name to delete")
):
    """
    Delete an entire dataset.
    
    Args:
        dataset: Dataset name to delete
        
    Returns:
        Success status
    """
    try:
        rag_store.delete_dataset(dataset)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Dataset deleted successfully",
            "dataset": dataset
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/get_document_chunks")
async def get_document_chunks(
    document_id: str = Query(..., description="Document ID")
):
    """
    Get all chunks for a specific document.
    
    Args:
        document_id: Document ID
        
    Returns:
        List of chunks
    """
    try:
        chunks = rag_store.get_document_chunks(document_id)
        
        return JSONResponse(content={
            "status": "success",
            "document_id": document_id,
            "chunks": chunks,
            "count": len(chunks)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
