"""
Module de recherche avancé avec support multi-moteurs.
Supporte Serper.dev (Google), Brave Search et DuckDuckGo.
"""

import httpx
from typing import List, Dict, Any, Optional
import asyncio
from backend.config.settings import settings


class AdvancedSearch:
    """Classe pour effectuer des recherches avancées sur plusieurs moteurs."""
    
    def __init__(self):
        """Initialise le client de recherche avancé."""
        self.serper_api_key = getattr(settings, 'SERPER_API_KEY', None)
        self.brave_api_key = getattr(settings, 'BRAVE_API_KEY', None)
        self.timeout = 10.0
    
    async def search_google(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Recherche via Serper.dev (API Google Search).
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Dict avec les résultats formatés
        """
        if not self.serper_api_key:
            return {
                "success": False,
                "error": "SERPER_API_KEY non configurée",
                "results": []
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": query,
                        "num": max_results
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Erreur API Serper: {response.status_code}",
                        "results": []
                    }
                
                data = response.json()
                results = []
                
                # Parser les résultats organiques
                for item in data.get("organic", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google"
                    })
                
                return {
                    "success": True,
                    "results": results,
                    "total": len(results)
                }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Timeout lors de la recherche Google",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur recherche Google: {str(e)}",
                "results": []
            }
    
    async def search_brave(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Recherche via Brave Search API.
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Dict avec les résultats formatés
        """
        if not self.brave_api_key:
            return {
                "success": False,
                "error": "BRAVE_API_KEY non configurée",
                "results": []
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.brave_api_key
                    },
                    params={
                        "q": query,
                        "count": max_results
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Erreur API Brave: {response.status_code}",
                        "results": []
                    }
                
                data = response.json()
                results = []
                
                # Parser les résultats web
                for item in data.get("web", {}).get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "source": "brave"
                    })
                
                return {
                    "success": True,
                    "results": results,
                    "total": len(results)
                }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Timeout lors de la recherche Brave",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur recherche Brave: {str(e)}",
                "results": []
            }
    
    async def search_duckduckgo(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Recherche via DuckDuckGo (sans API key requise).
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Dict avec les résultats formatés
        """
        try:
            from duckduckgo_search import AsyncDDGS
            
            results = []
            async with AsyncDDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                async for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                        "source": "duckduckgo"
                    })
                    
                    if len(results) >= max_results:
                        break
            
            return {
                "success": True,
                "results": results,
                "total": len(results)
            }
        
        except ImportError:
            return {
                "success": False,
                "error": "Module duckduckgo_search non installé",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur recherche DuckDuckGo: {str(e)}",
                "results": []
            }
    
    def merge_results(self, *results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fusionne les résultats de plusieurs moteurs de recherche.
        Déduplique par URL et conserve les meilleures sources.
        
        Args:
            *results: Résultats de différents moteurs
            
        Returns:
            Dict avec résultats fusionnés et dédupliqués
        """
        merged = []
        seen_urls = set()
        errors = []
        
        # Ordre de priorité: Google > Brave > DuckDuckGo
        priority_order = ["google", "brave", "duckduckgo"]
        
        # Trier les résultats par priorité
        sorted_results = sorted(
            results,
            key=lambda x: priority_order.index(
                x.get("results", [{}])[0].get("source", "duckduckgo")
            ) if x.get("results") else 999
        )
        
        for result in sorted_results:
            if not result.get("success", False):
                if result.get("error"):
                    errors.append(result["error"])
                continue
            
            for item in result.get("results", []):
                url = item.get("url", "")
                
                # Dédupliquer par URL
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    merged.append(item)
        
        return {
            "success": len(merged) > 0,
            "results": merged,
            "total": len(merged),
            "sources": list(set(item.get("source") for item in merged)),
            "errors": errors if errors else None
        }
    
    async def search_all(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Effectue une recherche sur tous les moteurs disponibles et fusionne les résultats.
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats par moteur
            
        Returns:
            Dict avec résultats fusionnés de tous les moteurs
        """
        # Lancer toutes les recherches en parallèle
        tasks = [
            self.search_google(query, max_results),
            self.search_brave(query, max_results),
            self.search_duckduckgo(query, max_results)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                valid_results.append({
                    "success": False,
                    "error": str(result),
                    "results": []
                })
        
        # Fusionner tous les résultats
        merged = self.merge_results(*valid_results)
        merged["query"] = query
        
        return merged

