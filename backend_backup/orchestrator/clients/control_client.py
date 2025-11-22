"""
MCP Control Client - HTTP client for mouse and keyboard control operations
"""
import httpx
from typing import Dict, Any, List, Optional


class ControlClient:
    """Client for MCP Control Service"""
    
    def __init__(self, base_url: str = "http://localhost:8007"):
        """
        Initialize the Control MCP client.
        
        Args:
            base_url: Base URL of the MCP Control service
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30.0
    
    async def health(self) -> Dict[str, Any]:
        """
        Check health status of the control service.
        
        Returns:
            Health status information
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}",
                "status": "unhealthy"
            }
    
    async def move_mouse(
        self, 
        x: int, 
        y: int, 
        duration: float = 0.5
    ) -> Dict[str, Any]:
        """
        Move mouse to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of movement in seconds
            
        Returns:
            Result of the mouse move operation
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/control/move_mouse",
                    json={"x": x, "y": y, "duration": duration}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Move mouse failed: {str(e)}",
                "action": "move_mouse"
            }
    
    async def click_mouse(
        self,
        button: int = 1,
        x: Optional[int] = None,
        y: Optional[int] = None,
        clicks: int = 1
    ) -> Dict[str, Any]:
        """
        Click mouse button at specified coordinates.
        
        Args:
            button: Mouse button (1=left, 2=right, 3=middle)
            x: X coordinate (optional, clicks at current position if None)
            y: Y coordinate (optional, clicks at current position if None)
            clicks: Number of clicks
            
        Returns:
            Result of the mouse click operation
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"button": button, "clicks": clicks}
                if x is not None:
                    payload["x"] = x
                if y is not None:
                    payload["y"] = y
                    
                response = await client.post(
                    f"{self.base_url}/control/click_mouse",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Click mouse failed: {str(e)}",
                "action": "click_mouse"
            }
    
    async def scroll(
        self,
        scroll_x: int = 0,
        scroll_y: int = 0,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scroll mouse wheel.
        
        Args:
            scroll_x: Horizontal scroll amount
            scroll_y: Vertical scroll amount
            x: X coordinate (optional)
            y: Y coordinate (optional)
            
        Returns:
            Result of the scroll operation
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y,
                    "x": x,
                    "y": y
                }
                
                response = await client.post(
                    f"{self.base_url}/control/scroll",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Scroll failed: {str(e)}",
                "action": "scroll"
            }
    
    async def type(
        self,
        text: str,
        interval: float = 0.05
    ) -> Dict[str, Any]:
        """
        Type text using keyboard.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes in seconds
            
        Returns:
            Result of the typing operation
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/control/type",
                    json={"text": text, "interval": interval}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Type failed: {str(e)}",
                "action": "type"
            }
    
    async def keypress(
        self,
        keys: List[str]
    ) -> Dict[str, Any]:
        """
        Press key combination.
        
        Args:
            keys: List of keys to press (e.g., ['ctrl', 'c'])
            
        Returns:
            Result of the keypress operation
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/control/keypress",
                    json={"keys": keys}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Keypress failed: {str(e)}",
                "action": "keypress"
            }

