#!/usr/bin/env python3
"""Focus Timer — Pomodoro timer with configurable cycle and a stats view (stdlib only).

Adds a settings row for focus/break durations, an auto-starting break cycle,
and a Stats button that opens a second window: total focused minutes today,
this week, and a bar per day for the last 7 days (computed from sessions.csv).
"""
import csv
import os
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime, timedelta

DEFAULT_FOCUS = 25
DEFAULT_BREAK = 5
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.csv")

FOCUS_COLOR = "#89dceb"
BREAK_COLOR = "#f9e2af"


class FocusTimer:
    def __init__(self, root):
        self.root = root
        root.title("Focus Timer")
        root.geometry("380x380")
        root.configure(bg="#1e1e2e")

        self.mode = "focus"          # "focus" or "break"
        self.running = False
        self._job = None

        tk.Label(root, text="What are you working on?", bg="#1e1e2e",
                 fg="#a6adc8", font=("Helvetica", 11)).pack(pady=(16, 4))
        self.label_var = tk.StringVar()
        tk.Entry(root, textvariable=self.label_var, width=32,
                 font=("Helvetica", 12)).pack(pady=4)

        # settings row
        settings = tk.Frame(root, bg="#1e1e2e")
        settings.pack(pady=8)
        tk.Label(settings, text="Focus", bg="#1e1e2e", fg="#a6adc8").grid(row=0, column=0, padx=4)
        self.focus_var = tk.IntVar(value=DEFAULT_FOCUS)
        tk.Spinbox(settings, from_=1, to=180, width=4, textvariable=self.focus_var,
                   command=self._settings_changed).grid(row=0, column=1, padx=4)
        tk.Label(settings, text="Break", bg="#1e1e2e", fg="#a6adc8").grid(row=0, column=2, padx=4)
        self.break_var = tk.IntVar(value=DEFAULT_BREAK)
        tk.Spinbox(settings, from_=1, to=60, width=4, textvariable=self.break_var).grid(row=0, column=3, padx=4)
        tk.Label(settings, text="min", bg="#1e1e2e", fg="#6c7086").grid(row=0, column=4, padx=2)

        self.remaining = self.focus_var.get() * 60
        self.total_seconds = self.remaining

        self.mode_var = tk.StringVar(value="Focus")
        tk.Label(root, textvariable=self.mode_var, bg="#1e1e2e", fg="#a6adc8",
                 font=("Helvetica", 12, "bold")).pack()
        self.time_var = tk.StringVar(value=self._fmt(self.remaining))
        self.time_lbl = tk.Label(root, textvariable=self.time_var, bg="#1e1e2e",
                                 fg=FOCUS_COLOR, font=("Helvetica", 44, "bold"))
        self.time_lbl.pack(pady=10)

        btns = tk.Frame(root, bg="#1e1e2e")
        btns.pack()
        self._btn(btns, "Start", self.start, "#a6e3a1").grid(row=0, column=0, padx=5)
        self._btn(btns, "Pause", self.pause, "#f9e2af").grid(row=0, column=1, padx=5)
        self._btn(btns, "Reset", self.reset, "#f38ba8").grid(row=0, column=2, padx=5)

        self._btn(root, "📊 Stats", self.show_stats, "#cba6f7").pack(pady=(12, 0))

        self.count_var = tk.StringVar()
        tk.Label(root, textvariable=self.count_var, bg="#1e1e2e", fg="#a6adc8",
                 font=("Helvetica", 11)).pack(pady=(16, 0))
        self._update_count()

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, width=6, bg=color,
                         fg="#1e1e2e", relief="flat", font=("Helvetica", 11, "bold"))

    @staticmethod
    def _fmt(secs):
        return f"{secs // 60:02d}:{secs % 60:02d}"

    def _settings_changed(self):
        # Only reflect a changed focus length when idle in focus mode.
        if not self.running and self.mode == "focus":
            self.total_seconds = self.focus_var.get() * 60
            self.remaining = self.total_seconds
            self.time_var.set(self._fmt(self.remaining))

    def start(self):
        if self.running:
            return
        self.running = True
        self._tick()

    def pause(self):
        self.running = False
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None

    def reset(self):
        if self.mode == "focus":
            elapsed = self.total_seconds - self.remaining
            if elapsed >= 60:
                self._log_session(elapsed // 60, completed=False)
        self.pause()
        self._enter_focus()
        self._update_count()

    def _enter_focus(self):
        self.mode = "focus"
        self.mode_var.set("Focus")
        self.time_lbl.config(fg=FOCUS_COLOR)
        self.total_seconds = self.focus_var.get() * 60
        self.remaining = self.total_seconds
        self.time_var.set(self._fmt(self.remaining))

    def _enter_break(self):
        self.mode = "break"
        self.mode_var.set("Break — relax ☕")
        self.time_lbl.config(fg=BREAK_COLOR)
        self.total_seconds = self.break_var.get() * 60
        self.remaining = self.total_seconds
        self.time_var.set(self._fmt(self.remaining))

    def _tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self._phase_complete()
            return
        self.remaining -= 1
        self.time_var.set(self._fmt(self.remaining))
        self._job = self.root.after(1000, self._tick)

    def _phase_complete(self):
        self.running = False
        if self.mode == "focus":
            self._log_session(self.total_seconds // 60, completed=True)
            self._update_count()
            self._enter_break()
            self.start()  # auto-start the break
        else:
            # break done — prompt for next focus
            self._enter_focus()
            if messagebox.askyesno("Break over", "Break's over! Start the next focus session?"):
                self.start()

    def _log_session(self, minutes, completed):
        new_file = not os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(["timestamp", "label", "minutes", "completed"])
            w.writerow([datetime.now().isoformat(timespec="seconds"),
                        self.label_var.get().strip() or "(no label)",
                        minutes, "yes" if completed else "no"])

    def _today_count(self):
        if not os.path.exists(CSV_PATH):
            return 0
        today = date.today().isoformat()
        return sum(1 for row in csv.DictReader(open(CSV_PATH, newline=""))
                   if row["completed"] == "yes" and row["timestamp"].startswith(today))

    def _update_count(self):
        n = self._today_count()
        self.count_var.set(f"✅ {n} focus session{'s' if n != 1 else ''} completed today")

    # ---- Stats ----
    @staticmethod
    def _minutes_by_day():
        """Return {date_iso: total_completed_minutes} from sessions.csv."""
        totals = {}
        if not os.path.exists(CSV_PATH):
            return totals
        with open(CSV_PATH, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("completed") != "yes":
                    continue
                day = row["timestamp"][:10]
                try:
                    totals[day] = totals.get(day, 0) + int(row["minutes"])
                except (ValueError, KeyError):
                    pass
        return totals

    def show_stats(self):
        totals = self._minutes_by_day()
        today = date.today()
        week_days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # oldest -> newest
        today_min = totals.get(today.isoformat(), 0)
        week_min = sum(totals.get(d.isoformat(), 0) for d in week_days)
        peak = max((totals.get(d.isoformat(), 0) for d in week_days), default=0) or 1

        win = tk.Toplevel(self.root)
        win.title("Focus Stats")
        win.configure(bg="#1e1e2e")
        win.geometry("420x360")

        tk.Label(win, text=f"Today: {today_min} min", bg="#1e1e2e", fg="#a6e3a1",
                 font=("Helvetica", 14, "bold")).pack(pady=(16, 2))
        tk.Label(win, text=f"This week: {week_min} min", bg="#1e1e2e", fg="#89dceb",
                 font=("Helvetica", 12)).pack(pady=(0, 10))

        canvas = tk.Canvas(win, width=380, height=220, bg="#1e1e2e", highlightthickness=0)
        canvas.pack()
        n = len(week_days)
        slot = 380 / n
        bar_w = slot * 0.6
        base_y = 180
        for i, d in enumerate(week_days):
            mins = totals.get(d.isoformat(), 0)
            h = (mins / peak) * 140
            x0 = i * slot + (slot - bar_w) / 2
            canvas.create_rectangle(x0, base_y - h, x0 + bar_w, base_y,
                                    fill="#89dceb", outline="")
            if mins:
                canvas.create_text(x0 + bar_w / 2, base_y - h - 8, text=str(mins),
                                   fill="#cdd6f4", font=("Helvetica", 8))
            canvas.create_text(x0 + bar_w / 2, base_y + 14,
                               text=d.strftime("%a"), fill="#a6adc8",
                               font=("Helvetica", 9))


if __name__ == "__main__":
    root = tk.Tk()
    FocusTimer(root)
    root.mainloop()
