"""
API Client - Communication with FastAPI backend
Sends screenshots to /vision/screenshot endpoint
"""
import logging
import requests
from typing import Optional, Dict
import io

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 7  # seconds
        self.session = requests.Session()
        logger.info(f"API Client initialized with base URL: {self.base_url}")
        
    def send_screenshot(self, screenshot_bytes: bytes) -> Optional[Dict]:
        """
        Send screenshot to backend for vision analysis
        
        Args:
            screenshot_bytes: PNG image data as bytes
            
        Returns:
            dict: Vision analysis result, or None if failed
        """
        try:
            endpoint = f"{self.base_url}/vision/screenshot"
            
            # Prepare multipart file upload
            files = {
                'file': ('screenshot.png', io.BytesIO(screenshot_bytes), 'image/png')
            }
            
            logger.debug(f"Sending screenshot to {endpoint}")
            
            # Send POST request
            response = self.session.post(
                endpoint,
                files=files,
                timeout=self.timeout
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                logger.info("Screenshot analysis successful")
                # Extract the analysis from the wrapped response
                if "analysis" in result:
                    return result["analysis"]
                return result
            else:
                logger.error(f"Backend returned status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - is the backend running?")
            return None
        except Exception as e:
            logger.error(f"Error sending screenshot: {e}", exc_info=True)
            return None
            
    def get_next_gui_action(self, image_bytes: bytes, goal: str, history: list = None) -> Optional[Dict]:
        """
        Get next GUI action from backend based on screenshot and goal
        
        Args:
            image_bytes: Screenshot PNG bytes
            goal: User's objective
            history: Recent action history (optional)
            
        Returns:
            dict: Action to execute, or None if failed
        """
        try:
            endpoint = f"{self.base_url}/orchestrate"
            
            # Prepare multipart request
            files = {
                'file': ('screenshot.png', io.BytesIO(image_bytes), 'image/png')
            }
            
            data = {
                'goal': goal,
                'mode': 'gui_control',
                'history': str(history) if history else '[]'
            }
            
            logger.debug(f"Requesting next GUI action for goal: {goal}")
            
            response = self.session.post(
                endpoint,
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Next GUI action received")
                
                # Extract action from response
                if "action" in result:
                    return result["action"]
                elif "next_action" in result:
                    return result["next_action"]
                    
                # Fallback: try to parse as direct action
                if "action_type" in result:
                    return result
                    
                logger.warning("No action found in response")
                return None
            else:
                logger.error(f"Backend returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting next GUI action: {e}", exc_info=True)
            return None
    
    def check_health(self) -> bool:
        """
        Check if backend is available
        
        Returns:
            bool: True if backend is healthy, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/health"
            response = self.session.get(endpoint, timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False
            
    def close(self):
        """Close the session"""
        try:
            self.session.close()
            logger.info("API client session closed")
        except Exception as e:
            logger.error(f"Error closing API client: {e}")
            
    def __del__(self):
        """Destructor"""
        self.close()