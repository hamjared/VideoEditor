"""
Media Player Interface
Defines the interface that all media player implementations must follow.
"""

from abc import ABCMeta, abstractmethod
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from sip import wrappertype


# Create a metaclass that combines Qt's metaclass with ABC
class MediaPlayerMeta(wrappertype, ABCMeta):
    pass


class MediaPlayerInterface(QWidget, metaclass=MediaPlayerMeta):
    """
    Abstract base class for media player implementations.

    All media players must emit these signals and implement these methods.

    Signals:
        mark_start_clicked: Emitted with timestamp string when Mark Start is clicked
        mark_end_clicked: Emitted with timestamp string when Mark End is clicked
    """

    mark_start_clicked = pyqtSignal(str)  # timestamp string
    mark_end_clicked = pyqtSignal(str)    # timestamp string

    def __init__(self, parent=None):
        super().__init__(parent)

    @abstractmethod
    def load_video(self, video_path: str) -> bool:
        """
        Load a video file into the player.

        Args:
            video_path: Path to the video file

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def play_pause(self):
        """Toggle play/pause."""
        pass

    @abstractmethod
    def stop(self):
        """Stop playback."""
        pass

    @abstractmethod
    def get_current_timestamp(self) -> str:
        """
        Get the current playback position as a timestamp string.

        Returns:
            Timestamp string in format "HH:MM:SS.mmm"
        """
        pass

    @abstractmethod
    def close_player(self):
        """Clean up the media player resources."""
        pass

    @abstractmethod
    def seek_to_timestamp(self, timestamp: str):
        """
        Seek to a specific timestamp in the video.

        Args:
            timestamp: Timestamp string in format "HH:MM:SS.mmm"
        """
        pass

    @staticmethod
    def milliseconds_to_timestamp(milliseconds: int) -> str:
        """
        Convert milliseconds to timestamp string.

        Args:
            milliseconds: Time in milliseconds

        Returns:
            Timestamp string in format "HH:MM:SS.mmm"
        """
        seconds = milliseconds / 1000.0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"

    @staticmethod
    def timestamp_to_milliseconds(timestamp: str) -> int:
        """
        Convert timestamp string to milliseconds.

        Args:
            timestamp: Timestamp string in format "HH:MM:SS.mmm" or "HH:MM:SS"

        Returns:
            Time in milliseconds
        """
        # Split by ':' to get hours, minutes, seconds
        parts = timestamp.split(':')
        if len(parts) != 3:
            raise ValueError(f"Invalid timestamp format: {timestamp}")

        hours = int(parts[0])
        minutes = int(parts[1])

        # Handle seconds with optional milliseconds
        if '.' in parts[2]:
            secs_parts = parts[2].split('.')
            seconds = int(secs_parts[0])
            milliseconds = int(secs_parts[1])
        else:
            seconds = int(parts[2])
            milliseconds = 0

        # Convert to total milliseconds
        total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
        return total_ms

    @staticmethod
    def get_player_name() -> str:
        """
        Get the name of this player implementation.

        Returns:
            Human-readable name of the player
        """
        return "Unknown Player"
