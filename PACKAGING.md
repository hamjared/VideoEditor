# Packaging the Video Editor as an Executable

This guide explains how to create a standalone executable file that can be run on any system without installing Python or dependencies.

## Prerequisites

1. Install all dependencies including PyInstaller:
```bash
pip install -r requirements.txt
```

2. Make sure the application runs correctly before packaging:
```bash
python main.py
```

## Building the Executable

### Windows

Simply run the build script:
```bash
build.bat
```

Or manually:
```bash
pyinstaller build.spec
```

The executable will be created at: `dist\VideoEditor.exe`

### Linux/Mac

Make the build script executable and run it:
```bash
chmod +x build.sh
./build.sh
```

Or manually:
```bash
pyinstaller build.spec
```

The executable will be created at: `dist/VideoEditor`

## Build Output

After building, you'll find:
- `dist/VideoEditor.exe` (Windows) or `dist/VideoEditor` (Linux/Mac) - The standalone executable
- `build/` - Temporary build files (can be deleted)

## Distribution

### What to Distribute

**The Easy Way:**
- Just distribute the single `.exe` file from the `dist/` folder
- This file contains everything except FFmpeg

**What Users Need:**
- The executable file
- FFmpeg installed on their system

### FFmpeg Requirement

The executable still requires FFmpeg to be installed on the target system because:
- FFmpeg is a large external program (not a Python library)
- Including FFmpeg would make the .exe much larger
- MoviePy uses FFmpeg as a separate process

### Installing FFmpeg (for end users)

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Or use: `choco install ffmpeg` (if Chocolatey is installed)

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## Bundle FFmpeg with Your Application (Optional)

If you want to include FFmpeg and make it truly portable:

### Option 1: Include FFmpeg Binary

1. Download FFmpeg for your platform
2. Place the `ffmpeg.exe` (Windows) or `ffmpeg` binary in the same folder as your .exe
3. Modify `video_editor.py` to use the local FFmpeg:

```python
import os
import imageio_ffmpeg

# In VideoEditor.__init__:
ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
if os.path.exists(ffmpeg_path):
    os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
```

4. Rebuild with PyInstaller

This creates a portable package but increases the distribution size significantly.

### Option 2: Use imageio-ffmpeg (Embedded)

ImageIO can download FFmpeg automatically:
```bash
pip install imageio-ffmpeg
```

This is already included in MoviePy dependencies, but you can ensure it downloads FFmpeg on first run.

## Customization

### Add an Icon

1. Create or download an `.ico` file (Windows) or `.icns` file (Mac)
2. Update `build.spec`:
```python
icon='path/to/your/icon.ico'
```
3. Rebuild

### Reduce File Size

The current configuration uses UPX compression. To disable:
```python
upx=False,  # in build.spec
```

### Show/Hide Console Window

Edit `build.spec`:
```python
console=True,   # Show console (useful for debugging)
console=False,  # Hide console (cleaner for end users)
```

## Troubleshooting

### Build Fails

1. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Try cleaning and rebuilding:
```bash
# Windows
rmdir /s /q build dist
build.bat

# Linux/Mac
rm -rf build dist
./build.sh
```

### Executable Doesn't Run

1. Check if antivirus is blocking it (common with PyInstaller executables)
2. Run from command line to see error messages:
```bash
# Windows
dist\VideoEditor.exe

# Linux/Mac
./dist/VideoEditor
```

### "FFmpeg not found" Error

1. Ensure FFmpeg is installed on the target system
2. Or bundle FFmpeg with your application (see above)

### Large File Size

The executable will be 100-200 MB because it includes:
- Python interpreter
- PyQt5 libraries
- MoviePy and dependencies
- NumPy

This is normal for PyInstaller applications.

## Testing

After building, test the executable on a clean system or VM to ensure:
1. The .exe runs without Python installed
2. All features work correctly
3. FFmpeg is properly detected

## Notes

- The executable is platform-specific (Windows .exe won't run on Mac/Linux)
- Build on the target platform or use separate builds for each platform
- First run may be slower as it extracts temporary files
- The executable creates a temporary folder on each run (cleaned up automatically)

## Advanced: Multi-Platform Builds

To create executables for multiple platforms, you need to build on each platform:

1. **Windows**: Build on Windows → creates `.exe`
2. **Mac**: Build on Mac → creates Mac application
3. **Linux**: Build on Linux → creates Linux binary

You cannot cross-compile (e.g., build Windows .exe on Mac).
