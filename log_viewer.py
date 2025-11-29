"""
Log Viewer Dialog
Displays application logs in a GUI window with auto-refresh capability.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QCheckBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import os
from logging_config import get_log_file_path


class LogViewerDialog(QDialog):
    """Dialog to view application logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_file_path = get_log_file_path()
        self.init_ui()

        # Load initial content
        self.refresh_logs()

        # Set up auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_logs)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Application Logs')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Header with log file path
        header_layout = QHBoxLayout()
        header_label = QLabel(f"Log File: {self.log_file_path}")
        header_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Log text display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)

        # Use monospace font for better log readability
        font = QFont("Courier New", 9)
        self.log_text.setFont(font)

        layout.addWidget(self.log_text)

        # Bottom controls
        controls_layout = QHBoxLayout()

        # Auto-refresh checkbox
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh")
        self.auto_refresh_checkbox.setChecked(False)
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_checkbox)

        controls_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(refresh_btn)

        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)

        # Open in editor button
        open_btn = QPushButton("Open in Editor")
        open_btn.clicked.connect(self.open_in_editor)
        controls_layout.addWidget(open_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)

        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def refresh_logs(self):
        """Reload and display the log file content."""
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Save current scroll position
                scrollbar = self.log_text.verticalScrollBar()
                was_at_bottom = scrollbar.value() == scrollbar.maximum()

                # Update content
                self.log_text.setPlainText(content)

                # If we were at the bottom, stay at the bottom
                # (useful for auto-refresh to see new logs)
                if was_at_bottom:
                    scrollbar.setValue(scrollbar.maximum())
            else:
                self.log_text.setPlainText(f"Log file not found: {self.log_file_path}")
        except Exception as e:
            self.log_text.setPlainText(f"Error reading log file: {e}")

    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh timer."""
        if state == Qt.Checked:
            self.timer.start(2000)  # Refresh every 2 seconds
        else:
            self.timer.stop()

    def clear_logs(self):
        """Clear the log file."""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            'Clear Logs',
            'Are you sure you want to clear the log file?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Clear the file
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write('')

                # Refresh display
                self.refresh_logs()

                QMessageBox.information(self, 'Success', 'Log file cleared successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to clear log file: {e}')

    def open_in_editor(self):
        """Open the log file in the default text editor."""
        import subprocess
        import sys

        try:
            if sys.platform == 'win32':
                os.startfile(self.log_file_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', self.log_file_path])
            else:
                subprocess.run(['xdg-open', self.log_file_path])
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, 'Error', f'Failed to open log file: {e}')

    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop timer when closing
        self.timer.stop()
        event.accept()
