"""
MCP RAG Client - HTTP client for RAG operations
"""
import httpx
from typing import Dict, Any, Optional, List


class RagClient:
    """Client for MCP RAG Service"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        """
        Initialize the RAG MCP client.
        
        Args:
            base_url: Base URL of the MCP RAG service
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def add_document(
        self,
        dataset: str,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the RAG store with embeddings.
        
        Args:
            dataset: Dataset name
            document_id: Document identifier (used as filename)
            text: Document text content
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rag/add_document",
                json={
                    "dataset": dataset,
                    "document_id": document_id,
                    "text": text,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("document_id", document_id)
    
    async def query(
        self,
        dataset: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the RAG store for relevant documents.
        
        Args:
            dataset: Dataset name
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with similarity scores
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rag/query",
                json={
                    "dataset": dataset,
                    "query": query,
                    "top_k": top_k
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("results", [])
    
    async def list_documents(
        self,
        dataset: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List documents in the RAG store.
        
        Args:
            dataset: Optional dataset name to filter by
            
        Returns:
            List of documents
        """
        params = {}
        if dataset:
            params["dataset"] = dataset
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rag/list_documents",
                params=params if params else None
            )
            response.raise_for_status()
            result = response.json()
            return result.get("documents", [])
    
    async def list_datasets(self) -> List[str]:
        """
        List all available datasets.
        
        Returns:
            List of dataset names
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rag/list_datasets"
            )
            response.raise_for_status()
            result = response.json()
            return result.get("datasets", [])
    
    async def get_dataset_info(self, dataset: str) -> Dict[str, Any]:
        """
        Get information about a dataset.
        
        Args:
            dataset: Dataset name
            
        Returns:
            Dataset statistics and information
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rag/get_dataset_info",
                params={"dataset": dataset}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("info", {})
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document from the RAG store.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Success status
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/rag/delete_document",
                params={"document_id": document_id}
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_dataset(self, dataset: str) -> Dict[str, Any]:
        """
        Delete an entire dataset.
        
        Args:
            dataset: Dataset name to delete
            
        Returns:
            Success status
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/rag/delete_dataset",
                params={"dataset": dataset}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of chunks
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rag/get_document_chunks",
                params={"document_id": document_id}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("chunks", [])
    
    async def cleanup_memory(self, retention_days: int = 1) -> Dict[str, Any]:
        """
        Clean up old ephemeral memory (scratchpad dataset).
        This is a convenience method that deletes old documents from the scratchpad.
        
        Args:
            retention_days: Number of days to retain (not implemented in server yet)
            
        Returns:
            Success status
        """
        # For now, this is a placeholder that would need server-side implementation
        # In the meantime, we can delete the scratchpad dataset entirely
        try:
            result = await self.delete_dataset("scratchpad")
            return {
                "status": "success",
                "message": f"Scratchpad cleaned (retention_days={retention_days})",
                "details": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to cleanup memory: {str(e)}"
            }
