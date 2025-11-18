"""
RAG Store - Local document storage with Gemini embeddings
Stores documents in SQLite with vector embeddings for semantic search
"""

import sqlite3
import json
import os
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import aiohttp
import asyncio
from datetime import datetime


class RAGStore:
    """
    RAG Store for managing documents with embeddings.
    Uses SQLite for storage and Gemini API for embeddings.
    """
    
    def __init__(self, db_path: str = "rag/rag.db"):
        """
        Initialize RAG store with database path.
        
        Args:
            db_path: Path to SQLite database file (relative to project root)
        """
        # Ensure absolute path
        if not os.path.isabs(db_path):
            base_dir = Path(__file__).resolve().parents[2]  # C:\AGENT LOCAL
            db_path = str(base_dir / db_path)
        
        self.db_path = db_path
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.embedding_model = "models/text-embedding-004"
        self.embedding_url = f"https://generativelanguage.googleapis.com/v1beta/{self.embedding_model}:embedContent"
        
        # Create directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_db()
    
    def init_db(self) -> None:
        """
        Initialize SQLite database with required tables.
        Creates tables for documents, chunks, and embeddings.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                dataset TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Chunks table (for splitting large documents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk TEXT NOT NULL,
                embedding TEXT,
                order_index INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_dataset 
            ON documents(dataset)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document 
            ON chunks(document_id)
        """)
        
        conn.commit()
        conn.close()
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector from Gemini API.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        payload = {
            "model": self.embedding_model,
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        params = {"key": self.gemini_api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.embedding_url,
                json=payload,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini embedding API error: {error_text}")
                
                data = await response.json()
                embedding = data.get("embedding", {}).get("values", [])
                
                if not embedding:
                    raise Exception("No embedding returned from Gemini API")
                
                return embedding
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    async def add_document(
        self,
        dataset: str,
        filename: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the RAG store with embeddings.
        
        Args:
            dataset: Dataset/collection name
            filename: Name of the document
            content: Document content
            metadata: Optional metadata dictionary
            
        Returns:
            Document ID
        """
        # Generate document ID
        doc_id = hashlib.sha256(f"{dataset}:{filename}:{content[:100]}".encode()).hexdigest()
        
        # Prepare metadata
        metadata_json = json.dumps(metadata or {})
        now = datetime.utcnow().isoformat() + "Z"
        
        # Store document
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (id, dataset, filename, content, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, dataset, filename, content, metadata_json, now, now))
        
        # Chunk the content
        chunks = self._chunk_text(content)
        
        # Store chunks with embeddings
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{idx}"
            
            # Get embedding
            embedding = await self._get_embedding(chunk)
            embedding_json = json.dumps(embedding)
            
            cursor.execute("""
                INSERT OR REPLACE INTO chunks
                (id, document_id, chunk, embedding, order_index, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (chunk_id, doc_id, chunk, embedding_json, idx, now))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    async def query(
        self,
        dataset: str,
        question: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the RAG store for relevant documents.
        
        Args:
            dataset: Dataset to search in
            question: Query question
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        # Get question embedding
        question_embedding = await self._get_embedding(question)
        
        # Get all chunks from dataset
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.chunk, c.embedding, d.filename, d.metadata
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.dataset = ?
        """, (dataset,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Calculate similarities
        results = []
        for row in rows:
            chunk_id, content, embedding_json, filename, metadata_json = row
            
            if not embedding_json:
                continue
            
            chunk_embedding = json.loads(embedding_json)
            similarity = self._cosine_similarity(question_embedding, chunk_embedding)
            
            results.append({
                "chunk_id": chunk_id,
                "content": content,
                "filename": filename,
                "metadata": json.loads(metadata_json) if metadata_json else {},
                "similarity": similarity
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def delete_dataset(self, dataset: str) -> None:
        """
        Delete all documents in a dataset.
        
        Args:
            dataset: Dataset name to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get document IDs
        cursor.execute("SELECT id FROM documents WHERE dataset = ?", (dataset,))
        doc_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete chunks
        for doc_id in doc_ids:
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
        
        # Delete documents
        cursor.execute("DELETE FROM documents WHERE dataset = ?", (dataset,))
        
        conn.commit()
        conn.close()
    
    def list_datasets(self) -> List[str]:
        """
        List all available datasets.
        
        Returns:
            List of dataset names
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT dataset FROM documents ORDER BY dataset")
        datasets = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return datasets
    
    def get_dataset_info(self, dataset: str) -> Dict[str, Any]:
        """
        Get information about a dataset.
        
        Args:
            dataset: Dataset name
            
        Returns:
            Dictionary with dataset statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count documents
        cursor.execute(
            "SELECT COUNT(*) FROM documents WHERE dataset = ?",
            (dataset,)
        )
        doc_count = cursor.fetchone()[0]
        
        # Count chunks
        cursor.execute("""
            SELECT COUNT(*) FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.dataset = ?
        """, (dataset,))
        chunk_count = cursor.fetchone()[0]
        
        # Get document list
        cursor.execute(
            "SELECT filename, created_at FROM documents WHERE dataset = ? ORDER BY created_at DESC",
            (dataset,)
        )
        documents = [{"filename": row[0], "created_at": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "dataset": dataset,
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "documents": documents
        }
    
    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of chunks with content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, chunk, order_index
            FROM chunks
            WHERE document_id = ?
            ORDER BY order_index
        """, (doc_id,))
        
        chunks = [
            {
                "id": row[0],
                "content": row[1],
                "order_index": row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return chunks
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents across all datasets.
        
        Returns:
            List of all documents with metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, dataset, filename, content, metadata, created_at
            FROM documents
            ORDER BY created_at DESC
        """)
        
        documents = []
        for row in cursor.fetchall():
            doc_id, dataset, filename, content, metadata_json, created_at = row
            documents.append({
                "id": doc_id,
                "content": content,
                "metadata": {
                    "dataset": dataset,
                    "filename": filename,
                    **(json.loads(metadata_json) if metadata_json else {})
                },
                "created_at": created_at
            })
        
        conn.close()
        return documents
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a specific document and its chunks.
        
        Args:
            doc_id: Document ID to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete chunks first (foreign key constraint)
        cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
        
        # Delete document
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        
        conn.commit()
        conn.close()