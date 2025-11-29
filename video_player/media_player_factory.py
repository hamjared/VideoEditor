"""
Media Player Factory
Creates VLC media player instance.
"""

from typing import Optional
from .media_player_interface import MediaPlayerInterface


class MediaPlayerFactory:
    """
    Factory class for creating media player instances.

    Uses VLC player with bundled VLC libraries for best audio/video sync.
    """

    @staticmethod
    def create_player(parent=None) -> Optional[MediaPlayerInterface]:
        """
        Create VLC media player.

        Args:
            parent: Parent widget

        Returns:
            VLCMediaPlayerWidget instance or None if VLC not available
        """
        try:
            from .vlc_media_player import VLCMediaPlayerWidget
            player = VLCMediaPlayerWidget(parent)
            print(f"Using {player.get_player_name()}")
            return player
        except ImportError as e:
            print(f"Could not load VLC player: {e}")
        except Exception as e:
            print(f"Error creating VLC player: {e}")
            import traceback
            traceback.print_exc()

        print("Warning: VLC player not available")
        return None

    @staticmethod
    def get_available_players() -> list:
        """
        Get list of available player names.

        Returns:
            List of available player implementation names
        """
        available = []

        # Check VLC
        try:
            import vlc
            available.append("VLC Player")
        except ImportError:
            pass

        return available
