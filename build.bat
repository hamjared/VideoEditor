@echo off
REM Build script for Video Editor executable
REM This will create a standalone .exe file in the dist folder

echo ========================================
echo Video Editor - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed!
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...
echo This may take a few minutes...
echo.

pyinstaller build.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo ========================================
echo.
echo The executable has been created at:
echo   dist\VideoEditor.exe
echo.
echo You can copy this .exe file to any Windows computer
echo and run it without installing Python or dependencies.
echo.
echo IMPORTANT: FFmpeg must still be installed on the target system!
echo.
pause
