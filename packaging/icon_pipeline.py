from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


ICON_BASE_SIZES = [16, 32, 128, 256, 512]


def render_png(svg_path: Path, png_path: Path, size: int) -> None:
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer = QSvgRenderer(str(svg_path))
    renderer.render(painter)
    painter.end()
    image.save(str(png_path))


def build_icns(project_root: Path) -> Path | None:
    svg_path = project_root / "assets" / "tensor_calc_icon.svg"
    iconset_dir = project_root / "build" / "tensor_calc.iconset"
    icns_path = project_root / "assets" / "tensor_calc_icon.icns"

    iconutil = shutil.which("iconutil")
    if iconutil is None:
        return None

    _app = QGuiApplication.instance() or QGuiApplication([])

    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    iconset_dir.mkdir(parents=True, exist_ok=True)

    try:
        for size in ICON_BASE_SIZES:
            render_png(svg_path, iconset_dir / f"icon_{size}x{size}.png", size)
            render_png(svg_path, iconset_dir / f"icon_{size}x{size}@2x.png", size * 2)

        subprocess.run(
            [iconutil, "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
            check=True,
        )
    except Exception:
        if icns_path.exists():
            icns_path.unlink()
        return None

    return icns_path
