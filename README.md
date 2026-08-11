# Engagement Book

A tiny engagement book for a one-person **fractional CTO** practice. Runs in your
browser, no dependencies beyond Python itself.

Log an enquiry — **company, contact, what they need, where it came from** — scope
it, and every engagement is saved as a line in `data/engagements.csv`.

## Pricing

| Setting | Value |
| --- | --- |
| Day rate | **$1,850** / day (GST-exclusive) |
| Handling on pass-through costs | **10%** on top |
| GST | **15%** (New Zealand), shown as a GST-inclusive total |

For each enquiry:

```
fees            = days × $1,850
handling        = pass-through costs × 10%
subtotal (ex)   = fees + pass-through + handling
GST             = subtotal × 15%
total (incl)    = subtotal + GST
```

A **live quote** on the page recalculates as you type, and the figures are saved
exactly as shown.

## Status & follow-ups

Every engagement is marked **pending**, **won**, or **lost** (new enquiries
default to pending). The book shows a coloured badge per row and a
won / pending / lost tally.

Any enquiry left **pending for more than 7 days** is flagged — the row shows a
`⚠ Nd` age marker and a banner at the top reminds you how many need a follow-up.
The threshold is `PENDING_STALE_DAYS` in `engagements.py`.

## Capacity — per calendar month

A capacity bar is shown **for each calendar month** that has activity (plus the
current month), against a ceiling of **14 billable days**. Each bar runs green,
turns **amber past 11 days**, and **red past 14** (over capacity), with a marker
at 11 and a note on days remaining or days over.

Only **won** days count toward committed capacity — pending is potential, lost
is gone. A month is decided by the date an engagement was logged. Thresholds
live as constants (`MONTHLY_CAPACITY_DAYS`, `CAPACITY_AMBER_DAYS`) in
`engagements.py`.

## Run it

```bash
python3 app.py
```

Then open **http://localhost:8000** (it tries to open your browser for you).
No `pip install` needed — it uses only the Python standard library.

To change the port: `PORT=9000 python3 app.py`.

## Data

Every engagement is appended to `data/engagements.csv` with these columns:

```
logged_at, company, contact, need, source, status,
days, day_rate, fees, pass_through, handling_rate, handling,
subtotal_ex_gst, gst_rate, gst, total_inc_gst
```

Older CSVs written before `status` existed are upgraded in place automatically
on first run (the column is added with a `pending` default; existing figures are
untouched).

Open it in any spreadsheet, or keep it under version control.

## Proposal PDF (branded as Keel)

Every engagement in the book has a **PDF ↓** link that generates a one-page
proposal and saves it into `exports/`:

- **Hull-green** header band with the **Keel** wordmark
- A **brass** rule as the waterline, and brass rules through the fee table
- **Monospaced (Courier) figures** so the money column aligns to the cent
- A clean **Scope & fees** table: day rate, days, pass-through + handling,
  subtotal, GST, and the GST-inclusive total

Generate one from the command line too (writes a worked example to `exports/`):

```bash
python3 proposal.py
```

The PDF is written with the standard PDF fonts and no third-party libraries, so
export needs no `pip install` either. `exports/keel-sample-proposal.pdf` is a
committed example; other generated PDFs are git-ignored.

## Tests

```bash
python3 test_engagements.py
```

## Layout

```
app.py              # web server + page routing (stdlib http.server)
engagements.py      # pricing maths + CSV read/write (framework-free, testable)
proposal.py         # one-page Keel proposal PDF (stdlib, no PDF library)
templates/index.html# the page: enquiry form, live quote, the book
test_engagements.py # pricing, capacity, status + proposal checks
data/engagements.csv# your engagement book
exports/            # generated proposal PDFs land here
```
