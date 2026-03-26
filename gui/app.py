from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gui.main_window import TensorCalcWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Tensor Calculator")
    icon_path = PROJECT_ROOT / "assets" / "tensor_calc_icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = TensorCalcWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
