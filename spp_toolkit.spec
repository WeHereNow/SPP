# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['spp_toolkit_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'pylogix',
        'docx',
        'concurrent.futures',
        'threading',
        'queue',
        'dataclasses',
        'datetime',
        'csv',
        'json',
        'hashlib',
        'socket',
        'ipaddress',
        're',
        'pathlib',
        'atexit'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'reportlab',
        'cryptography',
        'pytest',
        'black',
        'flake8',
        'mypy'
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
    [],
    exclude_binaries=True,
    name='SPP_Toolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SPP_Toolkit',
)
