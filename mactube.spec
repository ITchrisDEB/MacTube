# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mactube.py'],
    pathex=[],
    binaries=[
        ('ffmpeg_binary', '.'),
    ],
    datas=[
        ('mactube.icns', '.'),
        ('mactube.jpeg', '.'),
    ],
    hiddenimports=[
        'yt_dlp',
        'customtkinter',
        'darkdetect',
        'packaging',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'future',
        'json',
        'pathlib',
        'os',
        'io',
        'time',
        'datetime',
        'queue',
        'threading',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'ffmpeg',  # Exclure le module Python ffmpeg pour éviter les conflits
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
    name='MacTube',
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
    icon='mactube.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MacTube'
)

app = BUNDLE(
    coll,
    name='MacTube.app',
    icon='mactube.icns',
    bundle_identifier='com.mactube.app',
    info_plist={
        'CFBundleName': 'MacTube',
        'CFBundleDisplayName': 'MacTube',
        'CFBundleIdentifier': 'com.mactube.app',
        'CFBundleVersion': '1.2.0',
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.14.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'YouTube URL',
                'CFBundleTypeExtensions': ['youtube', 'youtu.be'],
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Owner',
            }
        ],
        'NSAppleEventsUsageDescription': 'MacTube needs to access system events to handle YouTube URLs.',
    },
)
