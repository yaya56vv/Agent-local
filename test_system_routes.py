"""
Script de test pour les routes System API
Utilise des requêtes HTTP pour tester les endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
SYSTEM_URL = f"{BASE_URL}/system"


def print_response(response):
    """Affiche la réponse de manière formatée"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_health():
    """Test le health check"""
    print("=== Test Health Check ===")
    response = requests.get(f"{SYSTEM_URL}/health")
    print_response(response)


def test_system_info():
    """Test les infos système"""
    print("=== Test System Info ===")
    response = requests.get(f"{SYSTEM_URL}/info")
    print_response(response)


def test_exists():
    """Test la vérification d'existence"""
    print("=== Test Exists - Without Permission ===")
    response = requests.post(
        f"{SYSTEM_URL}/exists",
        json={"path": "C:\\Windows", "allow": False}
    )
    print_response(response)

    print("=== Test Exists - With Permission ===")
    response = requests.post(
        f"{SYSTEM_URL}/exists",
        json={"path": "C:\\Windows", "allow": True}
    )
    print_response(response)

    print("=== Test Exists - Nonexistent Path ===")
    response = requests.post(
        f"{SYSTEM_URL}/exists",
        json={"path": "C:\\nonexistent_12345", "allow": True}
    )
    print_response(response)


def test_list_processes():
    """Test le listage des processus"""
    print("=== Test List Processes ===")
    response = requests.post(
        f"{SYSTEM_URL}/list",
        json={"allow": True}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {data['count']} processes")
        print("First 5 processes:")
        for proc in data['processes'][:5]:
            print(f"  - {proc['name']} (PID: {proc['pid']}, Mem: {proc['memory_mb']} MB)")
        print()
    else:
        print_response(response)


def test_open_file():
    """Test l'ouverture d'un fichier (exemple avec notepad)"""
    print("=== Test Open File (simulation) ===")
    # Note: Ne pas exécuter réellement pour éviter d'ouvrir des fichiers
    # Juste montrer la structure de la requête
    payload = {
        "path": "C:\\Windows\\System32\\notepad.exe",
        "allow": False  # False pour la démo
    }
    print(f"Would send: POST {SYSTEM_URL}/open/file")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("(Not executed to avoid opening files)")
    print()


def test_run_program():
    """Test le lancement d'un programme (exemple)"""
    print("=== Test Run Program (simulation) ===")
    # Note: Ne pas exécuter réellement
    payload = {
        "path": "C:\\Windows\\System32\\cmd.exe",
        "args": ["/c", "echo", "Hello"],
        "allow": False  # False pour la démo
    }
    print(f"Would send: POST {SYSTEM_URL}/run")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("(Not executed to avoid running programs)")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("System Routes API - Test Suite")
    print("=" * 60)
    print()
    print("NOTE: Make sure the FastAPI server is running on localhost:8000")
    print("Start with: uvicorn main:app --reload")
    print()
    print("=" * 60)
    print()

    try:
        # Tests qui ne modifient pas le système
        test_health()
        test_system_info()
        test_exists()
        test_list_processes()

        # Tests en simulation (ne s'exécutent pas vraiment)
        test_open_file()
        test_run_program()

        print("=" * 60)
        print("Tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Start with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\nERROR: {e}")

