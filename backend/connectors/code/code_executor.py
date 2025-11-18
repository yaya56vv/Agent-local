# ============================================================
# CODE EXECUTOR — Analyse et exécution de code Python
# ============================================================

import asyncio
import subprocess
import sys
import json
from typing import Dict, Any, Optional
import httpx
from backend.config.settings import settings


class CodeExecutor:
    """
    Code analysis and execution module.
    - Uses Kimi-Dev API for code analysis, debugging, and optimization
    - Executes Python code in a sandboxed subprocess with timeout
    - Returns structured JSON responses
    """

    def __init__(self):
        """Initialize the CodeExecutor with Kimi API configuration."""
        self.kimi_endpoint = settings.KIMI_ENDPOINT
        self.kimi_api_key = settings.KIMI_API_KEY
        self.timeout_seconds = 5

    async def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code using Kimi-Dev API for debugging, optimization, and suggestions.
        
        Args:
            code: The source code to analyze
            language: Programming language (default: "python")
            
        Returns:
            dict: Analysis results with suggestions, issues, and optimizations
        """
        try:
            analysis_prompt = f"""You are an expert code analyzer. Analyze the following {language} code and provide:

1. **Code Quality**: Rate the code quality (1-10) and explain why
2. **Issues**: List any bugs, errors, or potential problems
3. **Optimizations**: Suggest performance improvements
4. **Best Practices**: Note any violations of best practices
5. **Security**: Identify potential security vulnerabilities

Code to analyze:
```{language}
{code}
```

Respond in JSON format:
{{
  "quality_score": 7,
  "summary": "Brief overall assessment",
  "issues": [
    {{"type": "error|warning|info", "line": 10, "message": "Description"}}
  ],
  "optimizations": [
    {{"suggestion": "Description", "impact": "high|medium|low"}}
  ],
  "security": [
    {{"severity": "critical|high|medium|low", "issue": "Description"}}
  ],
  "best_practices": ["Recommendation 1", "Recommendation 2"]
}}"""

            # Call Kimi API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.kimi_endpoint}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.kimi_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert code analyst. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": analysis_prompt
                            }
                        ],
                        "temperature": 0.3,
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "error": f"Kimi API error: {response.status_code}",
                        "details": response.text
                    }
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from markdown code blocks if present
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()
                    elif "```" in content:
                        json_start = content.find("```") + 3
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()
                    
                    analysis_data = json.loads(content)
                    
                    return {
                        "status": "success",
                        "language": language,
                        "analysis": analysis_data
                    }
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, return raw content
                    return {
                        "status": "success",
                        "language": language,
                        "analysis": {
                            "summary": content,
                            "raw_response": True
                        }
                    }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "analysis_error"
            }

    async def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed subprocess with timeout.
        
        Args:
            code: Python code to execute
            
        Returns:
            dict: Execution results with stdout, stderr, return code, and timing
        """
        try:
            # Prepare execution environment
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-c",
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                return {
                    "status": "success",
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "return_code": process.returncode,
                    "timeout": False,
                    "timeout_seconds": self.timeout_seconds
                }
                
            except asyncio.TimeoutError:
                # Kill process on timeout
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                
                return {
                    "status": "timeout",
                    "error": f"Execution exceeded {self.timeout_seconds} seconds timeout",
                    "timeout": True,
                    "timeout_seconds": self.timeout_seconds
                }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "execution_error"
            }

    async def debug(self, code: str, error_message: str) -> Dict[str, Any]:
        """
        Debug code with error message using Kimi-Dev API.
        
        Args:
            code: The problematic code
            error_message: The error message received
            
        Returns:
            dict: Debug suggestions and fixed code
        """
        try:
            debug_prompt = f"""You are an expert debugger. The following code produced an error:

**Code:**
```python
{code}
```

**Error:**
```
{error_message}
```

Please provide:
1. **Root Cause**: Explain what caused the error
2. **Fixed Code**: Provide the corrected version
3. **Explanation**: Explain what you changed and why

Respond in JSON format:
{{
  "root_cause": "Explanation of the error",
  "fixed_code": "Corrected code here",
  "explanation": "What was changed and why",
  "additional_tips": ["Tip 1", "Tip 2"]
}}"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.kimi_endpoint}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.kimi_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert debugger. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": debug_prompt
                            }
                        ],
                        "temperature": 0.3,
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "error": f"Kimi API error: {response.status_code}"
                    }
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()
                    
                    debug_data = json.loads(content)
                    
                    return {
                        "status": "success",
                        "debug": debug_data
                    }
                    
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "debug": {
                            "explanation": content,
                            "raw_response": True
                        }
                    }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "debug_error"
            }

    async def optimize(self, code: str) -> Dict[str, Any]:
        """
        Optimize code for performance using Kimi-Dev API.
        
        Args:
            code: Code to optimize
            
        Returns:
            dict: Optimized code with explanations
        """
        try:
            optimize_prompt = f"""You are an expert code optimizer. Optimize the following Python code for:
- Performance
- Memory efficiency
- Readability
- Best practices

**Original Code:**
```python
{code}
```

Respond in JSON format:
{{
  "optimized_code": "Optimized version here",
  "improvements": [
    {{"change": "What was changed", "benefit": "Why it's better", "impact": "high|medium|low"}}
  ],
  "performance_gain": "Estimated improvement (e.g., '2x faster', '50% less memory')"
}}"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.kimi_endpoint}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.kimi_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert code optimizer. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": optimize_prompt
                            }
                        ],
                        "temperature": 0.3,
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "error": f"Kimi API error: {response.status_code}"
                    }
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        content = content[json_start:json_end].strip()
                    
                    optimize_data = json.loads(content)
                    
                    return {
                        "status": "success",
                        "optimization": optimize_data
                    }
                    
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "optimization": {
                            "suggestions": content,
                            "raw_response": True
                        }
                    }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "optimization_error"
            }
