from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.connectors.reasoning.gemini_connector import GeminiReasoner
from backend.orchestrator.orchestrator import Orchestrator


router = APIRouter()


class OrchestrateRequest(BaseModel):
    """Request model for orchestration endpoint."""
    prompt: str = Field(..., description="User's input text to orchestrate")
    context: Optional[str] = Field(None, description="Optional additional context")


class ActionStep(BaseModel):
    """Model for an action step in the orchestration plan."""
    action: str
    description: str
    priority: int


class OrchestrateResponse(BaseModel):
    """Response model for orchestration endpoint."""
    intention: str = Field(..., description="Detected primary intention")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    steps: List[Dict[str, Any]] = Field(..., description="Action plan steps")
    response: str = Field(..., description="Human-readable response")
    error: Optional[str] = Field(None, description="Error message if any")
    parse_warning: Optional[str] = Field(None, description="Warning if response parsing had issues")


class CapabilitiesResponse(BaseModel):
    """Response model for capabilities endpoint."""
    capabilities: Dict[str, List[str]]
    status: str


# Initialize orchestrator components
try:
    gemini_reasoner = GeminiReasoner()
    orchestrator = Orchestrator(reasoner=gemini_reasoner)
except Exception as e:
    # If initialization fails, we'll create instances per request
    gemini_reasoner = None
    orchestrator = None
    print(f"Warning: Could not initialize orchestrator at startup: {e}")


@router.post("/", response_model=OrchestrateResponse)
async def orchestrate(request: OrchestrateRequest):
    """
    Main orchestration endpoint.
    
    Analyzes user input, detects intention, creates action plan,
    and returns structured orchestration result.
    
    Args:
        request: OrchestrateRequest with prompt and optional context
        
    Returns:
        OrchestrateResponse: Structured orchestration result
        
    Raises:
        HTTPException: If orchestration fails
    """
    try:
        # Create orchestrator if not initialized at startup
        if orchestrator is None:
            reasoner = GeminiReasoner()
            orch = Orchestrator(reasoner=reasoner)
        else:
            orch = orchestrator
        
        # Execute orchestration
        result = await orch.think(request.prompt, request.context)
        
        return OrchestrateResponse(**result)
    
    except ValueError as e:
        # Configuration or validation error
        raise HTTPException(
            status_code=400,
            detail=f"Configuration error: {str(e)}"
        )
    
    except Exception as e:
        # General orchestration error
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """
    Get orchestrator capabilities.
    
    Returns available modules and their capabilities.
    
    Returns:
        CapabilitiesResponse: Available capabilities
    """
    try:
        if orchestrator is None:
            reasoner = GeminiReasoner()
            orch = Orchestrator(reasoner=reasoner)
        else:
            orch = orchestrator
        
        capabilities = orch.get_capabilities()
        
        return CapabilitiesResponse(
            capabilities=capabilities,
            status="available"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve capabilities: {str(e)}"
        )


@router.post("/execute")
async def execute_plan(plan: Dict[str, Any]):
    """
    Execute an orchestration plan (placeholder for future implementation).
    
    Args:
        plan: The orchestration plan to execute
        
    Returns:
        dict: Execution results
    """
    try:
        if orchestrator is None:
            reasoner = GeminiReasoner()
            orch = Orchestrator(reasoner=reasoner)
        else:
            orch = orchestrator
        
        result = await orch.execute_plan(plan)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plan execution failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for orchestration service.
    
    Returns:
        dict: Health status
    """
    try:
        # Try to initialize components
        if orchestrator is None:
            reasoner = GeminiReasoner()
            status = "healthy"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "service": "orchestration",
            "gemini_configured": True
        }
    
    except ValueError as e:
        return {
            "status": "unhealthy",
            "service": "orchestration",
            "gemini_configured": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "orchestration",
            "error": str(e)
        }