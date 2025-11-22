"""
MCP Control Server
Provides REST API endpoints for mouse and keyboard control operations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from connectors.control.input_controller import InputController

app = FastAPI(
    title="MCP Control Service",
    description="Service for mouse and keyboard control operations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the input controller
controller = InputController()


# Request models
class MouseMoveRequest(BaseModel):
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    duration: float = Field(0.5, description="Duration of movement in seconds")


class MouseClickRequest(BaseModel):
    button: int = Field(1, description="Mouse button (1=left, 2=right, 3=middle)")
    x: Optional[int] = Field(None, description="X coordinate (optional)")
    y: Optional[int] = Field(None, description="Y coordinate (optional)")
    clicks: int = Field(1, description="Number of clicks")


class MouseScrollRequest(BaseModel):
    x: Optional[int] = Field(None, description="X coordinate (optional)")
    y: Optional[int] = Field(None, description="Y coordinate (optional)")
    scroll_x: int = Field(0, description="Horizontal scroll amount")
    scroll_y: int = Field(0, description="Vertical scroll amount")


class TypeRequest(BaseModel):
    text: str = Field(..., description="Text to type")
    interval: float = Field(0.05, description="Interval between keystrokes")


class KeypressRequest(BaseModel):
    keys: List[str] = Field(..., description="List of keys to press (e.g., ['ctrl', 'c'])")


# Endpoints
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "MCP Control",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "move_mouse": "POST /control/move_mouse",
            "click_mouse": "POST /control/click_mouse",
            "scroll": "POST /control/scroll",
            "type": "POST /control/type",
            "keypress": "POST /control/keypress"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-control"}


@app.post("/control/move_mouse")
async def move_mouse(request: MouseMoveRequest):
    """
    Move mouse to specified coordinates.
    
    Args:
        request: MouseMoveRequest with x, y coordinates and optional duration
        
    Returns:
        Result of the mouse move operation
    """
    try:
        result = controller.mouse_move(
            x=request.x,
            y=request.y,
            duration=request.duration
        )
        return {
            "success": True,
            "action": "move_mouse",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control/click_mouse")
async def click_mouse(request: MouseClickRequest):
    """
    Click mouse button at specified coordinates.
    
    Args:
        request: MouseClickRequest with button, coordinates, and click count
        
    Returns:
        Result of the mouse click operation
    """
    try:
        # Map button number to button name
        button_map = {1: "left", 2: "right", 3: "middle"}
        button_name = button_map.get(request.button, "left")
        
        result = controller.mouse_click(
            x=request.x,
            y=request.y,
            button=button_name,
            clicks=request.clicks
        )
        return {
            "success": True,
            "action": "click_mouse",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control/scroll")
async def scroll(request: MouseScrollRequest):
    """
    Scroll mouse wheel.
    
    Args:
        request: MouseScrollRequest with scroll amounts
        
    Returns:
        Result of the scroll operation
    """
    try:
        # Use scroll_y as the primary scroll amount (vertical scrolling)
        result = controller.mouse_scroll(clicks=request.scroll_y)
        return {
            "success": True,
            "action": "scroll",
            "data": result,
            "scroll_x": request.scroll_x,
            "scroll_y": request.scroll_y
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control/type")
async def type_text(request: TypeRequest):
    """
    Type text using keyboard.
    
    Args:
        request: TypeRequest with text to type and interval
        
    Returns:
        Result of the typing operation
    """
    try:
        result = controller.keyboard_type(
            text=request.text,
            interval=request.interval
        )
        return {
            "success": True,
            "action": "type",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control/keypress")
async def keypress(request: KeypressRequest):
    """
    Press key combination.
    
    Args:
        request: KeypressRequest with list of keys to press
        
    Returns:
        Result of the keypress operation
    """
    try:
        result = controller.keyboard_press(keys=request.keys)
        return {
            "success": True,
            "action": "keypress",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
