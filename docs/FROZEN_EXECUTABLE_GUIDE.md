# PyInstaller Frozen Executable - Best Practices Guide

This guide helps avoid common issues when building frozen executables with PyInstaller.

## Common Issues in Frozen Executables

### 1. **sys.stdout/stderr/stdin is None**

**Problem:** In GUI applications frozen with PyInstaller (console=False), the standard streams are None.

**Solution:**
```python
# BAD: Will crash in frozen GUI app
print("Hello")  # AttributeError: 'NoneType' object has no attribute 'write'

# GOOD: Check before using
if sys.stdout is not None:
    print("Hello")

# BETTER: Use logging instead
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
logging.info("Hello")
```

**For third-party libraries:**
```python
# If a library uses print() or stdout, wrap it
class SilentLogger(ProgressBarLogger):
    def __init__(self):
        super().__init__()
        self.print_messages = False  # Prevent stdout access

    def bars_callback(self, bar, attr, value, old_value=None):
        pass  # Suppress output
```

### 2. **File Path Detection**

**Problem:** `__file__` and working directory behave differently in frozen apps.

**Solution:**
```python
import sys
import os

# Detect if running as frozen executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = sys._MEIPASS
else:
    # Running as script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Use app_dir for bundled resources
resource_path = os.path.join(app_dir, 'bin', 'win32', 'vlc')
```

### 3. **Subprocess Calls**

**Problem:** subprocess may fail if stdout/stderr not specified.

**Solution:**
```python
import subprocess

# BAD: Inherits None stdout in frozen GUI
result = subprocess.run(['ffmpeg', '-version'])

# GOOD: Explicitly specify
result = subprocess.run(
    ['ffmpeg', '-version'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
```

### 4. **Dynamic Imports**

**Problem:** PyInstaller can't detect dynamically imported modules.

**Solution:**
```python
# BAD: PyInstaller won't include 'optional_module'
module = __import__('optional_module')

# GOOD: Add to hiddenimports in .spec file
# Or import normally at top of file even if conditional
import optional_module  # PyInstaller will detect this
```

### 5. **Logging Configuration**

**Problem:** Default logging tries to write to stderr (which is None).

**Solution:**
```python
import logging
import sys

# BAD: Will fail in frozen GUI
logging.basicConfig(level=logging.INFO)

# GOOD: Use file handler
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# OR: Use NullHandler for libraries
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
```

## Testing Strategy

### 1. **Frozen Compatibility Unit Tests**

Run before every build:
```bash
python tests/test_frozen_compatibility.py
```

These tests simulate the frozen environment by:
- Setting `sys.frozen = True`
- Setting `sys.stdout = None`
- Setting `sys._MEIPASS` to a temp directory

### 2. **Build and Smoke Test**

Include in CI/CD:
```yaml
- name: Build and test executable
  run: |
    pyinstaller build.spec
    # Basic smoke tests
    ./dist/VideoEditor.exe --version
```

### 3. **Manual Testing Checklist**

Before release, manually test the executable:
- [ ] Application starts without errors
- [ ] Can load a video file
- [ ] Can create clips
- [ ] Can export clips (tests FFmpeg integration)
- [ ] Can play video (tests VLC integration)
- [ ] Check log file for errors
- [ ] Test with antivirus enabled (false positives common)

## Debugging Frozen Executable Issues

### 1. **Enable Console Output**

Temporarily set `console=True` in build.spec to see error messages:
```python
exe = EXE(
    ...
    console=True,  # Change to True for debugging
    ...
)
```

### 2. **Check Log Files**

Configure logging early in your app:
```python
# In main.py, before any other imports
import logging
logging.basicConfig(
    filename='video_editor_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log startup info
logging.info(f"Starting app, frozen={getattr(sys, 'frozen', False)}")
logging.info(f"sys.stdout={sys.stdout}")
logging.info(f"sys.stderr={sys.stderr}")
```

### 3. **Capture Unhandled Exceptions**

Add exception hook:
```python
import sys
import logging
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    """Log unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

sys.excepthook = handle_exception
```

### 4. **Test on Clean Machine**

Use a VM or clean Windows install to test:
- Missing DLL dependencies
- Missing Visual C++ redistributables
- Antivirus false positives

## Code Review Checklist

Before committing code, check:

- [ ] No bare `print()` statements (use logging or check `sys.stdout`)
- [ ] All subprocess calls specify `stdout=subprocess.PIPE`
- [ ] File paths use frozen-aware detection
- [ ] Third-party library output is suppressed or redirected
- [ ] Logging configured to use files, not stdout/stderr
- [ ] Exception handling covers frozen environment edge cases
- [ ] Frozen compatibility tests pass
- [ ] New dependencies added to `hiddenimports` in build.spec if needed

## Common Patterns

### Pattern: Safe Print Function
```python
def safe_print(*args, **kwargs):
    """Print only if stdout available."""
    if sys.stdout is not None:
        print(*args, **kwargs)
    else:
        # Optionally log instead
        import logging
        logging.info(' '.join(str(arg) for arg in args))
```

### Pattern: Logger Wrapper for Libraries
```python
class NullOutputLogger(ProgressBarLogger):
    """Logger that doesn't require stdout/stderr."""

    def __init__(self):
        super().__init__()
        self.print_messages = False

    def bars_callback(self, bar, attr, value, old_value=None):
        pass

    def callback(self, **changes):
        pass
```

### Pattern: Resource Path Helper
```python
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and frozen."""
    if getattr(sys, 'frozen', False'):
        # Running as frozen executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# Usage
vlc_path = get_resource_path('bin/win32/vlc')
```

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Runtime Information](https://pyinstaller.org/en/stable/runtime-information.html)
- [Common Issues and Workarounds](https://github.com/pyinstaller/pyinstaller/wiki)

## Summary

The key to avoiding frozen executable issues:

1. **Never assume stdout/stderr exists** - use logging to files
2. **Test in frozen environment** - use the compatibility test suite
3. **Build and test regularly** - don't wait until release
4. **Log everything** - especially during startup and external library calls
5. **Use explicit paths** - detect frozen mode and adjust accordingly
