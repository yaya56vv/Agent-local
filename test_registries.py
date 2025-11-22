from backend.config.model_registry import model_registry
from backend.config.agent_registry import agent_registry

def test_registries():
    print("=== Model Registry ===")
    roles = model_registry.list_roles()
    print(f"Roles: {roles}")
    
    for role in roles:
        model = model_registry.get_model(role)
        available = model_registry.provider_available(role)
        print(f"Role: {role:<12} | Available: {str(available):<5} | Config: {model}")

    print("\n=== Agent Registry ===")
    active_agents = agent_registry.list_active_agents()
    print(f"Active Agents: {active_agents}")
    
    for role in roles:
        agent = agent_registry.get_agent(role)
        if agent:
            print(f"Agent: {role:<12} | Tools: {len(agent.get('mcp_tools', []))} | RAG: {agent.get('rag_profile', {})}")

if __name__ == "__main__":
    test_registries()

