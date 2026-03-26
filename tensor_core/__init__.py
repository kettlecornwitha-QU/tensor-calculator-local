"""Core workflow and tensor calculation modules for the desktop app."""

from .calculator import RESULT_SECTION_ORDER, run_tensor_calculator
from .presets import PRESET_DEFINITIONS
from .workflow import (
    BOOL_STEP_INPUT_KEYS,
    StepResult,
    TensorCalcSession,
    advance_session,
    build_result_sections,
    generate_metric_labels,
    get_prompt,
    is_bool_step,
    load_session_from_file,
    save_session_to_file,
)

__all__ = [
    "RESULT_SECTION_ORDER",
    "PRESET_DEFINITIONS",
    "BOOL_STEP_INPUT_KEYS",
    "StepResult",
    "TensorCalcSession",
    "advance_session",
    "build_result_sections",
    "generate_metric_labels",
    "get_prompt",
    "is_bool_step",
    "load_session_from_file",
    "run_tensor_calculator",
    "save_session_to_file",
]
