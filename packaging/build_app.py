from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from icon_pipeline import build_icns


APP_NAME = "Tensor Calculator"


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    dist_apps_dir = project_root / "dist_apps"
    bundle_path = dist_dir / f"{APP_NAME}.app"
    published_bundle_path = dist_apps_dir / f"{APP_NAME}.app"

    os.environ.setdefault("PYINSTALLER_CONFIG_DIR", str(project_root / ".pyinstaller"))

    bundle_icon = build_icns(project_root)
    if bundle_icon is None:
        print("Warning: failed to build .icns app icon; continuing with runtime SVG icon.", file=sys.stderr)

    env = os.environ.copy()
    if bundle_icon is not None:
        env["TENSOR_CALC_BUNDLE_ICON"] = str(bundle_icon)
    else:
        env.pop("TENSOR_CALC_BUNDLE_ICON", None)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(build_dir),
            "packaging/tensor_calc.spec",
        ],
        check=True,
        cwd=project_root,
        env=env,
    )

    dist_apps_dir.mkdir(exist_ok=True)
    if published_bundle_path.exists():
        shutil.rmtree(published_bundle_path)
    shutil.move(str(bundle_path), str(published_bundle_path))

    print()
    print("Standalone app created at:")
    print(f"  {published_bundle_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
