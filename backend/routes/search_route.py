"""
Search Routes - API endpoints for web search operations
Provides unified endpoint for web search with multiple engines
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.search.web_search import WebSearch

router = APIRouter()

# Initialize web search
web_search = WebSearch()


class SearchRequest(BaseModel):
    """Request model for web search endpoint."""
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: Optional[int] = Field(5, description="Maximum number of results", ge=1, le=50)


class SearchResultItem(BaseModel):
    """Model for a single search result."""
    title: str
    url: str
    snippet: str
    source: str
    score: float


class SearchResponse(BaseModel):
    """Response model for web search endpoint."""
    query: str
    results: List[SearchResultItem]


@router.post("/web", response_model=SearchResponse)
async def search_web(request: SearchRequest):
    """
    Perform a web search using DuckDuckGo.
    
    Args:
        request: SearchRequest with query and max_results
        
    Returns:
        SearchResponse: Structured search results with unified format
    """
    try:
        # Perform search
        result = await web_search.search(
            query=request.query,
            max_results=request.max_results
        )
        
        # Transform to unified format
        results = []
        for idx, item in enumerate(result.get("results", [])):
            results.append(SearchResultItem(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source="duckduckgo",
                score=1.0 - (idx * 0.1)  # Simple scoring based on rank
            ))
        
        return SearchResponse(
            query=request.query,
            results=results
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for search service.
    
    Returns:
        dict: Health status
    """
    try:
        # Test with a simple query
        test_result = await web_search.search("test", max_results=1)
        
        if test_result["status"] == "success":
            return {
                "status": "healthy",
                "service": "web_search",
                "engine": "duckduckgo"
            }
        else:
            return {
                "status": "degraded",
                "service": "web_search",
                "engine": "duckduckgo",
                "message": "Search working but may have issues"
            }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "web_search",
            "error": str(e)
        }