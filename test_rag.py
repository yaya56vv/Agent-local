"""
Test rapide du module RAG
Vérifie que tous les composants fonctionnent
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.rag_helper import rag_helper
from backend.connectors.local_llm.local_llm_connector import LocalLLMConnector, LocalLLMProvider


async def test_rag_system():
    """Test complet du système RAG"""
    
    print("=" * 60)
    print("🧪 TEST MODULE RAG - Agent Local")
    print("=" * 60)
    print()
    
    # Test 1: Vérifier LLM local
    print("1️⃣  Vérification du LLM local...")
    try:
        llm_available = await rag_helper.check_llm_available()
        if llm_available:
            print("   ✅ LLM local disponible")
            models = await rag_helper.llm.list_models()
            if models:
                print(f"   📋 Modèles disponibles: {', '.join(models[:3])}")
        else:
            print("   ⚠️  LLM local non disponible")
            print("   💡 Lancez Ollama ou LM Studio pour utiliser le LLM")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 2: Ajouter un document de test
    print("2️⃣  Ajout d'un document de test...")
    try:
        doc_id = rag_helper.add_document_sync(
            dataset="test_rag",
            filename="python_intro.txt",
            content="""
Python est un langage de programmation interprété, multi-paradigme et multiplateformes.
Il favorise la programmation impérative structurée, fonctionnelle et orientée objet.
Python est un langage de haut niveau avec typage dynamique fort.
Python a été créé par Guido van Rossum en 1991.
Le langage est très utilisé pour le développement web, la data science et l'IA.
            """.strip(),
            metadata={
                "type": "documentation",
                "language": "fr",
                "topic": "python"
            }
        )
        print(f"   ✅ Document ajouté (ID: {doc_id[:12]}...)")
    except Exception as e:
        print(f"   ❌ Erreur lors de l'ajout: {e}")
        return
    print()
    
    # Test 3: Lister les datasets
    print("3️⃣  Liste des datasets...")
    try:
        datasets = rag_helper.get_datasets()
        print(f"   📁 {len(datasets)} dataset(s) disponible(s)")
        for ds in datasets:
            info = rag_helper.get_dataset_info(ds)
            print(f"      - {ds}: {info['document_count']} docs, {info['chunk_count']} chunks")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 4: Recherche simple (sans LLM)
    print("4️⃣  Recherche sémantique (sans LLM)...")
    try:
        results = await rag_helper.quick_search(
            dataset="test_rag",
            query="Qui a créé Python ?",
            top_k=2
        )
        print(f"   🔍 {len(results)} résultat(s) trouvé(s)")
        for i, result in enumerate(results, 1):
            similarity = result.get('similarity', 0) * 100
            content_preview = result['content'][:80] + "..."
            print(f"      {i}. Similarité: {similarity:.1f}% | {content_preview}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    print()
    
    # Test 5: Recherche avec génération LLM
    print("5️⃣  Recherche avec génération LLM...")
    if llm_available:
        try:
            result = await rag_helper.answer_with_rag(
                dataset="test_rag",
                question="Qui a créé Python et en quelle année ?",
                top_k=3,
                temperature=0.7,
                max_tokens=150
            )
            
            if result['success']:
                print("   ✅ Réponse générée:")
                print(f"      {result['answer']}")
                print(f"   📚 Sources utilisées: {len(result['sources'])}")
                print(f"   🤖 Modèle: {result.get('model', 'N/A')} ({result.get('provider', 'N/A')})")
            else:
                print(f"   ⚠️  Erreur: {result.get('error', 'Inconnue')}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    else:
        print("   ⏭️  Test ignoré (LLM non disponible)")
    print()
    
    # Résumé
    print("=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)
    print()
    print("📖 Pour continuer:")
    print("   1. Lancez le serveur: python backend/main.py")
    print("   2. Ouvrez: http://localhost:8000/ui/rag.html")
    print("   3. Consultez: RAG_README.md")
    print()


if __name__ == "__main__":
    print()
    asyncio.run(test_rag_system())

