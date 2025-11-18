"""
Hotkeys Service - Global hotkey management
F1 = Show window (no capture)
F8 = Show window + start auto capture
F9 = Stop auto capture
F10 = Single screenshot
"""
import logging
import keyboard
from PySide6.QtCore import QObject, QTimer, Signal
from .screenshot import ScreenshotService
from .api_client import APIClient

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """Manages global hotkeys and capture logic"""
    
    # Signals
    capture_started = Signal()
    capture_stopped = Signal()
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.screenshot_service = ScreenshotService()
        self.api_client = APIClient()
        
        # Auto-capture state
        self.auto_capture_active = False
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._do_auto_capture)
        self.capture_interval = 2000  # 2 seconds
        
        # Track if we're currently processing a capture
        self.is_processing = False
        
        logger.info("HotkeyManager initialized")
        
    def register_all_hotkeys(self):
        """Register all global hotkeys"""
        try:
            # F1 - Show window (no capture)
            keyboard.add_hotkey('f1', self._on_f1_pressed, suppress=True)
            logger.info("Registered F1 hotkey")
            
            # F8 - Show window + start auto capture
            keyboard.add_hotkey('f8', self._on_f8_pressed, suppress=True)
            logger.info("Registered F8 hotkey")
            
            # F9 - Stop auto capture
            keyboard.add_hotkey('f9', self._on_f9_pressed, suppress=True)
            logger.info("Registered F9 hotkey")
            
            # F10 - Single screenshot
            keyboard.add_hotkey('f10', self._on_f10_pressed, suppress=True)
            logger.info("Registered F10 hotkey")
            
            logger.info("All hotkeys registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering hotkeys: {e}", exc_info=True)
            
    def unregister_all_hotkeys(self):
        """Unregister all global hotkeys"""
        try:
            keyboard.unhook_all_hotkeys()
            logger.info("All hotkeys unregistered")
        except Exception as e:
            logger.error(f"Error unregistering hotkeys: {e}", exc_info=True)
            
    def _on_f1_pressed(self):
        """F1 - Show window without capture"""
        logger.info("F1 pressed - showing window")
        try:
            if not self.window.isVisible():
                self.window.show()
                self.window.activateWindow()
                self.window.raise_()
                self.window.set_state(self.window.STATE_READY)
                self.window.append_output("🟠 Fenêtre activée (F1)")
            else:
                self.window.activateWindow()
                self.window.raise_()
        except Exception as e:
            logger.error(f"Error handling F1: {e}", exc_info=True)
            
    def _on_f8_pressed(self):
        """F8 - Show window + start auto capture"""
        logger.info("F8 pressed - starting auto capture")
        try:
            # Show window if hidden
            if not self.window.isVisible():
                self.window.show()
                self.window.activateWindow()
                self.window.raise_()
                
            # Start auto capture
            if not self.auto_capture_active:
                self.auto_capture_active = True
                self.window.set_state(self.window.STATE_VISION_ACTIVE)
                self.window.append_output("🟢 Capture automatique démarrée (F8)")
                self.capture_timer.start(self.capture_interval)
                self.capture_started.emit()
            else:
                self.window.append_output("⚠️ Capture automatique déjà active")
                
        except Exception as e:
            logger.error(f"Error handling F8: {e}", exc_info=True)
            
    def _on_f9_pressed(self):
        """F9 - Stop auto capture (window stays open)"""
        logger.info("F9 pressed - stopping auto capture")
        try:
            if self.auto_capture_active:
                self.auto_capture_active = False
                self.capture_timer.stop()
                self.window.set_state(self.window.STATE_VISION_STOPPED)
                self.window.append_output("🟡 Capture automatique arrêtée (F9)")
                self.capture_stopped.emit()
            else:
                self.window.append_output("⚠️ Capture automatique non active")
                
        except Exception as e:
            logger.error(f"Error handling F9: {e}", exc_info=True)
            
    def _on_f10_pressed(self):
        """F10 - Single screenshot"""
        logger.info("F10 pressed - single screenshot")
        try:
            # Show window if hidden
            if not self.window.isVisible():
                self.window.show()
                self.window.activateWindow()
                self.window.raise_()
                
            self.window.append_output("📸 Capture unique en cours... (F10)")
            self._capture_and_analyze()
            
        except Exception as e:
            logger.error(f"Error handling F10: {e}", exc_info=True)
            
    def _do_auto_capture(self):
        """Perform automatic capture (called by timer)"""
        if not self.auto_capture_active:
            return
            
        if self.is_processing:
            logger.debug("Skipping capture - previous one still processing")
            return
            
        logger.debug("Auto capture triggered")
        self._capture_and_analyze()
        
    def _capture_and_analyze(self):
        """Capture screen and send to backend for analysis"""
        if self.is_processing:
            logger.warning("Already processing a capture, skipping")
            return
            
        self.is_processing = True
        
        try:
            # Capture screenshot
            logger.debug("Capturing screenshot...")
            screenshot_bytes = self.screenshot_service.capture_screen()
            
            if not screenshot_bytes:
                logger.error("Failed to capture screenshot")
                self.window.append_output("❌ Erreur de capture d'écran")
                self.is_processing = False
                return
                
            logger.debug(f"Screenshot captured: {len(screenshot_bytes)} bytes")
            
            # Send to backend
            logger.debug("Sending to backend...")
            result = self.api_client.send_screenshot(screenshot_bytes)
            
            if result:
                logger.info("Vision analysis received")
                self.window.display_vision_result(result)
            else:
                logger.error("Failed to get vision analysis")
                self.window.append_output("❌ Erreur d'analyse (backend)")
                self.window.set_state(self.window.STATE_OFFLINE)
                
        except Exception as e:
            logger.error(f"Error in capture and analyze: {e}", exc_info=True)
            self.window.append_output(f"❌ Erreur: {str(e)}")
            
        finally:
            self.is_processing = False
            
    def set_capture_interval(self, interval_ms: int):
        """Set the auto-capture interval in milliseconds"""
        self.capture_interval = interval_ms
        if self.auto_capture_active:
            self.capture_timer.setInterval(interval_ms)
        logger.info(f"Capture interval set to {interval_ms}ms")