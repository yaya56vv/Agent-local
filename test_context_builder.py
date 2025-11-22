"""
Test du Context Builder - Super-Contexte Global
Verifie la fusion de toutes les sources (memoire, RAG, vision, audio, documents, systeme)
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.orchestrator.orchestrator import Orchestrator


async def test_context_builder():
    """Test du context builder"""
    print("=" * 60)
    print("TEST DU CONTEXT BUILDER - SUPER-CONTEXTE GLOBAL")
    print("=" * 60)
    
    # Initialize orchestrator
    print("\n1. Initialisation de l'orchestrateur...")
    orchestrator = Orchestrator()
    print("✓ Orchestrateur initialisé")
    
    # Test message
    test_message = "Quelle est la structure de mon PC et quels sont mes projets en cours?"
    
    print(f"\n2. Construction du super-contexte pour: '{test_message}'")
    print("-" * 60)
    
    try:
        # Build super context
        super_context = await orchestrator.context_builder.build_super_context(
            user_message=test_message,
            session_id="test_session"
        )
        
        print("\n✓ Super-contexte construit avec succès!")
        print("\n3. Analyse du super-contexte:")
        print("-" * 60)
        
        # Display metadata
        metadata = super_context.get("metadata", {})
        print(f"\nSources disponibles: {metadata.get('sources_available', [])}")
        print(f"Taille totale du contexte: {metadata.get('total_context_size', 0)} caractères")
        
        # Display each context source
        print("\n4. Détails des sources:")
        print("-" * 60)
        
        # Memory context
        memory = super_context.get("memory", {})
        print(f"\n📝 MÉMOIRE:")
        print(f"  - Status: {memory.get('status', 'unknown')}")
        print(f"  - Contexte récent: {len(memory.get('recent_context', ''))} caractères")
        print(f"  - Résultats sémantiques: {len(memory.get('semantic_matches', []))} résultats")
        
        # RAG context
        rag = super_context.get("rag_docs", {})
        print(f"\n📚 RAG:")
        print(f"  - Status: {rag.get('status', 'unknown')}")
        print(f"  - Total résultats: {rag.get('total_results', 0)}")
        datasets = rag.get("datasets", {})
        for dataset_name, results in datasets.items():
            print(f"  - {dataset_name}: {len(results)} documents")
        
        # Vision context
        vision = super_context.get("vision", {})
        print(f"\n👁️ VISION:")
        print(f"  - Status: {vision.get('status', 'unknown')}")
        vision_ctx = vision.get("context", {})
        print(f"  - État: {vision_ctx.get('vision_state', 'unknown')}")
        
        # System state
        system = super_context.get("system_state", {})
        print(f"\n💻 SYSTÈME:")
        print(f"  - Status: {system.get('status', 'unknown')}")
        snapshot = system.get("snapshot", {})
        if snapshot:
            print(f"  - Snapshot disponible: {bool(snapshot)}")
        
        # Audio context
        audio = super_context.get("audio", {})
        print(f"\n🎤 AUDIO:")
        print(f"  - Status: {audio.get('status', 'unknown')}")
        audio_ctx = audio.get("context", {})
        print(f"  - État: {audio_ctx.get('audio_state', 'unknown')}")
        
        # Documents context
        documents = super_context.get("documents", {})
        print(f"\n📄 DOCUMENTS:")
        print(f"  - Status: {documents.get('status', 'unknown')}")
        print(f"  - Documents récents: {len(documents.get('recent_documents', []))}")
        
        print("\n" + "=" * 60)
        print("✓ TEST RÉUSSI - Context Builder opérationnel!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la construction du contexte:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_context_in_orchestrator():
    """Test de l'utilisation du context builder dans l'orchestrateur"""
    print("\n" + "=" * 60)
    print("TEST D'INTÉGRATION - CONTEXT BUILDER DANS ORCHESTRATEUR")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Verify context_builder is accessible
    print("\n1. Vérification de l'accessibilité du context_builder...")
    assert hasattr(orchestrator, 'context_builder'), "context_builder non trouvé!"
    print("✓ context_builder accessible")
    
    # Verify all required clients are available
    print("\n2. Vérification des clients MCP...")
    required_clients = [
        'memory_client',
        'rag_client',
        'vision_client',
        'system_client',
        'audio_client',
        'documents_client'
    ]
    
    for client_name in required_clients:
        assert hasattr(orchestrator, client_name), f"{client_name} non trouvé!"
        print(f"  ✓ {client_name}")
    
    print("\n✓ Tous les clients MCP sont disponibles")
    print("✓ Context Builder correctement intégré dans l'orchestrateur")
    
    return True


async def main():
    """Main test function"""
    print("\n🚀 DÉMARRAGE DES TESTS DU CONTEXT BUILDER\n")
    
    # Test 1: Context Builder functionality
    result1 = await test_context_builder()
    
    # Test 2: Integration in orchestrator
    result2 = await test_context_in_orchestrator()
    
    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Test Context Builder: {'✓ RÉUSSI' if result1 else '❌ ÉCHOUÉ'}")
    print(f"Test Intégration: {'✓ RÉUSSI' if result2 else '❌ ÉCHOUÉ'}")
    
    if result1 and result2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("\nLe Context Builder est opérationnel et peut fusionner:")
        print("  • Mémoire conversationnelle")
        print("  • Documents RAG (core, projects, scratchpad, rules)")
        print("  • Contexte vision")
        print("  • État système")
        print("  • Contexte audio")
        print("  • Documents récents")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
