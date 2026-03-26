"""Starter presets for common tensor calculator sessions."""

from __future__ import annotations


PRESET_DEFINITIONS = {
    "2-Sphere Coordinate Basis": {
        "n": 2,
        "coords": ["theta", "phi"],
        "use_alt_basis": False,
        "metric_diag": True,
        "metric": ["1", "sin(theta)^2"],
    },
    "2-Sphere with Orthonormal Basis": {
        "n": 2,
        "coords": ["theta", "phi"],
        "use_alt_basis": True,
        "alt_basis": ["1", "0", "0", "1/sin(theta)"],
        "ortho": True,
        "is_pseudo_riemannian": False,
    },
    "Wormhole with Orthonormal Basis": {
        "n": 4,
        "coords": ["t", "l", "theta", "phi"],
        "use_alt_basis": True,
        "alt_basis": [
            "1",
            "0",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "0",
            "1/r(l)",
            "0",
            "0",
            "0",
            "0",
            "1/(r(l)*sin(theta))",
        ],
        "ortho": True,
        "is_pseudo_riemannian": True,
    },
    "Schwarzschild Spacetime/Schwarzschild Coordinates": {
        "n": 4,
        "coords": ["t", "r", "theta", "phi"],
        "use_alt_basis": False,
        "metric_diag": True,
        "metric": [
            "-(1 - 2*M/r)",
            "1/(1 - 2*M/r)",
            "r^2",
            "r^2*sin(theta)^2",
        ],
    },
}
