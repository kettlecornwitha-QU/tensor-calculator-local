"""Calculator entry points for the tensor engine."""

from __future__ import annotations

from .run_calc_adapter import run_tensor_calculator as _run_tensor_calculator


RESULT_SECTION_ORDER = [
    "Metric",
    "Inverse metric",
    "∂ Metric",
    "Christoffel symbols",
    "∂ Christoffel symbols",
    "Riemann curvature tensor",
    "Ricci curvature tensor",
    "Ricci scalar",
    "Einstein tensor",
    "Mixed-index Einstein tensor",
    "Contravariant Einstein tensor",
]


def run_tensor_calculator(inputs: dict) -> dict[str, list[str]]:
    """Run the existing tensor engine with the collected user inputs."""
    return _run_tensor_calculator(inputs)
