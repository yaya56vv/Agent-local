# -*- coding: utf-8 -*-
"""
Script de test pour les 3 modules de la Mission 3
Teste SEARCH, CODE et SYSTEM
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_search_web():
    """Test MODULE SEARCH - POST /search/web"""
    print("\n" + "="*60)
    print("TEST SEARCH - POST /search/web")
    print("="*60)
    
    url = f"{BASE_URL}/search/web"
    payload = {
        "query": "Python FastAPI",
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Query: {data.get('query')}")
            print(f"Nombre de resultats: {len(data.get('results', []))}")
            
            if data.get('results'):
                print("\nPremier resultat:")
                result = data['results'][0]
                print(f"  - Title: {result.get('title')}")
                print(f"  - URL: {result.get('url')}")
                print(f"  - Source: {result.get('source')}")
                print(f"  - Score: {result.get('score')}")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_code_execute():
    """Test MODULE CODE - POST /code/execute"""
    print("\n" + "="*60)
    print("TEST CODE - POST /code/execute")
    print("="*60)
    
    url = f"{BASE_URL}/code/execute"
    payload = {
        "code": "print('hello mission 3')",
        "language": "python"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Output: {data.get('output')}")
            print(f"Errors: {data.get('errors')}")
            print(f"Explanation: {data.get('explanation')}")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_code_analyze():
    """Test MODULE CODE - POST /code/analyze"""
    print("\n" + "="*60)
    print("TEST CODE - POST /code/analyze")
    print("="*60)
    
    url = f"{BASE_URL}/code/analyze"
    payload = {
        "code": "def add(a, b):\n    return a + b",
        "language": "python"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Analysis: {str(data.get('analysis'))[:200]}...")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_code_explain():
    """Test MODULE CODE - POST /code/explain"""
    print("\n" + "="*60)
    print("TEST CODE - POST /code/explain")
    print("="*60)
    
    url = f"{BASE_URL}/code/explain"
    payload = {
        "code": "x = [i**2 for i in range(10)]",
        "language": "python"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Explanation: {data.get('explanation')[:200]}...")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_system_open_path():
    """Test MODULE SYSTEM - POST /system/open_path"""
    print("\n" + "="*60)
    print("TEST SYSTEM - POST /system/open_path")
    print("="*60)
    
    # Create a test file first
    test_file = "C:/AGENT LOCAL/test_mission3.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test file for Mission 3")
        print(f"[INFO] Test file created: {test_file}")
    except Exception as e:
        print(f"[ATTENTION] Could not create test file: {e}")
        return
    
    url = f"{BASE_URL}/system/open_path"
    payload = {
        "path": test_file
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def test_system_list_processes():
    """Test MODULE SYSTEM - POST /system/list_processes"""
    print("\n" + "="*60)
    print("TEST SYSTEM - POST /system/list_processes")
    print("="*60)
    
    url = f"{BASE_URL}/system/list_processes"
    
    try:
        response = requests.post(url, json={}, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Succes!")
            print(f"Status: {data.get('status')}")
            processes = data.get('data', {}).get('processes', [])
            print(f"Nombre de processus: {len(processes)}")
            if processes:
                print(f"Premier processus: {processes[0].get('name')}")
        else:
            print(f"[ERREUR] {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")


def main():
    """Execute all tests"""
    print("\n" + "="*60)
    print("TESTS DES MODULES - MISSION 3")
    print("="*60)
    print(f"URL de base: {BASE_URL}")
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("[OK] Serveur accessible")
    except Exception as e:
        print(f"[ERREUR] Serveur non accessible: {e}")
        print("\n[ATTENTION] Assurez-vous que le serveur est demarre:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        return
    
    # Run tests
    test_search_web()
    test_code_execute()
    test_code_analyze()
    test_code_explain()
    test_system_open_path()
    test_system_list_processes()
    
    print("\n" + "="*60)
    print("[OK] TESTS TERMINES")
    print("="*60)


if __name__ == "__main__":
    main()
