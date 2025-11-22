"""
Test script for MCP Control Service
Tests all endpoints with simulated actions.
"""

import requests
import json

BASE_URL = "http://localhost:8007"

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
    assert response.json()["service"] == "MCP Control"
    print("[OK] Root endpoint passed")

def test_move_mouse():
    """Test move_mouse endpoint."""
    print("\n=== Testing Move Mouse ===")
    data = {"x": 100, "y": 200}
    response = requests.post(f"{BASE_URL}/control/move_mouse", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["action"] == "move_mouse"
    print("[OK] Move mouse passed")

def test_click_mouse():
    """Test click_mouse endpoint."""
    print("\n=== Testing Click Mouse ===")
    data = {"button": 1, "x": 150, "y": 250}
    response = requests.post(f"{BASE_URL}/control/click_mouse", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["action"] == "click_mouse"
    print("[OK] Click mouse passed")

def test_scroll():
    """Test scroll endpoint."""
    print("\n=== Testing Scroll ===")
    data = {"x": 0, "y": 0, "scroll_x": 0, "scroll_y": 5}
    response = requests.post(f"{BASE_URL}/control/scroll", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["action"] == "scroll"
    print("[OK] Scroll passed")

def test_type():
    """Test type endpoint."""
    print("\n=== Testing Type ===")
    data = {"text": "Hello, World!"}
    response = requests.post(f"{BASE_URL}/control/type", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["action"] == "type"
    print("[OK] Type passed")

def test_keypress():
    """Test keypress endpoint."""
    print("\n=== Testing Keypress ===")
    data = {"keys": ["ctrl", "c"]}
    response = requests.post(f"{BASE_URL}/control/keypress", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["action"] == "keypress"
    print("[OK] Keypress passed")

def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Control Service - Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_move_mouse()
        test_click_mouse()
        test_scroll()
        test_type()
        test_keypress()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nMCP Control Service is working correctly.")
        print("All endpoints return simulated actions as expected.")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to server.")
        print("Make sure the server is running on port 8007:")
        print("python -m uvicorn backend.mcp.control.server:app --reload --port 8007")
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
