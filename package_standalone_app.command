#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

python_bin="${PYTHON_BIN:-/Users/lukewalker/.rye/shims/python3}"
export PYINSTALLER_CONFIG_DIR="$PWD/.pyinstaller"

if [[ ! -x "$python_bin" ]]; then
  python_bin="$(command -v python3)"
fi

"$python_bin" packaging/build_app.py
