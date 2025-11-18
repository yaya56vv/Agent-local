# -*- coding: utf-8 -*-
"""
Script de test pour les endpoints RAG
Teste les 4 endpoints principaux selon les spécifications de la Mission 2
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_add_document():
    """Test 1 - Ajouter un document"""
    print("\n" + "="*60)
    print("TEST 1 - POST /rag/documents/add")
    print("="*60)
    
    url = f"{BASE_URL}/rag/documents/add"
    payload = {
        "content": "Le chat est un animal domestique très apprécié. Il est connu pour son indépendance et sa propreté.",
        "metadata": {"source": "test"}
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Document ID: {data.get('document_id')}")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Nombre de chunks: {len(data.get('chunks', []))}")
            return data.get('document_id')
        else:
            print(f"[ERREUR] Erreur: {response.text}")
            return None
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        return None


def test_query_rag():
    """Test 2 - Requête RAG"""
    print("\n" + "="*60)
    print("TEST 2 - POST /rag/query")
    print("="*60)
    
    url = f"{BASE_URL}/rag/query"
    payload = {
        "question": "Qu'est-ce qu'un chat ?"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"\nRéponse: {data.get('answer')[:200]}...")
            print(f"\nNombre de sources: {len(data.get('sources', []))}")
            
            if data.get('sources'):
                print("\nPremière source:")
                source = data['sources'][0]
                print(f"  - Chunk ID: {source.get('chunk_id')}")
                print(f"  - Score: {source.get('score'):.4f}")
                print(f"  - Contenu: {source.get('content')[:100]}...")
        else:
            print(f"[ERREUR] Erreur: {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_list_documents():
    """Test 3 - Lister les documents"""
    print("\n" + "="*60)
    print("TEST 3 - GET /rag/documents")
    print("="*60)
    
    url = f"{BASE_URL}/rag/documents"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Nombre de documents: {len(data)}")
            
            if data:
                print("\nPremier document:")
                doc = data[0]
                print(f"  - ID: {doc.get('id')}")
                print(f"  - Créé le: {doc.get('created_at')}")
                print(f"  - Contenu: {doc.get('content')[:100]}...")
        else:
            print(f"[ERREUR] Erreur: {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_delete_document(doc_id):
    """Test 4 - Supprimer un document"""
    print("\n" + "="*60)
    print("TEST 4 - DELETE /rag/documents/{id}")
    print("="*60)
    
    if not doc_id:
        print("[ATTENTION] Pas de document ID disponible, test ignore")
        return
    
    url = f"{BASE_URL}/rag/documents/{doc_id}"
    
    try:
        response = requests.delete(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
        else:
            print(f"[ERREUR] Erreur: {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("TESTS DES ENDPOINTS RAG - MISSION 2")
    print("="*60)
    print(f"URL de base: {BASE_URL}")
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("[OK] Serveur accessible")
    except Exception as e:
        print(f"[ERREUR] Serveur non accessible: {e}")
        print("\n[ATTENTION] Assurez-vous que le serveur est demarre:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        return
    
    # Exécuter les tests
    doc_id = test_add_document()
    test_query_rag()
    test_list_documents()
    test_delete_document(doc_id)
    
    print("\n" + "="*60)
    print("[OK] TESTS TERMINES")
    print("="*60)


if __name__ == "__main__":
    main()