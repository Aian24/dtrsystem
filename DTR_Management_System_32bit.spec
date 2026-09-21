# -*- mode: python ; coding: utf-8 -*-
import os
import glob
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets'), ('manual.html', '.')]
binaries = []
hiddenimports = ['charset_normalizer', 'zk', 'zk.base', 'zk.user', 'zk.finger', 'zk.attendance', 'future']

# Collect dependencies
for pkg in ['nicegui', 'webview', 'numpy', 'pandas', 'sqlalchemy', 'reportlab', 'openpyxl', 'bcrypt', 'zk', 'future']:
    try:
        t_datas, t_binaries, t_hidden = collect_all(pkg)
        datas += t_datas
        binaries += t_binaries
        hiddenimports += t_hidden
    except Exception:
        pass

# Add all site-packages DLLs directly to root
sp_dlls = [
    r'C:\Python38-32\lib\site-packages\numpy\.libs\libopenblas_v0.3.21-gcc_8_3_0.dll',
    r'C:\Python38-32\lib\site-packages\clr_loader\ffi\dlls\x86\ClrLoader.dll',
    r'C:\Python38-32\lib\site-packages\pythonnet\runtime\Python.Runtime.dll',
    r'C:\Python38-32\lib\site-packages\webview\lib\WebBrowserInterop.x86.dll',
    r'C:\Python38-32\lib\site-packages\webview\lib\runtimes\win-x86\native\WebView2Loader.dll',
]
for p in sp_dlls:
    if os.path.exists(p):
        binaries.append((p, '.'))

# Add MSVC 32-bit runtime DLLs from SysWOW64
syswow_dlls = [
    'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll',
    'msvcp140_atomic_wait.dll', 'msvcp140_codecvt_ids.dll',
    'vcruntime140.dll', 'vcruntime140_threads.dll',
    'concrt140.dll', 'vcomp140.dll'
]
for dll in syswow_dlls:
    src = os.path.join(r'C:\Windows\SysWOW64', dll)
    if os.path.exists(src):
        binaries.append((src, '.'))

# Add Universal CRT downlevel DLLs (api-ms-win-crt-*.dll and ucrtbase.dll)
for ucrt_dll in glob.glob(r'C:\Windows\SysWOW64\downlevel\*.dll'):
    binaries.append((ucrt_dll, '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rthook_orjson_shim.py'],
    excludes=['orjson', 'setuptools', 'pkg_resources', 'distutils', 'watchfiles', '_rust_notify', 'nicegui.testing', 'pytest', 'unittest', 'tkinter.test'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DTR_Management_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)

exe_debug = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DTR_Management_System_Debug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)

coll = COLLECT(
    exe,
    exe_debug,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DTR_Management_System_32bit',
)
