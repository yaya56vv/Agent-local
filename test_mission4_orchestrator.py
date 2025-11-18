"""
Test script for Mission 4 - Orchestrator Integration
Tests all module integrations through the orchestrator
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_web_search():
    """Test 1: Web search integration"""
    print("\n" + "="*60)
    print("TEST 1: Web Search Integration")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/orchestrate/",
            json={
                "prompt": "Cherche les dernières actualités sur Python 3.12",
                "session_id": "test_mission4"
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Intention: {result.get('intention')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Response: {result.get('response')}")
        print(f"Execution Results: {len(result.get('execution_results', []))} steps")
        
        return response.status_code == 200

async def test_code_execution():
    """Test 2: Code execution integration"""
    print("\n" + "="*60)
    print("TEST 2: Code Execution Integration")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/orchestrate/",
            json={
                "prompt": "Exécute ce code: print(2+2)",
                "session_id": "test_mission4"
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Intention: {result.get('intention')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Response: {result.get('response')}")
        print(f"Execution Results: {len(result.get('execution_results', []))} steps")
        
        if result.get('execution_results'):
            for i, exec_result in enumerate(result['execution_results'], 1):
                print(f"\nStep {i}:")
                print(f"  Action: {exec_result.get('action')}")
                print(f"  Status: {exec_result.get('status')}")
                if exec_result.get('data'):
                    print(f"  Data: {exec_result['data']}")
        
        return response.status_code == 200

async def test_system_actions():
    """Test 3: System actions integration"""
    print("\n" + "="*60)
    print("TEST 3: System Actions Integration")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/orchestrate/",
            json={
                "prompt": "Liste les processus actifs",
                "session_id": "test_mission4"
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Intention: {result.get('intention')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Response: {result.get('response')}")
        print(f"Execution Results: {len(result.get('execution_results', []))} steps")
        
        return response.status_code == 200

async def test_rag_integration():
    """Test 4: RAG integration"""
    print("\n" + "="*60)
    print("TEST 4: RAG Integration")
    print("="*60)
    
    # First add a document
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/orchestrate/",
            json={
                "prompt": "Ajoute ce texte à ma mémoire: Python est un langage de programmation interprété, orienté objet et de haut niveau.",
                "session_id": "test_mission4"
            }
        )
        
        print(f"Status (Add): {response.status_code}")
        result = response.json()
        print(f"Intention: {result.get('intention')}")
        print(f"Response: {result.get('response')}")
        
        return response.status_code == 200

async def test_health_check():
    """Test orchestrator health"""
    print("\n" + "="*60)
    print("HEALTH CHECK")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}/orchestrate/health")
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Service: {result.get('service')}")
        print(f"Status: {result.get('status')}")
        print(f"Orchestrator Available: {result.get('orchestrator_available')}")
        
        return response.status_code == 200

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MISSION 4 - ORCHESTRATOR INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Web Search", test_web_search),
        ("Code Execution", test_code_execution),
        ("System Actions", test_system_actions),
        ("RAG Integration", test_rag_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = "✓ PASS" if success else "✗ FAIL"
        except Exception as e:
            results[test_name] = f"✗ ERROR: {str(e)}"
            print(f"\nError in {test_name}: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print("\n" + "="*60)
    print("Mission 4 tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())