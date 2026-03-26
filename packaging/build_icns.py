from __future__ import annotations

from pathlib import Path

from icon_pipeline import build_icns


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    icns_path = build_icns(project_root)
    if icns_path is None:
        raise SystemExit("Could not build the macOS app icon.")
    print(f"Built icon at: {icns_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
