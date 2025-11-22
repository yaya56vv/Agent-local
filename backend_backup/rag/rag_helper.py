"""
RAG Helper - Utility functions for RAG operations
Provides easy-to-use functions for orchestrator integration
"""

from typing import List, Dict, Any, Optional
from backend.rag.rag_store import RAGStore


class RAGHelper:
    """Helper class for RAG operations - easy integration with orchestrator"""
    
    def __init__(self):
        """Initialize RAG helper with store"""
        self.rag_store = RAGStore()
    
    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to RAG store.
        
        Args:
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Dict with document_id and chunks
        """
        # Generate a simple filename from metadata or use default
        filename = metadata.get("source", "document") if metadata else "document"
        dataset = metadata.get("dataset", "default") if metadata else "default"
        
        doc_id = await self.rag_store.add_document(
            dataset=dataset,
            filename=filename,
            content=content,
            metadata=metadata
        )
        
        # Get chunks for this document
        chunks = self.rag_store.get_document_chunks(doc_id)
        
        return {
            "document_id": doc_id,
            "chunks": [chunk["content"] for chunk in chunks]
        }
    
    async def query(
        self,
        question: str,
        session_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query the RAG store and generate an answer.
        
        Args:
            question: Question to answer
            session_id: Optional session ID for conversation context
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Dict with answer and sources
        """
        # Use default dataset for now
        dataset = "default"
        
        # Retrieve relevant chunks
        sources = await self.rag_store.query(
            dataset=dataset,
            question=question,
            top_k=top_k
        )
        
        if not sources:
            return {
                "answer": "Aucun document pertinent trouvé dans la base de connaissances.",
                "sources": []
            }
        
        # Build context from sources
        context = "\n\n".join([
            f"[Source {i+1}]\n{src['content']}"
            for i, src in enumerate(sources)
        ])
        
        # For now, return a simple answer based on sources
        # TODO: Integrate with LLM for better answers
        answer = f"Voici les informations pertinentes trouvées :\n\n{context}"
        
        # Format sources with score
        formatted_sources = [
            {
                "chunk_id": src["chunk_id"],
                "content": src["content"],
                "similarity": src["similarity"]
            }
            for src in sources
        ]
        
        return {
            "answer": answer,
            "sources": formatted_sources
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the RAG store.
        
        Returns:
            List of documents with metadata
        """
        return self.rag_store.list_all_documents()
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the RAG store.
        
        Args:
            doc_id: Document ID to delete
        """
        self.rag_store.delete_document(doc_id)
    
    def get_datasets(self) -> List[str]:
        """Get list of all datasets"""
        return self.rag_store.list_datasets()
    
    def get_dataset_info(self, dataset: str) -> Dict[str, Any]:
        """Get information about a dataset"""
        return self.rag_store.get_dataset_info(dataset)


# Global instance for easy import
rag_helper = RAGHelper()

