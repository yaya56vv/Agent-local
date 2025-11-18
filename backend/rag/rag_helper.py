"""
RAG Helper - Utility functions for RAG operations
Provides easy-to-use functions for orchestrator integration
"""

from typing import List, Dict, Any, Optional
from backend.rag.rag_store import RAGStore
from backend.connectors.local_llm.local_llm_connector import LocalLLMConnector, LocalLLMProvider
from backend.config.settings import settings


class RAGHelper:
    """Helper class for RAG operations - easy integration with orchestrator"""
    
    def __init__(self):
        """Initialize RAG helper with store and LLM connector"""
        self.rag_store = RAGStore()
        self.llm = LocalLLMConnector(
            provider=LocalLLMProvider.OLLAMA,
            base_url=settings.LOCAL_LLM_BASE_URL,
            model=settings.LOCAL_LLM_MODEL
        )
    
    async def answer_with_rag(
        self,
        dataset: str,
        question: str,
        top_k: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        This is the main function for orchestrator integration.
        Retrieves relevant chunks and generates an answer using local LLM.
        
        Args:
            dataset: Dataset name to search in
            question: Question to answer
            top_k: Number of relevant chunks to retrieve
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens for LLM response
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Retrieve relevant chunks
            sources = self.rag_store.query(
                dataset=dataset,
                question=question,
                top_k=top_k
            )
            
            if not sources:
                return {
                    "success": False,
                    "answer": f"Aucun document pertinent trouvé dans le dataset '{dataset}'.",
                    "sources": [],
                    "dataset": dataset
                }
            
            # Build context from sources
            context = "\n\n".join([
                f"[Source: {src['filename']}]\n{src['content']}"
                for src in sources
            ])
            
            # Build prompt for LLM
            system_prompt = """Tu es un assistant intelligent qui répond aux questions en te basant uniquement sur le contexte fourni.
Utilise seulement les informations du contexte pour répondre.
Si le contexte ne contient pas assez d'informations, dis-le clairement.
Sois concis, précis et professionnel."""
            
            prompt = f"""Contexte:
{context}

Question: {question}

Réponds à la question en te basant uniquement sur le contexte ci-dessus:"""
            
            # Generate answer using local LLM
            try:
                answer = await self.llm.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return {
                    "success": True,
                    "answer": answer,
                    "sources": sources,
                    "dataset": dataset,
                    "model": self.llm.model,
                    "provider": self.llm.provider.value
                }
            
            except Exception as llm_error:
                return {
                    "success": False,
                    "answer": f"Erreur LLM: {str(llm_error)}\n\nSources trouvées mais impossible de générer une réponse. Vérifiez que votre LLM local est en cours d'exécution.",
                    "sources": sources,
                    "dataset": dataset,
                    "error": str(llm_error)
                }
        
        except Exception as e:
            return {
                "success": False,
                "answer": f"Erreur lors de la recherche RAG: {str(e)}",
                "sources": [],
                "dataset": dataset,
                "error": str(e)
            }
    
    async def quick_search(
        self,
        dataset: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Quick search without LLM generation.
        Returns only the relevant chunks.
        
        Args:
            dataset: Dataset to search in
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant chunks
        """
        try:
            return self.rag_store.query(
                dataset=dataset,
                question=query,
                top_k=top_k
            )
        except Exception as e:
            print(f"RAG search error: {e}")
            return []
    
    def add_document_sync(
        self,
        dataset: str,
        filename: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to RAG store (synchronous).
        
        Args:
            dataset: Dataset name
            filename: Document filename
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        return self.rag_store.add_document(
            dataset=dataset,
            filename=filename,
            content=content,
            metadata=metadata
        )
    
    def get_datasets(self) -> List[str]:
        """Get list of all datasets"""
        return self.rag_store.list_datasets()
    
    def get_dataset_info(self, dataset: str) -> Dict[str, Any]:
        """Get information about a dataset"""
        return self.rag_store.get_dataset_info(dataset)
    
    async def check_llm_available(self) -> bool:
        """Check if local LLM is available"""
        return await self.llm.is_available()


# Global instance for easy import
rag_helper = RAGHelper()


# Convenience function for orchestrator
async def answer_question_with_rag(
    dataset: str,
    question: str,
    top_k: int = 5
) -> str:
    """
    Simple function to answer a question with RAG.
    Returns just the answer text for easy integration.
    
    Args:
        dataset: Dataset to use
        question: Question to answer
        top_k: Number of sources to use
        
    Returns:
        Answer text
    """
    result = await rag_helper.answer_with_rag(
        dataset=dataset,
        question=question,
        top_k=top_k
    )
    return result.get("answer", "Erreur lors de la génération de la réponse.")
