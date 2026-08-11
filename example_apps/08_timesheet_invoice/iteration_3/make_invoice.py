#!/usr/bin/env python3
"""make_invoice.py — turn a timesheet CSV into a clean printable HTML invoice.

Standard library only.

The timesheet CSV must have the columns: date, description, hours
An optional expenses CSV may have the columns: description, amount

Usage:
    python3 make_invoice.py hours.csv --rate 120 --client "Acme Co" --invoice-number 1001
    python3 make_invoice.py hours.csv --rate 120 --client "Acme Co" \\
        --invoice-number 1001 --expenses expenses.csv
"""
import argparse
import csv
import html
import os
import sys
from datetime import date


def read_timesheet(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        required = {"date", "description", "hours"}
        if not required.issubset({c.strip() for c in (reader.fieldnames or [])}):
            raise ValueError(f"CSV must have columns: {', '.join(sorted(required))}")
        for r in reader:
            try:
                hours = float(r["hours"])
            except (ValueError, TypeError):
                continue
            rows.append({"date": r["date"].strip(),
                         "description": r["description"].strip(),
                         "hours": hours})
    return rows


def read_expenses(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        required = {"description", "amount"}
        if not required.issubset({c.strip() for c in (reader.fieldnames or [])}):
            raise ValueError(f"Expenses CSV must have columns: {', '.join(sorted(required))}")
        for r in reader:
            try:
                amount = float(r["amount"])
            except (ValueError, TypeError):
                continue
            rows.append({"description": r["description"].strip(), "amount": amount})
    return rows


def build_html(rows, rate, client, number, expenses=None, tax_rate=0.0):
    line_items = ""
    hours_subtotal = 0.0
    for r in rows:
        amount = r["hours"] * rate
        hours_subtotal += amount
        line_items += (
            f"<tr><td>{html.escape(r['date'])}</td>"
            f"<td>{html.escape(r['description'])}</td>"
            f"<td class='num'>{r['hours']:.2f}</td>"
            f"<td class='num'>${rate:,.2f}</td>"
            f"<td class='num'>${amount:,.2f}</td></tr>\n"
        )

    expenses = expenses or []
    expenses_total = sum(e["amount"] for e in expenses)
    expenses_html = ""
    if expenses:
        exp_rows = "".join(
            f"<tr><td>{html.escape(e['description'])}</td>"
            f"<td class='num'>${e['amount']:,.2f}</td></tr>\n" for e in expenses
        )
        expenses_html = f"""
  <h2 style="margin-top:32px; font-size:1.1rem;">Expenses</h2>
  <table>
    <thead><tr><th>Description</th><th class="num">Amount</th></tr></thead>
    <tbody>
{exp_rows}    </tbody>
    <tfoot><tr><td class="num">Expenses subtotal</td><td class="num">${expenses_total:,.2f}</td></tr></tfoot>
  </table>"""

    subtotal = hours_subtotal + expenses_total
    tax = subtotal * (tax_rate / 100.0)
    grand_total = subtotal + tax
    tax_html = ""
    if tax_rate:
        tax_html = (f'<tr><td class="num">Subtotal</td><td class="num">${subtotal:,.2f}</td></tr>\n'
                    f'      <tr><td class="num">Tax ({tax_rate:g}%)</td><td class="num">${tax:,.2f}</td></tr>\n      ')
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Invoice {html.escape(str(number))}</title>
<style>
  body {{ font-family: Arial, sans-serif; color:#222; max-width:800px; margin:40px auto; padding:0 20px; }}
  h1 {{ margin:0; font-size:2rem; }}
  .meta {{ display:flex; justify-content:space-between; margin:24px 0; }}
  .meta div {{ font-size:.95rem; line-height:1.6; }}
  table {{ width:100%; border-collapse:collapse; margin-top:16px; }}
  th, td {{ padding:10px 12px; border-bottom:1px solid #ddd; text-align:left; }}
  th {{ background:#f4f4f4; font-size:.85rem; text-transform:uppercase; letter-spacing:.5px; }}
  .num {{ text-align:right; }}
  tfoot td {{ font-weight:bold; border-top:2px solid #333; border-bottom:none; }}
  .total-row td {{ font-size:1.15rem; }}
  @media print {{ body {{ margin:0; }} }}
</style></head>
<body>
  <h1>INVOICE</h1>
  <div class="meta">
    <div><strong>Billed to:</strong><br>{html.escape(client)}</div>
    <div style="text-align:right;">
      <strong>Invoice #:</strong> {html.escape(str(number))}<br>
      <strong>Date:</strong> {date.today().isoformat()}
    </div>
  </div>
  <table>
    <thead><tr><th>Date</th><th>Description</th><th class="num">Hours</th><th class="num">Rate</th><th class="num">Amount</th></tr></thead>
    <tbody>
{line_items}    </tbody>
    <tfoot>
      <tr><td colspan="4" class="num">Hours subtotal</td><td class="num">${hours_subtotal:,.2f}</td></tr>
    </tfoot>
  </table>
{expenses_html}
  <table style="margin-top:24px;">
    <tfoot>
      {tax_html}<tr class="total-row"><td class="num">Total Due</td><td class="num" style="width:140px;">${grand_total:,.2f}</td></tr>
    </tfoot>
  </table>
</body></html>
"""


def main(argv=None):
    p = argparse.ArgumentParser(description="Generate an HTML invoice from a timesheet CSV.")
    p.add_argument("csv_file", help="Timesheet CSV with columns: date, description, hours")
    p.add_argument("--rate", type=float, required=True, help="Hourly rate.")
    p.add_argument("--client", required=True, help="Client name.")
    p.add_argument("--invoice-number", required=True, help="Invoice number.")
    p.add_argument("--expenses", help="Optional expenses CSV (columns: description, amount).")
    p.add_argument("--tax-rate", type=float, default=0.0, metavar="PCT",
                   help="Tax rate percent applied to the subtotal (e.g. 15).")
    args = p.parse_args(argv)

    if not os.path.isfile(args.csv_file):
        print(f"Error: {args.csv_file} not found.", file=sys.stderr)
        return 1
    try:
        rows = read_timesheet(args.csv_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if not rows:
        print("No valid rows found in the timesheet.", file=sys.stderr)
        return 1

    expenses = []
    if args.expenses:
        if not os.path.isfile(args.expenses):
            print(f"Error: {args.expenses} not found.", file=sys.stderr)
            return 1
        try:
            expenses = read_expenses(args.expenses)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    out = build_html(rows, args.rate, args.client, args.invoice_number, expenses, args.tax_rate)
    out_path = f"invoice_{args.invoice_number}.html"
    with open(out_path, "w") as f:
        f.write(out)

    hours_subtotal = sum(r["hours"] for r in rows) * args.rate
    expenses_total = sum(e["amount"] for e in expenses)
    subtotal = hours_subtotal + expenses_total
    tax = subtotal * (args.tax_rate / 100.0)
    grand_total = subtotal + tax

    # Companion CSV summary for the user's own records.
    csv_path = f"invoice_{args.invoice_number}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["invoice_number", args.invoice_number])
        w.writerow(["client", args.client])
        w.writerow(["date", date.today().isoformat()])
        w.writerow([])
        w.writerow(["item", "amount"])
        w.writerow(["Hours subtotal", f"{hours_subtotal:.2f}"])
        if expenses:
            w.writerow(["Expenses subtotal", f"{expenses_total:.2f}"])
        w.writerow(["Subtotal", f"{subtotal:.2f}"])
        if args.tax_rate:
            w.writerow([f"Tax ({args.tax_rate:g}%)", f"{tax:.2f}"])
        w.writerow(["Total Due", f"{grand_total:.2f}"])

    print(f"Wrote {out_path} and {csv_path}  "
          f"({len(rows)} line items, {len(expenses)} expenses, total ${grand_total:,.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
