"""
Documents MCP Client
Handles communication with the Documents MCP server
"""
import httpx
from typing import Dict, Any, Optional


class DocumentsClient:
    """Client for MCP Documents Service"""
    
    def __init__(self, base_url: str = "http://localhost:8009"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def generate_document(
        self,
        content: str,
        title: str = "Document",
        format: str = "txt",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Génère un document
        
        Args:
            content: Contenu du document
            title: Titre du document
            format: Format (txt, md, html)
            metadata: Métadonnées optionnelles
            
        Returns:
            Document généré
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/documents/generate",
                json={
                    "content": content,
                    "title": title,
                    "format": format,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def fill_template(
        self,
        template: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Remplit un template
        
        Args:
            template: Template avec placeholders
            data: Données à insérer
            
        Returns:
            Document rempli
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/documents/fill",
                json={
                    "template": template,
                    "data": data
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_recent_documents(self) -> Dict[str, Any]:
        """
        Récupère les documents récents
        
        Returns:
            Contexte documents récents
        """
        # Pour l'instant, retourne un contexte vide
        # À implémenter selon les besoins (historique des documents générés, etc.)
        return {
            "status": "active",
            "recent_documents": [],
            "active_templates": [],
            "documents_state": "ready"
        }
