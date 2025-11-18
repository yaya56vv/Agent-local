"""
Assistant Windows - Main Entry Point
Floating copilot window with F1/F8/F9/F10 hotkeys
"""
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from ui.floating_window import FloatingWindow
from services.hotkeys import HotkeyManager
from services.mouse_controller import MouseController
from services.screenshot import ScreenshotService
from services.api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AssistantApp:
    """Main application controller"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.window = None
        self.hotkey_manager = None
        self.mouse_controller = None
        self.screenshot_service = None
        self.api_client = None
        
    def initialize(self):
        """Initialize the application components"""
        logger.info("Initializing Assistant Windows...")
        
        # Create services
        self.screenshot_service = ScreenshotService()
        self.api_client = APIClient()
        
        # Create floating window
        self.window = FloatingWindow()
        
        # Create mouse controller
        self.mouse_controller = MouseController(
            self.screenshot_service,
            self.api_client
        )
        
        # Link mouse controller to window
        self.window.set_mouse_controller(self.mouse_controller)
        
        # Create hotkey manager
        self.hotkey_manager = HotkeyManager(self.window)
        
        # Connect signals
        self.window.stop_requested.connect(self.shutdown)
        self.window.exploration_requested.connect(self.start_exploration)
        
        # Register hotkeys
        self.hotkey_manager.register_all_hotkeys()
        
        logger.info("Assistant Windows initialized successfully")
    
    def start_exploration(self, goal: str):
        """Start exploration mode with given goal"""
        logger.info(f"Starting exploration with goal: {goal}")
        if self.mouse_controller:
            self.mouse_controller.start_exploration(goal)
        
    def run(self):
        """Run the application"""
        try:
            self.initialize()
            logger.info("Assistant Windows is running. Press F1 to show window.")
            return self.app.exec()
        except Exception as e:
            logger.error(f"Error running application: {e}", exc_info=True)
            return 1
            
    def shutdown(self):
        """Shutdown the application - KILL SWITCH"""
        logger.info("🛑 SHUTTING DOWN Assistant Windows (KILL SWITCH)...")
        
        # Stop exploration if active
        if self.mouse_controller:
            self.mouse_controller.stop_exploration("Arrêt complet")
            self.mouse_controller.cleanup()
            
        # Stop auto capture if active
        if self.hotkey_manager:
            self.hotkey_manager.auto_capture_active = False
            self.hotkey_manager.capture_timer.stop()
            self.hotkey_manager.unregister_all_hotkeys()
            
        # Close window
        if self.window:
            self.window.close()
        
        # Cleanup services
        if self.screenshot_service:
            self.screenshot_service.cleanup()
            
        if self.api_client:
            self.api_client.close()
            
        # Quit application
        self.app.quit()
        
        logger.info("Assistant Windows shut down completely")


def main():
    """Main entry point"""
    try:
        app = AssistantApp()
        sys.exit(app.run())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()