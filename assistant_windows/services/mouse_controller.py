"""
Mouse Controller - Complete mouse/keyboard control with exploration mode
Supports user interruption detection and automated GUI actions
"""
import logging
import time
import threading
from typing import Optional, Dict, Callable
import pyautogui
from pynput import mouse
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


class MouseController(QObject):
    """
    Controls mouse and keyboard with exploration mode.
    Detects user interruption via mouse movement.
    """
    
    # Signals for thread-safe UI updates
    log_message = Signal(str)
    exploration_started = Signal()
    exploration_stopped = Signal(str)  # reason
    action_executed = Signal(dict)
    
    def __init__(self, screenshot_service, api_client):
        super().__init__()
        self.screenshot_service = screenshot_service
        self.api_client = api_client
        
        # Exploration state
        self.exploration_active = False
        self.exploration_thread = None
        self.goal = ""
        
        # User interruption detection
        self.user_moved_mouse = False
        self.last_agent_mouse_pos = None
        self.mouse_listener = None
        self.interruption_enabled = False
        
        # Action history (for context)
        self.action_history = []
        
        logger.info("MouseController initialized")
        
    def start_exploration(self, goal: str):
        """
        Start automated exploration mode
        
        Args:
            goal: User's objective (e.g., "open network settings")
        """
        if self.exploration_active:
            logger.warning("Exploration already active")
            return
            
        self.goal = goal
        self.exploration_active = True
        self.user_moved_mouse = False
        self.action_history = []
        
        # Start mouse listener for interruption detection
        self._start_mouse_listener()
        
        # Start exploration in separate thread
        self.exploration_thread = threading.Thread(
            target=self._exploration_loop,
            daemon=True
        )
        self.exploration_thread.start()
        
        self.exploration_started.emit()
        self.log_message.emit(f"🚀 Exploration démarrée : {goal}")
        logger.info(f"Exploration started with goal: {goal}")
        
    def stop_exploration(self, reason: str = "Arrêt manuel"):
        """
        Stop exploration mode
        
        Args:
            reason: Reason for stopping
        """
        if not self.exploration_active:
            return
            
        self.exploration_active = False
        
        # Stop mouse listener
        self._stop_mouse_listener()
        
        # Wait for thread to finish
        if self.exploration_thread and self.exploration_thread.is_alive():
            self.exploration_thread.join(timeout=2.0)
            
        self.exploration_stopped.emit(reason)
        self.log_message.emit(f"⏹ Exploration arrêtée : {reason}")
        logger.info(f"Exploration stopped: {reason}")
        
    def is_running(self) -> bool:
        """Check if exploration is active"""
        return self.exploration_active
        
    def _start_mouse_listener(self):
        """Start listening for user mouse movements"""
        self.interruption_enabled = True
        self.user_moved_mouse = False
        
        # Get current mouse position (agent's starting point)
        self.last_agent_mouse_pos = pyautogui.position()
        
        def on_move(x, y):
            if not self.interruption_enabled:
                return
                
            # Check if this is a user movement (not agent)
            if self.last_agent_mouse_pos:
                # Allow small tolerance for system jitter
                dx = abs(x - self.last_agent_mouse_pos[0])
                dy = abs(y - self.last_agent_mouse_pos[1])
                
                if dx > 5 or dy > 5:  # Significant movement
                    if self.exploration_active:
                        logger.info(f"User mouse movement detected: ({x}, {y})")
                        self.user_moved_mouse = True
                        self.stop_exploration("Tu as repris la main (mouvement souris)")
                        
        def on_click(x, y, button, pressed):
            if not self.interruption_enabled:
                return
                
            if pressed and self.exploration_active:
                logger.info(f"User click detected: {button} at ({x}, {y})")
                self.user_moved_mouse = True
                self.stop_exploration("Tu as repris la main (clic souris)")
                
        def on_scroll(x, y, dx, dy):
            if not self.interruption_enabled:
                return
                
            if self.exploration_active:
                logger.info(f"User scroll detected at ({x}, {y})")
                self.user_moved_mouse = True
                self.stop_exploration("Tu as repris la main (scroll)")
        
        try:
            self.mouse_listener = mouse.Listener(
                on_move=on_move,
                on_click=on_click,
                on_scroll=on_scroll
            )
            self.mouse_listener.start()
            logger.info("Mouse listener started")
        except Exception as e:
            logger.error(f"Failed to start mouse listener: {e}")
            
    def _stop_mouse_listener(self):
        """Stop listening for user mouse movements"""
        self.interruption_enabled = False
        
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
                self.mouse_listener = None
                logger.info("Mouse listener stopped")
            except Exception as e:
                logger.error(f"Error stopping mouse listener: {e}")
                
    def _exploration_loop(self):
        """Main exploration loop (runs in separate thread)"""
        try:
            self.log_message.emit(f"[Agent] Objectif : {self.goal}")
            iteration = 0
            max_iterations = 50  # Safety limit
            
            while self.exploration_active and iteration < max_iterations:
                iteration += 1
                
                # Check if user interrupted
                if self.user_moved_mouse:
                    break
                    
                self.log_message.emit(f"\n[Agent] Itération {iteration} - Analyse de l'écran...")
                
                # 1. Capture screen
                image_bytes = self.screenshot_service.capture_screen()
                if not image_bytes:
                    self.log_message.emit("[Agent] ❌ Erreur de capture d'écran")
                    break
                    
                # 2. Get next action from backend
                action = self.api_client.get_next_gui_action(
                    image_bytes=image_bytes,
                    goal=self.goal,
                    history=self.action_history[-5:]  # Last 5 actions
                )
                
                if not action:
                    self.log_message.emit("[Agent] ❌ Pas de réponse du backend")
                    break
                    
                # 3. Check if exploration should end
                if action.get("action_type") == "noop" or action.get("action_type") == "done":
                    self.log_message.emit("[Agent] ✅ Objectif atteint ou aucune action nécessaire")
                    break
                    
                # 4. Log what agent is doing
                comment = action.get("comment", "Action en cours...")
                self.log_message.emit(f"[Agent] {comment}")
                
                # 5. Execute action (if user hasn't interrupted)
                if not self.exploration_active or self.user_moved_mouse:
                    break
                    
                success = self.execute_action(action)
                
                if not success:
                    self.log_message.emit("[Agent] ⚠️ Échec de l'action")
                    
                # 6. Add to history
                self.action_history.append({
                    "action": action.get("action_type"),
                    "comment": comment,
                    "success": success
                })
                
                # 7. Small delay before next iteration
                time.sleep(0.5)
                
            # End of loop
            if iteration >= max_iterations:
                self.log_message.emit("[Agent] ⚠️ Limite d'itérations atteinte")
                
            self.stop_exploration("Exploration terminée")
            
        except Exception as e:
            logger.error(f"Error in exploration loop: {e}", exc_info=True)
            self.log_message.emit(f"[Agent] ❌ Erreur : {str(e)}")
            self.stop_exploration("Erreur")
            
    def execute_action(self, action: Dict) -> bool:
        """
        Execute a GUI action
        
        Args:
            action: Action dictionary with type and parameters
            
        Returns:
            bool: True if successful
        """
        try:
            action_type = action.get("action_type")
            
            # Disable interruption detection during agent action
            self.interruption_enabled = False
            
            if action_type == "mouse_move":
                x = action.get("x")
                y = action.get("y")
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=0.3)
                    self.last_agent_mouse_pos = (x, y)
                    logger.info(f"Mouse moved to ({x}, {y})")
                    
            elif action_type == "mouse_move_click":
                x = action.get("x")
                y = action.get("y")
                button = action.get("button", "left")
                clicks = action.get("clicks", 1)
                
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=0.3)
                    time.sleep(0.1)
                    pyautogui.click(x, y, clicks=clicks, button=button)
                    self.last_agent_mouse_pos = (x, y)
                    logger.info(f"Clicked {button} at ({x}, {y})")
                    
            elif action_type == "click":
                button = action.get("button", "left")
                clicks = action.get("clicks", 1)
                pyautogui.click(clicks=clicks, button=button)
                logger.info(f"Clicked {button}")
                
            elif action_type == "double_click":
                x = action.get("x")
                y = action.get("y")
                if x is not None and y is not None:
                    pyautogui.doubleClick(x, y)
                    self.last_agent_mouse_pos = (x, y)
                else:
                    pyautogui.doubleClick()
                logger.info("Double clicked")
                
            elif action_type == "right_click":
                x = action.get("x")
                y = action.get("y")
                if x is not None and y is not None:
                    pyautogui.rightClick(x, y)
                    self.last_agent_mouse_pos = (x, y)
                else:
                    pyautogui.rightClick()
                logger.info("Right clicked")
                
            elif action_type == "scroll":
                scroll_delta = action.get("scroll_delta", 0)
                x = action.get("x")
                y = action.get("y")
                
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=0.2)
                    
                pyautogui.scroll(scroll_delta * 100)  # Multiply for more noticeable scroll
                logger.info(f"Scrolled {scroll_delta}")
                
            elif action_type == "type_text":
                text = action.get("text", "")
                if text:
                    pyautogui.write(text, interval=0.05)
                    logger.info(f"Typed text: {text[:50]}...")
                    
            elif action_type == "press_key":
                key = action.get("key", "")
                if key:
                    pyautogui.press(key)
                    logger.info(f"Pressed key: {key}")
                    
            elif action_type == "hotkey":
                keys = action.get("keys", [])
                if keys:
                    pyautogui.hotkey(*keys)
                    logger.info(f"Pressed hotkey: {'+'.join(keys)}")
                    
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
            # Re-enable interruption detection
            time.sleep(0.1)
            self.interruption_enabled = True
            
            # Update last agent position
            self.last_agent_mouse_pos = pyautogui.position()
            
            self.action_executed.emit(action)
            return True
            
        except Exception as e:
            logger.error(f"Error executing action {action.get('action_type')}: {e}", exc_info=True)
            self.interruption_enabled = True
            return False
            
    def cleanup(self):
        """Cleanup resources"""
        self.stop_exploration("Cleanup")
        self._stop_mouse_listener()
        logger.info("MouseController cleaned up")
