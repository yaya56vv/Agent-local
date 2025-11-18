"""
Code Routes - API endpoints for code analysis and execution
Provides endpoints for analyzing, executing, and explaining code
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json

from backend.connectors.code.code_executor import CodeExecutor

router = APIRouter()
code_executor = CodeExecutor()


class CodeRequest(BaseModel):
    """Standard request model for code operations."""
    code: str = Field(..., description="Source code")
    language: str = Field(default="python", description="Programming language")


class CodeResponse(BaseModel):
    """Standard response model for code operations."""
    analysis: Optional[str] = None
    output: Optional[str] = None
    errors: Optional[str] = None
    explanation: Optional[str] = None


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_code(request: CodeRequest):
    """
    Analyze code for quality, issues, and optimizations.
    
    Args:
        request: CodeRequest with code and language
        
    Returns:
        dict: Analysis results with quality score, issues, and recommendations
    """
    try:
        result = await code_executor.analyze(
            code=request.code,
            language=request.language
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Analysis failed")
            )
        
        # Uniformize response format
        analysis_data = result.get("analysis", {})
        
        return {
            "analysis": analysis_data.get("summary", "Code analyzed successfully"),
            "output": None,
            "errors": None,
            "explanation": json.dumps(analysis_data, indent=2) if analysis_data else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code analysis failed: {str(e)}"
        )


@router.post("/execute", response_model=Dict[str, Any])
async def execute_code(request: CodeRequest):
    """
    Execute Python code in a sandboxed environment.
    
    Args:
        request: CodeRequest with code to execute
        
    Returns:
        dict: Execution results with output and errors
    """
    try:
        result = await code_executor.execute(code=request.code)
        
        if result.get("status") == "error":
            return {
                "analysis": None,
                "output": None,
                "errors": result.get("error", "Execution failed"),
                "explanation": None
            }
        
        if result.get("status") == "timeout":
            return {
                "analysis": None,
                "output": None,
                "errors": result.get("error", "Execution timeout"),
                "explanation": f"Code execution exceeded {result.get('timeout_seconds', 5)} seconds"
            }
        
        # Uniformize response format
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        
        return {
            "analysis": None,
            "output": stdout if stdout else None,
            "errors": stderr if stderr else None,
            "explanation": f"Execution completed with return code {result.get('return_code', 0)}" if stdout or stderr else None
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/explain", response_model=Dict[str, Any])
async def explain_code(request: CodeRequest):
    """
    Explain what the code does in natural language.
    
    Args:
        request: CodeRequest with code to explain
        
    Returns:
        dict: Explanation of the code
    """
    try:
        result = await code_executor.explain(
            code=request.code,
            language=request.language
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Explanation failed")
            )
        
        # Uniformize response format
        return {
            "analysis": None,
            "output": None,
            "errors": None,
            "explanation": result.get("explanation", "No explanation available")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code explanation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the code service.
    
    Returns:
        dict: Service status and capabilities
    """
    return {
        "status": "ok",
        "service": "code",
        "capabilities": [
            "analyze",
            "execute",
            "explain"
        ],
        "execution_timeout": "5 seconds"
    }
