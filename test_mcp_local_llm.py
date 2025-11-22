import requests
import time
import sys

BASE_URL = "http://localhost:8001"

def wait_for_server(retries=5, delay=2):
    print(f"Waiting for server at {BASE_URL}...")
    for i in range(retries):
        try:
            # Try root first
            try:
                root_resp = requests.get(f"{BASE_URL}/")
                print(f"Root status: {root_resp.status_code}")
                
                # Check openapi.json
                openapi = requests.get(f"{BASE_URL}/openapi.json").json()
                print("Routes found:")
                for path in openapi.get('paths', {}):
                    print(f" - {path}")
            except Exception as e:
                print(f"Error checking root/openapi: {e}")

            response = requests.get(f"{BASE_URL}/local_llm/health")
            if response.status_code == 200:
                print("Server is up!")
                return True
            else:
                print(f"Server returned status {response.status_code}")
                print(f"Response text: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"Connection refused, retrying ({i+1}/{retries})...")
        time.sleep(delay)
    return False

def test_health():
    print("\nTesting /local_llm/health...")
    try:
        response = requests.get(f"{BASE_URL}/local_llm/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_list_models():
    print("\nTesting /local_llm/list_models...")
    try:
        response = requests.get(f"{BASE_URL}/local_llm/list_models")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_generate():
    print("\nTesting /local_llm/generate...")
    payload = {
        "prompt": "Why is the sky blue?",
        "max_tokens": 50
    }
    try:
        response = requests.post(f"{BASE_URL}/local_llm/generate", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()['response'][:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_chat():
    print("\nTesting /local_llm/chat...")
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, who are you?"}
        ],
        "max_tokens": 50
    }
    try:
        response = requests.post(f"{BASE_URL}/local_llm/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()['response'][:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if wait_for_server():
        test_health()
        test_list_models()
        test_generate()
        test_chat()
    else:
        print("Could not connect to server.")

