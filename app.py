"""Engagement Book — a one-person fractional CTO practice, in your browser.

Log an enquiry, scope it (days x day rate + pass-through with handling, GST on
top), and every engagement is saved as a line in data/engagements.csv.

Runs on the Python standard library only:

    python3 app.py

then open http://localhost:8000 in your browser.
"""

from __future__ import annotations

import html
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from engagements import (
    DAY_RATE,
    GST_RATE,
    HANDLING_RATE,
    load_engagements,
    save_engagement,
    scope_engagement,
)

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")


def money(value) -> str:
    return f"${float(value):,.2f}"


def render_rows(engagements: list[dict]) -> str:
    if not engagements:
        return (
            '<tr class="empty"><td colspan="7">No engagements logged yet — '
            "scope your first enquiry above.</td></tr>"
        )
    cells = []
    for e in engagements:
        cells.append(
            "<tr>"
            f"<td class='when'>{html.escape(e['logged_at'])}</td>"
            f"<td><strong>{html.escape(e['company'])}</strong><br>"
            f"<span class='muted'>{html.escape(e['contact'])}</span></td>"
            f"<td>{html.escape(e['need'])}</td>"
            f"<td><span class='pill'>{html.escape(e['source'])}</span></td>"
            f"<td class='num'>{html.escape(str(e['days']))}</td>"
            f"<td class='num'>{money(e['fees'])}</td>"
            f"<td class='num total'>{money(e['total_inc_gst'])}</td>"
            "</tr>"
        )
    return "\n".join(cells)


def render_page(engagements: list[dict], flash: str = "") -> str:
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        template = fh.read()
    pipeline_inc = sum(float(e["total_inc_gst"]) for e in engagements)
    tokens = {
        "{{DAY_RATE}}": f"{DAY_RATE:,.0f}",
        "{{DAY_RATE_RAW}}": str(DAY_RATE),
        "{{HANDLING_PCT}}": f"{HANDLING_RATE * 100:.0f}",
        "{{HANDLING_RAW}}": str(HANDLING_RATE),
        "{{GST_PCT}}": f"{GST_RATE * 100:.0f}",
        "{{GST_RAW}}": str(GST_RATE),
        "{{ROWS}}": render_rows(engagements),
        "{{COUNT}}": str(len(engagements)),
        "{{PIPELINE}}": money(pipeline_inc),
        "{{FLASH}}": flash,
    }
    for token, value in tokens.items():
        template = template.replace(token, value)
    return template


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, body: str, status: int = 200) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        params = parse_qs(parsed.query)
        flash = ""
        if params.get("saved"):
            company = html.escape(params.get("company", [""])[0])
            total = html.escape(params.get("total", [""])[0])
            flash = (
                f'<div class="flash">Logged <strong>{company}</strong> — '
                f"GST-inclusive total {total}. Saved to data/engagements.csv.</div>"
            )
        self._send_html(render_page(load_engagements(), flash))

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/add":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))

        def field(name: str, default: str = "") -> str:
            return form.get(name, [default])[0].strip()

        company = field("company")
        contact = field("contact")
        need = field("need")
        source = field("source")
        if not company:
            self._send_html(render_page(load_engagements(),
                            '<div class="flash error">Company is required.</div>'), 400)
            return
        try:
            days = float(field("days", "0") or 0)
            pass_through = float(field("pass_through", "0") or 0)
        except ValueError:
            self._send_html(render_page(load_engagements(),
                            '<div class="flash error">Days and costs must be numbers.</div>'), 400)
            return

        engagement = scope_engagement(company, contact, need, source, days, pass_through)
        save_engagement(engagement)

        from urllib.parse import urlencode
        query = urlencode({"saved": "1", "company": company, "total": money(engagement.total_inc_gst)})
        self._redirect(f"/?{query}")

    def log_message(self, *args) -> None:  # keep the console quiet
        pass


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print("Engagement Book — fractional CTO practice")
    print(f"  Day rate ${DAY_RATE:,.0f}  |  Handling {HANDLING_RATE*100:.0f}%  |  GST {GST_RATE*100:.0f}%")
    print(f"  Running at {url}  (Ctrl+C to stop)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
