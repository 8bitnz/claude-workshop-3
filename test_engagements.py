"""Sanity checks for the engagement pricing maths."""

from engagements import scope_engagement


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
