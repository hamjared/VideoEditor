"""
Splash Screen
Displays a loading screen during application startup.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class SplashScreen(QWidget):
    """Custom splash screen with progress bar."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the splash screen UI."""
        # Window settings
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(400, 200)

        # Dark theme styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #3b3b3b;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 3px;
            }
        """)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Video Editor")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add some spacing
        layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Status message
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.setLayout(layout)

        # Center on screen
        self.center_on_screen()

    def center_on_screen(self):
        """Center the splash screen on the display."""
        from PyQt5.QtWidgets import QDesktopWidget
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def set_progress(self, value, message=None):
        """
        Update progress bar and optional status message.

        Args:
            value: Progress value (0-100)
            message: Optional status message to display
        """
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
            logger.debug(f"Splash screen: {value}% - {message}")

        # Process events to update UI
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
