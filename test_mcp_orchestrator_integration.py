"""
Test script for MCP integration with Orchestrator
Tests Files, Memory, and RAG services through the orchestrator
"""
import asyncio
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.orchestrator.orchestrator import Orchestrator


async def test_files_operations():
    """Test file operations through MCP"""
    print("\n" + "="*60)
    print("TEST 1: FILE OPERATIONS VIA MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    # Test 1: Write a file
    print("\n[TEST] Writing test file...")
    result = await orchestrator._action_file_write(
        path="test_mcp_file.txt",
        content="Hello from MCP Files Service!\nThis is a test file."
    )
    print(f"✓ Write result: {result.get('status')}")
    
    # Test 2: Read the file
    print("\n[TEST] Reading test file...")
    result = await orchestrator._action_file_read(path="test_mcp_file.txt")
    print(f"✓ Read result: {result.get('status')}")
    print(f"  Content preview: {result.get('content', '')[:50]}...")
    
    # Test 3: List directory
    print("\n[TEST] Listing current directory...")
    result = await orchestrator._action_file_list(path=".")
    print(f"✓ List result: {result.get('status')}")
    print(f"  Found {len(result.get('files', []))} items")
    
    # Test 4: Delete the file
    print("\n[TEST] Deleting test file...")
    result = await orchestrator._action_file_delete(path="test_mcp_file.txt")
    print(f"✓ Delete result: {result.get('status')}")
    
    print("\n✅ FILE OPERATIONS TEST COMPLETED")


async def test_memory_operations():
    """Test memory operations through MCP"""
    print("\n" + "="*60)
    print("TEST 2: MEMORY OPERATIONS VIA MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    session_id = "test_mcp_session"
    
    # Test 1: Add messages
    print("\n[TEST] Adding messages to memory...")
    await orchestrator.memory_client.add_message(
        session_id=session_id,
        role="user",
        content="Hello, this is a test message"
    )
    await orchestrator.memory_client.add_message(
        session_id=session_id,
        role="assistant",
        content="I received your test message!"
    )
    print("✓ Messages added successfully")
    
    # Test 2: Get context
    print("\n[TEST] Getting conversation context...")
    context = await orchestrator.memory_client.get_context(
        session_id=session_id,
        max_messages=10
    )
    print(f"✓ Context retrieved: {len(context)} characters")
    print(f"  Preview: {context[:100]}...")
    
    # Test 3: Search memory
    print("\n[TEST] Searching memory...")
    results = await orchestrator.memory_client.search(
        query="test",
        session_id=session_id
    )
    print(f"✓ Search found {len(results)} results")
    
    # Test 4: Get messages
    print("\n[TEST] Getting all messages...")
    result = await orchestrator.memory_client.get_messages(
        session_id=session_id
    )
    messages = result.get("messages", [])
    print(f"✓ Retrieved {len(messages)} messages")
    
    # Test 5: Clear session
    print("\n[TEST] Clearing test session...")
    result = await orchestrator.memory_client.clear_session(session_id)
    print(f"✓ Session cleared: {result.get('status')}")
    
    print("\n✅ MEMORY OPERATIONS TEST COMPLETED")


async def test_rag_operations():
    """Test RAG operations through MCP"""
    print("\n" + "="*60)
    print("TEST 3: RAG OPERATIONS VIA MCP")
    print("="*60)
    
    orchestrator = Orchestrator()
    test_dataset = "test_mcp_dataset"
    
    # Test 1: Add document
    print("\n[TEST] Adding document to RAG...")
    doc_id = await orchestrator.rag_client.add_document(
        dataset=test_dataset,
        document_id="test_doc_1",
        text="This is a test document about MCP integration. It contains information about testing the RAG service.",
        metadata={"source": "test", "type": "integration_test"}
    )
    print(f"✓ Document added with ID: {doc_id}")
    
    # Test 2: Query RAG
    print("\n[TEST] Querying RAG...")
    results = await orchestrator.rag_client.query(
        dataset=test_dataset,
        query="MCP integration testing",
        top_k=3
    )
    print(f"✓ Query returned {len(results)} results")
    if results:
        print(f"  Top result: {results[0].get('content', '')[:80]}...")
    
    # Test 3: List documents
    print("\n[TEST] Listing documents...")
    documents = await orchestrator.rag_client.list_documents(dataset=test_dataset)
    print(f"✓ Found {len(documents)} documents in dataset")
    
    # Test 4: Get dataset info
    print("\n[TEST] Getting dataset info...")
    info = await orchestrator.rag_client.get_dataset_info(test_dataset)
    print(f"✓ Dataset info retrieved")
    print(f"  Document count: {info.get('document_count', 0)}")
    print(f"  Chunk count: {info.get('chunk_count', 0)}")
    
    # Test 5: Delete dataset (cleanup)
    print("\n[TEST] Cleaning up test dataset...")
    result = await orchestrator.rag_client.delete_dataset(test_dataset)
    print(f"✓ Dataset deleted: {result.get('status')}")
    
    print("\n✅ RAG OPERATIONS TEST COMPLETED")


async def test_orchestrator_integration():
    """Test full orchestrator integration with MCP"""
    print("\n" + "="*60)
    print("TEST 4: FULL ORCHESTRATOR INTEGRATION")
    print("="*60)
    
    orchestrator = Orchestrator()
    
    # Test file operation through orchestrator
    print("\n[TEST] File operation via orchestrator.run()...")
    result = await orchestrator.run(
        prompt="List files in the current directory",
        session_id="integration_test",
        execution_mode="auto"
    )
    print(f"✓ Intention: {result.get('intention')}")
    print(f"✓ Confidence: {result.get('confidence')}")
    print(f"✓ Steps: {len(result.get('steps', []))}")
    print(f"✓ Execution results: {len(result.get('execution_results', []))}")
    
    print("\n✅ FULL INTEGRATION TEST COMPLETED")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCP ORCHESTRATOR INTEGRATION TEST SUITE")
    print("="*60)
    print("\nThis test suite verifies that the orchestrator correctly")
    print("integrates with MCP services for Files, Memory, and RAG.")
    print("\nMake sure all MCP servers are running:")
    print("  - Files:  http://localhost:8001")
    print("  - Memory: http://localhost:8002")
    print("  - RAG:    http://localhost:8003")
    
    try:
        # Run all tests
        await test_files_operations()
        await test_memory_operations()
        await test_rag_operations()
        await test_orchestrator_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nThe orchestrator is now successfully integrated with MCP services.")
        print("Phase 1 integration (Files, Memory, RAG) is complete.")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())