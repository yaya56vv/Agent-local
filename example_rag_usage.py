"""
Exemple d'utilisation du module RAG
Démontre l'ajout de documents et les requêtes RAG
"""

import asyncio
import os
from backend.rag.rag_store import RAGStore
from backend.connectors.local_llm import LocalLLMConnector, LocalLLMProvider


async def example_basic_rag():
    """Exemple basique : ajouter des documents et faire une recherche"""
    print("=" * 60)
    print("EXEMPLE 1 : RAG Basique (recherche vectorielle)")
    print("=" * 60)
    
    # Initialiser le RAG store
    rag = RAGStore()
    
    # Ajouter quelques documents d'exemple
    print("\n1. Ajout de documents...")
    
    doc1 = """
    Guide d'installation du système Agent Local
    
    Pour installer le système, suivez ces étapes :
    1. Clonez le repository
    2. Installez les dépendances avec pip install -r requirements.txt
    3. Configurez les variables d'environnement dans .env
    4. Lancez le serveur avec python -m uvicorn backend.main:app
    """
    
    doc2 = """
    Configuration des API
    
    Le système nécessite plusieurs clés API :
    - OPENROUTER_API_KEY : pour le raisonnement
    - LOCAL_LLM : Ollama ou LM Studio pour la génération locale
    
    Ajoutez ces clés dans votre fichier .env à la racine du projet.
    """
    
    doc3 = """
    Utilisation du module RAG
    
    Le module RAG permet de :
    - Stocker des documents avec embeddings
    - Rechercher des documents par similarité sémantique
    - Générer des réponses contextuelles avec un LLM local
    
    Les documents sont stockés dans une base SQLite locale.
    """
    
    # Ajouter les documents
    id1 = rag.add_document("documentation", "installation.txt", doc1)
    print(f"✓ Document 1 ajouté : {id1[:16]}...")
    
    id2 = rag.add_document("documentation", "configuration.txt", doc2)
    print(f"✓ Document 2 ajouté : {id2[:16]}...")
    
    id3 = rag.add_document("documentation", "rag_usage.txt", doc3)
    print(f"✓ Document 3 ajouté : {id3[:16]}...")
    
    # Faire une recherche
    print("\n2. Recherche de documents pertinents...")
    question = "Comment installer le système ?"
    print(f"Question : {question}")
    
    results = rag.query("documentation", question, top_k=2)
    
    print(f"\n✓ {len(results)} résultats trouvés :\n")
    for i, result in enumerate(results, 1):
        print(f"Résultat {i}:")
        print(f"  Fichier: {result['filename']}")
        print(f"  Score: {result['similarity']:.3f}")
        print(f"  Extrait: {result['content'][:150]}...")
        print()


async def example_rag_with_llm():
    """Exemple avancé : RAG avec génération de réponse par LLM"""
    print("=" * 60)
    print("EXEMPLE 2 : RAG avec LLM (génération de réponse)")
    print("=" * 60)
    
    # Initialiser
    rag = RAGStore()
    
    # Vérifier si Ollama est disponible
    llm = LocalLLMConnector(provider=LocalLLMProvider.OLLAMA)
    is_available = await llm.is_available()
    
    if not is_available:
        print("\n⚠️  Ollama n'est pas disponible.")
        print("   Installez Ollama depuis https://ollama.ai/")
        print("   Puis lancez : ollama pull llama3.2")
        return
    
    print("\n✓ Ollama est disponible")
    
    # Faire une requête RAG complète
    question = "Quelles sont les clés API nécessaires ?"
    print(f"\nQuestion : {question}")
    
    # 1. Rechercher les documents pertinents
    print("\n1. Recherche de documents pertinents...")
    sources = rag.query("documentation", question, top_k=2)
    
    if not sources:
        print("Aucun document pertinent trouvé.")
        return
    
    print(f"✓ {len(sources)} sources trouvées")
    
    # 2. Construire le contexte
    context = "\n\n".join([
        f"Source {i+1} (de {src['filename']}):\n{src['content']}"
        for i, src in enumerate(sources)
    ])
    
    # 3. Générer la réponse avec le LLM
    print("\n2. Génération de la réponse avec le LLM...")
    
    prompt = f"""Contexte:
{context}

Question: {question}

Réponds de manière concise en te basant uniquement sur le contexte fourni."""
    
    system_prompt = "Tu es un assistant qui répond aux questions en te basant sur le contexte fourni. Sois précis et concis."
    
    answer = await llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=500
    )
    
    print("\n" + "=" * 60)
    print("RÉPONSE GÉNÉRÉE :")
    print("=" * 60)
    print(answer)
    print("=" * 60)
    
    print("\n✓ Réponse générée avec succès")


async def example_dataset_management():
    """Exemple de gestion des datasets"""
    print("=" * 60)
    print("EXEMPLE 3 : Gestion des datasets")
    print("=" * 60)
    
    rag = RAGStore()
    
    # Lister les datasets
    print("\n1. Datasets disponibles :")
    datasets = rag.list_datasets()
    
    if not datasets:
        print("   Aucun dataset trouvé")
    else:
        for dataset in datasets:
            print(f"   - {dataset}")
    
    # Informations sur un dataset
    if "documentation" in datasets:
        print("\n2. Informations sur le dataset 'documentation' :")
        info = rag.get_dataset_info("documentation")
        print(f"   Documents : {info['document_count']}")
        print(f"   Chunks : {info['chunk_count']}")
        print(f"   Fichiers :")
        for doc in info['documents'][:5]:  # Afficher max 5
            print(f"     - {doc['filename']} ({doc['created_at']})")


async def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("DÉMONSTRATION DU MODULE RAG")
    print("=" * 60)
    
    # Vérifier la clé API OpenRouter
    # if not os.getenv("OPENROUTER_API_KEY"):
    #     print("\n⚠️  ERREUR : OPENROUTER_API_KEY non configurée")
    #     print("   Ajoutez votre clé API OpenRouter dans le fichier .env")
    #     return
    
    try:
        # Exemple 1 : RAG basique
        await example_basic_rag()
        
        print("\n" + "=" * 60)
        input("Appuyez sur Entrée pour continuer...")
        
        # Exemple 2 : RAG avec LLM
        await example_rag_with_llm()
        
        print("\n" + "=" * 60)
        input("Appuyez sur Entrée pour continuer...")
        
        # Exemple 3 : Gestion des datasets
        await example_dataset_management()
        
        print("\n" + "=" * 60)
        print("✓ Démonstration terminée avec succès !")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur : {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
