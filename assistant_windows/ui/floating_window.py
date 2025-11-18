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
    
    # State constants
    STATE_READY = "🟠 Prêt"
    STATE_VISION_ACTIVE = "🟢 Vision Active"
    STATE_VISION_STOPPED = "🟡 Vision Arrêtée"
    STATE_EXPLORATION = "🔵 Exploration Active"
    STATE_OFFLINE = "🔴 Hors Ligne"
    
    def __init__(self):
        super().__init__()
        self.current_state = self.STATE_READY
        self.mouse_controller = None
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
            
    def on_stop_clicked(self):
        """Handle stop button click - KILL SWITCH"""
        logger.info("STOP button clicked - shutting down completely")
        self.append_output("\n🛑 ARRÊT COMPLET DE L'ASSISTANT...")
        self.stop_requested.emit()
        
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
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