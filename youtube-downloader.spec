# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all

# Salida final: release/YouTube-Downloader/
# Archivos temporales de compilacion: .build/ (se borra al terminar)
distpath = os.path.join(SPECPATH, "release", "YouTube-Downloader")
workpath = os.path.join(SPECPATH, ".build")

block_cipher = None

datas = [("youtube-downloader.ico", ".")]
binaries = []
hiddenimports = ["imageio_ffmpeg"]

for package in ("customtkinter", "yt_dlp", "imageio_ffmpeg"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="YouTube-Downloader",
    icon="youtube-downloader.ico",
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
