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

# Enquiry lifecycle. Capacity counts only "won" (firmly committed) days.
STATUSES = ("pending", "won", "lost")
DEFAULT_STATUS = "pending"
PENDING_STALE_DAYS = 7       # a pending enquiry older than this needs chasing

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "engagements.csv")

# Column order for data/engagements.csv. Every logged engagement is one row.
FIELDNAMES = [
    "logged_at",
    "company",
    "contact",
    "need",
    "source",
    "status",
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
    status: str
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
    status: str = DEFAULT_STATUS,
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
    status = (status or DEFAULT_STATUS).strip().lower()
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")

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
        status=status,
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
        return
    _migrate_csv()


def _migrate_csv() -> None:
    """Upgrade an older CSV in place so appends stay column-aligned.

    Rewrites the file with the current ``FIELDNAMES`` header, backfilling any
    newly added columns (e.g. ``status`` defaults to pending). A no-op when the
    header already matches.
    """
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames == FIELDNAMES:
            return
        rows = list(reader)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            out = {k: row.get(k, "") for k in FIELDNAMES}
            if not out.get("status"):
                out["status"] = DEFAULT_STATUS
            writer.writerow(out)


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
    for row in rows:
        if not row.get("status"):
            row["status"] = DEFAULT_STATUS
    return list(reversed(rows))


def status_of(engagement: dict) -> str:
    return (engagement.get("status") or DEFAULT_STATUS).strip().lower()


def month_of(engagement: dict) -> str:
    """The ``YYYY-MM`` calendar month an engagement was logged in."""
    return str(engagement.get("logged_at", ""))[:7]


def committed_days(
    engagements: list[dict],
    month: str | None = None,
    statuses: tuple[str, ...] = ("won",),
) -> float:
    """Sum billable days committed within a calendar month.

    ``month`` is a ``YYYY-MM`` string; defaults to the current local month.
    By default only ``won`` engagements count toward committed capacity; pass
    ``statuses`` to widen (e.g. include ``pending`` as provisional load).
    """
    if month is None:
        month = datetime.now(timezone.utc).astimezone().strftime("%Y-%m")
    total = 0.0
    for e in engagements:
        if month_of(e) != month:
            continue
        if statuses and status_of(e) not in statuses:
            continue
        try:
            total += float(e.get("days") or 0)
        except (TypeError, ValueError):
            continue
    return _round2(total)


def months_present(engagements: list[dict]) -> list[str]:
    """Sorted list of calendar months (YYYY-MM) that have any engagement."""
    months = {month_of(e) for e in engagements if month_of(e)}
    return sorted(months)


def capacity_status(committed: float) -> str:
    """Traffic-light state for the capacity bar: 'ok', 'amber' or 'red'."""
    if committed > MONTHLY_CAPACITY_DAYS:
        return "red"
    if committed > CAPACITY_AMBER_DAYS:
        return "amber"
    return "ok"


def pending_age_days(engagement: dict, now: datetime | None = None) -> int | None:
    """Whole days an engagement has sat *pending*.

    Returns ``None`` if it is not pending or has no parseable logged date.
    """
    if status_of(engagement) != "pending":
        return None
    try:
        logged = datetime.fromisoformat(str(engagement.get("logged_at", "")))
    except ValueError:
        return None
    if logged.tzinfo is None:
        logged = logged.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    return max((now - logged).days, 0)


def is_stale_pending(engagement: dict, now: datetime | None = None) -> bool:
    """True when a pending enquiry has gone unanswered for too long."""
    age = pending_age_days(engagement, now)
    return age is not None and age > PENDING_STALE_DAYS
