"""
Clip Persistence Manager
Handles saving and loading clip data to/from files.
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ClipPersistenceManager:
    """
    Manages persistence of clip data to files.

    Supports both manual save/load and automatic recovery functionality.
    """

    FILE_VERSION = "1.0"

    def __init__(self, recovery_file_path: str):
        """
        Initialize the persistence manager.

        Args:
            recovery_file_path: Path to the recovery file
        """
        self.recovery_file = recovery_file_path

        # Ensure recovery directory exists
        recovery_dir = os.path.dirname(recovery_file_path)
        if recovery_dir:
            os.makedirs(recovery_dir, exist_ok=True)

    def save_to_file(self, file_path: str, clips: List[Dict], video_path: Optional[str],
                     output_path: Optional[str]) -> bool:
        """
        Save clips to a specified file.

        Args:
            file_path: Path where to save the clips
            clips: List of clip dictionaries with 'name', 'start', 'end' keys
            video_path: Path to the video file (can be None)
            output_path: Path to the output directory (can be None)

        Returns:
            True if save was successful, False otherwise
        """
        try:
            data = self._create_save_data(clips, video_path, output_path)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(clips)} clips to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save clips to {file_path}: {e}", exc_info=True)
            return False

    def load_from_file(self, file_path: str) -> Optional[Dict]:
        """
        Load clips from a specified file.

        Args:
            file_path: Path to the file to load

        Returns:
            Dictionary with 'clips', 'video_path', 'output_directory', 'timestamp' keys,
            or None if load failed
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not self.validate_data(data):
                logger.error(f"Invalid data format in {file_path}")
                return None

            logger.info(f"Loaded {len(data.get('clips', []))} clips from {file_path}")
            return data

        except Exception as e:
            logger.error(f"Failed to load clips from {file_path}: {e}", exc_info=True)
            return None

    def save_recovery(self, clips: List[Dict], video_path: Optional[str],
                      output_path: Optional[str]) -> bool:
        """
        Auto-save current state to recovery file.

        Args:
            clips: List of clip dictionaries
            video_path: Path to the video file (can be None)
            output_path: Path to the output directory (can be None)

        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Don't save empty recovery files
            if not clips and not video_path:
                return True

            return self.save_to_file(self.recovery_file, clips, video_path, output_path)

        except Exception as e:
            logger.error(f"Failed to save recovery: {e}", exc_info=True)
            return False

    def load_recovery(self) -> Optional[Dict]:
        """
        Load the recovery file if it exists.

        Returns:
            Dictionary with recovery data, or None if no valid recovery exists
        """
        try:
            if not self.has_recovery():
                return None

            return self.load_from_file(self.recovery_file)

        except Exception as e:
            logger.error(f"Failed to load recovery: {e}", exc_info=True)
            return None

    def clear_recovery(self) -> bool:
        """
        Delete the recovery file.

        Returns:
            True if successful or file doesn't exist, False on error
        """
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
                logger.info("Recovery file cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear recovery file: {e}", exc_info=True)
            return False

    def has_recovery(self) -> bool:
        """
        Check if a valid recovery file exists.

        Returns:
            True if recovery file exists and is valid, False otherwise
        """
        try:
            if not os.path.exists(self.recovery_file):
                return False

            # Quick validation - try to load and check format
            with open(self.recovery_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self.validate_data(data)

        except Exception as e:
            logger.warning(f"Recovery file exists but is invalid: {e}")
            return False

    def validate_data(self, data: Dict) -> bool:
        """
        Validate that loaded data has the required structure.

        Args:
            data: Dictionary to validate

        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required top-level keys
            if not isinstance(data, dict):
                return False

            if 'version' not in data or 'clips' not in data:
                return False

            # Validate clips array
            clips = data['clips']
            if not isinstance(clips, list):
                return False

            # Validate each clip has required fields
            for clip in clips:
                if not isinstance(clip, dict):
                    return False
                if not all(key in clip for key in ['name', 'start', 'end']):
                    return False

            return True

        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False

    def _create_save_data(self, clips: List[Dict], video_path: Optional[str],
                          output_path: Optional[str]) -> Dict:
        """
        Create the data structure to save.

        Args:
            clips: List of clip dictionaries
            video_path: Path to video file
            output_path: Path to output directory

        Returns:
            Dictionary with all save data
        """
        # Only include basic clip info (name, start, end)
        simplified_clips = [
            {
                'name': clip['name'],
                'start': clip['start'],
                'end': clip['end']
            }
            for clip in clips
        ]

        return {
            'version': self.FILE_VERSION,
            'video_path': video_path,
            'output_directory': output_path,
            'timestamp': datetime.now().isoformat(),
            'clips': simplified_clips
        }
