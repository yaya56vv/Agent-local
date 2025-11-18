from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.orchestrator.orchestrator import Orchestrator


router = APIRouter()


class OrchestrateRequest(BaseModel):
    """Request model for orchestration endpoint."""
    prompt: str = Field(..., description="User's input text to orchestrate")
    context: Optional[str] = Field(None, description="Optional additional context")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")


class OrchestrateResponse(BaseModel):
    """Response model for orchestration endpoint."""
    intention: str = Field(..., description="Detected primary intention")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    steps: List[Dict[str, Any]] = Field(..., description="Action plan steps")
    response: str = Field(..., description="Human-readable response")
    execution_results: Optional[List[Any]] = Field(None, description="Results from plan execution")


# Initialize orchestrator
try:
    orchestrator = Orchestrator()
except Exception as e:
    orchestrator = None
    print(f"Warning: Could not initialize orchestrator at startup: {e}")


@router.post("/", response_model=OrchestrateResponse)
async def orchestrate(request: OrchestrateRequest):
    """
    Main orchestration endpoint.
    
    Analyzes user input, detects intention, creates action plan,
    and executes it if possible.
    
    Args:
        request: OrchestrateRequest with prompt, optional context and session_id
        
    Returns:
        OrchestrateResponse: Structured orchestration result with execution results
        
    Raises:
        HTTPException: If orchestration fails
    """
    try:
        # Create orchestrator if not initialized at startup
        if orchestrator is None:
            orch = Orchestrator()
        else:
            orch = orchestrator
        
        # Step 1: Think - analyze and create plan
        plan = await orch.think(request.prompt, request.context)
        
        # Step 2: Execute - run the plan
        execution_result = await orch.execute_plan(plan)
        
        # Combine results
        return OrchestrateResponse(
            intention=plan.get("intention", "general"),
            confidence=plan.get("confidence", 0.0),
            steps=plan.get("steps", []),
            response=plan.get("response", ""),
            execution_results=execution_result.get("results", [])
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Configuration error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for orchestration service.
    
    Returns:
        dict: Health status and orchestrator availability
    """
    try:
        if orchestrator is None:
            test_orch = Orchestrator()
            status = "healthy"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "service": "orchestration",
            "orchestrator_available": True
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "orchestration",
            "orchestrator_available": False,
            "error": str(e)
        }