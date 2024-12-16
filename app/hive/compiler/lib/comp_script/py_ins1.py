#!name##PyInstall
#!types##comp_script
#!info##Compilation script
#!Compiler##WinePyInst



block_cipher = None

a = Analysis(
    ["{{_WORM_NAME}}"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes={{EXCLUDE_MODS}},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # Dodaj binaria
    a.zipfiles,
    a.datas,          # Dodaj dane
    [],
    name='{{EXE_NAME}}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={{UPX}},
    console={{CONSOLE}},    # Ustaw na True, jeśli aplikacja konsolowa
    icon="{{ICON}}",
    exclude_binaries=False  # Ważne dla jednoplikowego exe
)