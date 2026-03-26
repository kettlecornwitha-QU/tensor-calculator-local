from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QSize


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = PROJECT_ROOT / "assets"


def render_mathjax_document(
    title: str,
    *,
    lines: list[str] | None = None,
    formula: str | None = None,
    compact: bool = False,
    background: str = "#1b2129",
    centered: bool = False,
) -> str:
    if formula is not None:
        wrapper_class = "formula-inline" if compact else "formula-display"
        body_html = f"<div class='{wrapper_class}'>\\({escape(formula)}\\)</div>"
    elif lines:
        body = []
        for line in lines:
            body.append(
                "<div class='equation-card'><div class='equation'>\\["
                f"{escape(line)}"
                "\\]</div></div>"
            )
        body_html = "".join(body)
    else:
        body_html = "<p class='empty'>All components are zero for this section.</p>"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: light;
      }}
      html, body {{
        margin: 0;
        padding: 0;
        background: {background};
        color: #edf1f6;
        font-family: "Iowan Old Style", "Palatino Linotype", serif;
      }}
      body {{
        padding: {6 if compact else 12}px;
        text-align: {"center" if centered else "left"};
      }}
      .equation-card {{
        margin-bottom: 10px;
        padding: 10px 12px;
        background: #232b35;
        border: 1px solid #344050;
        border-radius: 10px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.22);
      }}
      .equation {{
        overflow-x: auto;
      }}
      .formula-inline {{
        display: inline-block;
        overflow: hidden;
      }}
      .formula-display {{
        overflow-x: auto;
      }}
      .empty {{
        color: #7f8b99;
        font-style: italic;
      }}
    </style>
    <script>
      window.MathJax = {{
        tex: {{
          inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
          displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
          processEscapes: true
        }},
        svg: {{
          fontCache: 'local'
        }},
        options: {{
          renderActions: {{
            addMenu: []
          }}
        }}
      }};
    </script>
    <script id="MathJax-script" async src="vendor/mathjax/tex-svg.js"></script>
  </head>
  <body>
    {body_html}
  </body>
</html>
"""


class MathJaxView(QWebEngineView):
    def __init__(self, title: str, lines: list[str]) -> None:
        super().__init__()
        self._measured_height = 0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setStyleSheet("background: #1b2129; border: none;")
        self.page().setBackgroundColor(QColor("#1b2129"))
        self.loadFinished.connect(self._schedule_height_updates)
        self.setHtml(
            render_mathjax_document(title, lines=lines),
            QUrl.fromLocalFile(str(ASSETS_ROOT) + "/"),
        )

    def sizeHint(self) -> QSize:
        if self._measured_height > 0:
            return QSize(super().sizeHint().width(), self._measured_height)
        return QSize(super().sizeHint().width(), 0)

    def minimumSizeHint(self) -> QSize:
        if self._measured_height > 0:
            return QSize(0, self._measured_height)
        return QSize(0, 0)

    def _schedule_height_updates(self) -> None:
        for delay_ms in (0, 150, 500, 1000):
            QTimer.singleShot(delay_ms, self._update_height_to_contents)

    def _update_height_to_contents(self) -> None:
        self.page().runJavaScript(
            """
            Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );
            """,
            self._apply_measured_height,
        )

    def _apply_measured_height(self, height: int | float | None) -> None:
        if not isinstance(height, (int, float)):
            return
        target_height = max(1, int(height) + 8)
        self._measured_height = target_height
        self.setMinimumHeight(target_height)
        self.setMaximumHeight(target_height)
        self.updateGeometry()


class FormulaView(QWebEngineView):
    def __init__(
        self,
        formula: str,
        *,
        min_height: int = 42,
        background: str = "#14181d",
        centered: bool = False,
    ) -> None:
        super().__init__()
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(f"background: {background}; border: none;")
        self.page().setBackgroundColor(QColor(background))
        self.setMinimumHeight(min_height)
        self.setMaximumHeight(min_height)
        self.setHtml(
            render_mathjax_document(
                "Formula",
                formula=formula,
                compact=True,
                background=background,
                centered=centered,
            ),
            QUrl.fromLocalFile(str(ASSETS_ROOT) + "/"),
        )
