from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.orchestrator.orchestrator import Orchestrator
from backend.config.agent_registry import agent_registry


router = APIRouter()


class OrchestrateRequest(BaseModel):
    """Request model for orchestration endpoint."""
    prompt: str = Field(..., description="User's input text to orchestrate")
    context: Optional[str] = Field(None, description="Optional additional context")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    execution_mode: Optional[str] = Field(
        default="auto",
        description="Execution mode: auto | plan_only | step_by_step"
    )
    agent_id: Optional[str] = Field(
        default=None,
        description="Specific agent to use (orchestrator, code, vision, local)"
    )
    auto_routing: Optional[bool] = Field(
        default=True,
        description="Whether to enable auto-routing of requests"
    )


class OrchestrateResponse(BaseModel):
    """Response model for orchestration endpoint."""
    intention: str = Field(..., description="Detected primary intention")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    steps: List[Dict[str, Any]] = Field(..., description="Action plan steps")
    response: str = Field(..., description="Human-readable response")
    execution_results: Optional[List[Any]] = Field(None, description="Results from plan execution")
    requires_confirmation: bool = Field(False, description="Whether user confirmation is required")
    execution_mode_used: str = Field("auto", description="Execution mode that was used")


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
        
        # Use session_id from request or default
        session_id = request.session_id or "default"
        
        # Run orchestrator with execution_mode
        result = await orch.run(
            prompt=request.prompt,
            context=request.context,
            session_id=session_id,
            execution_mode=request.execution_mode,
            agent_id=request.agent_id,
            auto_routing=request.auto_routing
        )
        
        # Return unified response
        return OrchestrateResponse(
            intention=result.get("intention", "fallback"),
            confidence=result.get("confidence", 0.0),
            steps=result.get("steps", []),
            response=result.get("response", ""),
            execution_results=result.get("execution_results", []),
            requires_confirmation=result.get("requires_confirmation", False),
            execution_mode_used=result.get("execution_mode_used", "auto")
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


@router.get("/agents")
async def list_agents():
    """
    List available agents and their status.
    """
    agents = []
    for role in agent_registry.list_active_agents():
        agent = agent_registry.get_agent(role)
        if agent:
            agents.append({
                "id": role,
                "name": role.capitalize(),
                "description": agent.get("description", ""),
                "model": agent.get("model", "Unknown"),
                "provider": agent.get("provider", "Unknown"),
                "tools": agent.get("mcp_tools", [])
            })
    return agents
