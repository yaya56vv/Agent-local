"""
Floating Window UI - PySide6 implementation
Always-on-top copilot window with dark theme
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QHBoxLayout, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtGui import QFont, QPalette, QColor
import logging

logger = logging.getLogger(__name__)


class FloatingWindow(QWidget):
    """Floating copilot window - always on top, dark theme"""
    
    # Signals
    stop_requested = Signal()
    exploration_requested = Signal(str)  # goal
    voice_response_ready = Signal(str)  # response text to speak
    
    # State constants
    STATE_READY = "🟠 Prêt"
    STATE_VISION_ACTIVE = "🟢 Vision Active"
    STATE_VISION_STOPPED = "🟡 Vision Arrêtée"
    STATE_EXPLORATION = "🔵 Exploration Active"
    STATE_VOICE_LISTENING = "🎙 En écoute..."
    STATE_OFFLINE = "🔴 Hors Ligne"
    
    def __init__(self):
        super().__init__()
        self.current_state = self.STATE_READY
        self.mouse_controller = None
        self.voice_service = None
        self.api_client = None
        
        # Mini-bubble mode
        self.is_mini_mode = False
        self.full_size = (320, 500)
        self.mini_size = (80, 80)
        
        # Store widgets for show/hide
        self.full_mode_widgets = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("Assistant Copilot")
        self.setGeometry(100, 100, 320, 500)
        
        # Always on top
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Enable mouse tracking for dragging
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMouseTracking(True)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title bar (custom)
        title_layout = QHBoxLayout()
        title_label = QLabel("🤖 Assistant Copilot")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #00D9FF;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        layout.addLayout(title_layout)
        
        # State indicator
        self.state_label = QLabel(self.current_state)
        self.state_label.setFont(QFont("Segoe UI", 9))
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("""
            QLabel {
                background-color: #2A2A2A;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.state_label)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.output_text.setPlaceholderText("Appuyez sur F8 pour démarrer la vision...")
        layout.addWidget(self.output_text, stretch=1)
        
        # Input field (optional for this mission)
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Segoe UI", 9))
        self.input_field.setPlaceholderText("Saisie manuelle (optionnel)...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.input_field)
        self.full_mode_widgets.append(self.input_field)
        
        # Mini-bubble toggle button
        self.mini_button = QPushButton("⬇ Réduire en bulle")
        self.mini_button.setFont(QFont("Segoe UI", 8))
        self.mini_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.mini_button.clicked.connect(self.toggle_mini_mode)
        layout.addWidget(self.mini_button)
        self.full_mode_widgets.append(self.mini_button)
        
        # Exploration button
        self.exploration_button = QPushButton("🚀 Lancer Exploration")
        self.exploration_button.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.exploration_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.exploration_button.clicked.connect(self.on_exploration_clicked)
        layout.addWidget(self.exploration_button)
        self.full_mode_widgets.append(self.exploration_button)
        
        # Stop button
        self.stop_button = QPushButton("⏹ STOP (Fermer)")
        self.stop_button.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #F44336;
            }
        """)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        layout.addWidget(self.stop_button)
        self.full_mode_widgets.append(self.stop_button)
        
        # Add output and state to full mode widgets
        self.full_mode_widgets.extend([self.output_text, self.state_label])
        
        self.setLayout(layout)
        
        # For window dragging
        self.drag_position = None
        
        logger.info("Floating window UI initialized")
        
    def apply_dark_theme(self):
        """Apply dark theme to the window"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
            }
        """)
        
        # Set window opacity and rounded corners effect
        self.setWindowOpacity(0.95)
        
    def set_state(self, state: str):
        """Update the state indicator"""
        self.current_state = state
        self.state_label.setText(state)
        logger.info(f"State changed to: {state}")
        
    def append_output(self, text: str):
        """Append text to the output area"""
        self.output_text.append(text)
        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)
        
    def clear_output(self):
        """Clear the output area"""
        self.output_text.clear()
        
    def display_vision_result(self, result: dict):
        """Display vision analysis result"""
        self.append_output("\n" + "="*40)
        self.append_output("📸 Analyse Vision")
        self.append_output("="*40 + "\n")
        
        # Description
        if "description" in result and result["description"]:
            self.append_output(f"📝 Description:\n{result['description']}\n")
        
        # Objects detected
        if "objects" in result and result["objects"]:
            self.append_output("🔍 Objets détectés:")
            for obj in result["objects"]:
                self.append_output(f"  • {obj}")
            self.append_output("")
            
        # Detected text
        if "detected_text" in result and result["detected_text"]:
            self.append_output(f"📄 Texte détecté:\n{result['detected_text']}\n")
        
        # Reasoning
        if "reasoning" in result and result["reasoning"]:
            self.append_output(f"🧠 Analyse:\n{result['reasoning']}\n")
            
        # Suggested actions
        if "suggested_actions" in result and result["suggested_actions"]:
            self.append_output("💡 Actions suggérées:")
            for action in result["suggested_actions"]:
                self.append_output(f"  • {action}")
            self.append_output("")
    
    def set_voice_service(self, voice_service):
        """Set the voice service reference"""
        self.voice_service = voice_service
        
        # Connect signals
        if voice_service:
            voice_service.listening_started.connect(self.on_voice_listening_started)
            voice_service.listening_stopped.connect(self.on_voice_listening_stopped)
            voice_service.transcription_ready.connect(self.on_voice_transcription)
            voice_service.speaking_started.connect(self.on_voice_speaking_started)
            voice_service.speaking_stopped.connect(self.on_voice_speaking_stopped)
            voice_service.error_occurred.connect(self.on_voice_error)
    
    def set_api_client(self, api_client):
        """Set the API client reference"""
        self.api_client = api_client
    
    def set_mouse_controller(self, controller):
        """Set the mouse controller reference"""
        self.mouse_controller = controller
        
        # Connect signals
        if controller:
            controller.log_message.connect(self.append_output)
            controller.exploration_started.connect(self.on_exploration_started)
            controller.exploration_stopped.connect(self.on_exploration_stopped)
            
    def on_exploration_clicked(self):
        """Handle exploration button click"""
        if not self.mouse_controller:
            self.append_output("❌ MouseController non initialisé")
            return
            
        if self.mouse_controller.is_running():
            # Stop exploration
            self.mouse_controller.stop_exploration("Arrêt manuel")
        else:
            # Ask for goal
            goal, ok = QInputDialog.getText(
                self,
                "Objectif d'exploration",
                "Quel est votre objectif ?\n(ex: 'ouvrir les paramètres réseau')",
                QLineEdit.EchoMode.Normal,
                ""
            )
            
            if ok and goal.strip():
                self.exploration_requested.emit(goal.strip())
            else:
                self.append_output("⚠️ Objectif requis pour l'exploration")
                
    @Slot()
    def on_exploration_started(self):
        """Handle exploration started"""
        self.set_state(self.STATE_EXPLORATION)
        self.exploration_button.setText("⏸ Arrêter Exploration")
        self.exploration_button.setStyleSheet("""
            QPushButton {
                background-color: #F57C00;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #FF9800;
            }
        """)
        
    @Slot(str)
    def on_exploration_stopped(self, reason: str):
        """Handle exploration stopped"""
        self.set_state(self.STATE_READY)
        self.exploration_button.setText("🚀 Lancer Exploration")
        self.exploration_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
        """)
    
    @Slot()
    def on_voice_listening_started(self):
        """Handle voice listening started"""
        self.set_state(self.STATE_VOICE_LISTENING)
        self.append_output("\n🎙 Écoute vocale activée... Parlez maintenant.")
        
    @Slot()
    def on_voice_listening_stopped(self):
        """Handle voice listening stopped"""
        if self.current_state == self.STATE_VOICE_LISTENING:
            self.set_state(self.STATE_READY)
            
    @Slot(str)
    def on_voice_transcription(self, text: str):
        """Handle voice transcription ready"""
        self.append_output(f"\n💬 Tu as dit : \"{text}\"")
        self.append_output("📤 Envoi au backend...")
        
        # Send to orchestrator
        if self.api_client:
            response = self.api_client.send_voice_prompt(text)
            if response:
                # Extract response text
                response_text = self._extract_response_text(response)
                self.append_output(f"\n🤖 Réponse : {response_text}")
                
                # Emit signal to speak response
                self.voice_response_ready.emit(response_text)
            else:
                self.append_output("❌ Erreur de communication avec le backend")
        else:
            self.append_output("❌ API client non disponible")
            
    def _extract_response_text(self, response: dict) -> str:
        """Extract readable text from orchestrator response"""
        # Try different response formats
        if isinstance(response, str):
            return response
        if "response" in response:
            return str(response["response"])
        if "result" in response:
            return str(response["result"])
        if "message" in response:
            return str(response["message"])
        # Fallback
        return str(response)
        
    @Slot(str)
    def on_voice_speaking_started(self, text: str):
        """Handle TTS started"""
        self.append_output(f"🔊 Lecture vocale en cours...")
        
    @Slot()
    def on_voice_speaking_stopped(self):
        """Handle TTS stopped"""
        pass
        
    @Slot(str)
    def on_voice_error(self, error: str):
        """Handle voice error"""
        self.append_output(f"❌ Erreur vocale : {error}")
    
    def toggle_mini_mode(self):
        """Toggle between full and mini-bubble mode"""
        if self.is_mini_mode:
            self._switch_to_full_mode()
        else:
            self._switch_to_mini_mode()
            
    def _switch_to_mini_mode(self):
        """Switch to mini-bubble mode"""
        self.is_mini_mode = True
        
        # Hide all full mode widgets
        for widget in self.full_mode_widgets:
            widget.hide()
            
        # Resize to mini
        self.setFixedSize(*self.mini_size)
        
        # Update styling for bubble
        self.setStyleSheet("""
            QWidget {
                background-color: """ + self._get_bubble_color() + """;
                border-radius: 40px;
            }
        """)
        
        logger.info("Switched to mini-bubble mode")
        
    def _switch_to_full_mode(self):
        """Switch to full window mode"""
        self.is_mini_mode = False
        
        # Show all full mode widgets
        for widget in self.full_mode_widgets:
            widget.show()
            
        # Resize to full
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.resize(*self.full_size)
        
        # Restore normal styling
        self.apply_dark_theme()
        
        logger.info("Switched to full window mode")
        
    def _get_bubble_color(self) -> str:
        """Get bubble color based on current state"""
        if self.current_state == self.STATE_READY:
            return "#FF9800"  # Orange
        elif self.current_state == self.STATE_VISION_ACTIVE:
            return "#4CAF50"  # Green
        elif self.current_state == self.STATE_EXPLORATION:
            return "#2196F3"  # Blue
        elif self.current_state == self.STATE_VOICE_LISTENING:
            return "#9C27B0"  # Purple
        elif self.current_state == self.STATE_OFFLINE:
            return "#F44336"  # Red
        else:
            return "#FFC107"  # Amber
            
    def on_stop_clicked(self):
        """Handle stop button click - KILL SWITCH"""
        logger.info("STOP button clicked - shutting down completely")
        self.append_output("\n🛑 ARRÊT COMPLET DE L'ASSISTANT...")
        self.stop_requested.emit()
        
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging or bubble click"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_mini_mode:
                # Click on bubble = switch to full mode
                self._switch_to_full_mode()
            else:
                # Normal dragging
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.drag_position = None
        
    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        logger.info("Window shown")
        
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Window closing")
        self.stop_requested.emit()
        super().closeEvent(event)
