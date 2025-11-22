"""
Vision MCP Client
Handles communication with the Vision MCP server for image analysis operations.
"""
import httpx
import base64


class VisionClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def analyze_image(self, image: bytes) -> dict:
        """
        Envoie l'image au serveur MCP Vision pour analyse.
        
        Args:
            image: Image bytes to analyze
            
        Returns:
            dict: Analysis results from Vision MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Encode image to base64
                image_b64 = base64.b64encode(image).decode('utf-8')
                
                response = await client.post(
                    f"{self.base_url}/vision/analyze",
                    json={"image": image_b64}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def extract_text(self, image: bytes) -> dict:
        """
        OCR via MCP Vision.
        
        Args:
            image: Image bytes to extract text from
            
        Returns:
            dict: Extracted text results from Vision MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Encode image to base64
                image_b64 = base64.b64encode(image).decode('utf-8')
                
                response = await client.post(
                    f"{self.base_url}/vision/ocr",
                    json={"image": image_b64}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def analyze_screenshot(self, image: bytes) -> dict:
        """
        Analyse de capture d'écran.
        
        Args:
            image: Screenshot bytes to analyze
            
        Returns:
            dict: Screenshot analysis results from Vision MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Encode image to base64
                image_b64 = base64.b64encode(image).decode('utf-8')
                
                response = await client.post(
                    f"{self.base_url}/vision/analyze_screenshot",
                    json={"image": image_b64}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_active_context(self) -> dict:
        """
        Récupère le contexte vision actif (dernières analyses, etc.)
        
        Returns:
            dict: Active vision context
        """
        # Pour l'instant, retourne un contexte vide
        # À implémenter selon les besoins (historique des analyses, etc.)
        return {
            "status": "active",
            "recent_analyses": [],
            "vision_state": "ready"
        }

