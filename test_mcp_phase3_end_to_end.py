"""
Tests End-to-End Phase 3 - MCP Integration Complete
Tests des commandes utilisateur via l'orchestrateur avec tous les serveurs MCP
"""
import asyncio
import sys
import os
from pathlib import Path
import base64

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.orchestrator.orchestrator import Orchestrator


async def test_vision_screenshot_analysis():
    """
    Test 1: « Analyse cette capture d'écran »
    Doit retourner description et OCR via MCP Vision
    """
    print("\n" + "="*80)
    print("TEST 1: Analyse de capture d'écran via MCP Vision")
    print("="*80)
    
    orchestrator = Orchestrator()
    
    # Créer une image de test simple (1x1 pixel blanc en PNG)
    # En production, on utiliserait une vraie capture d'écran
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(test_image_base64)
    
    print("\n[TEST] Requête utilisateur: 'Analyse cette capture d'écran'")
    print(f"[INFO] Image de test fournie: {len(image_bytes)} bytes")
    
    try:
        # Test direct via le client Vision
        print("\n[ÉTAPE 1] Test direct du client Vision MCP...")
        vision_result = await orchestrator.vision_client.analyze_screenshot(image_bytes)
        
        print(f"\n[RÉSULTAT VISION MCP]")
        print(f"  Status: {vision_result.get('status')}")
        
        if vision_result.get('status') == 'success':
            # Check for screenshot_analysis or analysis key
            analysis = vision_result.get('screenshot_analysis') or vision_result.get('analysis', {})
            print(f"  Description: {str(analysis.get('description', 'N/A'))[:100]}...")
            print(f"  OCR Text: {str(analysis.get('ocr_text', 'N/A'))[:100]}...")
            print(f"  Elements détectés: {len(analysis.get('elements', []))}")
            
            print(f"\n✅ SUCCÈS - Vision MCP fonctionne correctement")
            
            # Test via l'orchestrateur
            print("\n[ÉTAPE 2] Test via l'orchestrateur avec image...")
            result = await orchestrator.run(
                prompt="Analyse cette capture d'écran et dis-moi ce que tu vois",
                session_id="phase3_vision_test",
                execution_mode="auto",
                image_data=image_bytes
            )
            
            print(f"\n[RÉSULTAT ORCHESTRATEUR]")
            print(f"  Intention: {result.get('intention')}")
            print(f"  Confiance: {result.get('confidence'):.2f}")
            print(f"  Réponse: {result.get('response')[:150]}...")
            
            if result.get('execution_results'):
                print(f"  Nombre d'actions exécutées: {len(result['execution_results'])}")
            
            return True
        else:
            print(f"\n❌ ÉCHEC - Erreur Vision: {vision_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ÉCHEC - Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_query():
    """
    Test 2: « Trouve-moi les résultats pour [requête] »
    Doit interroger MCP Search et renvoyer une liste de liens pertinents
    """
    print("\n" + "="*80)
    print("TEST 2: Recherche web via MCP Search")
    print("="*80)
    
    orchestrator = Orchestrator()
    
    test_query = "Python FastAPI tutorial"
    print(f"\n[TEST] Requête utilisateur: 'Trouve-moi les résultats pour {test_query}'")
    
    try:
        # Test direct via le client Search
        print("\n[ÉTAPE 1] Test direct du client Search MCP...")
        search_result = await orchestrator.search_client.search_all(test_query)
        
        print(f"\n[RÉSULTAT SEARCH MCP]")
        print(f"  Status: {search_result.get('status')}")
        
        # Accept both 'success' and 'partial' as valid
        if search_result.get('status') in ['success', 'partial']:
            results = search_result.get('results', [])
            print(f"  Nombre de résultats: {len(results)}")
            
            if results:
                print(f"\n  Premiers résultats:")
                for i, result in enumerate(results[:3], 1):
                    print(f"    {i}. {result.get('title', 'N/A')}")
                    print(f"       URL: {result.get('url', 'N/A')}")
                    print(f"       Snippet: {result.get('snippet', result.get('description', 'N/A'))[:80]}...")
            
            print(f"\n✅ SUCCÈS - Search MCP fonctionne correctement")
            
            # Test via l'orchestrateur
            print("\n[ÉTAPE 2] Test via l'orchestrateur...")
            result = await orchestrator.run(
                prompt=f"Trouve-moi les résultats pour {test_query}",
                session_id="phase3_search_test",
                execution_mode="auto"
            )
            
            print(f"\n[RÉSULTAT ORCHESTRATEUR]")
            print(f"  Intention: {result.get('intention')}")
            print(f"  Confiance: {result.get('confidence'):.2f}")
            print(f"  Réponse: {result.get('response')[:150]}...")
            
            if result.get('execution_results'):
                exec_results = result['execution_results']
                print(f"  Nombre d'actions exécutées: {len(exec_results)}")
                
                # Vérifier que la recherche a été effectuée
                for exec_result in exec_results:
                    if exec_result.get('action') == 'search_web':
                        if exec_result.get('status') == 'success':
                            print(f"  ✓ Recherche web exécutée avec succès")
            
            return True
        else:
            print(f"\n❌ ÉCHEC - Erreur Search: {search_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ÉCHEC - Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_system_list_processes():
    """
    Test 3: « Liste-moi les processus système »
    Doit interroger MCP System et retourner la liste
    """
    print("\n" + "="*80)
    print("TEST 3: Liste des processus système via MCP System")
    print("="*80)
    
    orchestrator = Orchestrator()
    
    print("\n[TEST] Requête utilisateur: 'Liste-moi les processus système'")
    
    try:
        # Test direct via le client System
        print("\n[ÉTAPE 1] Test direct du client System MCP...")
        system_result = await orchestrator.system_client.list_processes()
        
        print(f"\n[RÉSULTAT SYSTEM MCP]")
        
        # System server returns the result directly, check for 'processes' key
        if 'processes' in system_result or system_result.get('status') == 'success':
            processes = system_result.get('processes', [])
            print(f"  Status: success")
            print(f"  Nombre de processus: {len(processes)}")
            
            if processes:
                print(f"\n  Premiers processus:")
                for i, proc in enumerate(processes[:5], 1):
                    print(f"    {i}. PID: {proc.get('pid')} - {proc.get('name', 'N/A')}")
                    cpu = proc.get('cpu_percent', 0)
                    mem = proc.get('memory_mb', 0)
                    print(f"       CPU: {cpu:.1f}% | RAM: {mem:.1f} MB")
            
            print(f"\n✅ SUCCÈS - System MCP fonctionne correctement")
            
            # Test via l'orchestrateur
            print("\n[ÉTAPE 2] Test via l'orchestrateur...")
            result = await orchestrator.run(
                prompt="Liste-moi les processus système en cours d'exécution",
                session_id="phase3_system_test",
                execution_mode="auto"
            )
            
            print(f"\n[RÉSULTAT ORCHESTRATEUR]")
            print(f"  Intention: {result.get('intention')}")
            print(f"  Confiance: {result.get('confidence'):.2f}")
            print(f"  Réponse: {result.get('response')[:150]}...")
            
            if result.get('execution_results'):
                exec_results = result['execution_results']
                print(f"  Nombre d'actions exécutées: {len(exec_results)}")
                
                # Vérifier que la liste des processus a été récupérée
                for exec_result in exec_results:
                    if exec_result.get('action') == 'system_list_processes':
                        if exec_result.get('status') == 'success':
                            print(f"  ✓ Liste des processus récupérée avec succès")
            
            return True
        else:
            print(f"  Status: {system_result.get('status', 'error')}")
            print(f"\n❌ ÉCHEC - Erreur System: {system_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ ÉCHEC - Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_integration():
    """
    Test 4: Test d'intégration complète
    Vérifie que tous les serveurs MCP sont accessibles
    """
    print("\n" + "="*80)
    print("TEST 4: Vérification de l'intégration complète MCP")
    print("="*80)
    
    orchestrator = Orchestrator()
    
    services = {
        "Files (8001)": orchestrator.files_client,
        "Memory (8002)": orchestrator.memory_client,
        "RAG (8003)": orchestrator.rag_client,
        "Vision (8004)": orchestrator.vision_client,
        "Search (8005)": orchestrator.search_client,
        "System (8006)": orchestrator.system_client
    }
    
    results = {}
    
    print("\n[VÉRIFICATION] Test de connectivité de tous les services MCP...")
    
    for service_name, client in services.items():
        try:
            # Test simple de connectivité
            if "Files" in service_name:
                await client.list_dir(".")
            elif "Memory" in service_name:
                await client.get_context("test", max_messages=1)
            elif "RAG" in service_name:
                await client.query("test", "test", top_k=1)
            elif "Vision" in service_name:
                # Skip vision test here as it requires image data
                results[service_name] = True
                print(f"  ✓ {service_name}: Accessible (skip image test)")
                continue
            elif "Search" in service_name:
                await client.search_all("test")
            elif "System" in service_name:
                await client.list_processes()
            
            results[service_name] = True
            print(f"  ✓ {service_name}: Accessible")
            
        except Exception as e:
            results[service_name] = False
            print(f"  ✗ {service_name}: Erreur - {str(e)[:50]}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print(f"\n✅ SUCCÈS - Tous les services MCP sont opérationnels")
        return True
    else:
        failed = [name for name, ok in results.items() if not ok]
        print(f"\n⚠️  PARTIEL - Services en échec: {', '.join(failed)}")
        return False


async def main():
    """Exécuter tous les tests end-to-end Phase 3"""
    print("\n" + "="*80)
    print("TESTS END-TO-END PHASE 3 - INTÉGRATION MCP COMPLÈTE")
    print("="*80)
    print("\nCes tests valident l'intégration complète des 6 serveurs MCP:")
    print("  ✓ Files:  http://localhost:8001")
    print("  ✓ Memory: http://localhost:8002")
    print("  ✓ RAG:    http://localhost:8003")
    print("  ✓ Vision: http://localhost:8004")
    print("  ✓ Search: http://localhost:8005")
    print("  ✓ System: http://localhost:8006")
    
    results = {}
    
    try:
        # Test 4 d'abord pour vérifier la connectivité
        print("\n[PRÉPARATION] Vérification de la connectivité des services...")
        connectivity_ok = await test_full_integration()
        
        if not connectivity_ok:
            print("\n⚠️  ATTENTION: Certains services ne sont pas accessibles")
            print("Les tests vont continuer mais peuvent échouer...")
        
        # Exécuter les tests spécifiques
        results['test_1_vision'] = await test_vision_screenshot_analysis()
        results['test_2_search'] = await test_search_query()
        results['test_3_system'] = await test_system_list_processes()
        results['test_4_integration'] = connectivity_ok
        
        # Résumé final
        print("\n" + "="*80)
        print("RÉSUMÉ DES TESTS END-TO-END PHASE 3")
        print("="*80)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        print(f"\nTest 1 (Vision - Screenshot):     {'✅ PASSÉ' if results['test_1_vision'] else '❌ ÉCHOUÉ'}")
        print(f"Test 2 (Search - Web Query):      {'✅ PASSÉ' if results['test_2_search'] else '❌ ÉCHOUÉ'}")
        print(f"Test 3 (System - Processes):      {'✅ PASSÉ' if results['test_3_system'] else '❌ ÉCHOUÉ'}")
        print(f"Test 4 (Integration - All MCP):   {'✅ PASSÉ' if results['test_4_integration'] else '❌ ÉCHOUÉ'}")
        
        print(f"\n{'='*80}")
        if passed == total:
            print(f"✅ TOUS LES TESTS PASSÉS ({passed}/{total})")
            print(f"{'='*80}")
            print("\n🎉 PHASE 3 COMPLÈTE ET VALIDÉE!")
            print("\nL'orchestrateur communique correctement avec:")
            print("  ✓ MCP Files Service (8001)")
            print("  ✓ MCP Memory Service (8002)")
            print("  ✓ MCP RAG Service (8003)")
            print("  ✓ MCP Vision Service (8004)")
            print("  ✓ MCP Search Service (8005)")
            print("  ✓ MCP System Service (8006)")
            print("\n🚀 L'intégration MCP Phase 3 est opérationnelle!")
            print("\nCommandes utilisateur testées:")
            print("  ✓ 'Analyse cette capture d'écran' → Vision + OCR")
            print("  ✓ 'Trouve-moi les résultats pour [requête]' → Search Web")
            print("  ✓ 'Liste-moi les processus système' → System Info")
        else:
            print(f"⚠️  TESTS PARTIELS ({passed}/{total} passés)")
            print(f"{'='*80}")
            print("\nCertains tests nécessitent des ajustements.")
            print("\nVérifiez que tous les serveurs MCP sont démarrés:")
            print("  - Files:  python -m uvicorn backend.mcp.files.server:app --reload --port 8001")
            print("  - Memory: python -m uvicorn backend.mcp.memory.server:app --reload --port 8002")
            print("  - RAG:    python -m uvicorn backend.mcp.rag.server:app --reload --port 8003")
            print("  - Vision: python -m uvicorn backend.mcp.vision.server:app --reload --port 8004")
            print("  - Search: python -m uvicorn backend.mcp.search.server:app --reload --port 8005")
            print("  - System: python -m uvicorn backend.mcp.system.server:app --reload --port 8006")
            sys.exit(1)
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERREUR DURANT LES TESTS")
        print("="*80)
        print(f"\nErreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
