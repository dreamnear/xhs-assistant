# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller简化配置 - 单文件版本
小红书数据抓取工具
"""

block_cipher = None

a = Analysis(
    ['main_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'playwright',
        'playwright.async_api',
        'playwright.sync_api',
        'pandas',
        'openpyxl',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'dotenv',
        'pathlib',
        'asyncio',
        'logging',
        'datetime',
        'typing',
        'json',
        'csv',
        'collections',
        'abc',
        're',
        'os',
        'sys',
        'time',
        'copy',
        'configparser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pytest',
        'setuptools',
        'pip',
        'unittest',
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
    name='小红书数据抓取工具',
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
