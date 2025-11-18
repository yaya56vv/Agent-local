import asyncio
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import aiohttp
from bs4 import BeautifulSoup


class WebSearch:
    """
    Professional web search module using DuckDuckGo HTML scraping.
    No API key required.
    """

    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.timeout = 10  # seconds
        self.max_retries = 3
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            dict: Structured search results
            {
                "query": "original query",
                "engine": "duckduckgo",
                "results": [
                    {
                        "title": "Result title",
                        "link": "https://...",
                        "snippet": "Description text..."
                    }
                ],
                "total_results": 5
            }
        """
        for attempt in range(self.max_retries):
            try:
                results = await self._perform_search(query, max_results)
                return {
                    "query": query,
                    "engine": "duckduckgo",
                    "results": results,
                    "total_results": len(results),
                    "status": "success"
                }
            
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    "query": query,
                    "engine": "duckduckgo",
                    "results": [],
                    "total_results": 0,
                    "status": "error",
                    "error": f"Network error: {str(e)}"
                }
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {
                    "query": query,
                    "engine": "duckduckgo",
                    "results": [],
                    "total_results": 0,
                    "status": "error",
                    "error": f"Search error: {str(e)}"
                }
        
        return {
            "query": query,
            "engine": "duckduckgo",
            "results": [],
            "total_results": 0,
            "status": "error",
            "error": "Max retries exceeded"
        }

    async def _perform_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Internal method to perform the actual search.
        
        Args:
            query: Search query
            max_results: Maximum results to extract
            
        Returns:
            List of result dictionaries
        """
        # Prepare search parameters
        params = {
            "q": query,
            "b": "",  # Start from beginning
            "kl": "us-en"  # Region
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                data=params,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=True
            ) as response:
                
                # Check for rate limiting or blocks
                if response.status == 429:
                    raise Exception("Rate limited by DuckDuckGo (429)")
                
                if response.status == 403:
                    raise Exception("Access forbidden by DuckDuckGo (403)")
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                html = await response.text()
                
                # Parse results
                return self._parse_results(html, max_results)

    def _parse_results(self, html: str, max_results: int) -> List[Dict[str, str]]:
        """
        Parse DuckDuckGo HTML results.
        
        Args:
            html: Raw HTML response
            max_results: Maximum results to extract
            
        Returns:
            List of parsed results
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all result divs
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs[:max_results]:
            try:
                # Extract title and link
                title_tag = div.find('a', class_='result__a')
                if not title_tag:
                    continue
                
                title = self._clean_text(title_tag.get_text())
                link = title_tag.get('href', '')
                
                # Extract snippet
                snippet_tag = div.find('a', class_='result__snippet')
                snippet = ""
                if snippet_tag:
                    snippet = self._clean_text(snippet_tag.get_text())
                
                # Only add if we have at least title and link
                if title and link:
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
            
            except Exception as e:
                # Skip malformed results
                continue
        
        return results

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and special characters.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    async def search_with_summary(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform search and provide a summary of results.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            dict: Search results with summary
        """
        search_result = await self.search(query, max_results)
        
        if search_result["status"] == "success" and search_result["results"]:
            # Create a simple summary
            summary = f"Found {search_result['total_results']} results for '{query}'.\n\n"
            summary += "Top results:\n"
            
            for i, result in enumerate(search_result["results"][:3], 1):
                summary += f"{i}. {result['title']}\n"
                if result['snippet']:
                    summary += f"   {result['snippet'][:100]}...\n"
                summary += f"   {result['link']}\n\n"
            
            search_result["summary"] = summary
        else:
            search_result["summary"] = f"No results found for '{query}'"
        
        return search_result

    async def quick_answer(self, query: str) -> str:
        """
        Get a quick text answer from search results.
        
        Args:
            query: Search query
            
        Returns:
            str: Quick answer text
        """
        result = await self.search(query, max_results=3)
        
        if result["status"] == "success" and result["results"]:
            top_result = result["results"][0]
            answer = f"**{top_result['title']}**\n\n"
            if top_result['snippet']:
                answer += f"{top_result['snippet']}\n\n"
            answer += f"Source: {top_result['link']}"
            return answer
        else:
            return f"No results found for: {query}"