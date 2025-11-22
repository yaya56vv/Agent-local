"""
RAG Routes - API endpoints for RAG operations
Provides endpoints for document management and RAG queries
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from backend.rag.rag_helper import RAGHelper

router = APIRouter()

# Initialize RAG helper
rag_helper = RAGHelper()


class AddDocumentRequest(BaseModel):
    """Request model for adding a document"""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class AddDocumentResponse(BaseModel):
    """Response model for adding a document"""
    status: str
    document_id: str
    chunks: List[str]
    message: str


class QueryRequest(BaseModel):
    """Request model for RAG query"""
    question: str
    session_id: Optional[str] = None


class SourceItem(BaseModel):
    """Source item in query response"""
    chunk_id: str
    content: str
    score: float


class QueryResponse(BaseModel):
    """Response model for RAG query"""
    answer: str
    sources: List[SourceItem]


class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class DatasetInfo(BaseModel):
    """Dataset information"""
    dataset: str
    document_count: int
    chunk_count: int
    documents: List[Dict[str, Any]]


@router.post("/documents/add", response_model=AddDocumentResponse)
async def add_document(request: AddDocumentRequest):
    """
    Add a document to the RAG store.
    
    Args:
        request: Document content and metadata
        
    Returns:
        Document ID, chunks, and status
    """
    try:
        result = await rag_helper.add_document(
            content=request.content,
            metadata=request.metadata or {}
        )
        
        return AddDocumentResponse(
            status="success",
            document_id=result["document_id"],
            chunks=result["chunks"],
            message="Document added to RAG."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG store and generate an answer.
    
    Args:
        request: Query question and optional session_id
        
    Returns:
        Answer and relevant sources
    """
    try:
        result = await rag_helper.query(
            question=request.question,
            session_id=request.session_id
        )
        
        # Transform sources to match expected format
        sources = [
            SourceItem(
                chunk_id=src.get("chunk_id", ""),
                content=src.get("content", ""),
                score=src.get("similarity", 0.0)
            )
            for src in result.get("sources", [])
        ]
        
        return QueryResponse(
            answer=result.get("answer", "No answer generated."),
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all documents in the RAG store.
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = rag_helper.list_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document from the RAG store.
    
    Args:
        doc_id: Document ID to delete
        
    Returns:
        Status message
    """
    try:
        rag_helper.delete_document(doc_id)
        return {
            "status": "success",
            "message": f"Document '{doc_id}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/datasets", response_model=List[str])
async def list_datasets():
    """
    List all available datasets in the RAG store.
    
    Returns:
        List of dataset names
    """
    try:
        return rag_helper.get_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")


@router.get("/datasets/{dataset_name}", response_model=DatasetInfo)
async def get_dataset_info(dataset_name: str):
    """
    Get information about a specific dataset.
    
    Args:
        dataset_name: Name of the dataset
        
    Returns:
        Dataset statistics and document list
    """
    try:
        return rag_helper.get_dataset_info(dataset_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset info: {str(e)}")
