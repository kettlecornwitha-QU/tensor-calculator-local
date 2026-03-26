"""Reusable workflow/state logic extracted from the old Flask app."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Literal, TypedDict, TypeGuard

from sympy import Symbol, latex

from .calculator import RESULT_SECTION_ORDER, run_tensor_calculator
from .presets import PRESET_DEFINITIONS


StepName = Literal[
    "ask_n",
    "ask_coords",
    "ask_alt_basis",
    "ask_alt_basis_vectors",
    "ask_orthonormal",
    "ask_manifold_type",
    "ask_basis_metric_type",
    "ask_diag",
    "ask_metric",
    "done",
]
WorkflowState = Literal["ask_n", "ask_coords", "ask_alt_basis", "ask_alt_basis_vectors", "ask_orthonormal", "ask_manifold_type", "ask_basis_metric_type", "ask_diag", "ask_metric", "ready"]
BoolStepName = Literal[
    "ask_alt_basis",
    "ask_diag",
    "ask_orthonormal",
    "ask_basis_metric_type",
    "ask_manifold_type",
]


class SessionInputs(TypedDict, total=False):
    n: int
    coords: list[str]
    use_alt_basis: bool
    alt_basis: list[str]
    ortho: bool
    is_pseudo_riemannian: bool
    metric_in_CB: bool
    metric_diag: bool
    metric: list[str]


class HistoryEntry(TypedDict, total=False):
    step: StepName
    inputs: SessionInputs
    metric_labels: list[str]
    question: str
    answer: str
    answer_html: str


BOOL_STEP_INPUT_KEYS: dict[BoolStepName, str] = {
    "ask_alt_basis": "use_alt_basis",
    "ask_diag": "metric_diag",
    "ask_orthonormal": "ortho",
    "ask_basis_metric_type": "metric_in_CB",
    "ask_manifold_type": "is_pseudo_riemannian",
}

BOOL_STEPS = frozenset(BOOL_STEP_INPUT_KEYS)


@dataclass
class StepResult:
    step: StepName
    inputs: SessionInputs
    metric_labels: list[str] = field(default_factory=list)
    results: dict[str, list[str]] | None = None


@dataclass
class TensorCalcSession:
    """Mutable session state for the desktop wizard."""

    inputs: SessionInputs = field(default_factory=dict)
    history: list[HistoryEntry] = field(default_factory=list)
    step: StepName = "ask_n"
    metric_labels: list[str] = field(default_factory=list)
    results: dict[str, list[str]] | None = None

    def reset(self) -> None:
        self.inputs.clear()
        self.history.clear()
        self.step = "ask_n"
        self.metric_labels = []
        self.results = None

    def to_dict(self) -> dict[str, object]:
        return {
            "inputs": deepcopy(self.inputs),
            "history": deepcopy(self.history),
            "step": self.step,
            "metric_labels": self.metric_labels[:],
            "results": deepcopy(self.results),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TensorCalcSession":
        session = cls()
        session.inputs = deepcopy(payload.get("inputs", {}))  # type: ignore[assignment]
        session.history = deepcopy(payload.get("history", []))  # type: ignore[assignment]
        session.step = payload.get("step", current_step(session.inputs))  # type: ignore[assignment]
        session.metric_labels = list(payload.get("metric_labels", []))  # type: ignore[arg-type]
        session.results = deepcopy(payload.get("results"))  # type: ignore[assignment]
        return session

    def can_go_back(self) -> bool:
        return bool(self.history)

    def go_back(self) -> None:
        if not self.history:
            return
        snapshot = self.history.pop()
        self.inputs = deepcopy(snapshot["inputs"])
        self.step = snapshot["step"]
        self.metric_labels = snapshot["metric_labels"][:]
        self.results = None

    def load_preset(self, preset_name: str) -> None:
        if preset_name not in PRESET_DEFINITIONS:
            raise ValueError(f"Unknown preset: {preset_name}")
        self.reset()
        self.inputs = deepcopy(PRESET_DEFINITIONS[preset_name])
        self.step = "done"
        self.results = run_tensor_calculator(self.inputs)


def save_session_to_file(session: TensorCalcSession, path: str | Path) -> None:
    Path(path).write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")


def load_session_from_file(path: str | Path) -> TensorCalcSession:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return TensorCalcSession.from_dict(payload)


def is_bool_step(step: str) -> TypeGuard[BoolStepName]:
    return step in BOOL_STEPS


def current_step(inputs: SessionInputs) -> WorkflowState:
    if "n" not in inputs:
        return "ask_n"
    if "coords" not in inputs:
        return "ask_coords"
    if "use_alt_basis" not in inputs:
        return "ask_alt_basis"

    n = inputs["n"]
    if not inputs["use_alt_basis"]:
        if "metric_diag" not in inputs:
            return "ask_diag"
        if "metric" not in inputs:
            return "ask_metric"
        return "ready"

    if "alt_basis" not in inputs:
        return "ask_alt_basis_vectors"
    if "ortho" not in inputs:
        return "ask_orthonormal"
    if inputs["ortho"]:
        if "is_pseudo_riemannian" not in inputs:
            return "ask_manifold_type"
        return "ready"
    if "metric_in_CB" not in inputs:
        return "ask_basis_metric_type"
    if "metric_diag" not in inputs:
        return "ask_diag"
    if "metric" not in inputs:
        return "ask_metric"
    return "ready"


def generate_metric_labels(
    n: int, coords: list[str], diagonal: bool = True, use_alt: bool = False
) -> list[str]:
    labels = []
    index = [f"{i}" for i in range(n)] if use_alt else [latex(Symbol(coord)) for coord in coords]
    for i in range(n):
        if diagonal:
            labels.append(f"g_{{{index[i]}{index[i]}}}")
            continue
        for j in range(i, n):
            labels.append(f"g_{{{index[i]}{index[j]}}}")
    return labels


def get_prompt(step: StepName, inputs: SessionInputs | None = None) -> str:
    data: SessionInputs = inputs or {}
    prompt_builders = {
        "ask_n": lambda _: "Enter number of dimensions of the manifold:",
        "ask_coords": lambda current: f"Enter {current['n']} coordinate labels:",
        "ask_alt_basis": lambda _: "Would you like to include an alternate basis?",
        "ask_alt_basis_vectors": lambda current: f"Enter {current['n'] ** 2} alternate basis components:",
        "ask_orthonormal": lambda _: "Is the alternate basis orthonormal?",
        "ask_manifold_type": lambda _: "Is the manifold pseudo-Riemannian?",
        "ask_basis_metric_type": lambda _: "Will the metric components be those of the coordinate basis or the alternate basis?",
        "ask_diag": lambda _: "Is the metric diagonal?",
        "ask_metric": lambda current: (
            f"Enter {current['n'] if current['metric_diag'] else (current['n'] * (current['n'] + 1)) // 2} metric components:"
        ),
        "done": lambda _: "",
    }
    return prompt_builders[step](data)


def advance_session(session: TensorCalcSession, user_input) -> StepResult:
    """Advance the workflow by one validated input."""

    snapshot = {
        "step": session.step,
        "inputs": deepcopy(session.inputs),
        "metric_labels": session.metric_labels[:],
    }

    step = current_step(session.inputs)
    inputs = session.inputs

    if step == "ask_n":
        n = int(user_input)
        if n <= 0:
            raise ValueError("n must be a positive integer")
        inputs["n"] = n

    elif step == "ask_coords":
        if not isinstance(user_input, list) or len(user_input) != inputs["n"]:
            raise ValueError(f"Expected {inputs['n']} coordinate labels")
        if not all(label.isalpha() for label in user_input):
            raise ValueError("All coordinate labels must only contain letters")
        inputs["coords"] = user_input

    elif step == "ask_alt_basis":
        inputs["use_alt_basis"] = bool(user_input)

    elif step == "ask_diag":
        inputs["metric_diag"] = bool(user_input)

    elif step == "ask_metric":
        expected_len = inputs["n"] if inputs["metric_diag"] else inputs["n"] * (inputs["n"] + 1) // 2
        if not isinstance(user_input, list) or len(user_input) != expected_len:
            raise ValueError(f"Expected {expected_len} metric components")
        inputs["metric"] = user_input

    elif step == "ask_alt_basis_vectors":
        expected = inputs["n"] ** 2
        if not isinstance(user_input, list) or len(user_input) != expected:
            raise ValueError(f"Expected {expected} components for alternate basis vectors")
        inputs["alt_basis"] = user_input

    elif step == "ask_manifold_type":
        inputs["is_pseudo_riemannian"] = bool(user_input)

    elif step == "ask_orthonormal":
        inputs["ortho"] = bool(user_input)

    elif step == "ask_basis_metric_type":
        inputs["metric_in_CB"] = bool(user_input)

    step = current_step(inputs)
    metric_labels: list[str] = []
    results = None

    if step == "ready":
        results = run_tensor_calculator(inputs)
        session.results = results
        session.metric_labels = []
        session.step = "done"
        session.history.append(snapshot)
        return StepResult(step="done", inputs=deepcopy(inputs), results=results)

    if step == "ask_metric":
        metric_labels = generate_metric_labels(
            inputs["n"],
            inputs["coords"],
            inputs["metric_diag"],
            use_alt=not inputs.get("metric_in_CB", True),
        )

    session.history.append(snapshot)
    session.step = step
    session.metric_labels = metric_labels
    return StepResult(step=step, inputs=deepcopy(inputs), metric_labels=metric_labels)


def build_result_sections(results: dict[str, list[str]] | None) -> list[tuple[str, list[str]]]:
    if not results:
        return []
    sections: list[tuple[str, list[str]]] = []
    for title in RESULT_SECTION_ORDER:
        lines = results.get(title, [])
        safe_lines = [line for line in lines if isinstance(line, str) and line.strip()]
        sections.append((title, safe_lines))
    return sections
