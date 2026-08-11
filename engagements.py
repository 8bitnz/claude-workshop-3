"""Core logic for the fractional CTO engagement book.

Kept free of any web framework so the pricing maths can be tested on its own
and reused from anywhere (the web app, a REPL, or a future CLI).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# --- Practice settings -------------------------------------------------------

DAY_RATE = 1850.0        # NZD per day, GST-exclusive
HANDLING_RATE = 0.10     # 10% handling added on top of pass-through costs
GST_RATE = 0.15          # New Zealand GST, 15%

MONTHLY_CAPACITY_DAYS = 14   # ceiling of billable days in a month
CAPACITY_AMBER_DAYS = 11     # bar turns amber once committed days pass this

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "engagements.csv")

# Column order for data/engagements.csv. Every logged engagement is one row.
FIELDNAMES = [
    "logged_at",
    "company",
    "contact",
    "need",
    "source",
    "days",
    "day_rate",
    "fees",
    "pass_through",
    "handling_rate",
    "handling",
    "subtotal_ex_gst",
    "gst_rate",
    "gst",
    "total_inc_gst",
]


def _round2(value: float) -> float:
    """Round to cents. Kept in one place so every figure rounds the same way."""
    return round(value + 1e-9, 2)


@dataclass
class Engagement:
    """A single scoped enquiry, priced and ready to save as a CSV line."""

    logged_at: str
    company: str
    contact: str
    need: str
    source: str
    days: float
    day_rate: float
    fees: float
    pass_through: float
    handling_rate: float
    handling: float
    subtotal_ex_gst: float
    gst_rate: float
    gst: float
    total_inc_gst: float

    def as_row(self) -> dict:
        return asdict(self)


def scope_engagement(
    company: str,
    contact: str,
    need: str,
    source: str,
    days: float,
    pass_through: float = 0.0,
    *,
    day_rate: float = DAY_RATE,
    handling_rate: float = HANDLING_RATE,
    gst_rate: float = GST_RATE,
    logged_at: str | None = None,
) -> Engagement:
    """Scope and price an enquiry.

    Fees are days x day rate. Pass-through costs carry a handling charge on top.
    The two together form the GST-exclusive subtotal; GST is added to give the
    GST-inclusive total.
    """
    days = float(days)
    pass_through = float(pass_through)
    if days < 0 or pass_through < 0:
        raise ValueError("days and pass-through costs cannot be negative")

    fees = _round2(days * day_rate)
    handling = _round2(pass_through * handling_rate)
    subtotal_ex_gst = _round2(fees + pass_through + handling)
    gst = _round2(subtotal_ex_gst * gst_rate)
    total_inc_gst = _round2(subtotal_ex_gst + gst)

    return Engagement(
        logged_at=logged_at or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        company=company.strip(),
        contact=contact.strip(),
        need=need.strip(),
        source=source.strip(),
        days=days,
        day_rate=day_rate,
        fees=fees,
        pass_through=_round2(pass_through),
        handling_rate=handling_rate,
        handling=handling,
        subtotal_ex_gst=subtotal_ex_gst,
        gst_rate=gst_rate,
        gst=gst,
        total_inc_gst=total_inc_gst,
    )


def _ensure_csv() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=FIELDNAMES).writeheader()


def save_engagement(engagement: Engagement) -> None:
    """Append one engagement as a line in data/engagements.csv."""
    _ensure_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=FIELDNAMES).writerow(engagement.as_row())


def load_engagements() -> list[dict]:
    """Return every saved engagement, newest first."""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return list(reversed(rows))


def committed_days(engagements: list[dict], month: str | None = None) -> float:
    """Sum billable days committed within a calendar month.

    ``month`` is a ``YYYY-MM`` string; defaults to the current local month.
    Engagements are matched on the ``YYYY-MM`` prefix of their ``logged_at``.
    """
    if month is None:
        month = datetime.now(timezone.utc).astimezone().strftime("%Y-%m")
    total = 0.0
    for e in engagements:
        if str(e.get("logged_at", ""))[:7] == month:
            try:
                total += float(e.get("days") or 0)
            except (TypeError, ValueError):
                continue
    return _round2(total)


def capacity_status(committed: float) -> str:
    """Traffic-light state for the capacity bar: 'ok', 'amber' or 'red'."""
    if committed > MONTHLY_CAPACITY_DAYS:
        return "red"
    if committed > CAPACITY_AMBER_DAYS:
        return "amber"
    return "ok"
