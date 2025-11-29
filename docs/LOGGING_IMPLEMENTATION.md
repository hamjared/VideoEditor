# Logging Implementation Guide

This document describes the logging system implemented in the Video Editor application.

## Overview

The application now uses Python's built-in `logging` module instead of print statements. This provides:
- **Frozen executable compatibility** - Logs to files instead of stdout (which is None in frozen GUI apps)
- **Different log levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Automatic log rotation** - Old logs are automatically archived
- **GUI log viewer** - View logs without leaving the application
- **Uncaught exception logging** - All crashes are logged automatically

## Quick Start

### Viewing Logs

**In the GUI:**
1. Go to `View -> Show Logs` in the menu bar
2. Click "Auto-refresh" to see logs update in real-time
3. Click "Open in Editor" to view in your text editor

**Log File Locations:**
- Development mode: `video_editor_dev.log`
- Frozen executable: `video_editor.log`

### Adding Logging to Your Code

```python
import logging

# At the top of each file
logger = logging.getLogger(__name__)

# Use instead of print()
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# Log with exception traceback
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

## Architecture

### Files

**`logging_config.py`** - Logging setup and configuration
- `setup_logging()` - Initialize logging (called in main.py)
- `get_log_file_path()` - Get current log file path
- `set_module_log_level()` - Adjust log level for specific modules

**`log_viewer.py`** - GUI log viewer dialog
- View logs in the application
- Auto-refresh capability
- Clear logs
- Open in external editor

**Modified Files:**
- `main.py` - Initializes logging, replaced print statements
- `gui.py` - Added menu bar and log viewer integration
- `video_player/vlc_media_player.py` - Replaced print statements
- `video_player/media_player_factory.py` - Replaced print statements

### Log Levels

**DEBUG** - Detailed information for debugging
```python
logger.debug(f"Seeked to {timestamp} ({ms}ms)")
```

**INFO** - General informational messages
```python
logger.info(f"Video loaded successfully: {video_path}")
```

**WARNING** - Warning messages (something unexpected but handled)
```python
logger.warning(f"Bundled VLC not found, using system VLC")
```

**ERROR** - Error messages (something failed but app continues)
```python
logger.error(f"Failed to load video: {e}", exc_info=True)
```

**CRITICAL** - Critical errors (app may crash)
```python
logger.critical("Uncaught exception", exc_info=(...))
```

## Configuration

### Changing Log Level

Edit `main.py`:
```python
# For more verbose logging during development
setup_logging(log_level=logging.DEBUG)

# For production (less verbose)
setup_logging(log_level=logging.INFO)
```

### Per-Module Log Levels

```python
from logging_config import set_module_log_level
import logging

# Make VLC player more verbose
set_module_log_level('video_player.vlc_media_player', logging.DEBUG)

# Make video editor less verbose
set_module_log_level('video_editor', logging.WARNING)
```

### Log File Rotation

Logs automatically rotate when they reach 10MB:
- Current log: `video_editor.log`
- Archived logs: `video_editor.log.1`, `video_editor.log.2`, `video_editor.log.3`
- Keeps last 3 archived logs

Configured in `logging_config.py`:
```python
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=3,               # Keep 3 backups
    encoding='utf-8'
)
```

## Features

### 1. Automatic Exception Logging

All uncaught exceptions are automatically logged:
```python
# In logging_config.py
def handle_exception(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception", exc_info=(...))

sys.excepthook = handle_exception
```

### 2. Frozen Executable Detection

Logging adapts based on whether running as script or frozen exe:
```python
if getattr(sys, 'frozen', False):
    # Frozen: Log only to file
    handlers = [file_handler]
else:
    # Development: Log to both file and console
    handlers = [file_handler, console_handler]
```

### 3. GUI Log Viewer

Access via `View -> Show Logs`:
- **Refresh** - Reload log file
- **Auto-refresh** - Automatically update every 2 seconds
- **Clear Logs** - Clear the log file
- **Open in Editor** - Open log in default text editor
- Automatically scrolls to bottom for new entries

### 4. Status Bar Integration

Important messages are shown in both:
- Log file (for debugging)
- Status bar (for user feedback)

Example from gui.py:
```python
logger.info(f"Video loaded successfully: {video_path}")
self.statusBar().showMessage(f"Video loaded: {filename}")
```

## Best Practices

### DO:
✅ Use logging instead of print statements
✅ Use appropriate log levels (DEBUG for details, INFO for general, ERROR for errors)
✅ Include exception info with `exc_info=True` for errors
✅ Use `logger = logging.getLogger(__name__)` in each file
✅ Show important messages in GUI status bar AND log them

### DON'T:
❌ Don't use print() - it crashes in frozen GUI apps
❌ Don't log passwords or sensitive data
❌ Don't use DEBUG level in production (too verbose)
❌ Don't forget to log errors - they're critical for debugging

## Troubleshooting

### "Log file not found"

The log file is created on first log message. If you see this error, try:
1. Run the application
2. Trigger any action (load video, etc.)
3. Refresh the log viewer

### "Error reading log file"

Check file permissions. The log file should be writable by the application.

### Logs not appearing in frozen executable

Make sure:
1. Logging is initialized in main.py before any other imports
2. No print statements (they crash when stdout is None)
3. Log file is in a writable location

### Too many logs

Reduce log level:
```python
setup_logging(log_level=logging.WARNING)  # Only warnings and errors
```

## Examples

### Example 1: Logging in a new module

```python
import logging

logger = logging.getLogger(__name__)

class MyProcessor:
    def process(self, data):
        logger.info("Starting data processing")

        try:
            result = self._do_work(data)
            logger.debug(f"Processing complete, result: {result}")
            return result
        except ValueError as e:
            logger.error(f"Invalid data: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error in processing", exc_info=True)
            raise
```

### Example 2: Conditional logging

```python
import logging

logger = logging.getLogger(__name__)

def expensive_operation():
    # Only compute if DEBUG logging is enabled
    if logger.isEnabledFor(logging.DEBUG):
        debug_info = compute_expensive_debug_info()
        logger.debug(f"Debug info: {debug_info}")

    # This always runs
    logger.info("Operation complete")
```

### Example 3: Logging with context

```python
import logging

logger = logging.getLogger(__name__)

def export_clip(clip_name, output_path):
    logger.info(f"Exporting clip '{clip_name}' to {output_path}")

    try:
        # ... export code ...
        logger.info(f"Successfully exported '{clip_name}'")
    except IOError as e:
        logger.error(f"Failed to write '{clip_name}' to {output_path}: {e}")
        raise
```

## Summary

The logging system is now:
- ✅ Working in frozen executables (no stdout crashes)
- ✅ Accessible via GUI (View -> Show Logs)
- ✅ Automatically capturing all errors
- ✅ Rotating log files to save disk space
- ✅ Supporting different log levels for development vs production

All print statements have been replaced with appropriate logging calls.
