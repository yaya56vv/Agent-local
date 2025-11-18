"""
Exemples avancés d'utilisation du RAG
Montre différents cas d'usage et patterns
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.rag_helper import rag_helper, answer_question_with_rag


# ============================================================
# EXEMPLE 1 : Base de connaissances multi-thèmes
# ============================================================

async def example_knowledge_base():
    """Créer une base de connaissances avec plusieurs thématiques"""
    
    print("=" * 60)
    print("📚 EXEMPLE 1 : Base de connaissances multi-thèmes")
    print("=" * 60)
    print()
    
    # Définir les connaissances
    knowledge = {
        "python": {
            "basics.txt": """
Python est un langage interprété de haut niveau.
Les variables n'ont pas besoin de déclaration de type.
L'indentation est significative en Python.
Python supporte la POO, la programmation fonctionnelle et impérative.
            """,
            "data_structures.txt": """
Python offre plusieurs structures de données natives :
- list : tableau dynamique modifiable
- tuple : séquence immuable
- dict : table de hachage (clé-valeur)
- set : ensemble d'éléments uniques
            """
        },
        "fastapi": {
            "intro.txt": """
FastAPI est un framework web moderne pour Python.
Il est basé sur les standards Python type hints.
FastAPI génère automatiquement une documentation OpenAPI.
Il utilise Pydantic pour la validation des données.
            """,
            "routes.txt": """
Les routes FastAPI sont décorées avec @app.get(), @app.post(), etc.
On peut définir des paramètres de path, query et body.
FastAPI supporte les requêtes asynchrones avec async/await.
            """
        }
    }
    
    # Ajouter tous les documents
    print("📝 Ajout des documents...")
    for dataset, files in knowledge.items():
        for filename, content in files.items():
            doc_id = rag_helper.add_document_sync(
                dataset=dataset,
                filename=filename,
                content=content.strip()
            )
            print(f"   ✅ {dataset}/{filename}")
    
    print()
    
    # Poser des questions sur différents datasets
    questions = [
        ("python", "Quelles sont les structures de données natives ?"),
        ("fastapi", "Comment définir des routes ?"),
    ]
    
    print("🔍 Questions et réponses :")
    print()
    
    for dataset, question in questions:
        print(f"   Dataset: {dataset}")
        print(f"   Q: {question}")
        
        answer = await answer_question_with_rag(
            dataset=dataset,
            question=question,
            top_k=3
        )
        
        print(f"   R: {answer[:200]}...")
        print()


# ============================================================
# EXEMPLE 2 : Documentation de code
# ============================================================

async def example_code_documentation():
    """Documenter et interroger du code"""
    
    print("=" * 60)
    print("💻 EXEMPLE 2 : Documentation de code")
    print("=" * 60)
    print()
    
    # Code source à documenter
    code_files = {
        "user_model.py": """
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.is_active = True
    
    def deactivate(self):
        '''Désactive l'utilisateur'''
        self.is_active = False
    
    def validate_email(self) -> bool:
        '''Vérifie que l'email est valide'''
        return '@' in self.email
        """,
        "auth_service.py": """
class AuthService:
    def login(self, username: str, password: str) -> Token:
        '''Authentifie un utilisateur et retourne un token JWT'''
        user = self.find_user(username)
        if not user or not self.verify_password(password):
            raise AuthenticationError()
        return self.create_token(user)
    
    def logout(self, token: str):
        '''Invalide un token d'authentification'''
        self.blacklist_token(token)
        """
    }
    
    print("📝 Ajout du code au RAG...")
    for filename, code in code_files.items():
        rag_helper.add_document_sync(
            dataset="codebase",
            filename=filename,
            content=code.strip(),
            metadata={"type": "python_code"}
        )
        print(f"   ✅ {filename}")
    
    print()
    
    # Interroger le code
    questions = [
        "Comment désactiver un utilisateur ?",
        "Quelle méthode permet de se connecter ?",
        "Comment valider un email ?"
    ]
    
    print("🔍 Questions sur le code :")
    print()
    
    for question in questions:
        print(f"   Q: {question}")
        result = await rag_helper.answer_with_rag(
            dataset="codebase",
            question=question,
            top_k=2
        )
        print(f"   R: {result['answer']}")
        print()


# ============================================================
# EXEMPLE 3 : Recherche contextuelle
# ============================================================

async def example_contextual_search():
    """Recherche avec contexte et filtrage"""
    
    print("=" * 60)
    print("🔎 EXEMPLE 3 : Recherche contextuelle avancée")
    print("=" * 60)
    print()
    
    # Base de données produits
    products = [
        {
            "name": "laptop_pro.txt",
            "content": """
Laptop Pro X1
Prix: 1299€
Processeur: Intel i7 12ème gen
RAM: 16GB DDR5
SSD: 512GB NVMe
Écran: 15.6" Full HD
Autonomie: 8 heures
Poids: 1.8kg
Garantie: 2 ans
            """
        },
        {
            "name": "laptop_gaming.txt",
            "content": """
Gaming Beast Z9
Prix: 1899€
Processeur: AMD Ryzen 9
RAM: 32GB DDR5
SSD: 1TB NVMe
GPU: NVIDIA RTX 4070
Écran: 17.3" QHD 165Hz
Autonomie: 4 heures
Poids: 2.5kg
Garantie: 3 ans
            """
        },
        {
            "name": "laptop_ultrabook.txt",
            "content": """
Ultrabook Air S3
Prix: 899€
Processeur: Intel i5 12ème gen
RAM: 8GB DDR4
SSD: 256GB NVMe
Écran: 13.3" Full HD
Autonomie: 12 heures
Poids: 1.1kg
Garantie: 1 an
            """
        }
    ]
    
    print("📝 Ajout des produits...")
    for product in products:
        rag_helper.add_document_sync(
            dataset="products",
            filename=product["name"],
            content=product["content"].strip(),
            metadata={"category": "laptop"}
        )
        print(f"   ✅ {product['name']}")
    
    print()
    
    # Différents types de recherches
    searches = [
        "Quel laptop est le plus léger ?",
        "Je cherche un laptop pour le gaming",
        "Quel est le laptop avec la meilleure autonomie ?",
        "Laptop avec 32GB de RAM"
    ]
    
    print("🔍 Recherches contextuelles :")
    print()
    
    for search in searches:
        print(f"   Q: {search}")
        
        # Recherche simple pour voir les sources
        sources = await rag_helper.quick_search(
            dataset="products",
            query=search,
            top_k=2
        )
        
        if sources:
            best_match = sources[0]
            similarity = best_match['similarity'] * 100
            print(f"   🎯 Meilleure correspondance: {best_match['filename']} ({similarity:.1f}%)")
        
        print()


# ============================================================
# EXEMPLE 4 : Q&A avec historique
# ============================================================

async def example_conversation():
    """Conversation avec contexte maintenu"""
    
    print("=" * 60)
    print("💬 EXEMPLE 4 : Conversation avec contexte")
    print("=" * 60)
    print()
    
    # Documentation à utiliser
    doc = """
L'Agent Local est un système d'agent intelligent modulaire.

Architecture:
- Backend FastAPI pour l'API REST
- Orchestrateur pour coordonner les actions
- Connecteurs pour services externes (LLM, recherche, etc.)
- Système RAG pour la base de connaissances
- Frontend web pour l'interface utilisateur

Fonctionnalités:
- Chat avec historique de conversation
- Recherche web avancée (Google, Brave, DuckDuckGo)
- Exécution de code Python
- Gestion de fichiers
- Système de mémoire persistante
- RAG avec LLM local (Ollama/LM Studio)

Technologies:
- Python 3.11+
- FastAPI pour l'API
- SQLite pour la persistance
- Gemini API pour les embeddings
- Ollama/LM Studio pour le LLM local
    """
    
    print("📝 Ajout de la documentation...")
    rag_helper.add_document_sync(
        dataset="agent_docs",
        filename="architecture.txt",
        content=doc.strip()
    )
    print("   ✅ Documentation ajoutée")
    print()
    
    # Série de questions liées
    conversation = [
        "Qu'est-ce que l'Agent Local ?",
        "Quels sont ses composants principaux ?",
        "Quelles technologies utilise-t-il ?",
        "Comment fonctionne le système RAG ?"
    ]
    
    print("💬 Conversation :")
    print()
    
    for i, question in enumerate(conversation, 1):
        print(f"   [{i}] Utilisateur: {question}")
        
        answer = await answer_question_with_rag(
            dataset="agent_docs",
            question=question,
            top_k=3
        )
        
        print(f"   [{i}] Agent: {answer}")
        print()


# ============================================================
# EXEMPLE 5 : Statistiques et analytics
# ============================================================

def example_analytics():
    """Analyser les datasets et documents"""
    
    print("=" * 60)
    print("📊 EXEMPLE 5 : Statistiques et analytics")
    print("=" * 60)
    print()
    
    datasets = rag_helper.get_datasets()
    
    if not datasets:
        print("   ℹ️  Aucun dataset disponible")
        return
    
    print(f"📁 {len(datasets)} dataset(s) disponible(s):")
    print()
    
    total_docs = 0
    total_chunks = 0
    
    for dataset in datasets:
        info = rag_helper.get_dataset_info(dataset)
        total_docs += info['document_count']
        total_chunks += info['chunk_count']
        
        print(f"   📦 {dataset}")
        print(f"      Documents: {info['document_count']}")
        print(f"      Chunks: {info['chunk_count']}")
        print(f"      Ratio: {info['chunk_count'] / max(info['document_count'], 1):.1f} chunks/doc")
        
        # Lister les documents
        if info['documents']:
            print(f"      Fichiers:")
            for doc in info['documents'][:3]:  # Top 3
                print(f"         - {doc['filename']}")
            if len(info['documents']) > 3:
                print(f"         ... et {len(info['documents']) - 3} autres")
        
        print()
    
    print("=" * 60)
    print(f"📈 Total: {total_docs} documents, {total_chunks} chunks")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

async def main():
    """Exécute tous les exemples"""
    
    print()
    print("🎯 EXEMPLES AVANCÉS - MODULE RAG")
    print()
    
    try:
        # Vérifier que le LLM est disponible
        llm_ok = await rag_helper.check_llm_available()
        if not llm_ok:
            print("⚠️  LLM local non disponible - certains exemples seront limités")
            print("   Lancez Ollama ou LM Studio pour une démo complète")
            print()
        
        # Exécuter les exemples
        await example_knowledge_base()
        await example_code_documentation()
        await example_contextual_search()
        await example_conversation()
        example_analytics()
        
        print()
        print("✅ TOUS LES EXEMPLES TERMINÉS")
        print()
        print("💡 Prochaines étapes:")
        print("   - Testez l'interface web: http://localhost:8000/ui/rag.html")
        print("   - Ajoutez vos propres documents: python add_to_rag.py --help")
        print("   - Consultez la doc: RAG_README.md")
        print()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
