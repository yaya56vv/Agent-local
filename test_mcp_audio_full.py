"""
Test script for MCP Audio Service with Whisper + XTTS-v2
Tests the three main endpoints with real AI models
"""

import requests
import base64
import io
import wave
import struct

# Service URL
BASE_URL = "http://localhost:8007"

def create_test_wav():
    """Create a simple test WAV file with a tone"""
    sample_rate = 16000
    duration = 1  # seconds
    frequency = 440  # Hz (A note)
    
    # Generate sine wave
    samples = []
    for i in range(int(sample_rate * duration)):
        value = int(32767 * 0.3 * (i % (sample_rate // frequency)) / (sample_rate // frequency))
        samples.append(struct.pack('<h', value))
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))
    
    wav_buffer.seek(0)
    return wav_buffer.read()


def test_transcribe():
    """Test 1: Audio transcription with Whisper"""
    print("\n[1] Testing POST /audio/transcribe with Whisper...")
    
    # Create a test audio file
    test_audio = create_test_wav()
    files = {"file": ("test.wav", io.BytesIO(test_audio), "audio/wav")}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/transcribe", files=files, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify response structure
        data = response.json()
        assert "text" in data, "Missing 'text' field"
        assert "confidence" in data, "Missing 'confidence' field"
        print("[OK] Test transcribe PASSED")
        print(f"Transcribed text: {data['text']}")
        return True
    except requests.exceptions.Timeout:
        print("[WARN] Request timed out - Whisper model may be loading")
        return False
    except Exception as e:
        print(f"[FAIL] Test transcribe FAILED: {e}")
        return False


def test_speech():
    """Test 2: Text-to-speech with XTTS-v2"""
    print("\n[2] Testing POST /audio/speech with XTTS-v2...")
    
    payload = {"text": "Bonjour, je suis ton agent local."}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/speech", json=payload, timeout=120)
        print(f"Status: {response.status_code}")
        
        # Verify response structure
        data = response.json()
        assert "audio_base64" in data, "Missing 'audio_base64' field"
        
        # Decode and check audio data
        audio_bytes = base64.b64decode(data["audio_base64"])
        print(f"Generated audio size: {len(audio_bytes)} bytes")
        
        # Optionally save to file for manual verification
        with open("test_output.wav", "wb") as f:
            f.write(audio_bytes)
        print("Audio saved to test_output.wav")
        
        print("[OK] Test speech PASSED")
        return True
    except requests.exceptions.Timeout:
        print("[WARN] Request timed out - XTTS model may be loading")
        return False
    except Exception as e:
        print(f"[FAIL] Test speech FAILED: {e}")
        return False


def test_analyze():
    """Test 3: Audio analysis with librosa"""
    print("\n[3] Testing POST /audio/analyze with librosa...")
    
    # Create a test audio file
    test_audio = create_test_wav()
    files = {"file": ("test.wav", io.BytesIO(test_audio), "audio/wav")}
    
    try:
        response = requests.post(f"{BASE_URL}/audio/analyze", files=files, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify response structure
        data = response.json()
        assert "duration_seconds" in data, "Missing 'duration_seconds' field"
        assert "amplitude_mean" in data, "Missing 'amplitude_mean' field"
        assert "amplitude_std" in data, "Missing 'amplitude_std' field"
        print("[OK] Test analyze PASSED")
        return True
    except Exception as e:
        print(f"[FAIL] Test analyze FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP AUDIO SERVICE - FULL AI TEST SUITE")
    print("Whisper + XTTS-v2 + librosa")
    print("=" * 60)
    print(f"\nTesting service at: {BASE_URL}")
    print("\nMake sure the service is running:")
    print("  python -m uvicorn backend.mcp.audio.server:app --host 0.0.0.0 --port 8007")
    print("\nNote: First run may take time as models load into memory")
    print("\n" + "=" * 60)
    
    results = []
    results.append(("Transcribe (Whisper)", test_transcribe()))
    results.append(("Speech (XTTS-v2)", test_speech()))
    results.append(("Analyze (librosa)", test_analyze()))
    
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
        print("WARNING: SOME TESTS FAILED - Check logs above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    main()
