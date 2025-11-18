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
        
    def initialize(self):
        """Initialize the application components"""
        logger.info("Initializing Assistant Windows...")
        
        # Create floating window
        self.window = FloatingWindow()
        
        # Create hotkey manager
        self.hotkey_manager = HotkeyManager(self.window)
        
        # Connect signals
        self.window.stop_requested.connect(self.shutdown)
        
        # Register hotkeys
        self.hotkey_manager.register_all_hotkeys()
        
        logger.info("Assistant Windows initialized successfully")
        
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
        """Shutdown the application"""
        logger.info("Shutting down Assistant Windows...")
        
        if self.hotkey_manager:
            self.hotkey_manager.unregister_all_hotkeys()
            
        if self.window:
            self.window.close()
            
        self.app.quit()


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