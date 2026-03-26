# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path


project_root = Path(SPECPATH).resolve().parent
bundle_icon = os.environ.get("TENSOR_CALC_BUNDLE_ICON")

datas = [(str(project_root / "assets"), "assets")]
hiddenimports = [
    "PySide6.QtPrintSupport",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
]

analysis = Analysis(
    [str(project_root / "gui" / "app_entry.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    name="Tensor Calculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    exclude_binaries=True,
)

collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Tensor Calculator",
)

app = BUNDLE(
    collect,
    name="Tensor Calculator.app",
    icon=bundle_icon,
    bundle_identifier="com.lukewalker.tensorcalc",
)
