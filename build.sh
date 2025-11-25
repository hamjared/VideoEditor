#!/bin/bash
# Build script for Video Editor executable (Linux/Mac)
# This will create a standalone executable in the dist folder

echo "========================================"
echo "Video Editor - Build Script"
echo "========================================"
echo ""

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller is not installed!"
    echo "Please run: pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "Cleaning previous builds..."
rm -rf build dist

echo ""
echo "Building executable..."
echo "This may take a few minutes..."
echo ""

pyinstaller build.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build successful!"
echo "========================================"
echo ""
echo "The executable has been created at:"
echo "  dist/VideoEditor"
echo ""
echo "You can copy this file to other systems"
echo "and run it without installing Python or dependencies."
echo ""
echo "IMPORTANT: FFmpeg must still be installed on the target system!"
echo ""
