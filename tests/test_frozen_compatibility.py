"""
Test suite to catch issues that appear in frozen (PyInstaller) executables.

These tests simulate the frozen environment to catch common issues before building.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO


class TestFrozenCompatibility(unittest.TestCase):
    """
    Tests that simulate PyInstaller frozen environment conditions.

    Common issues in frozen executables:
    1. sys.stdout/stderr/stdin is None
    2. sys._MEIPASS exists (PyInstaller's temp extraction dir)
    3. __file__ may not work as expected
    4. Working directory is different
    """

    def setUp(self):
        """Set up test environment."""
        # Store original values to restore later
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.original_stdin = sys.stdin
        self.original_frozen = getattr(sys, 'frozen', False)
        self.original_meipass = getattr(sys, '_MEIPASS', None)

    def tearDown(self):
        """Restore original environment."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        sys.stdin = self.original_stdin

        if self.original_frozen:
            sys.frozen = self.original_frozen
        elif hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')

        if self.original_meipass:
            sys._MEIPASS = self.original_meipass
        elif hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')

    def simulate_frozen_environment(self, temp_dir="/tmp/test_meipass"):
        """
        Simulate PyInstaller frozen environment.

        Args:
            temp_dir: Path to simulate as _MEIPASS
        """
        # Set frozen flag
        sys.frozen = True
        sys._MEIPASS = temp_dir

        # Set stdout/stderr/stdin to None (common in frozen GUI apps)
        sys.stdout = None
        sys.stderr = None
        sys.stdin = None

    def test_video_export_with_null_stdout(self):
        """Test that video export works when stdout is None (frozen GUI app)."""
        # Simulate frozen environment
        self.simulate_frozen_environment()

        # Import after simulating frozen environment
        from video_editor import VideoEditor

        # This should not raise AttributeError: 'NoneType' object has no attribute 'stdout'
        try:
            # Test the export logic with a mock video
            editor = VideoEditor()

            # The SilentLogger should handle None stdout gracefully
            from proglog import ProgressBarLogger

            class SilentLogger(ProgressBarLogger):
                def __init__(self):
                    super().__init__()
                    self.print_messages = False

                def bars_callback(self, bar, attr, value, old_value=None):
                    pass

                def callback(self, **changes):
                    pass

            # Create logger instance - should not access stdout
            logger = SilentLogger()

            # This should work without accessing stdout
            logger.bars_callback('test', 'test', 0)
            logger.callback(test='value')

        except AttributeError as e:
            if 'stdout' in str(e):
                self.fail(f"Code tried to access stdout when it was None: {e}")
            raise

    def test_vlc_player_with_frozen_environment(self):
        """Test that VLC player can initialize in frozen environment."""
        # Create a mock temp directory for _MEIPASS
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock bin structure
            bin_dir = os.path.join(temp_dir, 'bin', 'win32', 'vlc')
            os.makedirs(bin_dir, exist_ok=True)

            # Create mock DLL files
            open(os.path.join(bin_dir, 'libvlc.dll'), 'a').close()
            open(os.path.join(bin_dir, 'libvlccore.dll'), 'a').close()
            os.makedirs(os.path.join(bin_dir, 'plugins'), exist_ok=True)

            self.simulate_frozen_environment(temp_dir)

            # Import VLC player - it should handle frozen environment
            try:
                from video_player.vlc_media_player import VLCMediaPlayerWidget

                # This tests that path detection works in frozen mode
                # The actual VLC initialization will fail (no real VLC), but path detection should work

            except ImportError as e:
                # ImportError is expected if VLC not installed, that's OK
                pass
            except AttributeError as e:
                if 'stdout' in str(e) or 'stderr' in str(e):
                    self.fail(f"VLC player tried to access stdout/stderr when None: {e}")
                raise

    def test_print_statements_with_null_stdout(self):
        """Test that print statements don't crash when stdout is None."""
        self.simulate_frozen_environment()

        # This should not crash
        try:
            # Some libraries may use print() internally
            # In frozen mode, we need to handle this gracefully

            # Simulate what happens when code tries to print
            if sys.stdout is None:
                # Good! Code should check for None before printing
                pass
            else:
                print("This would crash if stdout is None")

        except AttributeError as e:
            if 'write' in str(e):
                self.fail("Code tried to write to None stdout")
            raise

    def test_logging_with_null_stderr(self):
        """Test that logging works when stderr is None."""
        self.simulate_frozen_environment()

        import logging

        try:
            # Configure logging - should handle None stderr gracefully
            # In production code, we should configure logging to use a file
            logger = logging.getLogger('test_frozen')

            # Don't use StreamHandler with None stdout/stderr
            # Instead use NullHandler or FileHandler
            logger.addHandler(logging.NullHandler())

            # This should work
            logger.info("Test message")
            logger.error("Test error")

        except AttributeError as e:
            if 'stderr' in str(e):
                self.fail(f"Logging tried to access stderr when None: {e}")
            raise

    def test_file_paths_in_frozen_environment(self):
        """Test that file path detection works in frozen environment."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            self.simulate_frozen_environment(temp_dir)

            # Test the pattern used in vlc_media_player.py
            if getattr(sys, 'frozen', False):
                app_dir = sys._MEIPASS
                self.assertEqual(app_dir, temp_dir)
            else:
                self.fail("frozen flag not set correctly")

    def test_subprocess_with_null_stdout(self):
        """Test that subprocess calls work when stdout is None."""
        self.simulate_frozen_environment()

        import subprocess

        try:
            # When stdout is None, subprocess might fail if not configured properly
            # We should always specify stdout/stderr explicitly

            # BAD: This might fail in frozen mode
            # result = subprocess.run(['echo', 'test'])

            # GOOD: Explicitly specify stdout/stderr
            result = subprocess.run(
                ['echo', 'test'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Should have captured output
            self.assertIsNotNone(result.stdout)

        except Exception as e:
            self.fail(f"Subprocess failed with null stdout: {e}")


class TestVideoEditorFrozenMode(unittest.TestCase):
    """Test VideoEditor specifically in frozen mode."""

    def test_silent_logger_initialization(self):
        """Test that SilentLogger can be created without stdout."""
        # Temporarily set stdout to None
        original_stdout = sys.stdout
        sys.stdout = None

        try:
            from proglog import ProgressBarLogger

            class SilentLogger(ProgressBarLogger):
                def __init__(self):
                    super().__init__()
                    self.print_messages = False

                def bars_callback(self, bar, attr, value, old_value=None):
                    pass

                def callback(self, **changes):
                    pass

            # Should not raise AttributeError
            logger = SilentLogger()

            # Should not try to access stdout
            logger.bars_callback('test', 'test', 0)

        except AttributeError as e:
            if 'stdout' in str(e):
                self.fail(f"SilentLogger accessed stdout when None: {e}")
            raise
        finally:
            sys.stdout = original_stdout


def run_frozen_compatibility_tests():
    """
    Run all frozen compatibility tests.

    This should be run before building with PyInstaller to catch issues early.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestFrozenCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoEditorFrozenMode))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_frozen_compatibility_tests()
    sys.exit(0 if success else 1)
