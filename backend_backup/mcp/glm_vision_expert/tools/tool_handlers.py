"""
Tool Handlers for GLM Vision Expert
Implements all MCP tools with GLM-4.6 integration
"""

import os
import re
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.mcp.glm_vision_expert.clients.glm_client import GLMClient
from backend.rag.rag_store import EnhancedRAGStore
from backend.config.settings import settings


class ToolHandlers:
    """
    Handles all tool operations for GLM Vision Expert MCP server.
    Each tool uses GLM-4.6 for intelligent processing.
    """
    
    # Whitelist of safe shell commands
    SAFE_COMMANDS = {
        "ls", "dir", "pwd", "cd", "echo", "cat", "type",
        "git", "npm", "pip", "python", "node",
        "mkdir", "touch", "rm", "cp", "mv"
    }
    
    def __init__(self):
        """Initialize tool handlers with GLM client and RAG store."""
        self.glm_client = GLMClient()
        self.rag_store = EnhancedRAGStore()
        self.workspace_root = Path("c:/AGENT LOCAL")
    
    async def solve_problem(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Solve a problem using GLM-4.6 reasoning capabilities.
        
        Args:
            description: Problem description
            context: Optional context information
            
        Returns:
            Solution with reasoning steps
        """
        system_prompt = """You are GLM Vision Expert, a highly capable AI assistant.
Analyze the problem carefully and provide a structured solution with:
1. Problem understanding
2. Analysis approach
3. Step-by-step solution
4. Recommendations"""
        
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{context}"
        
        prompt = f"Problem: {description}{context_str}\n\nProvide a comprehensive solution:"
        
        try:
            result = await self.glm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2048
            )
            
            return {
                "status": "success",
                "solution": result["text"],
                "model": result["model"],
                "usage": result.get("usage", {})
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def analyze_code(
        self,
        filepath: str,
        task: str
    ) -> Dict[str, Any]:
        """
        Analyze code file with GLM-4.6.
        
        Args:
            filepath: Path to code file
            task: Analysis task description
            
        Returns:
            Code analysis results
        """
        try:
            # Read file
            file_path = self.workspace_root / filepath
            if not file_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {filepath}"
                }
            
            code_content = file_path.read_text(encoding="utf-8")
            
            system_prompt = """You are an expert code analyzer. Provide detailed analysis including:
1. Code structure and organization
2. Potential issues or bugs
3. Performance considerations
4. Best practices recommendations
5. Security concerns if any"""
            
            prompt = f"""Analyze this code file: {filepath}

Task: {task}

Code:
```
{code_content}
```

Provide comprehensive analysis:"""
            
            result = await self.glm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2048
            )
            
            return {
                "status": "success",
                "filepath": filepath,
                "analysis": result["text"],
                "model": result["model"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def analyze_visual_screenshot(
        self,
        image_base64: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Analyze screenshot using GLM-4.6 vision capabilities.
        
        Args:
            image_base64: Base64 encoded screenshot
            question: Question about the screenshot
            
        Returns:
            Visual analysis results
        """
        system_prompt = """You are a vision analysis expert. Analyze screenshots with focus on:
1. UI/UX elements and layout
2. Text content (OCR)
3. Visual hierarchy
4. Potential issues or errors
5. User experience insights"""
        
        try:
            analysis = await self.glm_client.analyze_image(
                image_base64=image_base64,
                question=question,
                system_prompt=system_prompt
            )
            
            return {
                "status": "success",
                "analysis": analysis,
                "question": question
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def rag_query(
        self,
        query: str,
        dataset: str
    ) -> Dict[str, Any]:
        """
        Query RAG store and synthesize answer with GLM-4.6.
        
        Args:
            query: Search query
            dataset: Dataset to search in
            
        Returns:
            RAG query results with synthesized answer
        """
        try:
            # Query RAG store
            results = await self.rag_store.query(
                dataset=dataset,
                question=query,
                top_k=5
            )
            
            if not results:
                return {
                    "status": "success",
                    "answer": "No relevant information found in the dataset.",
                    "sources": []
                }
            
            # Build context from results
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(
                    f"[Source {i}] {result['filename']}:\n{result['content']}\n"
                )
            
            context = "\n".join(context_parts)
            
            # Synthesize answer with GLM
            system_prompt = """You are a knowledge synthesis expert. Use the provided sources to answer the question accurately.
Always cite your sources and be precise."""
            
            prompt = f"""Question: {query}

Available Information:
{context}

Provide a comprehensive answer based on the sources:"""
            
            result = await self.glm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            return {
                "status": "success",
                "answer": result["text"],
                "sources": [
                    {
                        "filename": r["filename"],
                        "similarity": r["similarity"]
                    }
                    for r in results
                ],
                "dataset": dataset
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def rag_write(
        self,
        content: str,
        dataset: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write content to RAG store with validation.
        
        Args:
            content: Content to store
            dataset: Target dataset
            filename: Optional filename
            metadata: Optional metadata
            
        Returns:
            Write operation result
        """
        try:
            # Validate dataset
            valid_datasets = ["agent_core", "context_flow", "agent_memory", "projects", "scratchpad"]
            if dataset not in valid_datasets:
                return {
                    "status": "error",
                    "error": f"Invalid dataset. Must be one of: {', '.join(valid_datasets)}"
                }
            
            # Generate filename if not provided
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"glm_entry_{timestamp}.txt"
            
            # Add document to RAG
            doc_id = await self.rag_store.add_document(
                dataset=dataset,
                filename=filename,
                content=content,
                metadata=metadata or {}
            )
            
            return {
                "status": "success",
                "document_id": doc_id,
                "dataset": dataset,
                "filename": filename,
                "message": "Content successfully stored in RAG"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def file_read(
        self,
        filepath: str
    ) -> Dict[str, Any]:
        """
        Read file content.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content
        """
        try:
            file_path = self.workspace_root / filepath
            if not file_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {filepath}"
                }
            
            content = file_path.read_text(encoding="utf-8")
            
            return {
                "status": "success",
                "filepath": filepath,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def file_write(
        self,
        filepath: str,
        content: str,
        allow: bool = False
    ) -> Dict[str, Any]:
        """
        Write content to file with validation.
        
        Args:
            filepath: Target file path
            content: Content to write
            allow: Must be True to authorize write
            
        Returns:
            Write operation result
        """
        if not allow:
            return {
                "status": "error",
                "error": "Permission denied: allow=True required for file write"
            }
        
        try:
            file_path = self.workspace_root / filepath
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding="utf-8")
            
            return {
                "status": "success",
                "filepath": filepath,
                "size": len(content),
                "message": "File written successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def file_search(
        self,
        pattern: str,
        directory: str = "."
    ) -> Dict[str, Any]:
        """
        Search for files matching pattern.
        
        Args:
            pattern: Search pattern (glob or regex)
            directory: Directory to search in
            
        Returns:
            List of matching files
        """
        try:
            search_path = self.workspace_root / directory
            if not search_path.exists():
                return {
                    "status": "error",
                    "error": f"Directory not found: {directory}"
                }
            
            # Use glob pattern
            matches = list(search_path.glob(pattern))
            
            results = [
                {
                    "path": str(m.relative_to(self.workspace_root)),
                    "name": m.name,
                    "is_file": m.is_file(),
                    "size": m.stat().st_size if m.is_file() else None
                }
                for m in matches
            ]
            
            return {
                "status": "success",
                "pattern": pattern,
                "directory": directory,
                "matches": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def shell_execute_safe(
        self,
        command: str,
        allow: bool = False
    ) -> Dict[str, Any]:
        """
        Execute shell command with safety checks.
        
        Args:
            command: Command to execute
            allow: Must be True to authorize execution
            
        Returns:
            Command execution result
        """
        if not allow:
            return {
                "status": "error",
                "error": "Permission denied: allow=True required for command execution"
            }
        
        # Extract base command
        base_cmd = command.split()[0] if command else ""
        
        # Check whitelist
        if base_cmd not in self.SAFE_COMMANDS:
            return {
                "status": "error",
                "error": f"Command '{base_cmd}' not in whitelist. Safe commands: {', '.join(self.SAFE_COMMANDS)}"
            }
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace_root)
            )
            
            return {
                "status": "success",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Command execution timeout (30s)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def browser_search(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Perform web search and summarize results with GLM-4.6.
        
        Args:
            query: Search query
            
        Returns:
            Search results with summary
        """
        try:
            # Use DuckDuckGo for search
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return {
                    "status": "success",
                    "query": query,
                    "summary": "No results found.",
                    "results": []
                }
            
            # Build context from results
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(
                    f"[Result {i}] {result['title']}\n{result['body']}\nURL: {result['href']}\n"
                )
            
            context = "\n".join(context_parts)
            
            # Summarize with GLM
            system_prompt = "You are a web search summarizer. Provide a concise, accurate summary of search results."
            
            prompt = f"""Search Query: {query}

Search Results:
{context}

Provide a comprehensive summary of the findings:"""
            
            glm_result = await self.glm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            return {
                "status": "success",
                "query": query,
                "summary": glm_result["text"],
                "results": [
                    {
                        "title": r["title"],
                        "url": r["href"],
                        "snippet": r["body"]
                    }
                    for r in results
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
