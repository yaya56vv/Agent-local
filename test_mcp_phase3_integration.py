"""
Test MCP Phase 3 Integration
Tests Vision, Search, and System MCP clients integration with orchestrator.
"""
import asyncio
import sys
from backend.orchestrator.orchestrator import Orchestrator


async def test_vision_analysis():
    """Test vision analysis through MCP Vision Client."""
    print("\n" + "="*60)
    print("TEST 1: Vision Analysis via MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    # Test with a simple prompt (no actual image for now)
    prompt = "Analyse cette image et dis-moi ce que tu vois"
    
    try:
        result = await orchestrator.run(
            prompt=prompt,
            execution_mode="plan_only"  # Just plan, don't execute yet
        )
        
        print(f"\n[OK] Intention detectee: {result['intention']}")
        print(f"[OK] Confiance: {result['confidence']}")
        print(f"[OK] Nombre d'etapes: {len(result['steps'])}")
        print(f"[OK] Reponse: {result['response']}")
        
        if result['steps']:
            print("\nEtapes planifiees:")
            for i, step in enumerate(result['steps'], 1):
                print(f"  {i}. {step.get('action', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"\n[FAIL] Erreur: {str(e)}")
        return False


async def test_web_search():
    """Test web search through MCP Search Client."""
    print("\n" + "="*60)
    print("TEST 2: Web Search via MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    prompt = "Fais une recherche web sur Python FastAPI"
    
    try:
        result = await orchestrator.run(
            prompt=prompt,
            execution_mode="plan_only"
        )
        
        print(f"\n[OK] Intention detectee: {result['intention']}")
        print(f"[OK] Confiance: {result['confidence']}")
        print(f"[OK] Nombre d'etapes: {len(result['steps'])}")
        print(f"[OK] Reponse: {result['response']}")
        
        if result['steps']:
            print("\nEtapes planifiees:")
            for i, step in enumerate(result['steps'], 1):
                action = step.get('action', 'unknown')
                query = step.get('query', 'N/A')
                print(f"  {i}. {action} - Query: {query}")
        
        return True
    except Exception as e:
        print(f"\n[FAIL] Erreur: {str(e)}")
        return False


async def test_system_processes():
    """Test system process listing through MCP System Client."""
    print("\n" + "="*60)
    print("TEST 3: System Process Listing via MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    prompt = "Quels processus tournent actuellement ?"
    
    try:
        result = await orchestrator.run(
            prompt=prompt,
            execution_mode="plan_only"
        )
        
        print(f"\n[OK] Intention detectee: {result['intention']}")
        print(f"[OK] Confiance: {result['confidence']}")
        print(f"[OK] Nombre d'etapes: {len(result['steps'])}")
        print(f"[OK] Reponse: {result['response']}")
        
        if result['steps']:
            print("\nEtapes planifiees:")
            for i, step in enumerate(result['steps'], 1):
                print(f"  {i}. {step.get('action', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"\n[FAIL] Erreur: {str(e)}")
        return False


async def test_mcp_clients_instantiation():
    """Test that all MCP clients are properly instantiated."""
    print("\n" + "="*60)
    print("TEST 4: MCP Clients Instantiation")
    print("="*60)
    
    try:
        orchestrator = Orchestrator()
        
        # Check all MCP clients exist
        clients = {
            "files_client": orchestrator.files_client,
            "memory_client": orchestrator.memory_client,
            "rag_client": orchestrator.rag_client,
            "vision_client": orchestrator.vision_client,
            "search_client": orchestrator.search_client,
            "system_client": orchestrator.system_client,
        }
        
        print("\nMCP Clients verifies:")
        for name, client in clients.items():
            status = "[OK]" if client is not None else "[FAIL]"
            base_url = getattr(client, 'base_url', 'N/A')
            print(f"  {status} {name}: {base_url}")
        
        all_ok = all(client is not None for client in clients.values())
        return all_ok
    except Exception as e:
        print(f"\n[FAIL] Erreur: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTS D'INTEGRATION MCP PHASE 3")
    print("Vision, Search, System -> Orchestrator")
    print("="*60)
    
    tests = [
        ("Instantiation des clients MCP", test_mcp_clients_instantiation),
        ("Analyse Vision", test_vision_analysis),
        ("Recherche Web", test_web_search),
        ("Liste des processus", test_system_processes),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] Test '{test_name}' a echoue: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("RESUME DES TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nResultat: {passed}/{total} tests reussis")
    
    if passed == total:
        print("\n[SUCCESS] Tous les tests sont passes!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) ont echoue")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)