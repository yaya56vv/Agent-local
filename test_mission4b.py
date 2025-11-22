"""
Test script for Mission 4B - Execution Modes + Permission System + Live Logging
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_orchestrator(prompt: str, execution_mode: str = "auto", test_name: str = ""):
    """Test orchestrator with different modes."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    print(f"Mode: {execution_mode}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/orchestrate/",
            json={
                "prompt": prompt,
                "execution_mode": execution_mode
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Status: SUCCESS")
            print(f"  Intention: {result.get('intention')}")
            print(f"  Confidence: {result.get('confidence')}")
            print(f"  Steps: {len(result.get('steps', []))}")
            print(f"  Requires Confirmation: {result.get('requires_confirmation')}")
            print(f"  Execution Mode Used: {result.get('execution_mode_used')}")
            print(f"  Execution Results: {len(result.get('execution_results', []))}")
            print(f"  Response: {result.get('response', '')[:100]}...")
            
            # Show steps
            if result.get('steps'):
                print(f"\n  Plan Steps:")
                for i, step in enumerate(result.get('steps', []), 1):
                    print(f"    {i}. {step.get('action')} - {step}")
            
            return result
        else:
            print(f"[FAIL] Status: FAILED")
            print(f"  Error: {response.status_code}")
            print(f"  Message: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        return None


def main():
    print("\n" + "="*60)
    print("MISSION 4B - TEST SUITE")
    print("="*60)
    
    # Test 1: Short safe action (should execute in auto mode)
    test_orchestrator(
        prompt="Explique ce code : print(2+2)",
        execution_mode="auto",
        test_name="Test 1 - Action courte et sûre (auto)"
    )
    
    # Test 2: Long plan (should require confirmation in auto mode)
    test_orchestrator(
        prompt="Organise un plan pour restructurer mon projet Python avec tests et documentation",
        execution_mode="auto",
        test_name="Test 2 - Plan long (auto)"
    )
    
    # Test 3: Plan only mode (never execute)
    test_orchestrator(
        prompt="Recherche les dernières nouvelles sur l'IA",
        execution_mode="plan_only",
        test_name="Test 3 - Mode plan_only"
    )
    
    # Test 4: Step by step mode
    test_orchestrator(
        prompt="Analyse ce code Python et optimise-le",
        execution_mode="step_by_step",
        test_name="Test 4 - Mode step_by_step"
    )
    
    # Test 5: Sensitive action (should require confirmation)
    test_orchestrator(
        prompt="Ouvre le dossier Documents",
        execution_mode="auto",
        test_name="Test 5 - Action sensible (auto)"
    )
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nCheck the server console for detailed logs!")


if __name__ == "__main__":
    main()
