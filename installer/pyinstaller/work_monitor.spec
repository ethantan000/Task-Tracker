# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification for Task-Tracker Work Monitor
Bundles the monitoring application into a standalone Windows executable.
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all dependencies
hiddenimports = [
    'PIL',
    'PIL._imagingtk',
    'PIL._tkinter_finder',
    'pystray',
    'pystray._win32',
    'psutil',
    'email_reports',
    'overlay_widget',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'json',
    'base64',
    'hashlib',
    'threading',
    'logging',
    'pathlib',
]

# Collect data files
datas = [
    ('../../WorkMonitor/icon.ico', '.'),
    ('../../WorkMonitor/src/email_reports.py', '.'),
    ('../../WorkMonitor/src/overlay_widget.py', '.'),
]

a = Analysis(
    ['../../WorkMonitor/src/work_monitor.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pytest',
    ],
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
    name='TaskTrackerMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../WorkMonitor/icon.ico',
    version_file='version_monitor.txt',
)
