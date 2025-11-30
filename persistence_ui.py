"""
Persistence UI Components
Handles all GUI dialogs and interactions for clip persistence.
"""

import os
from enum import Enum
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import logging

logger = logging.getLogger(__name__)


class RecoveryAction(Enum):
    """Actions a user can take when prompted about recovery."""
    LOAD = "load"
    DISCARD = "discard"
    CANCEL = "cancel"


class PersistenceUI:
    """
    Manages all persistence-related UI interactions.

    Provides dialogs for recovery, save/load, and error handling.
    """

    def __init__(self, parent_window, persistence_manager):
        """
        Initialize the persistence UI handler.

        Args:
            parent_window: The main window (for dialog parent)
            persistence_manager: ClipPersistenceManager instance
        """
        self.parent = parent_window
        self.manager = persistence_manager

    def show_recovery_dialog(self, recovery_data) -> RecoveryAction:
        """
        Show dialog asking user if they want to restore from recovery.

        Args:
            recovery_data: Dictionary with recovery information

        Returns:
            RecoveryAction indicating user's choice
        """
        try:
            timestamp_str = recovery_data.get('timestamp', 'unknown time')
            try:
                # Parse ISO format timestamp
                timestamp = datetime.fromisoformat(timestamp_str)
                timestamp_display = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp_display = timestamp_str

            clip_count = len(recovery_data.get('clips', []))
            video_path = recovery_data.get('video_path', 'No video')
            video_name = os.path.basename(video_path) if video_path else 'No video'

            message = (
                f"Found unsaved session from {timestamp_display}\n\n"
                f"Video: {video_name}\n"
                f"Clips: {clip_count}\n\n"
                f"Do you want to restore this session?"
            )

            reply = QMessageBox.question(
                self.parent,
                "Restore Session?",
                message,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                return RecoveryAction.LOAD
            elif reply == QMessageBox.No:
                return RecoveryAction.DISCARD
            else:
                return RecoveryAction.CANCEL

        except Exception as e:
            logger.error(f"Error showing recovery dialog: {e}", exc_info=True)
            return RecoveryAction.CANCEL

    def show_video_mismatch_dialog(self, recovery_video: str, current_video: str) -> bool:
        """
        Show dialog when recovery file is for a different video.

        Args:
            recovery_video: Video path from recovery file
            current_video: Currently loaded video path

        Returns:
            True to load clips anyway, False to skip
        """
        try:
            recovery_name = os.path.basename(recovery_video)
            current_name = os.path.basename(current_video)

            message = (
                f"The clips you're loading are from a different video:\n\n"
                f"Clips from: {recovery_name}\n"
                f"Current video: {current_name}\n\n"
                f"Load clips anyway?"
            )

            reply = QMessageBox.question(
                self.parent,
                "Video Mismatch",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            return reply == QMessageBox.Yes

        except Exception as e:
            logger.error(f"Error showing video mismatch dialog: {e}", exc_info=True)
            return False

    def show_missing_video_dialog(self, video_path: str) -> bool:
        """
        Show dialog when video file referenced in recovery doesn't exist.

        Args:
            video_path: The missing video file path

        Returns:
            True to load clips anyway, False to skip recovery
        """
        try:
            message = (
                f"The video file referenced in the saved clips was not found:\n\n"
                f"{video_path}\n\n"
                f"Load clips anyway? (You can load the video manually later)"
            )

            reply = QMessageBox.question(
                self.parent,
                "Video Not Found",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            return reply == QMessageBox.Yes

        except Exception as e:
            logger.error(f"Error showing missing video dialog: {e}", exc_info=True)
            return False

    def prompt_save_location(self, default_dir: str, default_name: str) -> str:
        """
        Show save file dialog for saving clips.

        Args:
            default_dir: Default directory to show
            default_name: Default filename to suggest

        Returns:
            Selected file path or empty string if cancelled
        """
        try:
            default_path = os.path.join(default_dir, default_name)

            file_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Clips",
                default_path,
                "Video Editor Clips (*.vedclips);;All Files (*.*)"
            )

            # Ensure .vedclips extension
            if file_path and not file_path.endswith('.vedclips'):
                file_path += '.vedclips'

            return file_path

        except Exception as e:
            logger.error(f"Error showing save dialog: {e}", exc_info=True)
            return ""

    def prompt_load_location(self) -> str:
        """
        Show load file dialog for loading clips.

        Returns:
            Selected file path or empty string if cancelled
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent,
                "Load Clips",
                "",
                "Video Editor Clips (*.vedclips);;All Files (*.*)"
            )

            return file_path

        except Exception as e:
            logger.error(f"Error showing load dialog: {e}", exc_info=True)
            return ""

    def show_save_success(self, file_path: str):
        """
        Show success message after saving clips.

        Args:
            file_path: Path where clips were saved
        """
        try:
            file_name = os.path.basename(file_path)
            QMessageBox.information(
                self.parent,
                "Save Successful",
                f"Clips saved successfully to:\n{file_name}"
            )
        except Exception as e:
            logger.error(f"Error showing save success dialog: {e}", exc_info=True)

    def show_load_error(self, error_message: str):
        """
        Show error dialog when loading clips fails.

        Args:
            error_message: The error message to display
        """
        try:
            QMessageBox.critical(
                self.parent,
                "Load Error",
                f"Failed to load clips:\n\n{error_message}"
            )
        except Exception as e:
            logger.error(f"Error showing load error dialog: {e}", exc_info=True)

    def show_save_error(self, error_message: str):
        """
        Show error dialog when saving clips fails.

        Args:
            error_message: The error message to display
        """
        try:
            QMessageBox.critical(
                self.parent,
                "Save Error",
                f"Failed to save clips:\n\n{error_message}"
            )
        except Exception as e:
            logger.error(f"Error showing save error dialog: {e}", exc_info=True)
