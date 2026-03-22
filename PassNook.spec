# -*- mode: python ; coding: utf-8 -*-
# Build: C:\Python313\python.exe -m PyInstaller PassNook.spec --noconfirm

import subprocess, sys
_CTK_PATH = subprocess.check_output(
    [sys.executable, "-c",
     "import customtkinter; print(customtkinter.__path__[0])"],
    text=True).strip()

a = Analysis(
    ['passnook.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (_CTK_PATH, 'customtkinter'),
    ],
    hiddenimports=[
        'customtkinter',
        'pystray',
        'PIL',
        'PIL._tkinter_finder',
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PassNook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version=None,
    uac_admin=False,
)
