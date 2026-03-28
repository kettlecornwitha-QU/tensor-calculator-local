# User Guide

## What This App Is For

If you have a metric tensor and you want the non-zero components of the inverse metric, the partial derivatives of the metric, the Christoffel symbols, the partial derivatives of the Christoffel symbols, the Riemann curvature tensor, the Ricci curvature tensor, the Ricci scalar, or the Einstein tensor, this app is meant to save you from doing pages of symbolic tensor algebra by hand.

The calculator also allows you to include an alternate basis in addition to the default coordinate basis.

## What The App Computes

For a given metric, the app can compute and display:

- metric
- inverse metric
- partial derivatives of the metric
- Christoffel symbols
- partial derivatives of the Christoffel symbols
- Riemann curvature tensor
- Ricci curvature tensor
- Ricci scalar
- Einstein tensor
- mixed-index Einstein tensor
- contravariant Einstein tensor

The results are shown in collapsible sections, and only the non-zero components are listed for non-scalar objects.

## Basic Workflow

The app guides you through the inputs step by step:

1. Enter the number of dimensions of the manifold.
2. Enter coordinate labels.
3. Choose whether to include an alternate basis.
4. If needed, enter alternate basis vector components.
5. Enter the metric information.
6. Review the rendered results.

You can also use a built-in starter preset from the dropdown at the top of the input workspace.

## Coordinate Labels

The dimensionality of the manifold is up to you, and the coordinate labels are also up to you.

Examples:

- `x`
- `y`
- `z`
- `t`
- `r`
- `theta`
- `phi`

Use simple symbolic names for coordinates. Coordinate labels should be symbolic identifiers rather than names containing numerals.

## Entering Mathematical Expressions

When entering metric components or alternate basis vector components:

- use explicit multiplication
- use `^` for powers
- you can include symbolic parameters such as `M`
- you can include undefined functions, as long as you specify their arguments

Examples:

- `r^2`
- `sin(theta)^2`
- `1/(1 - 2*M/r)`
- `r(l)^2`

Important note:

- implicit multiplication is not supported, so write `2*M/r`, not `2M/r`

If a quantity is a function of a coordinate, include the argument explicitly. For example, if your coordinates are `t`, `l`, `theta`, and `phi`, then writing `r(l)^2` correctly indicates that `r` is a function of `l`.

## Alternate Basis Input

If you choose to include an alternate basis, the components of those basis vectors should be entered in terms of the coordinate basis.

For example, in two-dimensional Cartesian coordinates, if you wanted an alternate basis analogous to polar-coordinate directions, you would enter the radial basis vector and angular basis vector using their `x` and `y` components in the coordinate basis.

More generally:

- each alternate basis vector is entered by its coordinate-basis components
- the app labels alternate basis vectors as `e_0`, `e_1`, ..., `e_{n-1}`
- indices shown for coordinate-basis objects use the coordinate labels you entered
- indices shown for alternate-basis objects use integers from `0` to `n - 1`

## Results View

After the calculation finishes:

- the right-hand workspace switches from input mode to results mode
- each tensor object appears in its own collapsible section
- zero-output sections are dimmed
- you can copy section output with the `Copy` button
- you can open a detached results window for easier reading

The results are rendered in LaTeX for readability.

## Session Tools

The app includes a few convenience features:

- `Starter Preset` loads a built-in example
- `Back` returns to the previous step
- `Reset` clears the current session
- `Save Session` writes the current state to JSON
- `Load Session` restores a saved session
- `Export Results` saves current output as JSON or plain text

## Platform Note

This local desktop app is intended for Apple Silicon Macs.
