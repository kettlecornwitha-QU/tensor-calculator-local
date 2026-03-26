# Tensor Calculator

`tensor_calc` is the local desktop version of the tensor calculator. It replaces the older split web deployment with a self-contained `PySide6` macOS app that talks directly to the Python tensor engine.

The main goal of this repo is simple: make the calculator fast, local, and easy to run on Apple Silicon Macs without relying on a hosted Flask server.

GitHub repository:

- `https://github.com/kettlecornwitha-QU/tensor-calculator-local`

## What It Does

The app walks the user through a guided input workflow for:

- manifold dimension
- coordinate labels
- optional alternate basis vectors
- metric entry

It then computes and displays:

- metric
- inverse metric
- metric derivatives
- Christoffel symbols
- Christoffel derivatives
- Riemann tensor
- Ricci tensor
- Ricci scalar
- Einstein tensor in multiple index placements

Results are rendered as LaTeX in the desktop UI, and the app includes starter presets for common geometries.

## Starter Presets

Current built-in presets live in [`tensor_core/presets.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/presets.py):

- `2-Sphere Coordinate Basis`
- `2-Sphere with Orthonormal Basis`
- `Wormhole with Orthonormal Basis`
- `Schwarzschild Spacetime/Schwarzschild Coordinates`

## Repository Layout

- `tensor_core/`
  The workflow engine, preset definitions, and tensor-calculation backend.
- `gui/`
  The desktop application, wizard UI, results panes, and MathJax-backed LaTeX rendering.
- `packaging/`
  The standalone app build pipeline, PyInstaller spec, and icon-generation helpers.
- `assets/`
  The runtime app icon and bundled MathJax assets.
- `dist_apps/`
  Output location for the packaged `.app` bundle after a successful build.

## Running In Development

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Launch the desktop app:

```bash
python3 -m gui.app
```

You can also launch through the packaged entrypoint module:

```bash
python3 -m gui.app_entry
```

## Packaging A Standalone macOS App

Build the app bundle with:

```bash
./package_standalone_app.command
```

The published bundle is written to:

- `dist_apps/Tensor Calculator.app`

The packaging flow is coordinated by [`packaging/build_app.py`](/Users/lukewalker/dev/tensor_calc/packaging/build_app.py).

## GitHub Releases

This repo is set up for packaged macOS app releases through GitHub Actions.

- Manual build/test runs can be started from the Actions tab with `workflow_dispatch`.
- Pushing a tag like `v0.1.0` will build the app and publish release assets automatically.

Expected release assets:

- `Tensor Calculator.app.zip`
- `SHA256SUMS.txt`

## Architecture Overview

The project is intentionally split into three layers:

1. `tensor_core`
   Pure Python workflow and tensor logic. This is the part to reuse if you ever want a CLI or another UI frontend.
2. `gui`
   The `PySide6` desktop interface. It collects inputs, shows session history, and renders results with local LaTeX support.
3. `packaging`
   PyInstaller-based app bundling for Apple Silicon macOS.

Key files:

- [`tensor_core/workflow.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/workflow.py)
  Step sequencing, typed workflow state, and session logic.
- [`tensor_core/calculator.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/calculator.py)
  Entry point for the tensor engine.
- [`tensor_core/gr_tensor_calculator.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/gr_tensor_calculator.py)
  Core symbolic tensor machinery.
- [`gui/main_window.py`](/Users/lukewalker/dev/tensor_calc/gui/main_window.py)
  Main desktop window and high-level orchestration.
- [`gui/wizard_form.py`](/Users/lukewalker/dev/tensor_calc/gui/wizard_form.py)
  Step-specific input form rendering and collection.
- [`gui/result_sections.py`](/Users/lukewalker/dev/tensor_calc/gui/result_sections.py)
  Expandable results sections shared by the native pane and detached results window.
- [`gui/mathjax_view.py`](/Users/lukewalker/dev/tensor_calc/gui/mathjax_view.py)
  Embedded offline LaTeX rendering.

## Common Development Tasks

Update starter presets:

- edit [`tensor_core/presets.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/presets.py)

Adjust wizard flow or validation:

- edit [`tensor_core/workflow.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/workflow.py)

Adjust UI layout or styling:

- edit [`gui/main_window.py`](/Users/lukewalker/dev/tensor_calc/gui/main_window.py)
- edit [`gui/wizard_form.py`](/Users/lukewalker/dev/tensor_calc/gui/wizard_form.py)
- edit [`gui/result_sections.py`](/Users/lukewalker/dev/tensor_calc/gui/result_sections.py)

Adjust packaging behavior:

- edit [`packaging/build_app.py`](/Users/lukewalker/dev/tensor_calc/packaging/build_app.py)
- edit [`packaging/tensor_calc.spec`](/Users/lukewalker/dev/tensor_calc/packaging/tensor_calc.spec)

## Known Packaging Note

The runtime app icon is bundled and works in the running app, but the full macOS `.icns` generation path is still imperfect in this environment. If `.icns` generation fails, the build falls back cleanly and still produces a working `.app`.

## Legacy Context

This repository replaced the previous deployment model:

- React/Vite frontend
- Flask backend hosted remotely

Those older repos can still serve as migration references, but this repository is now the source of truth for local desktop use and future development.

## More Detail

Developer-oriented notes are in [`docs/DEVELOPMENT.md`](/Users/lukewalker/dev/tensor_calc/docs/DEVELOPMENT.md).
