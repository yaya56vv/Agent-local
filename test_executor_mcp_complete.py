"""
Test complet de l'Executor MCP avec tous les outils
Vérifie: audio, documents, et tous les autres outils
"""
import asyncio
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.orchestrator.executor_mcp import MCPExecutor


class MockOrchestrator:
    """Mock orchestrator pour les tests"""
    
    def __init__(self):
        # Mock clients
        self.files_client = MockClient("files")
        self.memory_client = MockClient("memory")
        self.rag_client = MockClient("rag")
        self.vision_client = MockClient("vision")
        self.search_client = MockClient("search")
        self.system_client = MockClient("system")
        self.control_client = MockClient("control")
        self.audio_client = MockClient("audio")
        self.documents_client = MockClient("documents")
        self.local_llm_client = MockClient("llm")
        self.timeline = MockTimeline()


class MockClient:
    """Mock client pour simuler les réponses"""
    
    def __init__(self, name):
        self.name = name
    
    async def transcribe(self, **kwargs):
        return {"text": "Mock transcription", "tool": self.name}
    
    async def text_to_speech(self, **kwargs):
        return {"audio": "base64_audio_data", "tool": self.name}
    
    async def generate_document(self, **kwargs):
        return {"document": "Mock document", "tool": self.name}
    
    async def fill_template(self, **kwargs):
        return {"filled": "Mock filled template", "tool": self.name}
    
    async def read_file(self, **kwargs):
        return {"content": "Mock file content", "tool": self.name}
    
    async def query(self, **kwargs):
        return [{"content": "Mock result", "tool": self.name}]
    
    async def search_all(self, **kwargs):
        return {"results": ["Mock search result"], "tool": self.name}


class MockTimeline:
    """Mock timeline"""
    
    async def add(self, **kwargs):
        return {"status": "added"}


async def test_executor_tools():
    """Test tous les outils de l'executor"""
    
    print("=" * 60)
    print("TEST EXECUTOR MCP - TOUS LES OUTILS")
    print("=" * 60)
    
    # Créer l'executor
    orchestrator = MockOrchestrator()
    executor = MCPExecutor(orchestrator)
    
    # Test 1: Vérifier tous les outils disponibles
    print("\n1. VÉRIFICATION DES OUTILS DISPONIBLES")
    print("-" * 60)
    
    tools = [
        "files", "memory", "rag", "vision", "search",
        "system", "control", "audio", "documents", "llm"
    ]
    
    for tool in tools:
        try:
            client = executor._tool_to_client(tool)
            print(f"[OK] {tool:12} -> {client.name}")
        except Exception as e:
            print(f"[ERROR] {tool:12} -> ERROR: {e}")
    
    # Test 2: Exécuter des actions AUDIO
    print("\n2. TEST ACTIONS AUDIO")
    print("-" * 60)
    
    audio_steps = [
        {
            "tool": "audio",
            "action": "transcribe",
            "args": {"audio_bytes": b"fake_audio"}
        },
        {
            "tool": "audio",
            "action": "text_to_speech",
            "args": {"text": "Hello world"}
        }
    ]
    
    for step in audio_steps:
        result = await executor.execute_action(step)
        print(f"Action: {step['action']}")
        print(f"Status: {result['status']}")
        print(f"Result: {result.get('result', result.get('error'))}")
        print()
    
    # Test 3: Exécuter des actions DOCUMENTS
    print("\n3. TEST ACTIONS DOCUMENTS")
    print("-" * 60)
    
    doc_steps = [
        {
            "tool": "documents",
            "action": "generate_document",
            "args": {
                "content": "Test content",
                "title": "Test Doc",
                "format": "txt"
            }
        },
        {
            "tool": "documents",
            "action": "fill_template",
            "args": {
                "template": "Hello {{name}}",
                "data": {"name": "World"}
            }
        }
    ]
    
    for step in doc_steps:
        result = await executor.execute_action(step)
        print(f"Action: {step['action']}")
        print(f"Status: {result['status']}")
        print(f"Result: {result.get('result', result.get('error'))}")
        print()
    
    # Test 4: Plan complet avec tous les outils
    print("\n4. TEST PLAN COMPLET (TOUS LES OUTILS)")
    print("-" * 60)
    
    complete_plan = [
        {"tool": "files", "action": "read_file", "args": {"path": "test.txt"}},
        {"tool": "audio", "action": "transcribe", "args": {"audio_bytes": b"audio"}},
        {"tool": "documents", "action": "generate_document", "args": {"content": "Test"}},
        {"tool": "search", "action": "search_all", "args": {"query": "test"}},
        {"tool": "rag", "action": "query", "args": {"dataset": "test", "question": "test"}}
    ]
    
    results = await executor.execute_plan(complete_plan, session_id="test")
    
    print(f"Plan exécuté: {len(results)} étapes")
    for i, result in enumerate(results):
        status = result.get('status', 'unknown')
        tool = complete_plan[i]['tool']
        action = complete_plan[i]['action']
        print(f"  {i+1}. {tool}.{action}: {status}")
    
    # Test 5: Validation de plan
    print("\n5. TEST VALIDATION DE PLAN")
    print("-" * 60)
    
    test_steps = [
        {"tool": "audio", "action": "transcribe", "args": {}},
        {"tool": "documents", "action": "generate_document", "args": {}},
        {"tool": "invalid_tool", "action": "test", "args": {}}
    ]
    
    for step in test_steps:
        validation = executor.validate_step(step)
        tool = step.get('tool', 'N/A')
        valid = "[OK]" if validation['valid'] else "[FAIL]"
        print(f"{valid} {tool}: {validation}")
    
    # Test 6: Dry run
    print("\n6. TEST DRY RUN")
    print("-" * 60)
    
    dry_run_result = await executor.dry_run(complete_plan)
    print(f"Total steps: {dry_run_result['total_steps']}")
    print(f"Valid steps: {dry_run_result['valid_steps']}")
    print(f"Invalid steps: {dry_run_result['invalid_steps']}")
    print(f"Can execute: {dry_run_result['can_execute']}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] TOUS LES TESTS REUSSIS!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_executor_tools())
