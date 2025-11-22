"""
Tests d'intégration Phase 5 - Super Contexte + Multi-LLM + Timeline Multimodale
Tests: ContextBuilder, MCPPlanner, MCPExecutor, Timeline, CognitiveEngine
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.orchestrator.orchestrator import Orchestrator
from backend.orchestrator.context_builder import ContextBuilder
from backend.orchestrator.planner_mcp import MCPPlanner
from backend.orchestrator.executor_mcp import MCPExecutor
from backend.orchestrator.timeline import Timeline
from backend.orchestrator.cognitive_engine import CognitiveEngine


async def test_context_builder():
    """Test 1: ContextBuilder - Agrégation de tous les contextes"""
    print("\n" + "="*80)
    print("TEST 1: ContextBuilder - Super Contexte Global")
    print("="*80)
    
    try:
        orchestrator = Orchestrator()
        
        # Initialiser les composants Phase 5
        orchestrator.context_builder = ContextBuilder(orchestrator)
        orchestrator.timeline = Timeline()
        
        # Construire le super-contexte
        print("\n📊 Construction du super-contexte...")
        super_context = await orchestrator.context_builder.build_super_context(
            user_message="Analyse le système et montre-moi les fichiers récents",
            session_id="test_phase5"
        )
        
        print(f"\n✅ Super-contexte construit avec succès!")
        print(f"   - Sources disponibles: {super_context['metadata']['sources_available']}")
        print(f"   - Taille estimée: {super_context['metadata']['total_context_size']} bytes")
        
        # Vérifier les composants
        print("\n📋 Composants du super-contexte:")
        for key in ['memory', 'rag_docs', 'vision', 'system_state', 'audio', 'documents']:
            status = super_context[key].get('status', 'unknown')
            print(f"   - {key}: {status}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_planner():
    """Test 2: MCPPlanner - Planification multi-étapes avec sélection LLM"""
    print("\n" + "="*80)
    print("TEST 2: MCPPlanner - Planification Multi-LLM")
    print("="*80)
    
    try:
        orchestrator = Orchestrator()
        
        # Initialiser les composants
        orchestrator.context_builder = ContextBuilder(orchestrator)
        orchestrator.planner = MCPPlanner(orchestrator)
        orchestrator.timeline = Timeline()
        
        # Générer un plan
        print("\n🎯 Génération d'un plan multi-étapes...")
        plan = await orchestrator.planner.plan(
            user_message="Recherche des informations sur Python FastAPI et crée un résumé",
            session_id="test_phase5"
        )
        
        print(f"\n✅ Plan généré avec {len(plan)} étapes:")
        for i, step in enumerate(plan, 1):
            print(f"\n   Étape {i}:")
            print(f"      - Tool: {step.get('tool')}")
            print(f"      - Action: {step.get('action')}")
            print(f"      - LLM préféré: {step.get('preferred_llm')}")
            print(f"      - Args: {list(step.get('args', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_executor():
    """Test 3: MCPExecutor - Exécution d'actions MCP"""
    print("\n" + "="*80)
    print("TEST 3: MCPExecutor - Exécution d'Actions")
    print("="*80)
    
    try:
        orchestrator = Orchestrator()
        
        # Initialiser les composants
        orchestrator.timeline = Timeline()
        orchestrator.executor = MCPExecutor(orchestrator)
        
        # Plan de test simple
        test_plan = [
            {
                "tool": "memory",
                "action": "get_context",
                "args": {"session_id": "test_phase5", "max_messages": 5},
                "preferred_llm": "reasoning"
            }
        ]
        
        print("\n⚙️ Exécution du plan de test...")
        results = await orchestrator.executor.execute_plan(
            plan=test_plan,
            session_id="test_phase5"
        )
        
        print(f"\n✅ Plan exécuté avec {len(results)} résultats:")
        for i, result in enumerate(results, 1):
            print(f"\n   Résultat {i}:")
            print(f"      - Status: {result.get('status')}")
            print(f"      - Tool: {result.get('tool')}")
            print(f"      - Action: {result.get('action')}")
        
        # Test de validation
        print("\n🔍 Test de validation d'étape...")
        validation = orchestrator.executor.validate_step(test_plan[0])
        print(f"   - Valide: {validation['valid']}")
        if not validation['valid']:
            print(f"   - Erreurs: {validation['errors']}")
        
        # Test de dry-run
        print("\n🧪 Test de dry-run...")
        dry_run_result = await orchestrator.executor.dry_run(test_plan)
        print(f"   - Peut exécuter: {dry_run_result['can_execute']}")
        print(f"   - Étapes valides: {dry_run_result['valid_steps']}/{dry_run_result['total_steps']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_timeline_multimodal():
    """Test 4: Timeline - Support multimodal complet"""
    print("\n" + "="*80)
    print("TEST 4: Timeline - Support Multimodal")
    print("="*80)
    
    try:
        timeline = Timeline()
        
        # Ajouter des événements de différentes modalités
        print("\n📝 Ajout d'événements multimodaux...")
        
        # Événement texte
        await timeline.add(
            event_type="execution",
            data={"tool": "memory", "action": "get_context"},
            session_id="test_phase5",
            metadata={"modality": "text"}
        )
        
        # Événement audio
        await timeline.add(
            event_type="audio_transcription",
            data={"tool": "audio", "action": "transcribe", "result": {"transcription": "Test audio"}},
            session_id="test_phase5"
        )
        
        # Événement vision
        await timeline.add(
            event_type="vision_analysis",
            data={"tool": "vision", "action": "analyze_screenshot", "result": {"analysis": "Test vision"}},
            session_id="test_phase5"
        )
        
        print("✅ Événements ajoutés")
        
        # Récupérer par modalité
        print("\n🔍 Récupération par modalité:")
        
        audio_events = timeline.get_audio_events(session_id="test_phase5")
        print(f"   - Audio: {len(audio_events)} événements")
        
        vision_events = timeline.get_vision_events(session_id="test_phase5")
        print(f"   - Vision: {len(vision_events)} événements")
        
        # Résumé multimodal
        print("\n📊 Résumé multimodal:")
        summary = timeline.get_multimodal_summary(session_id="test_phase5")
        print(f"   - Total événements: {summary['total_events']}")
        print(f"   - Modalités utilisées: {summary['modalities_used']}")
        print(f"   - Répartition: {summary['modality_breakdown']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_cognitive_engine():
    """Test 5: CognitiveEngine - Opérations autonomes"""
    print("\n" + "="*80)
    print("TEST 5: CognitiveEngine - Intelligence Autonome")
    print("="*80)
    
    try:
        orchestrator = Orchestrator()
        
        # Initialiser les composants
        orchestrator.timeline = Timeline()
        orchestrator.context_builder = ContextBuilder(orchestrator)
        orchestrator.cognitive_engine = CognitiveEngine(orchestrator)
        
        # Ajouter quelques événements pour tester
        for i in range(5):
            await orchestrator.timeline.add(
                event_type="execution",
                data={"step": i, "action": "test"},
                session_id="test_phase5"
            )
        
        print("\n🧠 Test des fonctions cognitives...")
        
        # Test auto-résumé
        print("\n1. Auto-résumé:")
        summary_result = await orchestrator.cognitive_engine.autosummarize(
            session_id="test_phase5",
            force=True
        )
        print(f"   - Status: {summary_result.get('status')}")
        if summary_result.get('status') == 'success':
            print(f"   - Événements résumés: {summary_result.get('events_summarized')}")
        
        # Test suggestions proactives
        print("\n2. Suggestions proactives:")
        super_context = await orchestrator.context_builder.build_super_context(
            user_message="Test",
            session_id="test_phase5"
        )
        suggestions = await orchestrator.cognitive_engine.proactive_suggestions(
            context=super_context,
            session_id="test_phase5"
        )
        print(f"   - Nombre de suggestions: {len(suggestions)}")
        for suggestion in suggestions:
            print(f"      • {suggestion.get('type')}: {suggestion.get('message')}")
        
        # Test cycle autonome
        print("\n3. Cycle autonome:")
        cycle_result = await orchestrator.cognitive_engine.run_autonomous_cycle(
            session_id="test_phase5"
        )
        print(f"   - Opérations effectuées: {len(cycle_result['operations'])}")
        for op in cycle_result['operations']:
            print(f"      • {op['operation']}: {op['result'].get('status')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_integration():
    """Test 6: Intégration complète Phase 5"""
    print("\n" + "="*80)
    print("TEST 6: Intégration Complète Phase 5")
    print("="*80)
    
    try:
        orchestrator = Orchestrator()
        
        # Initialiser tous les composants Phase 5
        print("\n🔧 Initialisation des composants Phase 5...")
        orchestrator.context_builder = ContextBuilder(orchestrator)
        orchestrator.planner = MCPPlanner(orchestrator)
        orchestrator.executor = MCPExecutor(orchestrator)
        orchestrator.timeline = Timeline()
        orchestrator.cognitive_engine = CognitiveEngine(orchestrator)
        
        print("✅ Tous les composants initialisés")
        
        # Workflow complet
        print("\n🔄 Workflow complet:")
        
        # 1. Construire le contexte
        print("\n   1. Construction du super-contexte...")
        super_context = await orchestrator.context_builder.build_super_context(
            user_message="Analyse le système",
            session_id="test_integration"
        )
        print(f"      ✓ Contexte construit ({len(super_context['metadata']['sources_available'])} sources)")
        
        # 2. Générer un plan
        print("\n   2. Génération du plan...")
        plan = await orchestrator.planner.plan(
            user_message="Liste les processus système",
            session_id="test_integration"
        )
        print(f"      ✓ Plan généré ({len(plan)} étapes)")
        
        # 3. Valider le plan
        print("\n   3. Validation du plan...")
        dry_run = await orchestrator.executor.dry_run(plan)
        print(f"      ✓ Validation: {dry_run['valid_steps']}/{dry_run['total_steps']} étapes valides")
        
        # 4. Exécuter (si valide)
        if dry_run['can_execute']:
            print("\n   4. Exécution du plan...")
            results = await orchestrator.executor.execute_plan(plan, session_id="test_integration")
            print(f"      ✓ Exécution terminée ({len(results)} résultats)")
        
        # 5. Vérifier la timeline
        print("\n   5. Vérification de la timeline...")
        events = orchestrator.timeline.get_events(session_id="test_integration")
        print(f"      ✓ Timeline: {len(events)} événements enregistrés")
        
        # 6. Résumé multimodal
        print("\n   6. Résumé multimodal...")
        summary = orchestrator.timeline.get_multimodal_summary(session_id="test_integration")
        print(f"      ✓ Modalités: {summary['modalities_used']}")
        
        print("\n✅ Intégration complète Phase 5 réussie!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Exécute tous les tests Phase 5"""
    print("\n" + "="*80)
    print("🚀 TESTS PHASE 5 - MCP FULLSTACK COMPLET")
    print("="*80)
    print("\nComposants testés:")
    print("  • ContextBuilder (Super-Contexte)")
    print("  • MCPPlanner (Planification Multi-LLM)")
    print("  • MCPExecutor (Exécution MCP)")
    print("  • Timeline (Support Multimodal)")
    print("  • CognitiveEngine (Intelligence Autonome)")
    
    results = {
        "ContextBuilder": await test_context_builder(),
        "MCPPlanner": await test_mcp_planner(),
        "MCPExecutor": await test_mcp_executor(),
        "Timeline Multimodal": await test_timeline_multimodal(),
        "CognitiveEngine": await test_cognitive_engine(),
        "Intégration Complète": await test_full_integration()
    }
    
    # Résumé final
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS PHASE 5")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 PHASE 5 COMPLÈTE - TOUS LES TESTS RÉUSSIS!")
        print("\n✨ Fonctionnalités disponibles:")
        print("   • Super-Contexte global (mémoire + RAG + vision + audio + documents + système)")
        print("   • Planification multi-étapes avec sélection automatique de LLM")
        print("   • Exécution d'actions sur tous les outils MCP")
        print("   • Timeline multimodale avec support audio/vision/documents")
        print("   • Moteur cognitif autonome (résumés, sync, suggestions)")
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s)")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
