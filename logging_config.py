"""
Logging Configuration for Video Editor
Handles logging setup for both development and frozen executable modes.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the application.

    In frozen mode (exe): Logs only to file
    In development mode: Logs to both file and console

    Args:
        log_level: Logging level (default: logging.INFO)
    """
    # Determine if running as frozen executable
    is_frozen = getattr(sys, 'frozen', False)

    # Determine log file location
    if is_frozen:
        # For frozen exe, put logs in user-writable location
        log_file = 'video_editor.log'
    else:
        # For development, use dev log file
        log_file = 'video_editor_dev.log'

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create handlers
    handlers = []

    # File handler with rotation (max 10MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    handlers.append(file_handler)

    # Console handler (only in development mode)
    if not is_frozen and sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter)
        console_handler.setLevel(log_level)
        handlers.append(console_handler)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Set up exception hook to log uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Video Editor Starting")
    logger.info(f"Running as frozen executable: {is_frozen}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Log file: {os.path.abspath(log_file)}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info("=" * 70)


def get_log_file_path():
    """
    Get the path to the current log file.

    Returns:
        Absolute path to the log file
    """
    is_frozen = getattr(sys, 'frozen', False)
    log_file = 'video_editor.log' if is_frozen else 'video_editor_dev.log'
    return os.path.abspath(log_file)


def set_module_log_level(module_name, level):
    """
    Set the log level for a specific module.

    Args:
        module_name: Name of the module (e.g., 'video_player.vlc_media_player')
        level: Logging level (e.g., logging.DEBUG)
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(level)


# Convenience function for getting a logger
def get_logger(name):
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
