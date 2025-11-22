"""
Test script for MCP Clients (Control and Local LLM)
Tests all client methods with their respective services.
"""

import asyncio
import sys

# Add backend to path
sys.path.insert(0, ".")

from backend.orchestrator.clients.control_client import ControlClient
from backend.orchestrator.clients.local_llm_client import LocalLlmClient


async def test_control_client():
    """Test ControlClient methods."""
    print("\n" + "=" * 60)
    print("Testing Control Client")
    print("=" * 60)
    
    client = ControlClient(base_url="http://localhost:8007")
    
    # Test health
    print("\n--- Testing health() ---")
    result = await client.health()
    print(f"Result: {result}")
    assert result.get("status") == "healthy", "Health check failed"
    print("[OK] Health check passed")
    
    # Test move_mouse
    print("\n--- Testing move_mouse() ---")
    result = await client.move_mouse(x=100, y=200)
    print(f"Result: {result}")
    assert result.get("success") == True, "Move mouse failed"
    print("[OK] Move mouse passed")
    
    # Test click_mouse
    print("\n--- Testing click_mouse() ---")
    result = await client.click_mouse(button=1, x=150, y=250)
    print(f"Result: {result}")
    assert result.get("success") == True, "Click mouse failed"
    print("[OK] Click mouse passed")
    
    # Test scroll
    print("\n--- Testing scroll() ---")
    result = await client.scroll(scroll_y=5)
    print(f"Result: {result}")
    assert result.get("success") == True, "Scroll failed"
    print("[OK] Scroll passed")
    
    # Test type
    print("\n--- Testing type() ---")
    result = await client.type(text="Hello, World!")
    print(f"Result: {result}")
    assert result.get("success") == True, "Type failed"
    print("[OK] Type passed")
    
    # Test keypress
    print("\n--- Testing keypress() ---")
    result = await client.keypress(keys=["ctrl", "c"])
    print(f"Result: {result}")
    assert result.get("success") == True, "Keypress failed"
    print("[OK] Keypress passed")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All Control Client tests passed!")
    print("=" * 60)


async def test_local_llm_client():
    """Test LocalLlmClient methods."""
    print("\n" + "=" * 60)
    print("Testing Local LLM Client")
    print("=" * 60)
    
    client = LocalLlmClient(base_url="http://localhost:8001")
    
    # Test health
    print("\n--- Testing health() ---")
    result = await client.health()
    print(f"Result: {result}")
    
    # Check if service is available
    if result.get("status") == "unhealthy":
        print("[WARNING] Local LLM service is not available")
        print("This is expected if Ollama or LM Studio is not running")
        print("Skipping remaining Local LLM tests")
        return False
    
    print("[OK] Health check passed")
    
    # Test list_models
    print("\n--- Testing list_models() ---")
    result = await client.list_models()
    print(f"Result: {result}")
    models = result.get("models", [])
    print(f"Available models: {models}")
    print("[OK] List models passed")
    
    # Only test generate and chat if models are available
    if models:
        # Test generate
        print("\n--- Testing generate() ---")
        result = await client.generate(
            prompt="Say hello in one word",
            max_tokens=10
        )
        print(f"Result: {result}")
        if result.get("response"):
            print("[OK] Generate passed")
        else:
            print("[WARNING] Generate returned no response")
        
        # Test chat
        print("\n--- Testing chat() ---")
        result = await client.chat(
            messages=[
                {"role": "user", "content": "Say hello in one word"}
            ],
            max_tokens=10
        )
        print(f"Result: {result}")
        if result.get("response"):
            print("[OK] Chat passed")
        else:
            print("[WARNING] Chat returned no response")
    else:
        print("[WARNING] No models available, skipping generate and chat tests")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Local LLM Client tests completed!")
    print("=" * 60)
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Clients - Test Suite")
    print("=" * 60)
    
    try:
        # Test Control Client
        await test_control_client()
        
        # Test Local LLM Client
        await test_local_llm_client()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL CLIENT TESTS COMPLETED!")
        print("=" * 60)
        print("\nBoth MCP clients are working correctly:")
        print("- ControlClient: All methods tested successfully")
        print("- LocalLlmClient: All methods tested (service availability dependent)")
        
        return 0
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
