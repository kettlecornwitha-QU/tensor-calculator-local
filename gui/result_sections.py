from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from gui.mathjax_view import MathJaxView


class ResultSectionWidget(QFrame):
    def __init__(
        self,
        *,
        title: str,
        lines: list[str],
        on_copy,
    ) -> None:
        super().__init__()
        self.title = title
        self.lines = lines
        self.expandable = bool(lines)
        self._on_copy = on_copy
        self._content_widget: QWidget | None = None
        self._content_container: QFrame | None = None

        self.setObjectName("resultSection")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(10)

        self.toggle_button = QToolButton()
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.toggled.connect(self._handle_toggled)
        header_layout.addWidget(self.toggle_button, 1)

        if self.expandable:
            count_text = self._count_text()
            self.count_label = QLabel(count_text)
            self.count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.count_label.setMinimumWidth(170)
            self.count_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            self.copy_button = QPushButton("Copy")
            self.copy_button.setFixedWidth(68)
            self.copy_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.copy_button.setStyleSheet(
                """
                QPushButton {
                    background: #334155;
                    color: #f8fbff;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #43556d;
                }
                """
            )
            self.copy_button.clicked.connect(lambda: self._on_copy(self.title, self.lines))
            header_layout.addWidget(self.count_label)
            header_layout.addWidget(self.copy_button)
        else:
            self.count_label = QLabel(self._zero_text())
            self.count_label.setObjectName("resultMutedLabel")
            self.count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.count_label.setMinimumWidth(170)
            self.count_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            self.copy_button = None
            self.toggle_button.setEnabled(False)
            header_layout.addWidget(self.count_label)

        layout.addWidget(header)

        if not self.expandable:
            self.setProperty("emptySection", True)
            self.toggle_button.setArrowType(Qt.NoArrow)
            self.toggle_button.setStyleSheet("text-align: left; color: #8b98a8;")
        else:
            self._content_container = QFrame()
            self._content_container.setObjectName("resultSectionContent")
            self._content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            content_layout = QVBoxLayout(self._content_container)
            content_layout.setContentsMargins(10, 0, 10, 10)
            content_layout.setSpacing(0)
            self._content_widget = MathJaxView(self.title, self.lines)
            content_layout.addWidget(self._content_widget)
            layout.addWidget(self._content_container)
            self.toggle_button.setStyleSheet("text-align: left;")
            self._content_container.setVisible(False)
            self.set_expanded(False)

    def _count_text(self) -> str:
        if self._is_ricci_scalar():
            return ""
        component_count = len(self.lines)
        noun = "component" if component_count == 1 else "components"
        return f"{component_count} non-zero {noun}"

    def _zero_text(self) -> str:
        if self._is_ricci_scalar():
            return "Ricci scalar is zero"
        return "All components are zero"

    def _is_ricci_scalar(self) -> bool:
        return self.title.strip().casefold() == "ricci scalar"

    def set_expanded(self, expanded: bool) -> None:
        if not self.expandable:
            return
        self.toggle_button.setChecked(expanded)

    def _handle_toggled(self, expanded: bool) -> None:
        if not self.expandable:
            return

        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        if self._content_container is not None:
            self._content_container.setVisible(expanded)
