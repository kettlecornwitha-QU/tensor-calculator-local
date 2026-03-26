from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from sympy import Symbol, latex

from gui.mathjax_view import FormulaView
from tensor_core import is_bool_step


class WizardFormController:
    def __init__(
        self,
        *,
        host_layout: QVBoxLayout,
        submit_handler: Callable[[], None],
        submit_enabled_handler: Callable[[], None],
        toggle_values: dict,
    ) -> None:
        self.host_layout = host_layout
        self.submit_handler = submit_handler
        self.submit_enabled_handler = submit_enabled_handler
        self.toggle_values = toggle_values

        self._bool_group: QButtonGroup | None = None
        self._text_inputs: list[QLineEdit] = []
        self._n_lineedit: QLineEdit | None = None

    def clear(self) -> None:
        while self.host_layout.count():
            item = self.host_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._bool_group = None
        self._text_inputs = []
        self._n_lineedit = None

    def render(
        self,
        *,
        session,
        metric_labels: list[str],
        input_key_for_step: Callable[[str], str],
    ) -> None:
        self.clear()
        step = session.step

        if step == "done":
            label = QLabel("Calculation complete. Use Back to adjust inputs or Reset to start a new session.")
            label.setWordWrap(True)
            self.host_layout.addWidget(label)
            self.host_layout.addStretch(1)
            return

        if step == "ask_n":
            line = QLineEdit()
            line.setPlaceholderText("e.g. 4")
            line.setValidator(QIntValidator(1, 12, line))
            if "n" in session.inputs:
                line.setText(str(session.inputs["n"]))
            line.returnPressed.connect(self.submit_handler)
            line.textChanged.connect(self.submit_enabled_handler)
            self._n_lineedit = line
            self.host_layout.addWidget(line)
            self.host_layout.addStretch(1)
            self.submit_enabled_handler()
            return

        if is_bool_step(step):
            group = QButtonGroup()
            default_value = session.inputs.get(input_key_for_step(step))
            for index, (label, value) in enumerate(self.toggle_values[step]):
                radio = QRadioButton(label)
                radio.setProperty("choiceValue", value)
                radio.toggled.connect(self.submit_enabled_handler)
                if default_value is not None and default_value == value:
                    radio.setChecked(True)
                if default_value is None and index == 0:
                    radio.setChecked(False)
                group.addButton(radio)
                self.host_layout.addWidget(radio)
            self._bool_group = group
            self.host_layout.addStretch(1)
            self.submit_enabled_handler()
            return

        if step == "ask_coords":
            self._add_labeled_inputs(
                labels=[f"Coordinate {i}" for i in range(session.inputs["n"])],
                values=session.inputs.get("coords"),
                render_latex_labels=False,
                line_min_width=260,
            )
            return

        if step == "ask_alt_basis_vectors":
            self._add_matrix_inputs(
                dimension=session.inputs["n"],
                coords=session.inputs["coords"],
                values=session.inputs.get("alt_basis"),
            )
            return

        if step == "ask_metric":
            self._add_labeled_inputs(
                labels=metric_labels,
                values=session.inputs.get("metric"),
                label_min_width=40,
                line_min_width=360,
                use_monospace=True,
            )
            return

        raise ValueError(f"Unsupported wizard step: {step}")

    def is_current_input_complete(self, step: str) -> bool:
        if step == "done":
            return False
        if step == "ask_n":
            return self._n_lineedit is not None and self._n_lineedit.text().strip() != ""
        if is_bool_step(step):
            return self._bool_group is not None and self._bool_group.checkedButton() is not None
        return bool(self._text_inputs) and all(line.text().strip() for line in self._text_inputs)

    def collect_input(self, step: str):
        if step == "ask_n" and self._n_lineedit is not None:
            return int(self._n_lineedit.text().strip())

        if is_bool_step(step):
            if self._bool_group is None or self._bool_group.checkedButton() is None:
                raise ValueError("Please select an option before continuing.")
            return bool(self._bool_group.checkedButton().property("choiceValue"))

        if step in {"ask_coords", "ask_alt_basis_vectors", "ask_metric"}:
            values = [line.text().strip() for line in self._text_inputs]
            if any(not value for value in values):
                raise ValueError("Please fill in every field before continuing.")
            return values
        raise ValueError(f"Unsupported wizard step: {step}")

    def _add_labeled_inputs(
        self,
        *,
        labels: list[str],
        values: list[str] | None = None,
        render_latex_labels: bool = True,
        label_min_width: int | None = None,
        line_min_width: int = 220,
        use_monospace: bool = False,
    ) -> None:
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(10)
        font = QFont("Menlo") if use_monospace else None
        grid.setColumnStretch(1, 1)

        self._text_inputs = []
        for row, label_text in enumerate(labels):
            label = FormulaView(label_text, min_height=38) if render_latex_labels else QLabel(label_text)
            line = QLineEdit()
            line.setMinimumWidth(line_min_width)
            line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if values and row < len(values):
                line.setText(str(values[row]))
            if font is not None:
                line.setFont(font)
            if label_min_width is not None:
                label.setMinimumWidth(label_min_width)
                label.setMaximumWidth(label_min_width)
            line.returnPressed.connect(self.submit_handler)
            line.textChanged.connect(self.submit_enabled_handler)
            self._text_inputs.append(line)
            grid.addWidget(label, row, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
            grid.addWidget(line, row, 1)

        wrapper = QWidget()
        wrapper.setLayout(grid)
        self.host_layout.addWidget(wrapper)
        self.host_layout.addStretch(1)
        self._set_tab_chain(self._text_inputs)
        self.submit_enabled_handler()

    def _add_matrix_inputs(
        self,
        *,
        dimension: int,
        coords: list[str],
        values: list[str] | None = None,
    ) -> None:
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        matrix_inputs: list[QLineEdit | None] = [None] * (dimension * dimension)
        box_width = 140
        row_label_width = 116

        grid.setColumnMinimumWidth(0, row_label_width)
        for column in range(1, dimension + 1):
            grid.setColumnStretch(column, 1)

        for column in range(dimension):
            heading = FormulaView(rf"\mathbf{{e}}_{{{column}}}", min_height=46, centered=True)
            heading.setMinimumWidth(box_width)
            heading.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            grid.addWidget(heading, 0, column + 1, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        for row in range(dimension):
            row_label = FormulaView(rf"{latex(Symbol(coords[row]))}\ \text{{component}}", min_height=42)
            row_label.setMinimumWidth(row_label_width)
            row_label.setMaximumWidth(row_label_width)
            grid.addWidget(row_label, row + 1, 0)
            for column in range(dimension):
                index = row + column * dimension
                line = QLineEdit()
                line.setMinimumWidth(box_width)
                line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                if values and index < len(values):
                    line.setText(str(values[index]))
                line.returnPressed.connect(self.submit_handler)
                line.textChanged.connect(self.submit_enabled_handler)
                matrix_inputs[index] = line
                grid.addWidget(line, row + 1, column + 1)

        hint = QLabel(
            "Columns correspond to alternate basis vectors. Each column is one vector written in coordinate components."
        )
        hint.setWordWrap(True)
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(hint)
        layout.addLayout(grid)
        self.host_layout.addWidget(wrapper)
        self.host_layout.addStretch(1)
        self._text_inputs = [line for line in matrix_inputs if line is not None]
        self._set_tab_chain(self._text_inputs)
        self.submit_enabled_handler()

    @staticmethod
    def _set_tab_chain(widgets: list[QLineEdit]) -> None:
        for current, nxt in zip(widgets, widgets[1:]):
            QWidget.setTabOrder(current, nxt)
