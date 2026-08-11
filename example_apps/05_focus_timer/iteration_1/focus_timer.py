#!/usr/bin/env python3
"""Focus Timer — a Pomodoro-style focus timer (standard library only).

A 25-minute countdown with a label for what you're working on. Completed (or
stopped) sessions are logged to sessions.csv next to this script.
"""
import csv
import os
import tkinter as tk
from datetime import date, datetime

FOCUS_MINUTES = 25
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.csv")


class FocusTimer:
    def __init__(self, root):
        self.root = root
        root.title("Focus Timer")
        root.geometry("360x300")
        root.configure(bg="#1e1e2e")

        self.total_seconds = FOCUS_MINUTES * 60
        self.remaining = self.total_seconds
        self.running = False
        self._job = None

        tk.Label(root, text="What are you working on?", bg="#1e1e2e",
                 fg="#a6adc8", font=("Helvetica", 11)).pack(pady=(20, 4))
        self.label_var = tk.StringVar()
        tk.Entry(root, textvariable=self.label_var, width=30,
                 font=("Helvetica", 12)).pack(pady=4)

        self.time_var = tk.StringVar(value=self._fmt(self.remaining))
        tk.Label(root, textvariable=self.time_var, bg="#1e1e2e", fg="#89dceb",
                 font=("Helvetica", 44, "bold")).pack(pady=14)

        btns = tk.Frame(root, bg="#1e1e2e")
        btns.pack()
        self._btn(btns, "Start", self.start, "#a6e3a1").grid(row=0, column=0, padx=5)
        self._btn(btns, "Pause", self.pause, "#f9e2af").grid(row=0, column=1, padx=5)
        self._btn(btns, "Reset", self.reset, "#f38ba8").grid(row=0, column=2, padx=5)

        self.count_var = tk.StringVar()
        tk.Label(root, textvariable=self.count_var, bg="#1e1e2e", fg="#a6adc8",
                 font=("Helvetica", 11)).pack(pady=(18, 0))
        self._update_count()

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, width=6, bg=color,
                         fg="#1e1e2e", relief="flat", font=("Helvetica", 11, "bold"))

    @staticmethod
    def _fmt(secs):
        return f"{secs // 60:02d}:{secs % 60:02d}"

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
        # A reset mid-session counts as a stopped session and gets logged.
        elapsed = self.total_seconds - self.remaining
        if elapsed >= 60:
            self._log_session(elapsed // 60, completed=False)
        self.pause()
        self.remaining = self.total_seconds
        self.time_var.set(self._fmt(self.remaining))
        self._update_count()

    def _tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self._complete()
            return
        self.remaining -= 1
        self.time_var.set(self._fmt(self.remaining))
        self._job = self.root.after(1000, self._tick)

    def _complete(self):
        self.running = False
        self._log_session(self.total_seconds // 60, completed=True)
        self.remaining = self.total_seconds
        self.time_var.set(self._fmt(self.remaining))
        self._update_count()
        self.time_var.set("Done!")
        self.root.after(1500, lambda: self.time_var.set(self._fmt(self.remaining)))

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
        n = 0
        with open(CSV_PATH, newline="") as f:
            for row in csv.DictReader(f):
                if row["completed"] == "yes" and row["timestamp"].startswith(today):
                    n += 1
        return n

    def _update_count(self):
        n = self._today_count()
        self.count_var.set(f"✅ {n} focus session{'s' if n != 1 else ''} completed today")


if __name__ == "__main__":
    root = tk.Tk()
    FocusTimer(root)
    root.mainloop()
