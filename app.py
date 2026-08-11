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
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from proposal import build_proposal_pdf, proposal_filename
from engagements import (
    CAPACITY_AMBER_DAYS,
    DAY_RATE,
    DEFAULT_STATUS,
    GST_RATE,
    HANDLING_RATE,
    MONTHLY_CAPACITY_DAYS,
    PENDING_STALE_DAYS,
    STATUSES,
    capacity_status,
    committed_days,
    is_stale_pending,
    load_engagements,
    months_present,
    pending_age_days,
    save_engagement,
    scope_engagement,
    status_of,
)

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")


def money(value) -> str:
    return f"${float(value):,.2f}"


def _days_label(value) -> str:
    """Render 8 not 8.0, but keep 8.5."""
    return f"{float(value):g}"


def render_rows(engagements: list[dict]) -> str:
    if not engagements:
        return (
            '<tr class="empty"><td colspan="9">No engagements logged yet — '
            "scope your first enquiry above.</td></tr>"
        )
    cells = []
    for i, e in enumerate(engagements):
        st = status_of(e)
        badge = f"<span class='badge badge-{html.escape(st)}'>{html.escape(st)}</span>"
        flag, row_cls = "", ""
        if is_stale_pending(e):
            age = pending_age_days(e)
            flag = f" <span class='flag' title='Pending more than {PENDING_STALE_DAYS} days'>&#9888; {age}d</span>"
            row_cls = " class='stale'"
        cells.append(
            f"<tr{row_cls}>"
            f"<td class='when'>{html.escape(e['logged_at'])}</td>"
            f"<td><strong>{html.escape(e['company'])}</strong><br>"
            f"<span class='muted'>{html.escape(e['contact'])}</span></td>"
            f"<td>{html.escape(e['need'])}</td>"
            f"<td><span class='pill'>{html.escape(e['source'])}</span></td>"
            f"<td class='status'>{badge}{flag}</td>"
            f"<td class='num'>{html.escape(str(e['days']))}</td>"
            f"<td class='num'>{money(e['fees'])}</td>"
            f"<td class='num total'>{money(e['total_inc_gst'])}</td>"
            f"<td class='action'><a class='plink' href='/proposal?i={i}'>PDF &#8595;</a></td>"
            "</tr>"
        )
    return "\n".join(cells)


def render_capacity(engagements: list[dict]) -> str:
    """One capacity bar per calendar month. Only won days count as committed."""
    current = datetime.now().strftime("%Y-%m")
    months = sorted(set(months_present(engagements)) | {current})
    cards = []
    for m in months:
        committed = committed_days(engagements, month=m)  # won only
        state = capacity_status(committed)
        remaining = MONTHLY_CAPACITY_DAYS - committed
        fill = min(committed / MONTHLY_CAPACITY_DAYS * 100, 100) if MONTHLY_CAPACITY_DAYS else 0
        if state == "red":
            note = f"Over capacity by {_days_label(committed - MONTHLY_CAPACITY_DAYS)} days"
        elif state == "amber":
            note = f"{_days_label(remaining)} days left — nearing capacity"
        else:
            note = f"{_days_label(remaining)} days available"
        label = datetime.strptime(m, "%Y-%m").strftime("%b %Y")
        current_cls = " cap-current" if m == current else ""
        amber_left = CAPACITY_AMBER_DAYS / MONTHLY_CAPACITY_DAYS * 100
        cards.append(
            f"<div class='cap-card cap-{state}{current_cls}'>"
            f"<div class='cap-head'><span class='cap-label'>{html.escape(label)}</span>"
            f"<span class='cap-figure'><b class='cap-committed'>{_days_label(committed)}</b>"
            f"<span class='cap-of'>/ {MONTHLY_CAPACITY_DAYS} days</span></span></div>"
            f"<div class='cap-track' role='progressbar' aria-valuenow='{_days_label(committed)}' "
            f"aria-valuemin='0' aria-valuemax='{MONTHLY_CAPACITY_DAYS}'>"
            f"<div class='cap-fill' style='width:{fill:.1f}%'></div>"
            f"<div class='cap-mark' style='left:{amber_left:.2f}%'></div></div>"
            f"<div class='cap-note'>{html.escape(note)}</div>"
            "</div>"
        )
    return "\n".join(cards)


def render_page(engagements: list[dict], flash: str = "") -> str:
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        template = fh.read()
    pipeline_inc = sum(float(e["total_inc_gst"]) for e in engagements)

    stale = [e for e in engagements if is_stale_pending(e)]
    if stale:
        noun = "enquiry" if len(stale) == 1 else "enquiries"
        alerts = (
            f'<div class="flash warn">&#9888; {len(stale)} pending {noun} '
            f"over {PENDING_STALE_DAYS} days old — time to follow up.</div>"
        )
    else:
        alerts = ""

    counts = {s: sum(1 for e in engagements if status_of(e) == s) for s in STATUSES}

    tokens = {
        "{{DAY_RATE}}": f"{DAY_RATE:,.0f}",
        "{{DAY_RATE_RAW}}": str(DAY_RATE),
        "{{HANDLING_PCT}}": f"{HANDLING_RATE * 100:.0f}",
        "{{HANDLING_RAW}}": str(HANDLING_RATE),
        "{{GST_PCT}}": f"{GST_RATE * 100:.0f}",
        "{{GST_RAW}}": str(GST_RATE),
        "{{CAP_CEILING}}": str(MONTHLY_CAPACITY_DAYS),
        "{{CAP_AMBER}}": str(CAPACITY_AMBER_DAYS),
        "{{ROWS}}": render_rows(engagements),
        "{{CAPACITY}}": render_capacity(engagements),
        "{{COUNT}}": str(len(engagements)),
        "{{PIPELINE}}": money(pipeline_inc),
        "{{WON}}": str(counts["won"]),
        "{{PENDING}}": str(counts["pending"]),
        "{{LOST}}": str(counts["lost"]),
        "{{FLASH}}": flash,
        "{{ALERTS}}": alerts,
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

    def _send_pdf(self, data: bytes, filename: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Disposition", f'inline; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/proposal":
            self._handle_proposal(parse_qs(parsed.query))
            return
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

    def _handle_proposal(self, params: dict) -> None:
        engagements = load_engagements()
        try:
            i = int(params.get("i", ["-1"])[0])
        except ValueError:
            i = -1
        if not (0 <= i < len(engagements)):
            self.send_error(404, "No such engagement")
            return
        engagement = engagements[i]
        path = build_proposal_pdf(engagement)   # saves into exports/
        with open(path, "rb") as fh:
            self._send_pdf(fh.read(), proposal_filename(engagement))

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
        status = field("status", DEFAULT_STATUS).lower()
        if status not in STATUSES:
            status = DEFAULT_STATUS
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

        engagement = scope_engagement(company, contact, need, source, days, pass_through,
                                      status=status)
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
