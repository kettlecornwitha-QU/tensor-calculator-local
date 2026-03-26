from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget


HELP_HTML = """
<h2>Tensor Calculator Help</h2>
<p>
This desktop app guides you through defining a metric +/- an alternate basis and then computes
the associated tensor quantities locally.
</p>

<h3>Typical Workflow</h3>
<ol>
  <li>Enter the number of dimensions of the manifold.</li>
  <li>Enter coordinate labels.</li>
  <li>Choose whether you want an alternate basis.</li>
  <li>Enter either alternate basis components or metric components, depending on the path you chose.</li>
  <li>Review the computed results in the collapsible results sections.</li>
</ol>

<h3>Starter Presets</h3>
<p>
Use the <b>Starter Preset</b> dropdown near the top of the input workspace to instantly load a common geometry.
</p>

<h3>Results</h3>
<ul>
  <li>Each section can be expanded or collapsed independently.</li>
  <li>Sections with all-zero output are dimmed and not expandable.</li>
  <li>The <b>Copy</b> button copies the displayed LaTeX strings for that section.</li>
  <li><b>Open Results Window</b> opens a larger detached view for easier reading.</li>
</ul>

<h3>Session Tools</h3>
<ul>
  <li><b>Save Session</b> writes the current wizard state to JSON.</li>
  <li><b>Load Session</b> restores a saved session.</li>
  <li><b>Export Results</b> saves the current results as JSON or plain text.</li>
  <li><b>Reset</b> clears the current session and returns to the first step.</li>
</ul>

<h3>Notes</h3>
<ul>
  <li>Everything runs locally in the desktop app.</li>
  <li>LaTeX rendering is bundled and works offline.</li>
  <li>The app is intended for Apple Silicon macOS packaging, but the Python code can also run in development mode.</li>
</ul>
"""


class HelpWindow(QWidget):
    def __init__(self, *, icon: QIcon | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Tensor Calculator Help")
        self.resize(760, 640)
        if icon is not None:
            self.setWindowIcon(icon)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Tensor Calculator Help")
        title.setObjectName("helpTitle")

        browser = QTextBrowser()
        browser.setObjectName("helpBrowser")
        browser.setOpenExternalLinks(False)
        browser.setHtml(HELP_HTML)
        browser.setReadOnly(True)

        layout.addWidget(title)
        layout.addWidget(browser, 1)

        self.setAttribute(Qt.WA_DeleteOnClose, False)
