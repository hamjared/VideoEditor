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

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
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
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)
