from __future__ import annotations

from html import escape


def format_history_html(history: list[dict], *, has_loaded_results: bool) -> str:
    if not history:
        if has_loaded_results:
            return (
                "<p><b>Preset or saved session loaded.</b></p>"
                "<p>You can inspect results immediately, or press Reset to start a guided session.</p>"
            )
        return (
            "<p><b>No entries yet.</b></p>"
            "<p>The wizard will keep a running history of each answer here.</p>"
        )

    chunks = []
    for item in history:
        answer_html = item.get("answer_html")
        if answer_html is None:
            answer_html = escape(item["answer"]).replace("\n", "<br>")
        chunks.append(
            "<div style='margin-bottom:14px;'>"
            f"<div style='font-weight:700; color:#e7edf5;'>{escape(item['question'])}</div>"
            f"<div style='margin-top:4px; color:#c9d3df;'>{answer_html}</div>"
            "</div>"
        )
    return "".join(chunks)


def format_answer_for_history(step: str, answer_value, *, n: int | None, toggle_values: dict) -> tuple[str, str]:
    if step in toggle_values:
        for label, value in toggle_values[step]:
            if value == answer_value:
                return label, escape(label)
        text = str(answer_value)
        return text, escape(text)

    if isinstance(answer_value, list):
        if step == "ask_alt_basis_vectors" and n is not None:
            vectors = []
            for col in range(n):
                start = col * n
                vec = answer_value[start:start + n]
                vectors.append(f"e{col} = ({', '.join(vec)})")
            text = "; ".join(vectors)
            html = "<br>".join(escape(vec) for vec in vectors)
            return text, html
        text = ", ".join(answer_value)
        return text, escape(text)

    text = str(answer_value)
    return text, escape(text)
