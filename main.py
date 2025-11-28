"""
Simple Video Editor - Main Entry Point
A simple PyQt5-based video editor for cutting clips from videos.
"""

import os
import sys
import platform

# Set up ffplay and VLC paths BEFORE any imports
# This must be done first, as these libraries read paths on import
def setup_media_libs():
    """Configure bundled media libraries before they are loaded."""
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
        return

    # Get the application directory
    if getattr(sys, 'frozen', False):
        app_dir = sys._MEIPASS
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    # Set paths for both ffplay and ffmpeg
    ffplay_path = os.path.join(app_dir, "bin", platform_dir, exe_name)
    ffmpeg_name = "ffmpeg.exe" if system == "Windows" else "ffmpeg"
    ffmpeg_path = os.path.join(app_dir, "bin", platform_dir, ffmpeg_name)

    if os.path.exists(ffplay_path):
        os.environ["FFPLAY_BINARY"] = ffplay_path
        print(f"Startup: Set FFPLAY_BINARY to {ffplay_path}")
    else:
        print(f"Startup: Bundled ffplay not found at {ffplay_path}")

    if os.path.exists(ffmpeg_path):
        os.environ["FFMPEG_BINARY"] = ffmpeg_path
        print(f"Startup: Set FFMPEG_BINARY to {ffmpeg_path}")
    else:
        print(f"Startup: Bundled ffmpeg not found at {ffmpeg_path}")

    # Set up VLC path (Windows/macOS only, Linux uses system VLC)
    if system in ["Windows", "Darwin"]:
        vlc_dir = os.path.join(app_dir, "bin", platform_dir, "vlc")
        if os.path.exists(vlc_dir):
            # Add VLC directory to PATH so python-vlc can find the DLLs
            if vlc_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = vlc_dir + os.pathsep + os.environ.get('PATH', '')
                print(f"Startup: Added {vlc_dir} to PATH")

            # On Windows Python 3.8+, use add_dll_directory for better DLL loading
            if system == "Windows" and hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(vlc_dir)
                    print(f"Startup: Added {vlc_dir} to DLL search path")
                except Exception as e:
                    print(f"Startup: Failed to add DLL directory: {e}")

            # Set VLC plugin path
            vlc_plugin_path = os.path.join(vlc_dir, "plugins")
            if os.path.exists(vlc_plugin_path):
                os.environ['VLC_PLUGIN_PATH'] = vlc_plugin_path
                print(f"Startup: Set VLC_PLUGIN_PATH to {vlc_plugin_path}")
        else:
            print(f"Startup: Bundled VLC not found at {vlc_dir}")

# Set up media libraries BEFORE importing gui
setup_media_libs()

from gui import main

if __name__ == '__main__':
    main()
