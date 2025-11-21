"""
Test script for MCP System Server
Tests all endpoints including security checks.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8006"


def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("[OK] Health check passed")


def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("[OK] Root endpoint passed")


def test_list_processes():
    """Test list_processes endpoint."""
    print("\n=== Testing List Processes ===")
    response = requests.get(f"{BASE_URL}/system/list_processes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} processes")
    
    # Show first 5 processes as sample
    if data.get('processes'):
        print("\nSample processes:")
        for proc in data['processes'][:5]:
            print(f"  - PID: {proc['pid']}, Name: {proc['name']}, Memory: {proc['memory_mb']} MB")
    
    assert response.status_code == 200
    assert data["success"] is True
    assert "processes" in data
    print("[OK] List processes passed")


def test_kill_process_without_allow():
    """Test kill_process without allow=True (should fail)."""
    print("\n=== Testing Kill Process WITHOUT allow=True ===")
    payload = {
        "name": "notepad.exe",
        "allow": False
    }
    response = requests.post(f"{BASE_URL}/system/kill_process", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    print("[OK] Security check passed - operation correctly denied without allow=True")


def test_kill_process_with_allow():
    """Test kill_process with allow=True on a test process."""
    print("\n=== Testing Kill Process WITH allow=True ===")
    
    # First, start a test notepad process
    print("Starting test notepad process...")
    import subprocess
    test_proc = subprocess.Popen(["notepad.exe"])
    time.sleep(1)  # Give it time to start
    
    payload = {
        "name": "notepad.exe",
        "allow": True
    }
    response = requests.post(f"{BASE_URL}/system/kill_process", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["killed_count"] >= 1
    print(f"[OK] Kill process passed - killed {data['killed_count']} process(es)")


def test_open_file_without_allow():
    """Test open_file without allow=True (should fail)."""
    print("\n=== Testing Open File WITHOUT allow=True ===")
    payload = {
        "path": "README.md",
        "allow": False
    }
    response = requests.post(f"{BASE_URL}/system/open_file", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    print("[OK] Security check passed - operation correctly denied without allow=True")


def test_open_folder_without_allow():
    """Test open_folder without allow=True (should fail)."""
    print("\n=== Testing Open Folder WITHOUT allow=True ===")
    payload = {
        "path": ".",
        "allow": False
    }
    response = requests.post(f"{BASE_URL}/system/open_folder", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    print("[OK] Security check passed - operation correctly denied without allow=True")


def test_run_program_without_allow():
    """Test run_program without allow=True (should fail)."""
    print("\n=== Testing Run Program WITHOUT allow=True ===")
    payload = {
        "path": "notepad.exe",
        "allow": False
    }
    response = requests.post(f"{BASE_URL}/system/run_program", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    print("[OK] Security check passed - operation correctly denied without allow=True")


def test_exists_without_allow():
    """Test exists without allow=True (should fail)."""
    print("\n=== Testing Exists WITHOUT allow=True ===")
    payload = {
        "path": "README.md",
        "allow": False
    }
    response = requests.post(f"{BASE_URL}/system/exists", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]
    print("[OK] Security check passed - operation correctly denied without allow=True")


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP SYSTEM SERVER TESTS")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        test_root()
        
        # List processes (no allow needed)
        test_list_processes()
        
        # Security tests (without allow=True)
        test_kill_process_without_allow()
        test_open_file_without_allow()
        test_open_folder_without_allow()
        test_run_program_without_allow()
        test_exists_without_allow()
        
        # Functional test with allow=True
        test_kill_process_with_allow()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED [OK]")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Could not connect to server. Is it running on port 8006?")
        return 1
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())