"""
Simple Video Editor - Main Entry Point
A simple PyQt5-based video editor for cutting clips from videos.
"""

import os
import sys
import platform
import logging

# Import logging configuration
from logging_config import setup_logging

# Set up logging FIRST (before any other imports that might log)
setup_logging()

# Get logger for this module
logger = logging.getLogger(__name__)


# Set up ffplay and VLC paths BEFORE any other imports
# This must be done early, as these libraries read paths on import
def setup_media_libs():
    """Configure bundled media libraries before they are loaded."""
    logger.info("Setting up bundled media libraries")

    system = platform.system()
    if system == "Windows":
        platform_dir = "win32"
        exe_name = "ffplay.exe"
    elif system == "Darwin":
        platform_dir = "darwin"
        exe_name = "ffplay"
    elif system == "Linux":
        platform_dir = "linux"
        exe_name = "ffplay"
    else:
        logger.warning(f"Unsupported platform: {system}")
        return

    # Get the application directory
    if getattr(sys, 'frozen', False):
        app_dir = sys._MEIPASS
        logger.info(f"Running as frozen executable, app_dir: {app_dir}")
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Running as script, app_dir: {app_dir}")

    # Set paths for both ffplay and ffmpeg
    ffplay_path = os.path.join(app_dir, "bin", platform_dir, exe_name)
    ffmpeg_name = "ffmpeg.exe" if system == "Windows" else "ffmpeg"
    ffmpeg_path = os.path.join(app_dir, "bin", platform_dir, ffmpeg_name)

    if os.path.exists(ffplay_path):
        os.environ["FFPLAY_BINARY"] = ffplay_path
        logger.info(f"Set FFPLAY_BINARY to {ffplay_path}")
    else:
        logger.warning(f"Bundled ffplay not found at {ffplay_path}, will use system ffplay")

    if os.path.exists(ffmpeg_path):
        os.environ["FFMPEG_BINARY"] = ffmpeg_path
        logger.info(f"Set FFMPEG_BINARY to {ffmpeg_path}")
    else:
        logger.warning(f"Bundled ffmpeg not found at {ffmpeg_path}, will use system ffmpeg")

    # Set up VLC path (Windows/macOS only, Linux uses system VLC)
    if system in ["Windows", "Darwin"]:
        vlc_dir = os.path.join(app_dir, "bin", platform_dir, "vlc")
        if os.path.exists(vlc_dir):
            # Add VLC directory to PATH so python-vlc can find the DLLs
            if vlc_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = vlc_dir + os.pathsep + os.environ.get('PATH', '')
                logger.info(f"Added {vlc_dir} to PATH")

            # On Windows Python 3.8+, use add_dll_directory for better DLL loading
            if system == "Windows" and hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(vlc_dir)
                    logger.info(f"Added {vlc_dir} to DLL search path")
                except Exception as e:
                    logger.error(f"Failed to add DLL directory: {e}")

            # Set VLC plugin path
            vlc_plugin_path = os.path.join(vlc_dir, "plugins")
            if os.path.exists(vlc_plugin_path):
                os.environ['VLC_PLUGIN_PATH'] = vlc_plugin_path
                logger.info(f"Set VLC_PLUGIN_PATH to {vlc_plugin_path}")
        else:
            logger.warning(f"Bundled VLC not found at {vlc_dir}, will use system VLC")

# Set up media libraries BEFORE importing gui
setup_media_libs()

logger.info("Importing GUI module")
from gui import main

if __name__ == '__main__':
    main()
