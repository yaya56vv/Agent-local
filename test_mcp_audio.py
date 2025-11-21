"""
Test script for MCP Audio Service
Tests the three main endpoints: transcribe, speech, and analyze
"""

import requests
import base64
import io

# Service URL
BASE_URL = "http://localhost:8007"

def test_transcribe():
    """Test 1: Audio transcription endpoint"""
    print("\n[1] Testing POST /audio/transcribe...")
    
    # Create a fake audio file
    fake_audio = b"FAKE_WAV_DATA"
    files = {"file": ("test.wav", io.BytesIO(fake_audio), "audio/wav")}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/transcribe", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify response structure
        data = response.json()
        assert "text" in data, "Missing 'text' field"
        assert "confidence" in data, "Missing 'confidence' field"
        print("[OK] Test transcribe PASSED")
        return True
    except Exception as e:
        print(f"[FAIL] Test transcribe FAILED: {e}")
        return False


def test_speech():
    """Test 2: Text-to-speech endpoint"""
    print("\n[2] Testing POST /audio/speech...")
    
    payload = {"text": "Bonjour"}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/speech", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify response structure
        data = response.json()
        assert "audio_base64" in data, "Missing 'audio_base64' field"
        print("[OK] Test speech PASSED")
        return True
    except Exception as e:
        print(f"[FAIL] Test speech FAILED: {e}")
        return False


def test_analyze():
    """Test 3: Audio analysis endpoint"""
    print("\n[3] Testing POST /audio/analyze...")
    
    # Create a fake audio file
    fake_audio = b"FAKE_WAV_DATA"
    files = {"file": ("test.wav", io.BytesIO(fake_audio), "audio/wav")}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/analyze", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify response structure
        data = response.json()
        assert "analysis" in data, "Missing 'analysis' field"
        print("[OK] Test analyze PASSED")
        return True
    except Exception as e:
        print(f"[FAIL] Test analyze FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP AUDIO SERVICE - TEST SUITE")
    print("=" * 60)
    print(f"\nTesting service at: {BASE_URL}")
    print("\nMake sure the service is running:")
    print("  cd backend/mcp/audio")
    print("  python server.py")
    print("\n" + "=" * 60)
    
    results = []
    results.append(("Transcribe", test_transcribe()))
    results.append(("Speech", test_speech()))
    results.append(("Analyze", test_analyze()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: ALL TESTS PASSED - Ready for commit!")
    else:
        print("WARNING: SOME TESTS FAILED - Please fix before commit")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    main()