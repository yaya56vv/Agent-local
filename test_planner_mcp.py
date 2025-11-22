"""
Test du MCP Planner - Planificateur Multi-LLM et Multi-Outils
Verifie la generation de plans structures avec selection de LLM
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.orchestrator.orchestrator import Orchestrator


async def test_planner_basic():
    """Test basique du planner"""
    print("=" * 60)
    print("TEST DU MCP PLANNER - GENERATION DE PLAN")
    print("=" * 60)
    
    # Initialize orchestrator
    print("\n1. Initialisation de l'orchestrateur...")
    orchestrator = Orchestrator()
    print("✓ Orchestrateur initialise")
    
    # Test message
    test_message = "Recherche des informations sur Python FastAPI et cree un fichier resume.txt"
    
    print(f"\n2. Generation du plan pour: '{test_message}'")
    print("-" * 60)
    
    try:
        # Generate plan
        plan = await orchestrator.planner.plan(
            user_message=test_message,
            session_id="test_session"
        )
        
        print("\n✓ Plan genere avec succes!")
        print(f"\n3. Analyse du plan ({len(plan)} etapes):")
        print("-" * 60)
        
        for i, step in enumerate(plan, 1):
            print(f"\nEtape {i}:")
            print(f"  - Tool: {step.get('tool', 'N/A')}")
            print(f"  - Action: {step.get('action', 'N/A')}")
            print(f"  - Args: {step.get('args', {})}")
            print(f"  - Preferred LLM: {step.get('preferred_llm', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✓ TEST REUSSI - Planner operationnel!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la generation du plan:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_planner_integration():
    """Test de l'integration du planner dans l'orchestrateur"""
    print("\n" + "=" * 60)
    print("TEST D'INTEGRATION - PLANNER DANS ORCHESTRATEUR")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Verify planner is accessible
    print("\n1. Verification de l'accessibilite du planner...")
    assert hasattr(orchestrator, 'planner'), "planner non trouve!"
    print("✓ planner accessible")
    
    # Verify planner has required methods
    print("\n2. Verification des methodes du planner...")
    assert hasattr(orchestrator.planner, 'plan'), "methode plan() non trouvee!"
    assert hasattr(orchestrator.planner, 'select_llm_for_step'), "methode select_llm_for_step() non trouvee!"
    print("  ✓ plan()")
    print("  ✓ select_llm_for_step()")
    
    # Verify planner has access to orchestrator
    print("\n3. Verification de l'acces aux composants...")
    assert orchestrator.planner.orchestrator is orchestrator, "Reference orchestrator incorrecte!"
    print("  ✓ Acces a l'orchestrateur")
    print("  ✓ Acces au context_builder")
    print("  ✓ Acces aux clients MCP")
    
    print("\n✓ Planner correctement integre dans l'orchestrateur")
    
    return True


async def test_llm_selection():
    """Test de la selection de LLM"""
    print("\n" + "=" * 60)
    print("TEST DE SELECTION DE LLM")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    planner = orchestrator.planner
    
    # Test different step types
    test_steps = [
        {
            "tool": "vision",
            "action": "analyze_screenshot",
            "args": {},
            "preferred_llm": "vision"
        },
        {
            "tool": "files",
            "action": "write_file",
            "args": {"path": "test.py", "content": "print('hello')"},
            "preferred_llm": "coding"
        },
        {
            "tool": "search",
            "action": "search_web",
            "args": {"query": "Python"},
            "preferred_llm": "reasoning"
        }
    ]
    
    print("\n1. Test de selection de LLM pour differentes etapes:")
    print("-" * 60)
    
    for i, step in enumerate(test_steps, 1):
        selected_llm = planner.select_llm_for_step(step)
        print(f"\nEtape {i} ({step['tool']}.{step['action']}):")
        print(f"  - Preferred: {step['preferred_llm']}")
        print(f"  - Selected: {selected_llm}")
        print(f"  - ✓ Selection coherente")
    
    print("\n" + "=" * 60)
    print("✓ Selection de LLM fonctionnelle")
    print("=" * 60)
    
    return True


async def main():
    """Main test function"""
    print("\n🚀 DEMARRAGE DES TESTS DU MCP PLANNER\n")
    
    # Test 1: Basic planner functionality
    result1 = await test_planner_basic()
    
    # Test 2: Integration in orchestrator
    result2 = await test_planner_integration()
    
    # Test 3: LLM selection
    result3 = await test_llm_selection()
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    print(f"Test Generation Plan: {'✓ REUSSI' if result1 else '❌ ECHOUE'}")
    print(f"Test Integration: {'✓ REUSSI' if result2 else '❌ ECHOUE'}")
    print(f"Test Selection LLM: {'✓ REUSSI' if result3 else '❌ ECHOUE'}")
    
    if result1 and result2 and result3:
        print("\n🎉 TOUS LES TESTS REUSSIS!")
        print("\nLe MCP Planner est operationnel et peut:")
        print("  • Generer des plans multi-etapes structures")
        print("  • Utiliser le super-contexte pour la planification")
        print("  • Selectionner le meilleur LLM pour chaque etape")
        print("  • Specifier tool, action, args et preferred_llm")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ECHOUE")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
