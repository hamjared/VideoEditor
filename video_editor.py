"""
Video Editor Backend
Handles video loading, clip management, and export operations using MoviePy
"""

from moviepy import VideoFileClip
import os
import sys
from typing import Dict, List, Tuple
import re
import pandas as pd
from proglog import ProgressBarLogger
import logging
from io import StringIO

# Get logger for this module
logger = logging.getLogger(__name__)


class SuppressStdout:
    """
    Context manager to suppress stdout/stderr during MoviePy operations.
    This prevents crashes in frozen executables where stdout is None.
    """
    def __enter__(self):
        # Save original stdout/stderr
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # Replace with StringIO if they are None (frozen executable)
        if sys.stdout is None:
            sys.stdout = StringIO()
        if sys.stderr is None:
            sys.stderr = StringIO()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original stdout/stderr
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        return False


class MoviePyLogger:
    """
    Custom logger for MoviePy that redirects output to Python logging.
    This prevents stdout access issues in frozen executables.
    Does NOT inherit from ProgressBarLogger to avoid any stdout initialization.
    """
    def __init__(self):
        # Create minimal state without calling parent class
        from collections import OrderedDict
        self.state = {'bars': OrderedDict()}
        self.stored = {}
        self.logs = []
        self.log_indent = 0
        self.ignored_bars = set() if True else None  # Empty set instead of None
        self.logged_bars = 'all'
        self.min_time_interval = 0
        self.ignore_bars_under = 0
        self.logger = logging.getLogger('moviepy')

    def bar_is_ignored(self, bar):
        """Check if a bar should be ignored."""
        if self.ignored_bars is None:
            return False
        return bar in self.ignored_bars

    def bar_is_logged(self, bar):
        """Check if a bar should be logged."""
        if self.logged_bars == 'all':
            return True
        if self.logged_bars is None:
            return False
        return bar in self.logged_bars

    def bars_callback(self, bar, attr, value, old_value=None):
        """Log progress bar updates at DEBUG level."""
        # Only log significant progress to avoid spam
        if attr == 'index' and value is not None and old_value is not None:
            bar_state = self.state.get('bars', {}).get(bar, {})
            total = bar_state.get('total')
            if total and total > 0:
                percentage = int((value / total) * 100)
                old_percentage = int((old_value / total) * 100)
                if percentage // 10 != old_percentage // 10:
                    self.logger.debug(f"Progress: {percentage}%")

    def callback(self, **changes):
        """Log callback messages."""
        pass

    def store(self, **changes):
        """Store state changes."""
        self.stored.update(changes)

    def store_callback(self, **changes):
        """Store callback - compatibility method."""
        pass

    def iter_bar(self, *args, **kwargs):
        """Suppress iter_bar to avoid stdout."""
        # Return empty iterator instead of None
        return iter([])

    def iter(self, *args, **kwargs):
        """Iter method - compatibility."""
        # Return empty iterator instead of None
        return iter([])

    def iterable_is_too_short(self, *args, **kwargs):
        """Check if iterable is too short."""
        return False

    def dump_logs(self):
        """Dump logs - compatibility method."""
        return self.logs

    def log(self, message):
        """Log MoviePy messages to our logging system."""
        if message:
            message_str = str(message).strip()
            if message_str:
                self.logger.info(message_str)
                self.logs.append(message_str)

    def __call__(self, **changes):
        """Handle direct calls (MoviePy compatibility)."""
        self.callback(**changes)


class VideoEditor:
    """
    A simple video editor that allows loading videos, defining clips,
    and exporting them as separate files.
    """

    def __init__(self, video_path: str = None):
        """
        Initialize the video editor.

        Args:
            video_path: Path to the video file to load (optional)
        """
        self.video_path = video_path
        self.video_clip = None
        self.clips = {}  # {name: (start_time, end_time)}

        if video_path:
            self.load_video(video_path)

    def load_video(self, video_path: str) -> None:
        """
        Load a video file.

        Args:
            video_path: Path to the video file

        Raises:
            FileNotFoundError: If video file doesn't exist
            Exception: If video cannot be loaded
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Close previous video if exists
        if self.video_clip:
            self.video_clip.close()

        self.video_path = video_path
        self.video_clip = VideoFileClip(video_path)
        self.clips = {}  # Reset clips when loading new video

    def parse_timestamp(self, timestamp: str) -> float:
        """
        Parse timestamp string to seconds.

        Args:
            timestamp: Timestamp in format "HH:MM:SS" or "HH:MM:SS.mmm"

        Returns:
            Time in seconds as float

        Raises:
            ValueError: If timestamp format is invalid
        """
        # Match format HH:MM:SS or HH:MM:SS.mmm
        pattern = r'^(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?$'
        match = re.match(pattern, timestamp)

        if not match:
            raise ValueError(
                f"Invalid timestamp format: {timestamp}. "
                "Expected format: HH:MM:SS or HH:MM:SS.mmm"
            )

        hours, minutes, seconds, milliseconds = match.groups()

        total_seconds = (
            int(hours) * 3600 +
            int(minutes) * 60 +
            int(seconds)
        )

        if milliseconds:
            # Pad or truncate to 3 digits and convert to fraction
            ms = milliseconds.ljust(3, '0')[:3]
            total_seconds += int(ms) / 1000.0

        return float(total_seconds)

    def format_timestamp(self, seconds: float) -> str:
        """
        Format seconds to timestamp string.

        Args:
            seconds: Time in seconds

        Returns:
            Timestamp string in format "HH:MM:SS.mmm"
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"

    def add_clip(self, name: str, start: str, end: str) -> None:
        """
        Add a clip definition.

        Args:
            name: Name for the clip
            start: Start timestamp (HH:MM:SS or HH:MM:SS.mmm)
            end: End timestamp (HH:MM:SS or HH:MM:SS.mmm)

        Raises:
            ValueError: If timestamps are invalid or video not loaded
        """
        if not self.video_clip:
            raise ValueError("No video loaded. Load a video first.")

        start_seconds = self.parse_timestamp(start)
        end_seconds = self.parse_timestamp(end)

        # Validate timestamps
        if start_seconds < 0:
            raise ValueError("Start time cannot be negative")

        if end_seconds > self.video_clip.duration:
            raise ValueError(
                f"End time ({end_seconds}s) exceeds video duration "
                f"({self.video_clip.duration}s)"
            )

        if start_seconds >= end_seconds:
            raise ValueError("Start time must be before end time")

        self.clips[name] = (start_seconds, end_seconds)

    def edit_clip(self, old_name: str, new_name: str, start: str, end: str) -> None:
        """
        Edit an existing clip definition.

        Args:
            old_name: Current name of the clip
            new_name: New name for the clip
            start: New start timestamp (HH:MM:SS or HH:MM:SS.mmm)
            end: New end timestamp (HH:MM:SS or HH:MM:SS.mmm)

        Raises:
            KeyError: If clip doesn't exist
            ValueError: If timestamps are invalid or video not loaded
        """
        if old_name not in self.clips:
            raise KeyError(f"Clip '{old_name}' not found")

        if not self.video_clip:
            raise ValueError("No video loaded. Load a video first.")

        start_seconds = self.parse_timestamp(start)
        end_seconds = self.parse_timestamp(end)

        # Validate timestamps
        if start_seconds < 0:
            raise ValueError("Start time cannot be negative")

        if end_seconds > self.video_clip.duration:
            raise ValueError(
                f"End time ({end_seconds}s) exceeds video duration "
                f"({self.video_clip.duration}s)"
            )

        if start_seconds >= end_seconds:
            raise ValueError("Start time must be before end time")

        # If name changed, check if new name already exists (unless it's the same clip)
        if new_name != old_name and new_name in self.clips:
            raise ValueError(f"A clip named '{new_name}' already exists")

        # Remove old clip and add with new data
        del self.clips[old_name]
        self.clips[new_name] = (start_seconds, end_seconds)

    def remove_clip(self, name: str) -> None:
        """
        Remove a clip definition.

        Args:
            name: Name of the clip to remove

        Raises:
            KeyError: If clip doesn't exist
        """
        if name not in self.clips:
            raise KeyError(f"Clip '{name}' not found")

        del self.clips[name]

    def clear_clips(self) -> None:
        """Clear all clip definitions."""
        self.clips = {}

    def import_clips_from_file(self, file_path: str, clear_existing: bool = False) -> Dict[str, any]:
        """
        Import clips from a CSV or Excel file.

        Expected columns (case-insensitive):
        - 'clip name' or 'name': Name of the clip
        - 'start time' or 'start': Start timestamp (HH:MM:SS or HH:MM:SS.mmm)
        - 'end time' or 'end': End timestamp (HH:MM:SS or HH:MM:SS.mmm)

        Args:
            file_path: Path to CSV or Excel file
            clear_existing: If True, clear existing clips before importing

        Returns:
            Dictionary with import statistics:
            {
                'success': int,  # Number of clips successfully imported
                'failed': int,   # Number of clips that failed
                'errors': List[str]  # List of error messages
            }

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported or required columns are missing
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file type and read accordingly
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Use .csv, .xlsx, or .xls")
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")

        # Normalize column names (strip whitespace and convert to lowercase)
        df.columns = df.columns.str.strip().str.lower()

        # Find the column names (allow variations)
        name_col = None
        start_col = None
        end_col = None

        for col in df.columns:
            if col in ['clip name', 'name', 'clipname']:
                name_col = col
            elif col in ['start time', 'start', 'starttime']:
                start_col = col
            elif col in ['end time', 'end', 'endtime']:
                end_col = col

        # Validate required columns exist
        missing_cols = []
        if name_col is None:
            missing_cols.append("'clip name' or 'name'")
        if start_col is None:
            missing_cols.append("'start time' or 'start'")
        if end_col is None:
            missing_cols.append("'end time' or 'end'")

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_cols)}. "
                f"Found columns: {', '.join(df.columns)}"
            )

        # Clear existing clips if requested
        if clear_existing:
            self.clear_clips()

        # Import clips
        stats = {
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for idx, row in df.iterrows():
            try:
                clip_name = str(row[name_col]).strip()
                start_time = str(row[start_col]).strip()
                end_time = str(row[end_col]).strip()

                # Skip empty rows
                if pd.isna(row[name_col]) or not clip_name:
                    continue

                # Add the clip
                self.add_clip(clip_name, start_time, end_time)
                stats['success'] += 1

            except Exception as e:
                stats['failed'] += 1
                error_msg = f"Row {idx + 2}: {str(e)}"  # +2 because of 0-index and header row
                stats['errors'].append(error_msg)

        return stats

    def get_clips_info(self) -> List[Dict]:
        """
        Get information about all defined clips.

        Returns:
            List of dictionaries containing clip information, sorted by start time
        """
        clips_info = []
        for name, (start, end) in self.clips.items():
            clips_info.append({
                'name': name,
                'start': self.format_timestamp(start),
                'end': self.format_timestamp(end),
                'start_seconds': start,
                'end_seconds': end,
                'duration': end - start
            })
        # Sort by start time
        clips_info.sort(key=lambda x: x['start_seconds'])
        return clips_info

    def get_video_info(self) -> Dict:
        """
        Get information about the loaded video.

        Returns:
            Dictionary containing video information

        Raises:
            ValueError: If no video is loaded
        """
        if not self.video_clip:
            raise ValueError("No video loaded")

        return {
            'path': self.video_path,
            'filename': os.path.basename(self.video_path),
            'duration': self.video_clip.duration,
            'duration_formatted': self.format_timestamp(self.video_clip.duration),
            'fps': self.video_clip.fps,
            'size': self.video_clip.size,  # (width, height)
            'width': self.video_clip.w,
            'height': self.video_clip.h
        }

    def export_clip(self, clip_name: str, output_path: str,
                   codec: str = 'libx264', audio_codec: str = 'aac') -> None:
        """
        Export a single clip to a file.

        Args:
            clip_name: Name of the clip to export
            output_path: Path where the clip should be saved
            codec: Video codec to use (default: libx264)
            audio_codec: Audio codec to use (default: aac)

        Raises:
            ValueError: If video not loaded or clip doesn't exist
        """
        if not self.video_clip:
            raise ValueError("No video loaded")

        if clip_name not in self.clips:
            raise KeyError(f"Clip '{clip_name}' not found")

        start, end = self.clips[clip_name]

        logger.info(f"Exporting clip '{clip_name}' to {output_path}")

        try:
            # Extract subclip (MoviePy v2.0 uses subclipped method)
            subclip = self.video_clip.subclipped(start, end)

            # Export with stdout/stderr suppression for frozen executable compatibility
            with SuppressStdout():
                subclip.write_videofile(
                    output_path,
                    codec=codec,
                    audio_codec=audio_codec,
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    logger=None
                )

            # Close the subclip
            subclip.close()

            logger.info(f"Successfully exported '{clip_name}'")

        except Exception as e:
            logger.error(f"Failed to export clip '{clip_name}': {e}", exc_info=True)
            raise

    def export_all_clips(self, output_dir: str,
                        codec: str = 'libx264',
                        audio_codec: str = 'aac',
                        progress_callback=None) -> List[str]:
        """
        Export all clips to a directory.

        Args:
            output_dir: Directory where clips should be saved
            codec: Video codec to use (default: libx264)
            audio_codec: Audio codec to use (default: aac)
            progress_callback: Optional callback function(current, total, clip_name)

        Returns:
            List of exported file paths

        Raises:
            ValueError: If video not loaded or no clips defined
        """
        if not self.video_clip:
            raise ValueError("No video loaded")

        if not self.clips:
            raise ValueError("No clips defined")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        exported_files = []
        total_clips = len(self.clips)
        subclips = []  # Keep track of subclips to close them all at the end

        # Wrap entire export loop in SuppressStdout to avoid MoviePy audio reader issues
        with SuppressStdout():
            try:
                for idx, (clip_name, (start, end)) in enumerate(self.clips.items(), 1):
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(idx - 1, total_clips, clip_name)

                    # Generate output filename
                    output_filename = f"{clip_name}.mp4"
                    output_path = os.path.join(output_dir, output_filename)

                    logger.info(f"Exporting clip {idx}/{total_clips}: '{clip_name}' to {output_path}")

                    try:
                        # Extract subclip (MoviePy v2.0 uses subclipped method)
                        subclip = self.video_clip.subclipped(start, end)
                        subclips.append(subclip)  # Store for cleanup later

                        # Export the subclip
                        subclip.write_videofile(
                            output_path,
                            codec=codec,
                            audio_codec=audio_codec,
                            temp_audiofile=f'temp-audio-{clip_name}.m4a',
                            remove_temp=True,
                            logger=None
                        )

                        exported_files.append(output_path)
                        logger.info(f"Successfully exported '{clip_name}'")

                    except Exception as e:
                        logger.error(f"Failed to export clip '{clip_name}': {e}", exc_info=True)
                        raise

            finally:
                # Close all subclips at the end to avoid corrupting shared audio readers
                for subclip in subclips:
                    try:
                        subclip.close()
                    except:
                        pass  # Ignore errors during cleanup

        # Final progress callback
        if progress_callback:
            progress_callback(total_clips, total_clips, "Complete")

        return exported_files

    def close(self) -> None:
        """Close the video clip and release resources."""
        if self.video_clip:
            self.video_clip.close()
            self.video_clip = None

    def __del__(self):
        """Destructor to ensure video is closed."""
        self.close()
