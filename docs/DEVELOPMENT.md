# Development Notes

## Design Intent

This project is a desktop-first wrapper around an existing symbolic tensor engine. The most important architectural rule is to keep the computation layer separate from the GUI layer.

That means:

- `tensor_core/` should stay usable without `PySide6`
- GUI code should call into workflow and calculator helpers, not recreate tensor logic itself
- packaging code should stay isolated from both runtime logic layers

## Runtime Flow

At a high level, the app runs like this:

1. [`gui/app_entry.py`](/Users/lukewalker/dev/tensor_calc/gui/app_entry.py) configures packaged-runtime environment variables when frozen.
2. [`gui/app.py`](/Users/lukewalker/dev/tensor_calc/gui/app.py) starts the `QApplication`.
3. [`gui/main_window.py`](/Users/lukewalker/dev/tensor_calc/gui/main_window.py) coordinates the session, left-hand history pane, right-hand wizard/results workspace, and file actions.
4. [`gui/wizard_form.py`](/Users/lukewalker/dev/tensor_calc/gui/wizard_form.py) renders the current workflow step and collects user input.
5. [`tensor_core/workflow.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/workflow.py) validates and advances the session state.
6. [`tensor_core/calculator.py`](/Users/lukewalker/dev/tensor_calc/tensor_core/calculator.py) calls into the tensor engine.
7. [`gui/result_sections.py`](/Users/lukewalker/dev/tensor_calc/gui/result_sections.py) and [`gui/mathjax_view.py`](/Users/lukewalker/dev/tensor_calc/gui/mathjax_view.py) render the resulting LaTeX output.

## Key Modules

### `tensor_core/workflow.py`

Owns:

- typed workflow step definitions
- session inputs/state
- prompt progression
- save/load session serialization

This is the main place to edit if you want to change the input wizard behavior.

### `tensor_core/presets.py`

Owns the starter presets shown in the GUI dropdown. Presets should match the same input structure the workflow expects.

### `tensor_core/gr_tensor_calculator.py`

Owns the heavy symbolic tensor computation. This file is intentionally left closer to the original engine so correctness changes are easier to isolate from UI changes.

### `gui/main_window.py`

Owns:

- top-level layout
- workspace mode switching between input and results
- button wiring
- save/load/export actions
- integration of the form controller and results widgets

Keep this file focused on orchestration rather than low-level per-step widget details.

### `gui/wizard_form.py`

Owns step-specific widget creation and input collection. If a form step needs layout or tab-order changes, this is usually the first file to inspect.

### `gui/result_sections.py`

Owns collapsible results sections, section header text, copy buttons, and the distinction between zero-output and nonzero-output sections.

## Styling Notes

The current UI uses a dark theme. A few practical rules:

- keep outer panels, inner cards, and embedded LaTeX backgrounds visually consistent
- remember that tiny `QWebEngineView` widgets can behave differently from the larger results renderers
- when changing colors for LaTeX prompt labels, check both HTML/CSS and the Qt widget background

## Packaging Notes

Standalone app creation is driven by:

- [`package_standalone_app.command`](/Users/lukewalker/dev/tensor_calc/package_standalone_app.command)
- [`packaging/build_app.py`](/Users/lukewalker/dev/tensor_calc/packaging/build_app.py)
- [`packaging/tensor_calc.spec`](/Users/lukewalker/dev/tensor_calc/packaging/tensor_calc.spec)

The intended packaging flow is:

1. attempt to generate a bundle icon through [`packaging/icon_pipeline.py`](/Users/lukewalker/dev/tensor_calc/packaging/icon_pipeline.py)
2. pass the icon path into PyInstaller if available
3. build the app bundle into `dist/`
4. publish the final app into `dist_apps/`

If `.icns` generation fails, the build should still succeed.

## Recommended Editing Boundaries

When possible:

- change workflow behavior in `tensor_core/`
- change rendering behavior in `gui/`
- change distribution behavior in `packaging/`

Avoid reaching across layers unless the change truly belongs in more than one place.
