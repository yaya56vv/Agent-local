"""
Search MCP Client
Handles communication with the Search MCP server for web search operations.
"""
import httpx


class SearchClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def search_duckduckgo(self, query: str) -> dict:
        """
        Recherche via DuckDuckGo.
        
        Args:
            query: Search query string
            
        Returns:
            dict: DuckDuckGo search results from Search MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/duckduckgo",
                    params={"query": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def search_google(self, query: str) -> dict:
        """
        Recherche via Google.
        
        Args:
            query: Search query string
            
        Returns:
            dict: Google search results from Search MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/google",
                    params={"query": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def search_brave(self, query: str) -> dict:
        """
        Recherche via Brave.
        
        Args:
            query: Search query string
            
        Returns:
            dict: Brave search results from Search MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/brave",
                    params={"query": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def search_all(self, query: str) -> dict:
        """
        Recherche sur tous les moteurs disponibles.
        
        Args:
            query: Search query string
            
        Returns:
            dict: Combined search results from all search engines via Search MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/all",
                    params={"query": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

