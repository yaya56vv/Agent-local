"""
MCP Search Service - FastAPI Server
Provides HTTP endpoints for web search operations using WebSearch and AdvancedSearch
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.connectors.search.web_search import WebSearch
from backend.connectors.search.search_advanced import AdvancedSearch

# Initialize FastAPI app
app = FastAPI(
    title="MCP Search Service",
    description="Web search service for MCP protocol",
    version="1.0.0"
)

# Initialize search engines
web_search = WebSearch()
advanced_search = AdvancedSearch()


# Pydantic models for request bodies
class SearchRequest(BaseModel):
    query: str
    max_results: int = 10


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "MCP Search",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/search/duckduckgo")
async def search_duckduckgo(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Search using DuckDuckGo (no API key required).
    
    Args:
        query: Search query string
        max_results: Maximum number of results (1-50)
        
    Returns:
        Search results with titles, links, and snippets
        
    Raises:
        HTTPException: If search fails
    """
    try:
        result = await web_search.search(query, max_results)
        
        # Normalize response format
        normalized_results = []
        for item in result.get("results", []):
            normalized_results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": "duckduckgo"
            })
        
        return JSONResponse(content={
            "status": "success",
            "query": query,
            "engine": "duckduckgo",
            "results": normalized_results,
            "total": len(normalized_results)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/google")
async def search_google(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Search using Google via Serper.dev API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (1-50)
        
    Returns:
        Search results with titles, links, and snippets
        
    Raises:
        HTTPException: If search fails or API key not configured
    """
    try:
        result = await advanced_search.search_google(query, max_results)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            if "non configurée" in error_msg or "not configured" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="SERPER_API_KEY not configured. Please set it in .env file."
                )
            raise HTTPException(status_code=500, detail=error_msg)
        
        return JSONResponse(content={
            "status": "success",
            "query": query,
            "engine": "google",
            "results": result.get("results", []),
            "total": result.get("total", 0)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/brave")
async def search_brave(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Search using Brave Search API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (1-50)
        
    Returns:
        Search results with titles, links, and snippets
        
    Raises:
        HTTPException: If search fails or API key not configured
    """
    try:
        result = await advanced_search.search_brave(query, max_results)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            if "non configurée" in error_msg or "not configured" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="BRAVE_API_KEY not configured. Please set it in .env file."
                )
            raise HTTPException(status_code=500, detail=error_msg)
        
        return JSONResponse(content={
            "status": "success",
            "query": query,
            "engine": "brave",
            "results": result.get("results", []),
            "total": result.get("total", 0)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/all")
async def search_all(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, description="Maximum results per engine", ge=1, le=20)
):
    """
    Search across all available engines and merge results.
    Deduplicates by URL and prioritizes: Google > Brave > DuckDuckGo.
    
    Args:
        query: Search query string
        max_results: Maximum results per engine (1-20)
        
    Returns:
        Merged and deduplicated search results from all engines
    """
    try:
        result = await advanced_search.search_all(query, max_results)
        
        return JSONResponse(content={
            "status": "success" if result.get("success") else "partial",
            "query": result.get("query", query),
            "engine": "multi",
            "results": result.get("results", []),
            "total": result.get("total", 0),
            "sources": result.get("sources", []),
            "errors": result.get("errors")
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints
@app.get("/search/health")
async def health_check():
    """
    Detailed health check with API key validation.
    
    Returns:
        Service health status and API configuration
    """
    try:
        has_serper = bool(advanced_search.serper_api_key)
        has_brave = bool(advanced_search.brave_api_key)
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "MCP Search",
            "version": "1.0.0",
            "engines": {
                "duckduckgo": {
                    "available": True,
                    "requires_api_key": False
                },
                "google": {
                    "available": has_serper,
                    "requires_api_key": True,
                    "configured": has_serper
                },
                "brave": {
                    "available": has_brave,
                    "requires_api_key": True,
                    "configured": has_brave
                }
            }
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.post("/search/batch")
async def batch_search(queries: List[str], engine: str = "duckduckgo", max_results: int = 5):
    """
    Perform multiple searches in batch.
    
    Args:
        queries: List of search queries
        engine: Search engine to use (duckduckgo, google, brave, all)
        max_results: Maximum results per query
        
    Returns:
        Results for all queries
    """
    try:
        if len(queries) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 queries per batch request"
            )
        
        results = []
        
        for query in queries:
            if engine == "duckduckgo":
                result = await web_search.search(query, max_results)
                normalized = []
                for item in result.get("results", []):
                    normalized.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "duckduckgo"
                    })
                results.append({
                    "query": query,
                    "results": normalized,
                    "total": len(normalized)
                })
            
            elif engine == "google":
                result = await advanced_search.search_google(query, max_results)
                results.append({
                    "query": query,
                    "results": result.get("results", []),
                    "total": result.get("total", 0),
                    "success": result.get("success", False)
                })
            
            elif engine == "brave":
                result = await advanced_search.search_brave(query, max_results)
                results.append({
                    "query": query,
                    "results": result.get("results", []),
                    "total": result.get("total", 0),
                    "success": result.get("success", False)
                })
            
            elif engine == "all":
                result = await advanced_search.search_all(query, max_results)
                results.append({
                    "query": query,
                    "results": result.get("results", []),
                    "total": result.get("total", 0),
                    "sources": result.get("sources", [])
                })
            
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown engine: {engine}. Use: duckduckgo, google, brave, or all"
                )
        
        return JSONResponse(content={
            "status": "success",
            "engine": engine,
            "queries_count": len(queries),
            "results": results
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
