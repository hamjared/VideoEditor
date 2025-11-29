"""
VLC Media Player Implementation
Uses VLC for video playback with full audio support.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QStyle, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from .media_player_interface import MediaPlayerInterface
import sys
import os
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class VLCMediaPlayerWidget(MediaPlayerInterface):
    """
    VLC-based media player implementation.

    Uses libVLC for playback with perfect audio/video sync.
    VLC must be installed on the system.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_path = None
        self.is_playing = False
        self.is_reverse_playing = False
        self.reverse_speed = 1.0  # Multiplier for reverse speed

        # Set up bundled VLC path (Windows only, Linux uses system VLC)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = sys._MEIPASS
        else:
            # Running as script - go up one level from video_player/ directory
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        platform = sys.platform
        if platform.startswith('win'):
            platform_dir = "win32"
            lib_name = "libvlc.dll"
        elif platform.startswith('darwin'):
            platform_dir = "darwin"
            lib_name = "libvlc.dylib"
        else:
            # Linux - use system VLC
            platform_dir = None
            lib_name = None

        # Import VLC
        try:
            # Try bundled VLC first (Windows/macOS)
            if platform_dir:
                vlc_path = os.path.join(app_dir, "bin", platform_dir, "vlc")
                vlc_lib_path = os.path.join(vlc_path, lib_name)
                vlc_plugin_path = os.path.join(vlc_path, "plugins")

                if os.path.exists(vlc_lib_path):
                    logger.info(f"Using bundled VLC from {vlc_path}")

                    # Add VLC directory to PATH so python-vlc can find the libraries
                    if vlc_path not in os.environ.get('PATH', ''):
                        os.environ['PATH'] = vlc_path + os.pathsep + os.environ.get('PATH', '')

                    # Set VLC plugin path
                    os.environ['VLC_PLUGIN_PATH'] = vlc_plugin_path

                    # Import vlc module and explicitly preload DLLs
                    import ctypes

                    # Preload libvlccore.dll first (libvlc.dll depends on it)
                    vlc_core_path = os.path.join(vlc_path, "libvlccore.dll")
                    try:
                        vlc_core_dll = ctypes.CDLL(vlc_core_path)
                    except Exception as e:
                        logger.error(f"Failed to load libvlccore.dll: {e}")

                    # Then load libvlc.dll
                    try:
                        vlc_dll = ctypes.CDLL(vlc_lib_path)
                    except Exception as e:
                        logger.error(f"Failed to load libvlc.dll: {e}")

                    # Now import python-vlc
                    import vlc

                    # Create instance
                    self.instance = vlc.Instance()
                else:
                    logger.warning(f"Bundled VLC not found at {vlc_path}, using system VLC")
                    import vlc
                    self.instance = vlc.Instance()
            else:
                # Linux - use system VLC
                logger.info("Using system VLC (Linux)")
                import vlc
                self.instance = vlc.Instance()

            self.vlc = vlc

            # Check if instance was created successfully
            if self.instance is None:
                raise Exception("Failed to create VLC instance - instance is None")

            self.player = self.instance.media_player_new()

            if self.player is None:
                raise Exception("Failed to create media player - player is None")
        except Exception as e:
            logger.error(f"Failed to initialize VLC: {e}", exc_info=True)
            self.vlc = None
            self.instance = None
            self.player = None

        # Timer to update UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)

        self.init_ui()

    def init_ui(self):
        """Initialize the video player UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Video display frame
        self.video_frame = QFrame()
        self.video_frame.setMinimumSize(640, 360)
        self.video_frame.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_frame)

        # Attach VLC to the frame
        if self.player and sys.platform.startswith('win'):
            self.player.set_hwnd(int(self.video_frame.winId()))
        elif self.player and sys.platform == 'darwin':
            self.player.set_nsobject(int(self.video_frame.winId()))
        elif self.player:
            self.player.set_xwindow(int(self.video_frame.winId()))

        # Time display
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00:00.000 / 00:00:00.000")
        self.time_label.setStyleSheet("padding: 5px;")
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        layout.addLayout(time_layout)

        # Seek slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.seek_to_position)
        self.position_slider.sliderPressed.connect(self.slider_pressed)
        self.position_slider.sliderReleased.connect(self.slider_released)
        self.slider_being_dragged = False
        layout.addWidget(self.position_slider)

        # Playback controls
        controls_layout = QHBoxLayout()

        # Reverse Fast button (<<)
        self.reverse_fast_button = QPushButton("<<")
        self.reverse_fast_button.clicked.connect(self.reverse_fast)
        self.reverse_fast_button.setFixedWidth(40)
        self.reverse_fast_button.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.reverse_fast_button)

        # Reverse Normal button (<)
        self.reverse_button = QPushButton("<")
        self.reverse_button.clicked.connect(self.reverse_normal)
        self.reverse_button.setFixedWidth(40)
        self.reverse_button.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.reverse_button)

        # Play/Pause button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)
        self.play_button.setFixedWidth(40)
        self.play_button.setEnabled(False)
        controls_layout.addWidget(self.play_button)

        # Reset to 1x Speed button (without pausing)
        self.reset_speed_button = QPushButton(">")
        self.reset_speed_button.clicked.connect(self.reset_speed)
        self.reset_speed_button.setFixedWidth(40)
        self.reset_speed_button.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.reset_speed_button)

        # Increase Speed button
        self.increase_speed_button = QPushButton(">>")
        self.increase_speed_button.clicked.connect(self.increase_speed)
        self.increase_speed_button.setFixedWidth(40)
        self.increase_speed_button.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.increase_speed_button)

        # Stop button
        stop_button = QPushButton()
        stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        stop_button.clicked.connect(self.stop)
        stop_button.setFixedWidth(40)
        controls_layout.addWidget(stop_button)

        controls_layout.addSpacing(10)

        # Speed control
        speed_label = QLabel("Speed:")
        controls_layout.addWidget(speed_label)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.5x", "2x", "3x", "4x", "8x", "16x", "32x", "64x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentTextChanged.connect(self.on_speed_changed)
        self.speed_combo.setFixedWidth(70)
        controls_layout.addWidget(self.speed_combo)

        controls_layout.addSpacing(10)

        # Mark Start button
        self.mark_start_button = QPushButton("Mark Start")
        self.mark_start_button.clicked.connect(self.mark_start)
        self.mark_start_button.setEnabled(False)
        controls_layout.addWidget(self.mark_start_button)

        # Mark End button
        self.mark_end_button = QPushButton("Mark End")
        self.mark_end_button.clicked.connect(self.mark_end)
        self.mark_end_button.setEnabled(False)
        controls_layout.addWidget(self.mark_end_button)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def load_video(self, video_path: str) -> bool:
        """Load a video file into the player."""
        if not os.path.exists(video_path):
            return False

        if not self.player:
            logger.error("VLC not available, cannot load video")
            return False

        try:
            self.video_path = video_path
            media = self.instance.media_new(video_path)
            self.player.set_media(media)

            # Parse media to get duration
            media.parse()

            # Enable controls
            self.play_button.setEnabled(True)
            self.mark_start_button.setEnabled(True)
            self.mark_end_button.setEnabled(True)

            logger.info(f"Video loaded successfully: {video_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load video: {e}", exc_info=True)
            return False

    def play_pause(self):
        """Toggle play/pause."""
        if not self.player:
            return

        # Disable reverse mode when using play/pause
        if self.is_reverse_playing:
            self.is_reverse_playing = False

        if self.player.is_playing() or self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.timer.stop()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            # If playing at faster than 1x, reset to 1x
            current_speed = self.speed_combo.currentText()
            if current_speed != "1x":
                self.speed_combo.setCurrentText("1x")

            self.player.play()
            self.is_playing = True
            self.timer.start(100)  # Update every 100ms
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def stop(self):
        """Stop playback."""
        if not self.player:
            return

        self.player.stop()
        self.is_playing = False
        self.is_reverse_playing = False
        self.timer.stop()
        self.position_slider.setValue(0)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def seek_to_position(self, value):
        """Seek to a specific position from slider."""
        if not self.player or not self.player.get_length():
            return

        # Convert slider position (0-1000) to time position (0.0-1.0)
        position = value / 1000.0
        self.player.set_position(position)

    def seek_to_timestamp(self, timestamp: str):
        """Seek to a specific timestamp (HH:MM:SS.mmm format)."""
        if not self.player or not self.player.get_length():
            return

        try:
            # Convert timestamp to milliseconds
            ms = self.timestamp_to_milliseconds(timestamp)
            # Set player time in milliseconds
            self.player.set_time(ms)
            logger.debug(f"Seeked to {timestamp} ({ms}ms)")
        except Exception as e:
            logger.error(f"Failed to seek to {timestamp}: {e}")

    def slider_pressed(self):
        """Called when user starts dragging slider."""
        self.slider_being_dragged = True

    def slider_released(self):
        """Called when user releases slider."""
        self.slider_being_dragged = False

    def on_speed_changed(self, speed_text: str):
        """Handle playback speed change."""
        if not self.player:
            return

        # Parse speed (e.g., "2x" -> 2.0)
        speed_str = speed_text.replace('x', '')
        new_speed = float(speed_str)
        self.player.set_rate(new_speed)

    def increase_speed(self):
        """Increase playback speed to the next level."""
        current_index = self.speed_combo.currentIndex()
        if current_index < self.speed_combo.count() - 1:
            self.speed_combo.setCurrentIndex(current_index + 1)

    def reset_speed(self):
        """Reset playback speed to 1x without pausing."""
        self.speed_combo.setCurrentText("1x")

    def reverse_normal(self):
        """Play video in reverse at normal speed."""
        if not self.player:
            return

        # Pause the player (we'll handle reverse by seeking)
        self.player.pause()

        # Enable reverse playback mode at 1x speed
        self.is_reverse_playing = True
        self.reverse_speed = 1.0
        self.is_playing = True

        # Start the update timer
        self.timer.start(100)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def reverse_fast(self):
        """Play video in reverse at fast speed (4x)."""
        if not self.player:
            return

        # Pause the player (we'll handle reverse by seeking)
        self.player.pause()

        # Enable reverse playback mode at 4x speed
        self.is_reverse_playing = True
        self.reverse_speed = 4.0
        self.is_playing = True

        # Start the update timer
        self.timer.start(100)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def update_ui(self):
        """Update UI elements during playback."""
        if not self.player:
            return

        # Handle reverse playback by seeking backward
        if self.is_reverse_playing:
            current_time = self.player.get_time()
            if current_time is not None and current_time > 0:
                # Seek backward by 100ms * reverse_speed
                jump_back = int(100 * self.reverse_speed)
                new_time = max(0, current_time - jump_back)
                self.player.set_time(new_time)

                # Stop if we hit the beginning
                if new_time == 0:
                    self.is_reverse_playing = False
                    self.player.pause()
                    self.is_playing = False
                    self.timer.stop()
                    self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Update slider position (unless user is dragging it)
        if not self.slider_being_dragged:
            position = self.player.get_position()  # Returns 0.0 to 1.0
            if position >= 0:
                self.position_slider.setValue(int(position * 1000))

        # Update time display
        current_time = self.player.get_time()  # milliseconds
        length = self.player.get_length()  # milliseconds

        if current_time >= 0 and length > 0:
            current_str = self.milliseconds_to_timestamp(current_time)
            total_str = self.milliseconds_to_timestamp(length)
            self.time_label.setText(f"{current_str} / {total_str}")

    def get_current_timestamp(self) -> str:
        """Get the current playback position as a timestamp string."""
        if not self.player:
            return "00:00:00.000"

        current_time = self.player.get_time()
        if current_time >= 0:
            return self.milliseconds_to_timestamp(current_time)
        return "00:00:00.000"

    def close_player(self):
        """Clean up the media player."""
        self.timer.stop()
        if self.player:
            self.player.stop()
            self.player.release()
        if self.instance:
            self.instance.release()

    def mark_start(self):
        """Emit signal with current timestamp for marking start time."""
        timestamp = self.get_current_timestamp()
        self.mark_start_clicked.emit(timestamp)

    def mark_end(self):
        """Emit signal with current timestamp for marking end time."""
        timestamp = self.get_current_timestamp()
        self.mark_end_clicked.emit(timestamp)

    @staticmethod
    def get_player_name() -> str:
        """Get the name of this player implementation."""
        return "VLC Player"
