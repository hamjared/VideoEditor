# Testing Strategy for Frozen Executables

This document explains how to test for issues that only appear in PyInstaller-built executables.

## The Problem

When you build an executable with PyInstaller (`console=False` for GUI apps):
- `sys.stdout`, `sys.stderr`, and `sys.stdin` are all `None`
- Any code that tries to `print()` or access these streams will crash with `AttributeError: 'NoneType' object has no attribute 'write'` or similar
- This doesn't happen when running as a Python script, so regular testing won't catch it

## Solution: Multi-Layer Testing

### 1. Pre-Build Static Analysis

Run before every build:
```bash
python pre_build_check.py
```

This script:
- Scans all Python files for common frozen-exe issues
- Warns about `print()` statements
- Warns about direct `sys.stdout`/`sys.stderr` access
- Warns about subprocess calls without explicit stdout/stderr
- Runs frozen compatibility unit tests (if available)

### 2. Frozen Environment Unit Tests

Create: `tests/test_frozen_compatibility.py`

These tests simulate the frozen environment:
```python
# Simulate frozen GUI app environment
sys.frozen = True
sys._MEIPASS = '/tmp/test'
sys.stdout = None
sys.stderr = None
sys.stdin = None

# Test your code runs without accessing None streams
```

Run with:
```bash
python -m pytest tests/test_frozen_compatibility.py -v
```

### 3. Build and Smoke Test (CI/CD)

In `.github/workflows/test-frozen-build.yml`:
- Build the executable
- Test it starts without crashing
- Check file size is reasonable
- Upload as artifact for manual testing

### 4. Manual Testing Checklist

Before every release, manually test the **actual executable**:

- [ ] Application starts without errors
- [ ] Can load a video file
- [ ] Can create clips
- [ ] Can export clips (tests FFmpeg subprocess)
- [ ] Can play video (tests VLC integration)
- [ ] Check log files for hidden errors
- [ ] Test on clean Windows VM (checks missing dependencies)

## Quick Reference

### Before Building

```bash
# 1. Run pre-build checks
python pre_build_check.py

# 2. If checks pass, build
pyinstaller build.spec

# 3. Test the exe manually
# (Run through manual checklist above)
```

### Fixing Common Issues

**Issue: print() statements**
```python
# Before (will crash in frozen GUI)
print("Status:", status)

# After (use logging)
import logging
logging.info(f"Status: {status}")
```

**Issue: Direct stdout access**
```python
# Before (will crash)
sys.stdout.write("Message\n")

# After (check first)
if sys.stdout is not None:
    sys.stdout.write("Message\n")
```

**Issue: Third-party library outputs**
```python
# Before (library tries to print)
some_library.process()

# After (suppress output)
class SilentLogger(ProgressBarLogger):
    def __init__(self):
        super().__init__()
        self.print_messages = False  # Key line!

library.process(logger=SilentLogger())
```

**Issue: subprocess without stdout/stderr**
```python
# Before (inherits None stdout)
subprocess.run(['ffmpeg', '-version'])

# After (explicit output handling)
subprocess.run(
    ['ffmpeg', '-version'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
```

## Documentation

See these files for more details:
- `docs/FROZEN_EXECUTABLE_GUIDE.md` - Comprehensive guide with all patterns
- `tests/test_frozen_compatibility.py` - Example tests
- `pre_build_check.py` - Static analysis tool

## Integration with Development Workflow

### Recommended Workflow

1. **Write code** as normal
2. **Run pre-build check** before committing:
   ```bash
   python pre_build_check.py
   ```
3. **Fix any warnings** (especially new ones you introduced)
4. **Commit** your changes
5. **CI/CD** automatically:
   - Runs frozen compatibility tests
   - Builds executable
   - Runs smoke tests
6. **Manual test** executable before release

### Git Hooks (Optional)

You can add a pre-commit hook:

`.git/hooks/pre-commit`:
```bash
#!/bin/bash
python pre_build_check.py
if [ $? -ne 0 ]; then
    echo "Pre-build checks failed. Fix issues before committing."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Why This Matters

Without these tests, you'll only discover issues **after**:
- Building the executable
- Distributing to users
- Users try to use the feature

This leads to:
- Frustrated users
- Emergency patches
- Loss of trust

With these tests, you catch issues:
- Before building
- In CI/CD
- Before users see them

## Summary

**The key insight:** PyInstaller frozen executables have a fundamentally different runtime environment. You must test in that environment, not just as a regular Python script.

**The solution:** Simulate the frozen environment in unit tests, use static analysis to catch common patterns, and always manually test the actual executable before release.
