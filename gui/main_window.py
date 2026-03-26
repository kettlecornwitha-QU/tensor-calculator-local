from __future__ import annotations

from pathlib import Path
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from gui.help_window import HelpWindow
from gui.history_formatting import format_answer_for_history, format_history_html
from gui.result_sections import ResultSectionWidget
from gui.results_window import ResultsWindow
from gui.wizard_form import WizardFormController
from tensor_core import (
    BOOL_STEP_INPUT_KEYS,
    PRESET_DEFINITIONS,
    TensorCalcSession,
    advance_session,
    build_result_sections,
    get_prompt,
    load_session_from_file,
    save_session_to_file,
)


TOGGLE_VALUES = {
    "ask_alt_basis": [
        ("No alternate basis", False),
        ("Include alternate basis", True),
    ],
    "ask_diag": [
        ("Metric is diagonal", True),
        ("Metric is not diagonal", False),
    ],
    "ask_orthonormal": [
        ("Orthonormal", True),
        ("Not orthonormal", False),
    ],
    "ask_basis_metric_type": [
        ("Coordinate basis", True),
        ("Alternate basis", False),
    ],
    "ask_manifold_type": [
        ("Riemannian", False),
        ("Pseudo-Riemannian", True),
    ],
}


class TensorCalcWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.session = TensorCalcSession()
        self.setWindowTitle("Tensor Calculator")
        self.resize(1320, 860)
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "tensor_calc_icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.prompt_label = QLabel()
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setObjectName("promptLabel")

        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.history_browser = QTextBrowser()
        self.history_browser.setOpenExternalLinks(False)
        self.history_browser.setObjectName("historyBrowser")

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QFrame.NoFrame)
        self.results_host = QWidget()
        self.results_layout = QVBoxLayout(self.results_host)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(10)
        self.results_scroll.setWidget(self.results_host)
        self.results_summary = QLabel()
        self.results_summary.setObjectName("resultsSummary")
        self.results_summary.setWordWrap(True)
        self.input_stack = QStackedWidget()

        self.form_host = QWidget()
        self.form_layout = QVBoxLayout(self.form_host)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(12)
        self.form_layout.addWidget(self.prompt_label)
        self.form_layout.addWidget(self.error_label)
        self.form_body = QWidget()
        self.form_body_layout = QVBoxLayout(self.form_body)
        self.form_body_layout.setContentsMargins(0, 0, 0, 0)
        self.form_body_layout.setSpacing(12)
        self.form_layout.addWidget(self.form_body)

        self.submit_button = QPushButton("Continue")
        self.submit_button.clicked.connect(self.handle_submit)
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.handle_back)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.handle_reset)
        self.save_button = QPushButton("Save Session")
        self.save_button.clicked.connect(self.handle_save_session)
        self.load_button = QPushButton("Load Session")
        self.load_button.clicked.connect(self.handle_load_session)
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.handle_export_results)
        self.copy_section_button = QPushButton("Copy Section")
        self.copy_section_button.clicked.connect(self.handle_copy_current_section)
        self.open_results_window_button = QPushButton("Open Results Window")
        self.open_results_window_button.clicked.connect(self.handle_open_results_window)
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Load Starter Preset...")
        for name in PRESET_DEFINITIONS:
            self.preset_combo.addItem(name)
        self.preset_combo.currentIndexChanged.connect(self.handle_preset_selected)

        self.form_controller = WizardFormController(
            host_layout=self.form_body_layout,
            submit_handler=self.handle_submit,
            submit_enabled_handler=self._update_submit_enabled,
            toggle_values=TOGGLE_VALUES,
        )
        self.results_window = ResultsWindow()
        self.help_window = HelpWindow(icon=self.windowIcon())

        self._build_ui()
        self._apply_style()
        self.refresh_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        title = QLabel("Tensor Calculator")
        title.setObjectName("titleLabel")

        shared_controls = QHBoxLayout()
        shared_controls.setSpacing(10)
        shared_controls.addWidget(self.back_button)
        shared_controls.addWidget(self.reset_button)
        shared_controls.addWidget(self.save_button)
        shared_controls.addWidget(self.load_button)
        shared_controls.addStretch(1)

        input_controls = QHBoxLayout()
        input_controls.setSpacing(10)
        input_controls.addStretch(1)
        input_controls.addWidget(self.submit_button)

        results_controls = QHBoxLayout()
        results_controls.setSpacing(10)
        results_controls.addStretch(1)
        results_controls.addWidget(self.open_results_window_button)
        results_controls.addWidget(self.copy_section_button)
        results_controls.addWidget(self.export_button)

        top_tools = QHBoxLayout()
        top_tools.setSpacing(10)
        preset_label = QLabel("Starter Preset")
        preset_label.setObjectName("presetLabel")
        top_tools.addWidget(preset_label)
        top_tools.addWidget(self.preset_combo, 1)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        history_label = QLabel("Session History")
        history_label.setObjectName("sectionTitle")
        history_frame = self._framed(self.history_browser)
        left_layout.addWidget(history_label)
        left_layout.addWidget(history_frame, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        input_label = QLabel("Input Wizard")
        input_label.setObjectName("sectionTitle")
        self.workspace_label = input_label

        input_card = QWidget()
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(18, 18, 18, 18)
        input_card_layout.setSpacing(14)
        input_card_layout.addLayout(top_tools)

        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.NoFrame)
        form_scroll.setWidget(self.form_host)
        input_card_layout.addWidget(form_scroll, 1)
        input_card_layout.addLayout(input_controls)
        input_card.setObjectName("card")

        results_frame = self._framed(self.results_scroll)
        results_card = QWidget()
        results_card_layout = QVBoxLayout(results_card)
        results_card_layout.setContentsMargins(18, 18, 18, 18)
        results_card_layout.setSpacing(14)
        results_card_layout.addWidget(self.results_summary)
        results_card_layout.addWidget(results_frame, 1)
        results_card_layout.addLayout(results_controls)
        results_card.setObjectName("card")

        self.input_stack.addWidget(input_card)
        self.input_stack.addWidget(results_card)

        right_layout.addWidget(input_label)
        right_layout.addLayout(shared_controls)
        right_layout.addWidget(self.input_stack, 1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([280, 920])

        root_layout.addWidget(title)
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.show_help_window)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)

    def _apply_style(self) -> None:
        mono = QFont("Menlo")
        mono.setStyleHint(QFont.Monospace)
        self.history_browser.setFont(mono)

        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #14181d;
                color: #edf1f6;
                font-size: 14px;
            }
            #titleLabel {
                font-size: 28px;
                font-weight: 700;
                color: #f7fbff;
            }
            #sectionTitle {
                font-size: 16px;
                font-weight: 700;
                color: #e6edf5;
            }
            #promptLabel {
                font-size: 18px;
                font-weight: 600;
                color: #f5f8fc;
            }
            #presetLabel {
                background: #1b2129;
            }
            #errorLabel {
                color: #ffd7d7;
                background: #4a1f26;
                border: 1px solid #7a3340;
                border-radius: 8px;
                padding: 10px;
            }
            #resultsSummary {
                color: #dce6f2;
                background: #1f2630;
                border: 1px solid #334154;
                border-radius: 10px;
                padding: 10px 12px;
            }
            #card, #frameCard {
                background: #1b2129;
                border: 1px solid #2c3643;
                border-radius: 14px;
            }
            QTextBrowser, QScrollArea {
                background: #1b2129;
                border: none;
            }
            QComboBox {
                background: #232b35;
                color: #edf1f6;
                border: 1px solid #3a4656;
                border-radius: 8px;
                padding: 6px 10px;
                selection-background-color: #232b35;
                selection-color: #edf1f6;
            }
            QComboBox QAbstractItemView {
                background: #1b2129;
                color: #edf1f6;
                selection-background-color: #2d3745;
                selection-color: #ffffff;
            }
            QLineEdit {
                background: #232b35;
                color: #f7fbff;
                border: 1px solid #3a4656;
                border-radius: 8px;
                padding: 8px;
                min-height: 18px;
                selection-background-color: #4d6a8a;
                selection-color: #ffffff;
            }
            QPushButton {
                background: #334155;
                color: #f8fbff;
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #43556d;
            }
            QPushButton:disabled {
                background: #232a33;
                color: #7e8b9a;
            }
            QRadioButton {
                spacing: 8px;
                padding: 4px 0;
            }
            #resultSection {
                background: #202731;
                border: none;
                border-radius: 12px;
            }
            #resultSection[emptySection="true"] {
                background: #171c23;
                border: none;
            }
            #resultMutedLabel {
                color: #7f8b99;
            }
            """
        )

    def _framed(self, widget: QWidget) -> QWidget:
        frame = QWidget()
        frame.setObjectName("frameCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(widget)
        return frame

    def show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "About Tensor Calculator",
            "Tensor Calculator\n\n"
            "Desktop PySide6 build that reuses the original Python tensor engine\n"
            "without a browser, hosted frontend, or Flask server.",
        )

    def show_help_window(self) -> None:
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    def refresh_ui(self) -> None:
        self.prompt_label.setText(get_prompt(self.session.step, self.session.inputs))
        self.back_button.setEnabled(self.session.can_go_back())
        self.export_button.setEnabled(self.session.results is not None)
        self.open_results_window_button.setEnabled(self.session.results is not None)
        self.input_stack.setCurrentIndex(1 if self.session.results is not None else 0)
        self.workspace_label.setText("Results" if self.session.results is not None else "Input Wizard")
        self._render_history()
        self._render_form()
        self._render_results()
        self.results_window.set_results(self.session.results)

    def _update_submit_enabled(self) -> None:
        self.submit_button.setEnabled(self.form_controller.is_current_input_complete(self.session.step))

    def _render_form(self) -> None:
        self.error_label.hide()
        self.form_controller.render(
            session=self.session,
            metric_labels=self.session.metric_labels,
            input_key_for_step=BOOL_STEP_INPUT_KEYS.__getitem__,
        )

    def _render_history(self) -> None:
        self.history_browser.setHtml(
            format_history_html(
                self.session.history,
                has_loaded_results=bool(self.session.inputs and self.session.results is not None),
            )
        )

    def _render_results(self) -> None:
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        sections = build_result_sections(self.session.results)
        if not sections:
            self.results_summary.setText(
                "No tensor output yet. Complete the wizard or load a starter preset to populate the results pane."
            )
            placeholder = QLabel(
                "No results yet. Complete the wizard to compute the metric, Christoffel symbols, curvature tensors, and Einstein tensors."
            )
            placeholder.setWordWrap(True)
            placeholder.setObjectName("resultMutedLabel")
            self.results_layout.addWidget(placeholder)
            self.results_layout.addStretch(1)
            return

        non_zero_sections = sum(1 for _, lines in sections if lines)
        total_lines = sum(len(lines) for _, lines in sections)
        self.results_summary.setText(
            f"{non_zero_sections} sections contain non-zero output, with {total_lines} rendered equations across the current calculation."
        )

        for title, lines in sections:
            section = ResultSectionWidget(
                title=title,
                lines=lines,
                on_copy=self._copy_section_payload,
            )
            self.results_layout.addWidget(section)

        self.results_layout.addStretch(1)

    def handle_submit(self) -> None:
        try:
            answer_value = self.form_controller.collect_input(self.session.step)
            answer_text, answer_html = format_answer_for_history(
                self.session.step,
                answer_value,
                n=self.session.inputs.get("n"),
                toggle_values=TOGGLE_VALUES,
            )
            question = get_prompt(self.session.step, self.session.inputs)
            result = advance_session(self.session, answer_value)
            if self.session.history:
                self.session.history[-1]["question"] = question
                self.session.history[-1]["answer"] = answer_text
                self.session.history[-1]["answer_html"] = answer_html
            self.session.step = result.step
            self.session.metric_labels = result.metric_labels
            if result.results is not None:
                self.session.results = result.results
            self.error_label.hide()
            self.refresh_ui()
        except Exception as exc:
            self.error_label.setText(str(exc))
            self.error_label.show()

    def handle_back(self) -> None:
        self.session.go_back()
        self.refresh_ui()

    def handle_reset(self) -> None:
        self.session.reset()
        self.preset_combo.setCurrentIndex(0)
        self.refresh_ui()

    def handle_preset_selected(self, index: int) -> None:
        if index <= 0:
            return
        try:
            preset_name = self.preset_combo.currentText()
            self.session.load_preset(preset_name)
            self.error_label.hide()
            self.refresh_ui()
        except Exception as exc:
            self.error_label.setText(str(exc))
            self.error_label.show()
        finally:
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentIndex(0)
            self.preset_combo.blockSignals(False)

    def handle_save_session(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Tensor Calculator Session",
            str(Path.home() / "tensor_calc_session.json"),
            "JSON Files (*.json)",
        )
        if not path:
            return
        try:
            save_session_to_file(self.session, path)
        except Exception as exc:
            self.error_label.setText(f"Could not save session: {exc}")
            self.error_label.show()
            return
        QMessageBox.information(self, "Session Saved", f"Saved session to:\n{path}")

    def handle_load_session(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Tensor Calculator Session",
            str(Path.home()),
            "JSON Files (*.json)",
        )
        if not path:
            return
        try:
            self.session = load_session_from_file(path)
            self.error_label.hide()
            self.refresh_ui()
        except Exception as exc:
            self.error_label.setText(f"Could not load session: {exc}")
            self.error_label.show()

    def handle_export_results(self) -> None:
        if self.session.results is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tensor Calculator Results",
            str(Path.home() / "tensor_calc_results.json"),
            "JSON Files (*.json);;Text Files (*.txt)",
        )
        if not path:
            return
        target = Path(path)
        try:
            if target.suffix.lower() == ".txt":
                text_chunks = []
                for title, lines in build_result_sections(self.session.results):
                    text_chunks.append(title)
                    text_chunks.append("=" * len(title))
                    if lines:
                        text_chunks.extend(lines)
                    else:
                        text_chunks.append("All components are zero.")
                    text_chunks.append("")
                target.write_text("\n".join(text_chunks), encoding="utf-8")
            else:
                target.write_text(
                    json.dumps(self.session.results, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
        except Exception as exc:
            self.error_label.setText(f"Could not export results: {exc}")
            self.error_label.show()
            return
        QMessageBox.information(self, "Results Exported", f"Exported results to:\n{path}")

    def handle_copy_current_section(self) -> None:
        if self.session.results is None:
            return
        for title, lines in build_result_sections(self.session.results):
            if lines:
                self._copy_section_payload(title, lines)
                return
        QMessageBox.information(self, "Nothing To Copy", "All current result sections are zero.")

    def _copy_section_payload(self, title: str, lines: list[str]) -> None:
        QApplication.clipboard().setText("\n".join(lines))
        QMessageBox.information(self, "Section Copied", f"Copied results for:\n{title}")

    def handle_open_results_window(self) -> None:
        if self.session.results is None:
            return
        self.results_window.set_results(self.session.results)
        self.results_window.show()
        self.results_window.raise_()
        self.results_window.activateWindow()
