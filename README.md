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
logged_at, company, contact, need, source,
days, day_rate, fees, pass_through, handling_rate, handling,
subtotal_ex_gst, gst_rate, gst, total_inc_gst
```

Open it in any spreadsheet, or keep it under version control.

## Tests

```bash
python3 test_engagements.py
```

## Layout

```
app.py              # web server + page routing (stdlib http.server)
engagements.py      # pricing maths + CSV read/write (framework-free, testable)
templates/index.html# the page: enquiry form, live quote, the book
test_engagements.py # pricing sanity checks
data/engagements.csv# your engagement book
```
