"""
Direct test of Orchestrator MCP Control Client integration
Tests the action methods directly without LLM planning.
"""

import asyncio
import sys

# Add backend to path
sys.path.insert(0, ".")

from backend.orchestrator.orchestrator import Orchestrator


async def test_direct_mcp_actions():
    """Test orchestrator action methods directly."""
    print("\n" + "=" * 60)
    print("Testing Orchestrator MCP Control Actions (Direct)")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Test 1: Direct mouse_move action
    print("\n--- Test 1: Direct Mouse Move ---")
    result = await orchestrator._action_mouse_move(x=100, y=200)
    print(f"Result: {result}")
    assert result.get('success') == True, "Mouse move should succeed"
    assert result.get('action') == 'move_mouse', "Should be move_mouse action"
    print("[OK] Mouse move via MCP Control Client")
    
    # Test 2: Direct mouse_click action
    print("\n--- Test 2: Direct Mouse Click ---")
    result = await orchestrator._action_mouse_click(x=150, y=250, button="left")
    print(f"Result: {result}")
    assert result.get('success') == True, "Mouse click should succeed"
    assert result.get('action') == 'click_mouse', "Should be click_mouse action"
    print("[OK] Mouse click via MCP Control Client")
    
    # Test 3: Direct scroll action
    print("\n--- Test 3: Direct Mouse Scroll ---")
    result = await orchestrator._action_mouse_scroll(clicks=5)
    print(f"Result: {result}")
    assert result.get('success') == True, "Scroll should succeed"
    assert result.get('action') == 'scroll', "Should be scroll action"
    print("[OK] Mouse scroll via MCP Control Client")
    
    # Test 4: Direct keyboard_type action
    print("\n--- Test 4: Direct Keyboard Type ---")
    result = await orchestrator._action_keyboard_type(text="Hello, World!")
    print(f"Result: {result}")
    assert result.get('success') == True, "Type should succeed"
    assert result.get('action') == 'type', "Should be type action"
    print("[OK] Keyboard type via MCP Control Client")
    
    # Test 5: Direct keyboard_press action
    print("\n--- Test 5: Direct Keyboard Press ---")
    result = await orchestrator._action_keyboard_press(keys=["ctrl", "c"])
    print(f"Result: {result}")
    assert result.get('success') == True, "Keypress should succeed"
    assert result.get('action') == 'keypress', "Should be keypress action"
    print("[OK] Keyboard press via MCP Control Client")
    
    # Test 6: Verify MCP client configuration
    print("\n--- Test 6: Verify MCP Client Configuration ---")
    assert hasattr(orchestrator, 'control_client'), "Should have control_client"
    assert orchestrator.control_client.base_url == "http://localhost:8007", "Should use port 8007"
    print(f"Control Client URL: {orchestrator.control_client.base_url}")
    print("[OK] MCP Control Client properly configured")
    
    # Test 7: Verify LocalLLM client configuration
    print("\n--- Test 7: Verify LocalLLM Client Configuration ---")
    assert hasattr(orchestrator, 'local_llm_client'), "Should have local_llm_client"
    assert orchestrator.local_llm_client.base_url == "http://localhost:8008", "Should use port 8008"
    print(f"LocalLLM Client URL: {orchestrator.local_llm_client.base_url}")
    print("[OK] MCP LocalLLM Client properly configured")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All Direct MCP Action Tests Passed!")
    print("=" * 60)
    print("\nOrchestrator successfully integrated with:")
    print("✓ MCP Control Client (port 8007)")
    print("  - Mouse movements")
    print("  - Mouse clicks")
    print("  - Mouse scrolling")
    print("  - Keyboard typing")
    print("  - Keyboard key presses")
    print("✓ MCP LocalLLM Client (port 8008)")
    print("  - Ready for local LLM operations")


async def main():
    """Run all tests."""
    try:
        await test_direct_mcp_actions()
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
