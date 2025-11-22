"""
Test script for GLM Vision Expert MCP Server
Tests all endpoints to ensure proper functionality
"""

import requests
import json
import base64
from pathlib import Path

BASE_URL = "http://localhost:9001"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_list_tools():
    """Test MCP tools list endpoint"""
    print("\n=== Testing MCP Tools List ===")
    response = requests.get(f"{BASE_URL}/mcp/tools/list")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of tools: {data.get('count', 0)}")
    for tool in data.get('tools', [])[:3]:  # Show first 3 tools
        print(f"  - {tool['name']}: {tool['description']}")
    return response.status_code == 200


def test_solve_problem():
    """Test solve_problem endpoint"""
    print("\n=== Testing Solve Problem ===")
    payload = {
        "description": "How can I optimize a Python function that processes large lists?",
        "context": {
            "language": "Python",
            "data_size": "1M items"
        }
    }
    response = requests.post(f"{BASE_URL}/glm/solve_problem", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Solution preview: {data.get('solution', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def test_file_search():
    """Test file_search endpoint"""
    print("\n=== Testing File Search ===")
    payload = {
        "pattern": "*.py",
        "directory": "backend/mcp/glm_vision_expert"
    }
    response = requests.post(f"{BASE_URL}/glm/file_search", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('count', 0)} files")
        for match in data.get('matches', [])[:3]:
            print(f"  - {match['path']}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def test_rag_query():
    """Test RAG query endpoint"""
    print("\n=== Testing RAG Query ===")
    payload = {
        "query": "What are the core rules?",
        "dataset": "agent_core"
    }
    response = requests.post(f"{BASE_URL}/glm/rag_query", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Answer preview: {data.get('answer', '')[:200]}...")
        print(f"Sources: {len(data.get('sources', []))}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("GLM Vision Expert MCP Server - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("List Tools", test_list_tools),
        ("File Search", test_file_search),
        ("Solve Problem", test_solve_problem),
        ("RAG Query", test_rag_query),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the GLM Vision Expert server is running on port 9001")
    print("Start it with: python backend/mcp/glm_vision_expert/server.py\n")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
