"""
Test script for MCP Vision Service
Tests all endpoints with sample data
"""

import requests
import base64
import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base URL for the Vision MCP service
BASE_URL = "http://localhost:8004"


def create_test_image_base64():
    """
    Create a simple test image (1x1 red pixel PNG) encoded in base64.
    This is a minimal valid PNG for testing purposes.
    """
    # Minimal 1x1 red pixel PNG (base64 encoded)
    test_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    return test_png


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        print("✓ Health check passed")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_detailed_health():
    """Test the detailed health endpoint"""
    print("\n=== Testing Detailed Health ===")
    try:
        response = requests.get(f"{BASE_URL}/vision/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✓ Detailed health check passed")
        return True
    except Exception as e:
        print(f"✗ Detailed health check failed: {e}")
        return False


def test_analyze_image():
    """Test the analyze_image endpoint"""
    print("\n=== Testing Analyze Image ===")
    try:
        test_image = create_test_image_base64()
        
        payload = {
            "image": test_image,
            "prompt": "What do you see in this image?"
        }
        
        response = requests.post(
            f"{BASE_URL}/vision/analyze_image",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status')}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\nAnalysis Results:")
                print(f"  Description: {analysis.get('description', 'N/A')[:100]}...")
                print(f"  Detected Text: {analysis.get('detected_text', 'N/A')}")
                print(f"  Objects: {analysis.get('objects', [])}")
                print(f"  Reasoning: {analysis.get('reasoning', 'N/A')[:100]}...")
                print(f"  Suggested Actions: {analysis.get('suggested_actions', [])}")
            
            print("✓ Analyze image test passed")
            return True
        else:
            print(f"✗ Analyze image test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Analyze image test timed out (this is expected if API key is not configured)")
        return False
    except Exception as e:
        print(f"✗ Analyze image test failed: {e}")
        return False


def test_extract_text():
    """Test the extract_text endpoint"""
    print("\n=== Testing Extract Text ===")
    try:
        test_image = create_test_image_base64()
        
        payload = {
            "image": test_image
        }
        
        response = requests.post(
            f"{BASE_URL}/vision/extract_text",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status')}")
            
            if 'extracted_text' in result:
                extracted = result['extracted_text']
                print(f"\nExtracted Text Results:")
                print(f"  Text: {extracted.get('text', 'N/A')}")
                if 'full_analysis' in extracted:
                    print(f"  Full Analysis Available: Yes")
            
            print("✓ Extract text test passed")
            return True
        else:
            print(f"✗ Extract text test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Extract text test timed out (this is expected if API key is not configured)")
        return False
    except Exception as e:
        print(f"✗ Extract text test failed: {e}")
        return False


def test_analyze_screenshot():
    """Test the analyze_screenshot endpoint"""
    print("\n=== Testing Analyze Screenshot ===")
    try:
        test_image = create_test_image_base64()
        
        payload = {
            "image": test_image,
            "context": "This is a test screenshot"
        }
        
        response = requests.post(
            f"{BASE_URL}/vision/analyze_screenshot",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status')}")
            
            if 'screenshot_analysis' in result:
                analysis = result['screenshot_analysis']
                print(f"\nScreenshot Analysis Results:")
                print(f"  Description: {analysis.get('description', 'N/A')[:100]}...")
                print(f"  Detected Text: {analysis.get('detected_text', 'N/A')}")
                print(f"  Objects: {analysis.get('objects', [])}")
            
            print("✓ Analyze screenshot test passed")
            return True
        else:
            print(f"✗ Analyze screenshot test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Analyze screenshot test timed out (this is expected if API key is not configured)")
        return False
    except Exception as e:
        print(f"✗ Analyze screenshot test failed: {e}")
        return False


def test_invalid_base64():
    """Test error handling with invalid base64"""
    print("\n=== Testing Invalid Base64 Handling ===")
    try:
        payload = {
            "image": "invalid_base64_data!!!",
            "prompt": "Test"
        }
        
        response = requests.post(
            f"{BASE_URL}/vision/analyze_image",
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print(f"Response: {response.json()}")
            print("✓ Invalid base64 handling test passed")
            return True
        else:
            print(f"✗ Expected 400 status code, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Invalid base64 handling test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Vision Service Test Suite")
    print("=" * 60)
    
    results = {
        "Health Check": test_health_check(),
        "Detailed Health": test_detailed_health(),
        "Invalid Base64 Handling": test_invalid_base64(),
    }
    
    # These tests require a valid API key and may timeout
    print("\n" + "=" * 60)
    print("NOTE: The following tests require a valid OPENROUTER_API_KEY")
    print("They may timeout or fail if the API key is not configured")
    print("=" * 60)
    
    results["Analyze Image"] = test_analyze_image()
    results["Extract Text"] = test_extract_text()
    results["Analyze Screenshot"] = test_analyze_screenshot()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)