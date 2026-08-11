"""One-page proposal PDF, branded as Keel.

Writes a self-contained PDF with the standard 14 fonts (no embedding, no third-
party libraries) so the whole app stays install-free. Helvetica sets the text,
Courier the figures — monospace makes the money column align to the cent.

Palette: hull green header, a brass rule as the waterline, ink body.
"""

from __future__ import annotations

import os
import re
from datetime import datetime

from engagements import DAY_RATE, GST_RATE, HANDLING_RATE

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")

# Page (A4) and margins, in PDF points.
W, H = 595.28, 841.89
M = 56
HEADER_H = 132

# Brand palette (r, g, b in 0..1).
HULL = (0.106, 0.243, 0.204)    # hull green
BRASS = (0.706, 0.560, 0.337)   # brass rule
INK = (0.106, 0.118, 0.122)
MUTED = (0.42, 0.45, 0.48)
WHITE = (1.0, 1.0, 1.0)
MIST = (0.83, 0.87, 0.84)       # pale text on the green header

# Font resource names -> Courier is F3/F4 so figures come out monospaced.
HELV, HELV_BOLD, MONO, MONO_BOLD = "F1", "F2", "F3", "F4"
_MONO_EM = 0.6  # Courier advance width per glyph, in em


# --- low-level PDF drawing ---------------------------------------------------

def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _fill(c) -> str:
    return f"{c[0]:.3f} {c[1]:.3f} {c[2]:.3f} rg"


def _stroke(c) -> str:
    return f"{c[0]:.3f} {c[1]:.3f} {c[2]:.3f} RG"


def _rect(x, y, w, h, c) -> str:
    return f"{_fill(c)} {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f"


def _rule(x1, x2, top, c, width) -> str:
    """A horizontal rule at ``top`` points from the top of the page."""
    y = H - top
    return f"{_stroke(c)} {width:.2f} w {x1:.2f} {y:.2f} m {x2:.2f} {y:.2f} l S"


def _text(x, top, s, font=HELV, size=11, color=INK, tracking=0.0) -> str:
    y = H - top
    return (
        f"BT /{font} {size:.2f} Tf {tracking:.2f} Tc {_fill(color)} "
        f"1 0 0 1 {x:.2f} {y:.2f} Tm ({_esc(s)}) Tj ET"
    )


def _mono_right(x_right, top, s, size=11, color=INK, bold=False) -> str:
    width = len(s) * size * _MONO_EM
    return _text(x_right - width, top, s, font=(MONO_BOLD if bold else MONO), size=size, color=color)


def _wrap(text: str, max_chars: int, max_lines: int = 5) -> list[str]:
    words = (text or "").split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= max_chars:
            cur = f"{cur} {w}" if cur else w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if not lines:
        return ["—"]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;") + "…"
    return lines


# --- helpers -----------------------------------------------------------------

def _money(value) -> str:
    return f"${float(value or 0):,.2f}"


def _num(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _days_label(value) -> str:
    return f"{_num(value):g}"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-") or "client"


def proposal_filename(engagement: dict, date: datetime | None = None) -> str:
    date = date or datetime.now()
    return f"keel-proposal-{_slug(engagement.get('company', ''))}-{date:%Y%m%d}.pdf"


# --- the proposal ------------------------------------------------------------

def build_proposal_pdf(engagement: dict, out_path: str | None = None,
                       date: datetime | None = None) -> str:
    """Render a one-page Keel proposal for ``engagement`` and save it.

    Returns the path written. ``engagement`` is a row dict (as stored in the
    CSV or produced by ``Engagement.as_row()``).
    """
    date = date or datetime.now()
    if out_path is None:
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        out_path = os.path.join(EXPORTS_DIR, proposal_filename(engagement, date))
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    company = engagement.get("company", "") or "—"
    contact = engagement.get("contact", "")
    need = engagement.get("need", "")
    source = engagement.get("source", "") or "—"
    day_rate = _num(engagement.get("day_rate")) or DAY_RATE
    days = _num(engagement.get("days"))
    fees = _num(engagement.get("fees"))
    pass_through = _num(engagement.get("pass_through"))
    handling = _num(engagement.get("handling"))
    handling_rate = _num(engagement.get("handling_rate")) or HANDLING_RATE
    subtotal = _num(engagement.get("subtotal_ex_gst"))
    gst = _num(engagement.get("gst"))
    gst_rate = _num(engagement.get("gst_rate")) or GST_RATE
    total = _num(engagement.get("total_inc_gst"))

    date_str = f"{date:%-d %B %Y}"
    ref = f"KEEL-{date:%Y%m%d}-{_slug(company).upper().replace('-', '')[:4] or 'CLNT'}"
    x_right = W - M
    c: list[str] = []

    # Header band + brass waterline.
    c.append(_rect(0, H - HEADER_H, W, HEADER_H, HULL))
    c.append(_rule(0, W, HEADER_H, BRASS, 3))
    c.append(_rule(0, W, HEADER_H + 4.5, BRASS, 0.6))
    c.append(_text(M, 74, "KEEL", font=HELV_BOLD, size=32, color=WHITE, tracking=7))
    c.append(_text(M + 3, 97, "FRACTIONAL CTO PRACTICE", font=HELV, size=9, color=BRASS, tracking=2.4))
    rx = W - M - 150
    c.append(_text(rx, 58, "PROPOSAL", font=HELV_BOLD, size=12, color=BRASS, tracking=2))
    c.append(_text(rx, 80, f"Prepared {date_str}", font=HELV, size=9.5, color=MIST))
    c.append(_text(rx, 96, ref, font=MONO, size=9, color=MIST))

    # Prepared-for block + meta.
    y = HEADER_H + 44
    c.append(_text(M, y, "PREPARED FOR", font=HELV, size=9, color=MUTED, tracking=1.6))
    c.append(_text(M, y + 21, company, font=HELV_BOLD, size=17, color=INK))
    if contact:
        c.append(_text(M, y + 41, contact, font=HELV, size=11, color=MUTED))
    c.append(_text(rx, y, "DATE", font=HELV, size=9, color=MUTED, tracking=1.6))
    c.append(_text(rx, y + 16, date_str, font=MONO, size=10.5, color=INK))
    c.append(_text(rx, y + 38, "SOURCE", font=HELV, size=9, color=MUTED, tracking=1.6))
    c.append(_text(rx, y + 54, source[:22], font=MONO, size=10.5, color=INK))

    # The engagement.
    y = HEADER_H + 44 + 82
    c.append(_text(M, y, "THE ENGAGEMENT", font=HELV_BOLD, size=10, color=BRASS, tracking=1.4))
    y += 22
    for line in _wrap(need, 82, max_lines=4):
        c.append(_text(M, y, line, font=HELV, size=11.5, color=INK))
        y += 16

    # Scope & fees table.
    y += 18
    c.append(_text(M, y, "SCOPE & FEES", font=HELV_BOLD, size=10, color=BRASS, tracking=1.4))
    y += 8
    c.append(_rule(M, x_right, y, BRASS, 0.6))

    def line_item(label, sub, amount, *, big=False):
        nonlocal y
        y += 24 if not big else 28
        c.append(_text(M, y, label, font=(HELV_BOLD if big else HELV),
                       size=(13 if big else 11.5), color=(HULL if big else INK)))
        c.append(_mono_right(x_right, y, amount, size=(13 if big else 11),
                             color=(HULL if big else INK), bold=big))
        if sub:
            y += 13
            c.append(_text(M, y, sub, font=MONO, size=9, color=MUTED))

    line_item("Professional fees",
              f"{_days_label(days)} days  ×  {_money(day_rate)} / day", _money(fees))
    if pass_through:
        line_item("Pass-through costs", None, _money(pass_through))
        line_item(f"Handling ({handling_rate * 100:.0f}%)",
                  f"on {_money(pass_through)}", _money(handling))

    y += 20
    c.append(_rule(M, x_right, y, MUTED, 0.4))
    line_item("Subtotal", "excluding GST", _money(subtotal))
    line_item(f"GST ({gst_rate * 100:.0f}%)", None, _money(gst))
    y += 18
    c.append(_rule(M, x_right, y, BRASS, 2))
    line_item("Total", "including GST", _money(total), big=True)

    # Footer.
    foot = H - 58
    c.append(_rule(M, x_right, foot - 16, BRASS, 0.8))
    c.append(_text(M, foot, "Valid for 30 days. Total includes GST at "
                   f"{gst_rate * 100:.0f}%; pass-through costs carry "
                   f"{handling_rate * 100:.0f}% handling.",
                   font=HELV, size=8.5, color=MUTED))
    c.append(_text(M, foot + 13, "Keel  ·  Fractional CTO practice", font=HELV, size=8.5, color=HULL))

    _write_pdf(out_path, "\n".join(c))
    return out_path


def _write_pdf(out_path: str, content: str) -> None:
    stream = content.encode("cp1252", "replace")
    fonts = ("Helvetica", "Helvetica-Bold", "Courier", "Courier-Bold")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] "
        b"/Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R /F4 8 0 R >> >> "
        b"/Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]
    for i, name in enumerate(fonts):
        objs.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>"
            % name.encode("ascii")
        )

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref_pos = len(out)
    count = len(objs) + 1
    out += b"xref\n0 %d\n0000000000 65535 f \n" % count
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (count, xref_pos)

    with open(out_path, "wb") as fh:
        fh.write(out)


def _demo_engagement() -> dict:
    """A worked example so `python3 proposal.py` produces a file to look at."""
    from engagements import scope_engagement
    return scope_engagement(
        "Acme Robotics", "Jordan Lee — Founder",
        "Stabilise the platform rebuild, set the engineering hiring plan, and "
        "chair the architecture review for the next quarter.",
        "Referral", days=6, pass_through=1200, status="pending",
    ).as_row()


if __name__ == "__main__":
    path = build_proposal_pdf(_demo_engagement())
    print(f"Wrote {path}")
