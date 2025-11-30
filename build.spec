# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Video Editor
This configures how the application is packaged into an executable
"""

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = None

# Collect metadata for packages that need it
datas = []
datas += copy_metadata('imageio')
datas += copy_metadata('imageio-ffmpeg')
datas += copy_metadata('moviepy')
datas += collect_data_files('imageio')
datas += collect_data_files('imageio_ffmpeg')

# Collect VLC DLLs as binaries (not data files)
import os
import glob

binaries = []
vlc_path = os.path.join(os.getcwd(), 'bin', 'win32', 'vlc')
if os.path.exists(vlc_path):
    # Add all DLL files from VLC directory
    for dll in glob.glob(os.path.join(vlc_path, '*.dll')):
        binaries.append((dll, 'bin/win32/vlc'))

    # Add VLC plugins directory (as data files since they're loaded dynamically)
    datas += [(os.path.join(vlc_path, 'plugins'), 'bin/win32/vlc/plugins')]

    # Add other VLC directories
    for subdir in ['locale', 'lua', 'hrtfs']:
        subdir_path = os.path.join(vlc_path, subdir)
        if os.path.exists(subdir_path):
            datas += [(subdir_path, f'bin/win32/vlc/{subdir}')]

# Include bundled executables (ffmpeg, ffplay)
ffmpeg_path = os.path.join(os.getcwd(), 'bin', 'win32')
if os.path.exists(ffmpeg_path):
    for exe in ['ffmpeg.exe', 'ffplay.exe']:
        exe_path = os.path.join(ffmpeg_path, exe)
        if os.path.exists(exe_path):
            binaries.append((exe_path, 'bin/win32'))

    # Add ffmpeg DLLs
    for dll in glob.glob(os.path.join(ffmpeg_path, '*.dll')):
        binaries.append((dll, 'bin/win32'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'moviepy',
        'moviepy.video.io.VideoFileClip',
        'moviepy.Clip',
        'moviepy.video.VideoClip',
        'numpy',
        'imageio',
        'imageio_ffmpeg',
        'imageio.plugins',
        'imageio.core',
        'proglog',
        'decorator',
        'pandas',
        'openpyxl',
        'openpyxl.cell._writer',
        'vlc',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create splash screen object
splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(200, 170),  # Position for "Loading..." text (x, y from top-left)
    text_size=10,
    text_color='white',
    text_default='Loading...',
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,  # Add splash to exe
    splash.binaries,  # Add splash binaries
    [],
    name='VideoEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
