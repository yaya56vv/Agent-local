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
        self.timeout = 8  # seconds (as per Mission 3 specs)
        self.max_retries = 2
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
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1 + attempt)  # Simple backoff
                    continue
                # Return empty results on final failure
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
                    await asyncio.sleep(1 + attempt)
                    continue
                # Return empty results on final failure
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
