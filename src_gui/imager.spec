# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the project root directory
project_root = os.path.abspath('..')
src_dir = os.path.join(project_root, 'src')
build_dir = os.path.abspath('.')

# Collect all selenium and webdriver-manager data
datas = []
datas += collect_data_files('selenium')
datas += collect_data_files('webdriver_manager')

# Add the user_agent.json file
datas += [(os.path.join(src_dir, 'user_agent.json'), '.')]

# Collect all submodules
hiddenimports = []
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('webdriver_manager')
hiddenimports += collect_submodules('PIL')
hiddenimports += ['requests', 'urllib3', 'certifi', 'tkinter']

a = Analysis(
    [os.path.join(build_dir, 'main_gui.py')],
    pathex=[src_dir, build_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Imager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here if you have one
)
