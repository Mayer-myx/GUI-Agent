# -*- mode: python ; coding: utf-8 -*-
# PyInstaller配置文件 - GUI Agent Web版本

block_cipher = None

a = Analysis(
    ['web_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('gui_operator', 'gui_operator'),
        ('core', 'core'),
    ],
    hiddenimports=[
        'flask',
        'flask_socketio',
        'socketio',
        'engineio',
        'engineio.async_drivers.threading',
        'openai',
        'langgraph',
        'langgraph.graph',
        'pyautogui',
        'mss',
        'pyperclip',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'tkinter',
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
    name='GUI-Agent-Web',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台以查看Flask日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
