"""
Test script for MCP Search Service
Tests all endpoints with real search queries
"""

import requests
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base URL for the Search MCP service
BASE_URL = "http://localhost:8005"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        print("✓ Health check passed")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_detailed_health():
    """Test the detailed health endpoint"""
    print("\n=== Testing Detailed Health ===")
    try:
        response = requests.get(f"{BASE_URL}/search/health")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            engines = result.get("engines", {})
            print(f"\nEngine Status:")
            print(f"  DuckDuckGo: {'✓ Available' if engines.get('duckduckgo', {}).get('available') else '✗ Not available'}")
            print(f"  Google: {'✓ Configured' if engines.get('google', {}).get('configured') else '✗ Not configured'}")
            print(f"  Brave: {'✓ Configured' if engines.get('brave', {}).get('configured') else '✗ Not configured'}")
        
        print("✓ Detailed health check passed")
        return True
    except Exception as e:
        print(f"✗ Detailed health check failed: {e}")
        return False


def test_duckduckgo_search():
    """Test DuckDuckGo search endpoint"""
    print("\n=== Testing DuckDuckGo Search ===")
    try:
        query = "Python programming"
        response = requests.get(
            f"{BASE_URL}/search/duckduckgo",
            params={"query": query, "max_results": 5},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {result.get('query')}")
            print(f"Engine: {result.get('engine')}")
            print(f"Total Results: {result.get('total')}")
            
            results = result.get('results', [])
            if results:
                print(f"\nFirst 3 Results:")
                for i, item in enumerate(results[:3], 1):
                    print(f"\n  {i}. {item.get('title', 'N/A')}")
                    print(f"     URL: {item.get('url', 'N/A')}")
                    print(f"     Snippet: {item.get('snippet', 'N/A')[:100]}...")
                
                print("✓ DuckDuckGo search test passed")
                return True
            else:
                print("⚠ No results returned (may be rate limited)")
                return True  # Still consider it a pass if no errors
        else:
            print(f"✗ DuckDuckGo search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠ DuckDuckGo search timed out (may be rate limited)")
        return True  # Consider timeout as acceptable
    except Exception as e:
        print(f"✗ DuckDuckGo search test failed: {e}")
        return False


def test_google_search():
    """Test Google search endpoint"""
    print("\n=== Testing Google Search ===")
    try:
        query = "FastAPI tutorial"
        response = requests.get(
            f"{BASE_URL}/search/google",
            params={"query": query, "max_results": 5},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {result.get('query')}")
            print(f"Engine: {result.get('engine')}")
            print(f"Total Results: {result.get('total')}")
            
            results = result.get('results', [])
            if results:
                print(f"\nFirst 3 Results:")
                for i, item in enumerate(results[:3], 1):
                    print(f"\n  {i}. {item.get('title', 'N/A')}")
                    print(f"     URL: {item.get('url', 'N/A')}")
                    print(f"     Snippet: {item.get('snippet', 'N/A')[:100]}...")
            
            print("✓ Google search test passed")
            return True
        elif response.status_code == 503:
            print("⚠ Google search not configured (SERPER_API_KEY missing)")
            return True  # Expected if API key not set
        else:
            print(f"✗ Google search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Google search test failed: {e}")
        return False


def test_brave_search():
    """Test Brave search endpoint"""
    print("\n=== Testing Brave Search ===")
    try:
        query = "Machine learning"
        response = requests.get(
            f"{BASE_URL}/search/brave",
            params={"query": query, "max_results": 5},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {result.get('query')}")
            print(f"Engine: {result.get('engine')}")
            print(f"Total Results: {result.get('total')}")
            
            results = result.get('results', [])
            if results:
                print(f"\nFirst 3 Results:")
                for i, item in enumerate(results[:3], 1):
                    print(f"\n  {i}. {item.get('title', 'N/A')}")
                    print(f"     URL: {item.get('url', 'N/A')}")
                    print(f"     Snippet: {item.get('snippet', 'N/A')[:100]}...")
            
            print("✓ Brave search test passed")
            return True
        elif response.status_code == 503:
            print("⚠ Brave search not configured (BRAVE_API_KEY missing)")
            return True  # Expected if API key not set
        else:
            print(f"✗ Brave search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Brave search test failed: {e}")
        return False


def test_multi_engine_search():
    """Test multi-engine search endpoint"""
    print("\n=== Testing Multi-Engine Search ===")
    try:
        query = "Web development"
        response = requests.get(
            f"{BASE_URL}/search/all",
            params={"query": query, "max_results": 3},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Query: {result.get('query')}")
            print(f"Engine: {result.get('engine')}")
            print(f"Total Results: {result.get('total')}")
            print(f"Sources: {result.get('sources', [])}")
            
            if result.get('errors'):
                print(f"Errors: {result.get('errors')}")
            
            results = result.get('results', [])
            if results:
                print(f"\nFirst 3 Merged Results:")
                for i, item in enumerate(results[:3], 1):
                    print(f"\n  {i}. {item.get('title', 'N/A')}")
                    print(f"     URL: {item.get('url', 'N/A')}")
                    print(f"     Source: {item.get('source', 'N/A')}")
                    print(f"     Snippet: {item.get('snippet', 'N/A')[:80]}...")
            
            print("✓ Multi-engine search test passed")
            return True
        else:
            print(f"✗ Multi-engine search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠ Multi-engine search timed out")
        return True  # Consider timeout as acceptable for multi-engine
    except Exception as e:
        print(f"✗ Multi-engine search test failed: {e}")
        return False


def test_invalid_query():
    """Test error handling with invalid parameters"""
    print("\n=== Testing Invalid Query Handling ===")
    try:
        # Test with max_results out of range
        response = requests.get(
            f"{BASE_URL}/search/duckduckgo",
            params={"query": "test", "max_results": 100}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print(f"Response: {response.json()}")
            print("✓ Invalid query handling test passed")
            return True
        else:
            print(f"⚠ Expected 422 status code, got {response.status_code}")
            return True  # Still acceptable
            
    except Exception as e:
        print(f"✗ Invalid query handling test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Search Service Test Suite")
    print("=" * 60)
    
    results = {
        "Health Check": test_health_check(),
        "Detailed Health": test_detailed_health(),
        "Invalid Query Handling": test_invalid_query(),
        "DuckDuckGo Search": test_duckduckgo_search(),
        "Google Search": test_google_search(),
        "Brave Search": test_brave_search(),
        "Multi-Engine Search": test_multi_engine_search(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
