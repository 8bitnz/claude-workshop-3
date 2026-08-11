"""Sanity checks for the engagement pricing maths."""

from datetime import datetime, timedelta, timezone

from engagements import (
    CAPACITY_AMBER_DAYS,
    MONTHLY_CAPACITY_DAYS,
    PENDING_STALE_DAYS,
    STATUSES,
    capacity_status,
    committed_days,
    is_stale_pending,
    months_present,
    pending_age_days,
    scope_engagement,
)


def _row(logged_at, days, status="won"):
    return {"logged_at": logged_at, "days": str(days), "status": status}


def test_fees_only():
    e = scope_engagement("Acme", "Jordan", "Advisory", "Referral", days=5, pass_through=0)
    assert e.fees == 9250.0                 # 5 x 1850
    assert e.subtotal_ex_gst == 9250.0
    assert e.gst == 1387.5                   # 9250 x 0.15
    assert e.total_inc_gst == 10637.5


def test_with_pass_through_handling():
    e = scope_engagement("Beta", "Sam", "Rebuild", "LinkedIn", days=2, pass_through=1000)
    assert e.fees == 3700.0                  # 2 x 1850
    assert e.handling == 100.0               # 1000 x 0.10
    assert e.subtotal_ex_gst == 4800.0       # 3700 + 1000 + 100
    assert e.gst == 720.0                    # 4800 x 0.15
    assert e.total_inc_gst == 5520.0


def test_half_days_and_rounding():
    e = scope_engagement("Gamma", "Robin", "Scoping", "Website", days=1.5, pass_through=333.33)
    assert e.fees == 2775.0                  # 1.5 x 1850
    assert e.handling == 33.33               # 333.33 x 0.10
    assert e.subtotal_ex_gst == 3141.66
    assert e.total_inc_gst == 3612.91


def test_committed_days_is_per_calendar_month_and_won_only():
    rows = [
        _row("2026-08-03T09:00:00+12:00", 5, "won"),
        _row("2026-08-20T09:00:00+12:00", 2.5, "won"),
        _row("2026-08-22T09:00:00+12:00", 3, "pending"),   # not committed
        _row("2026-08-25T09:00:00+12:00", 4, "lost"),      # not committed
        _row("2026-07-28T09:00:00+12:00", 4, "won"),       # prior month
    ]
    assert committed_days(rows, month="2026-08") == 7.5       # won only, this month
    assert committed_days(rows, month="2026-07") == 4.0       # separate month
    # Widening statuses lets pending count as provisional load.
    assert committed_days(rows, month="2026-08", statuses=("won", "pending")) == 10.5


def test_months_present():
    rows = [
        _row("2026-08-03T09:00:00+12:00", 5),
        _row("2026-09-01T09:00:00+12:00", 2),
        _row("2026-08-20T09:00:00+12:00", 1),
    ]
    assert months_present(rows) == ["2026-08", "2026-09"]


def test_default_status_is_pending():
    e = scope_engagement("Acme", "Jordan", "Advisory", "Referral", days=1)
    assert e.status == "pending"
    assert "pending" in STATUSES and "won" in STATUSES and "lost" in STATUSES


def test_invalid_status_rejected():
    try:
        scope_engagement("Acme", "J", "x", "y", days=1, status="maybe")
    except ValueError:
        return
    raise AssertionError("expected ValueError for bad status")


def test_pending_over_seven_days_is_stale():
    now = datetime(2026, 8, 20, tzinfo=timezone.utc)
    fresh = {"status": "pending", "logged_at": (now - timedelta(days=5)).isoformat()}
    stale = {"status": "pending", "logged_at": (now - timedelta(days=8)).isoformat()}
    won_old = {"status": "won", "logged_at": (now - timedelta(days=30)).isoformat()}
    assert pending_age_days(fresh, now) == 5
    assert is_stale_pending(fresh, now) is False           # 5 days, still fresh
    assert is_stale_pending(stale, now) is True            # 8 days > 7
    assert pending_age_days(won_old, now) is None          # not pending
    assert is_stale_pending(won_old, now) is False
    assert PENDING_STALE_DAYS == 7


def test_capacity_thresholds():
    assert MONTHLY_CAPACITY_DAYS == 14
    assert CAPACITY_AMBER_DAYS == 11
    assert capacity_status(8) == "ok"
    assert capacity_status(11) == "ok"        # at threshold, not past it
    assert capacity_status(11.5) == "amber"   # past 11
    assert capacity_status(14) == "amber"     # at ceiling, not over
    assert capacity_status(14.5) == "red"     # past 14


def test_negative_rejected():
    try:
        scope_engagement("X", "Y", "Z", "Src", days=-1, pass_through=0)
    except ValueError:
        return
    raise AssertionError("expected ValueError for negative days")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("All tests passed.")
