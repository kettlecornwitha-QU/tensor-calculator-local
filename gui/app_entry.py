#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_packaged_runtime() -> None:
    if not getattr(sys, "frozen", False):
        return

    app_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent)).resolve()
    os.environ.setdefault("TENSOR_CALC_PACKAGED", "1")
    os.environ.setdefault("TENSOR_CALC_APP_ROOT", str(app_root))


_configure_packaged_runtime()

from gui.app import main


if __name__ == "__main__":
    raise SystemExit(main())
