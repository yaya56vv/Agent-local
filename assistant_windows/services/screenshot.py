"""
Screenshot Service - Screen capture with dxcam (fast) or mss (fallback)
"""
import logging
import io
from PIL import Image

logger = logging.getLogger(__name__)


class ScreenshotService:
    """Handles screen capture with dxcam or mss fallback"""
    
    def __init__(self):
        self.capture_method = None
        self.camera = None
        self.sct = None
        self._initialize_capture()
        
    def _initialize_capture(self):
        """Initialize the best available capture method"""
        # Try dxcam first (fastest for Windows)
        try:
            import dxcam
            self.camera = dxcam.create()
            if self.camera:
                self.capture_method = "dxcam"
                logger.info("Using dxcam for screen capture (fast)")
                return
        except ImportError:
            logger.warning("dxcam not available, trying mss")
        except Exception as e:
            logger.warning(f"dxcam initialization failed: {e}, trying mss")
            
        # Fallback to mss
        try:
            import mss
            self.sct = mss.mss()
            self.capture_method = "mss"
            logger.info("Using mss for screen capture (fallback)")
            return
        except ImportError:
            logger.error("Neither dxcam nor mss available!")
            raise RuntimeError("No screen capture library available. Install dxcam or mss.")
        except Exception as e:
            logger.error(f"mss initialization failed: {e}")
            raise
            
    def capture_screen(self) -> bytes:
        """
        Capture the screen and return PNG bytes
        
        Returns:
            bytes: PNG image data, or None if capture failed
        """
        try:
            if self.capture_method == "dxcam":
                return self._capture_with_dxcam()
            elif self.capture_method == "mss":
                return self._capture_with_mss()
            else:
                logger.error("No capture method initialized")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing screen: {e}", exc_info=True)
            return None
            
    def _capture_with_dxcam(self) -> bytes:
        """Capture screen using dxcam"""
        try:
            # Grab the screen
            frame = self.camera.grab()
            
            if frame is None:
                logger.error("dxcam returned None")
                return None
                
            # Convert numpy array to PIL Image
            image = Image.fromarray(frame)
            
            # Convert to PNG bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"dxcam capture error: {e}", exc_info=True)
            return None
            
    def _capture_with_mss(self) -> bytes:
        """Capture screen using mss"""
        try:
            # Grab the primary monitor
            monitor = self.sct.monitors[1]  # 0 is all monitors, 1 is primary
            screenshot = self.sct.grab(monitor)
            
            # Convert to PIL Image
            image = Image.frombytes(
                'RGB',
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )
            
            # Convert to PNG bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"mss capture error: {e}", exc_info=True)
            return None
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.camera:
                # dxcam cleanup if needed
                pass
            if self.sct:
                self.sct.close()
            logger.info("Screenshot service cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up screenshot service: {e}")
            
    def __del__(self):
        """Destructor"""
        self.cleanup()