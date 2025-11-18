from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.search.web_search import WebSearch
from backend.connectors.search.search_advanced import AdvancedSearch


router = APIRouter()


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=50)
    with_summary: Optional[bool] = Field(False, description="Include summary of results")


class SearchResult(BaseModel):
    """Model for a single search result."""
    title: str
    link: str
    snippet: str


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    query: str
    engine: str
    results: List[Dict[str, str]]
    total_results: int
    status: str
    summary: Optional[str] = None
    error: Optional[str] = None


# Initialize web search
web_search = WebSearch()
advanced_search = AdvancedSearch()


@router.post("/", response_model=SearchResponse)
async def search_web(request: SearchRequest):
    """
    Perform a web search using DuckDuckGo.
    
    Args:
        request: SearchRequest with query and options
        
    Returns:
        SearchResponse: Structured search results
        
    Raises:
        HTTPException: If search fails
    """
    try:
        # Perform search with or without summary
        if request.with_summary:
            result = await web_search.search_with_summary(
                query=request.query,
                max_results=request.max_results
            )
        else:
            result = await web_search.search(
                query=request.query,
                max_results=request.max_results
            )
        
        return SearchResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/quick")
async def quick_search(query: str):
    """
    Get a quick answer from search results.
    
    Args:
        query: Search query string
        
    Returns:
        dict: Quick answer with top result
    """
    try:
        answer = await web_search.quick_answer(query)
        return {
            "query": query,
            "answer": answer,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick search failed: {str(e)}"
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


@router.post("/batch")
async def batch_search(queries: List[str], max_results_per_query: int = 5):
    """
    Perform multiple searches in batch.
    
    Args:
        queries: List of search queries
        max_results_per_query: Maximum results per query
        
    Returns:
        dict: Batch search results
    """
    try:
        if len(queries) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 queries allowed in batch"
            )
        
        results = []
        for query in queries:
            result = await web_search.search(query, max_results=max_results_per_query)
            results.append(result)
        
        return {
            "total_queries": len(queries),
            "results": results,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch search failed: {str(e)}"
        )


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search endpoint."""
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: Optional[int] = Field(10, description="Maximum number of results per engine", ge=1, le=50)
    engines: Optional[List[str]] = Field(None, description="List of engines to use: google, brave, duckduckgo. If None, uses all available.")


class AdvancedSearchResponse(BaseModel):
    """Response model for advanced search endpoint."""
    query: str
    results: List[Dict[str, str]]
    total: int
    sources: List[str]
    errors: Optional[List[str]] = None


@router.post("/advanced", response_model=AdvancedSearchResponse)
async def search_advanced(request: AdvancedSearchRequest):
    """
    Effectue une recherche avancée multi-moteurs (Google via Serper, Brave, DuckDuckGo).
    Fusionne et déduplique les résultats.
    
    Args:
        request: AdvancedSearchRequest avec query, max_results et engines optionnel
        
    Returns:
        AdvancedSearchResponse: Résultats fusionnés de plusieurs moteurs
        
    Raises:
        HTTPException: Si la recherche échoue complètement
    """
    try:
        engines = request.engines or ["google", "brave", "duckduckgo"]
        results_list = []
        
        # Effectuer les recherches selon les moteurs demandés
        if "google" in engines:
            google_results = await advanced_search.search_google(request.query, request.max_results)
            results_list.append(google_results)
        
        if "brave" in engines:
            brave_results = await advanced_search.search_brave(request.query, request.max_results)
            results_list.append(brave_results)
        
        if "duckduckgo" in engines:
            ddg_results = await advanced_search.search_duckduckgo(request.query, request.max_results)
            results_list.append(ddg_results)
        
        # Fusionner les résultats
        merged = advanced_search.merge_results(*results_list)
        
        if not merged.get("success") or not merged.get("results"):
            raise HTTPException(
                status_code=500,
                detail=f"Aucun résultat trouvé. Erreurs: {merged.get('errors', [])}"
            )
        
        return AdvancedSearchResponse(
            query=request.query,
            results=merged["results"],
            total=merged["total"],
            sources=merged.get("sources", []),
            errors=merged.get("errors")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced search failed: {str(e)}"
        )


@router.get("/advanced/all")
async def search_all_engines(query: str, max_results: int = 10):
    """
    Recherche rapide sur tous les moteurs disponibles.
    
    Args:
        query: Search query string
        max_results: Maximum results per engine
        
    Returns:
        dict: Merged results from all engines
    """
    try:
        result = await advanced_search.search_all(query, max_results)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {result.get('errors', [])}"
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search all engines failed: {str(e)}"
        )