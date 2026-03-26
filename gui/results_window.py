from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QScrollArea, QVBoxLayout, QWidget

from gui.result_sections import ResultSectionWidget
from tensor_core import build_result_sections


class ResultsWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tensor Calculator Results")
        self.resize(1200, 900)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("resultsSummary")
        self.summary_label.setWordWrap(True)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.host = QWidget()
        self.layout_root = QVBoxLayout(self.host)
        self.layout_root.setContentsMargins(16, 16, 16, 16)
        self.layout_root.setSpacing(10)
        self.scroll.setWidget(self.host)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        root_layout.addWidget(self.summary_label)
        root_layout.addWidget(self.scroll, 1)
        self.setCentralWidget(root)

        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #14181d;
                color: #edf1f6;
                font-size: 14px;
            }
            #resultsSummary {
                color: #dce6f2;
                background: #1f2630;
                border: 1px solid #334154;
                border-radius: 10px;
                padding: 10px 12px;
            }
            """
        )

    def set_results(self, results: dict[str, list[str]] | None) -> None:
        while self.layout_root.count():
            item = self.layout_root.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        sections = build_result_sections(results)
        if not sections:
            self.summary_label.setText("No tensor output is available for this session yet.")
            empty = QLabel("No results yet.")
            self.layout_root.addWidget(empty)
            self.layout_root.addStretch(1)
            return

        non_zero_sections = sum(1 for _, lines in sections if lines)
        total_lines = sum(len(lines) for _, lines in sections)
        self.summary_label.setText(
            f"{non_zero_sections} sections contain non-zero output, with {total_lines} rendered equations across the current calculation."
        )

        for title, lines in sections:
            section = ResultSectionWidget(
                title=title,
                lines=lines,
                on_copy=self._copy_section_payload,
            )
            self.layout_root.addWidget(section)

        self.layout_root.addStretch(1)

    def _copy_section_payload(self, title: str, lines: list[str]) -> None:
        QApplication.clipboard().setText("\n".join(lines))
        QMessageBox.information(self, "Section Copied", f"Copied results for:\n{title}")
