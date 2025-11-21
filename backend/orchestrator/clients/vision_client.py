"""
Vision MCP Client
Handles communication with the Vision MCP server for image analysis operations.
"""


class VisionClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def analyze_image(self, image: bytes) -> dict:
        """
        TODO: Envoie l'image au serveur MCP Vision pour analyse.
        Enverra une requête HTTP asynchrone au service MCP Vision.
        
        Args:
            image: Image bytes to analyze
            
        Returns:
            dict: Analysis results from Vision MCP server
        """
        pass

    async def extract_text(self, image: bytes) -> dict:
        """
        TODO: OCR via MCP Vision.
        Enverra une requête HTTP asynchrone au service MCP Vision pour extraction de texte.
        
        Args:
            image: Image bytes to extract text from
            
        Returns:
            dict: Extracted text results from Vision MCP server
        """
        pass

    async def analyze_screenshot(self, image: bytes) -> dict:
        """
        TODO: Analyse de capture d'écran.
        Enverra une requête HTTP asynchrone au service MCP Vision pour analyse de screenshot.
        
        Args:
            image: Screenshot bytes to analyze
            
        Returns:
            dict: Screenshot analysis results from Vision MCP server
        """
        pass
