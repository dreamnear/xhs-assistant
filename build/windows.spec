# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 小红书数据抓取工具
用于打包Windows可执行文件
"""

block_cipher = None

a = Analysis(
    ['main_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含配置文件
        ('.env.example', '.'),

        # 包含config.py
        ('config.py', '.'),

        # 包含所有模块
        ('core', 'core'),
        ('modules', 'modules'),
        ('gui', 'gui'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        # Playwright相关
        'playwright',
        'playwright.async_api',
        'playwright.sync_api',
        'playwright._impl._api_types',

        # 数据处理
        'pandas',
        'openpyxl',
        'csv',
        'json',

        # GUI相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',

        # 其他依赖
        'dotenv',
        'pathlib',
        'asyncio',
        'logging',
        'datetime',
        'typing',
        'abc',
        'collections',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'numpy',
        'scipy',
        'pytest',
        'setuptools',
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
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加icon文件路径
)
