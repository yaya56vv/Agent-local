"""
Test script for Multi-Agent Router with PRE/POST processing
"""
import asyncio
from backend.orchestrator.router import MultiAgentRouter, AgentRegistry, ModelRegistry


async def test_agent_registry():
    """Test AgentRegistry functionality"""
    print("=" * 60)
    print("TEST 1: Agent Registry")
    print("=" * 60)
    
    agents = AgentRegistry.get_agents()
    print(f"\nAvailable agents: {len(agents)}")
    
    for agent_name, config in agents.items():
        print(f"\n{agent_name.upper()}:")
        print(f"  Model: {config['model']}")
        print(f"  Priority: {config['priority']}")
        print(f"  Capabilities: {', '.join(config['capabilities'][:3])}...")
    
    # Test capability lookup
    print("\n\nCapability Lookup Tests:")
    test_capabilities = ["code", "image_analysis", "summary", "complex_analysis"]
    
    for capability in test_capabilities:
        agent = AgentRegistry.get_agent_by_capability(capability)
        print(f"  {capability} -> {agent}")


async def test_model_registry():
    """Test ModelRegistry functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Model Registry")
    print("=" * 60)
    
    models = ModelRegistry.get_models()
    print(f"\nAvailable models: {len(models)}")
    
    for model_type, config in models.items():
        print(f"\n{model_type.upper()}:")
        print(f"  Model: {config['model']}")
        print(f"  Provider: {config['provider']}")
        print(f"  Description: {config['description']}")
    
    # Test model lookup for agents
    print("\n\nAgent Model Lookup:")
    test_agents = ["local", "code", "vision", "orchestrator"]
    
    for agent_name in test_agents:
        model_config = ModelRegistry.get_model_for_agent(agent_name)
        if model_config:
            print(f"  {agent_name} -> {model_config.get('model', 'N/A')}")
        else:
            print(f"  {agent_name} -> No model found")


async def test_pre_processing():
    """Test PRE-processing functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: PRE-Processing")
    print("=" * 60)
    
    router = MultiAgentRouter()
    
    test_messages = [
        "Can you help me fix this bug in my Python code?",
        "Analyze this screenshot and tell me what's wrong",
        "What's the weather like today?",
        "I need a detailed analysis of the current market trends and how they might affect our business strategy over the next quarter"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test Message {i} ---")
        print(f"Message: {message[:60]}...")
        
        result = await router.pre_process(message)
        
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Intention: {result.get('intention', 'N/A')}")
            print(f"Tasks: {', '.join(result.get('tasks', []))}")
            print(f"Agent: {result.get('agent_used', 'N/A')}")
        elif result['status'] == 'skipped':
            print(f"Reason: No pre-processing needed")


async def test_routing():
    """Test routing functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Routing")
    print("=" * 60)
    
    router = MultiAgentRouter()
    
    test_cases = [
        {
            "message": "Fix this bug in my code",
            "intention": "code"
        },
        {
            "message": "Analyze this image for me",
            "intention": "vision"
        },
        {
            "message": "I need a complex analysis of market trends",
            "intention": "analysis"
        },
        {
            "message": "What's 2+2?",
            "intention": "general"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Routing Test {i} ---")
        print(f"Message: {test_case['message']}")
        print(f"Expected: {test_case['intention']}")
        
        # Create mock pre_result
        pre_result = {
            "status": "success",
            "intention": test_case['intention'],
            "processed_message": test_case['message']
        }
        
        result = await router.route(test_case['message'], pre_result)
        
        print(f"Selected Agent: {result.get('selected_agent', 'N/A')}")
        print(f"Model: {result.get('model_config', {}).get('model', 'N/A')}")
        print(f"Reason: {result.get('routing_reason', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")


async def test_post_processing():
    """Test POST-processing functionality"""
    print("\n" + "=" * 60)
    print("TEST 5: POST-Processing")
    print("=" * 60)
    
    router = MultiAgentRouter()
    
    test_results = [
        {
            "result": {"status": "success", "output": "Code fixed successfully"},
            "message": "Fix my code"
        },
        {
            "result": {"status": "error", "error": "File not found"},
            "message": "Read this file"
        },
        {
            "result": {
                "status": "success",
                "output": "Very long output " * 100
            },
            "message": "Analyze this"
        }
    ]
    
    for i, test_case in enumerate(test_results, 1):
        print(f"\n--- Post-Processing Test {i} ---")
        print(f"Original Message: {test_case['message']}")
        print(f"Result Status: {test_case['result'].get('status')}")
        
        result = await router.post_process(
            test_case['result'],
            test_case['message']
        )
        
        print(f"Post-Process Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Tasks Applied: {', '.join(result.get('tasks', []))}")
            print(f"Agent Used: {result.get('agent_used', 'N/A')}")


async def test_complete_pipeline():
    """Test complete processing pipeline"""
    print("\n" + "=" * 60)
    print("TEST 6: Complete Pipeline (PRE -> ROUTE -> POST)")
    print("=" * 60)
    
    router = MultiAgentRouter()
    
    test_messages = [
        "Can you help me debug this Python function?",
        "Look at this screenshot and tell me what's wrong"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'=' * 60}")
        print(f"Pipeline Test {i}: {message}")
        print('=' * 60)
        
        result = await router.process_message(message)
        
        print("\n1. PRE-PROCESSING:")
        pre = result.get('pre_processing', {})
        print(f"   Status: {pre.get('status')}")
        print(f"   Intention: {pre.get('intention', 'N/A')}")
        print(f"   Tasks: {', '.join(pre.get('tasks', []))}")
        
        print("\n2. ROUTING:")
        routing = result.get('routing', {})
        print(f"   Selected Agent: {routing.get('selected_agent')}")
        print(f"   Model: {routing.get('model_config', {}).get('model', 'N/A')}")
        print(f"   Confidence: {routing.get('confidence', 0):.2f}")
        
        print("\n3. POST-PROCESSING:")
        post = result.get('post_processing', {})
        print(f"   Status: {post.get('status')}")
        print(f"   Tasks: {', '.join(post.get('tasks', []))}")
        
        print(f"\n4. FINAL RESULT:")
        print(f"   Agent Used: {result.get('agent_used')}")
        print(f"   Model Used: {result.get('model_used')}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MULTI-AGENT ROUTER TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: Agent Registry
        await test_agent_registry()
        
        # Test 2: Model Registry
        await test_model_registry()
        
        # Test 3: PRE-processing
        await test_pre_processing()
        
        # Test 4: Routing
        await test_routing()
        
        # Test 5: POST-processing
        await test_post_processing()
        
        # Test 6: Complete Pipeline
        await test_complete_pipeline()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
