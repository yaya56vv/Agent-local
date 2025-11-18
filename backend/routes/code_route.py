# ============================================================
# CODE ROUTE — Endpoints pour analyse et exécution de code
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from backend.connectors.code.code_executor import CodeExecutor


router = APIRouter()
code_executor = CodeExecutor()


# ============================================================
# REQUEST MODELS
# ============================================================

class AnalyzeRequest(BaseModel):
    """Request model for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(default="python", description="Programming language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def add(a, b):\n    return a + b",
                "language": "python"
            }
        }


class ExecuteRequest(BaseModel):
    """Request model for code execution."""
    code: str = Field(..., description="Python code to execute")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "print('Hello, World!')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"
            }
        }


class DebugRequest(BaseModel):
    """Request model for code debugging."""
    code: str = Field(..., description="Problematic code")
    error_message: str = Field(..., description="Error message received")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "result = 10 / 0",
                "error_message": "ZeroDivisionError: division by zero"
            }
        }


class OptimizeRequest(BaseModel):
    """Request model for code optimization."""
    code: str = Field(..., description="Code to optimize")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "numbers = [1, 2, 3, 4, 5]\nsquares = []\nfor n in numbers:\n    squares.append(n * n)"
            }
        }


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze code for quality, issues, optimizations, and security vulnerabilities.
    
    Uses Kimi-Dev API to provide comprehensive code analysis including:
    - Code quality assessment
    - Bug detection
    - Performance optimization suggestions
    - Security vulnerability identification
    - Best practices recommendations
    
    Args:
        request: AnalyzeRequest with code and language
        
    Returns:
        dict: Analysis results with quality score, issues, optimizations, and recommendations
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
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code analysis failed: {str(e)}"
        )


@router.post("/run", response_model=Dict[str, Any])
async def run_code(request: ExecuteRequest):
    """
    Execute Python code in a sandboxed subprocess with 5-second timeout.
    
    Safely executes Python code and captures:
    - Standard output (stdout)
    - Standard error (stderr)
    - Return code
    - Timeout status
    
    Security features:
    - Isolated subprocess execution
    - 5-second timeout limit
    - No file system access by default
    
    Args:
        request: ExecuteRequest with Python code
        
    Returns:
        dict: Execution results with stdout, stderr, and status
    """
    try:
        result = await code_executor.execute(code=request.code)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Execution failed")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/debug", response_model=Dict[str, Any])
async def debug_code(request: DebugRequest):
    """
    Debug problematic code using Kimi-Dev API.
    
    Analyzes code with error messages to provide:
    - Root cause analysis
    - Fixed code
    - Detailed explanation of changes
    - Additional debugging tips
    
    Args:
        request: DebugRequest with code and error message
        
    Returns:
        dict: Debug results with fixed code and explanations
    """
    try:
        result = await code_executor.debug(
            code=request.code,
            error_message=request.error_message
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Debugging failed")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code debugging failed: {str(e)}"
        )


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_code(request: OptimizeRequest):
    """
    Optimize code for performance and best practices using Kimi-Dev API.
    
    Provides optimized version with:
    - Performance improvements
    - Memory efficiency enhancements
    - Code readability improvements
    - Best practices compliance
    
    Args:
        request: OptimizeRequest with code to optimize
        
    Returns:
        dict: Optimization results with improved code and explanations
    """
    try:
        result = await code_executor.optimize(code=request.code)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Optimization failed")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code optimization failed: {str(e)}"
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
            "debug",
            "optimize"
        ],
        "execution_timeout": "5 seconds"
    }
