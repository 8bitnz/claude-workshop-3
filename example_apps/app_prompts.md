# Claude Code Workshop: 15 Single-Prompt App Ideas

Each idea below is a relatable workflow problem, scoped so Claude Code can build a working v1 from **one prompt in under 5 minutes**. No API keys, no paid dependencies — Python uses only the standard library; HTML/JS is a single self-contained file. Ideas 1–10 have two follow-up prompts for live iteration; ideas 11–15 are generalized from apps workshop attendees actually built, and are kept to the single build prompt.

---

## 1. Meeting Cost Calculator
**Problem it solves:** Meetings feel free. This makes the cost visible in real time, which changes how people run them.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Meeting Cost Calculator." Inputs: number of attendees, average hourly salary (or a dropdown of role presets with rough hourly rates), and a Start button. Once started, show a big live counter of money spent, ticking up every second, plus elapsed time. Include a Pause and Reset button. Style it clean and slightly alarming as the number grows (color shifts from green to red past $500). No external libraries — plain HTML/CSS/JS in one file.

**Iteration prompt 1:**
> Add a running list of past meetings (stored in localStorage) showing date, duration, attendee count, and total cost, with a "total spent this week" summary at the top.

**Iteration prompt 2:**
> Add a shareable summary: a button that generates a one-line text like "This meeting cost $342 and ran 47 minutes with 6 people" that copies to clipboard, so people can drop it in Slack after a meeting.

---

## 2. Standup Note Builder
**Problem it solves:** Turning yesterday's scattered notes into a clean "Yesterday / Today / Blockers" standup update every morning.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Standup Note Builder." Three text areas: Yesterday, Today, Blockers. As the user types bullet points (one per line), show a live-formatted preview panel with clean markdown-style formatting ready to paste into Slack (bullets with "•", blockers highlighted in red if non-empty). Add a "Copy to clipboard" button that copies the formatted version. Save the current draft to localStorage so it persists on refresh.

**Iteration prompt 2:**
> Add a history view: every time the user copies a standup, save it with today's date to a list. Show the last 7 entries in a collapsible sidebar so they can glance back at what they said this week.

**Iteration prompt 3:**
> Add a "carry forward" button that takes anything unfinished from yesterday's "Today" list and pre-fills it into today's "Yesterday" box automatically when the app loads on a new day.

---

## 3. Local Kanban Board
**Problem it solves:** Sometimes you just want a quick personal task board without signing into another tool.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS Kanban board with three columns: To Do, In Progress, Done. Users can add a card with a title by typing into an input and pressing Enter under any column. Cards should be draggable between columns (use native HTML5 drag-and-drop, no libraries). Persist all cards and their columns to localStorage so the board survives a page refresh. Keep the styling minimal and card-based.

**Iteration prompt 1:**
> Add a due date and a priority tag (Low/Medium/High, color-coded) to each card, shown as small pills on the card. Let the user click a card to edit these fields in a small modal.

**Iteration prompt 2:**
> Add a "Done today" counter at the top that shows how many cards moved into Done today, and add a clear-completed button that archives Done cards older than 7 days (removes from board but logs them to a "history" list you can view separately).

---

## 4. Habit Tracker Grid
**Problem it solves:** Seeing a habit streak (GitHub contribution-graph style) is a stronger motivator than a checklist.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS habit tracker. Let the user define up to 5 habits by name. For each habit, render a GitHub-style grid of the last 90 days as small squares; clicking a square toggles it filled/unfilled for that day. Store everything in localStorage. Show each habit's current streak (consecutive filled days ending today or yesterday) next to its name.

**Iteration prompt 1:**
> Add a percentage completion stat per habit for the last 30 days, and color the squares in a gradient intensity (like GitHub) if you ever mark a day with a 1-5 "effort" score instead of just on/off.

**Iteration prompt 2:**
> Add the ability to export all habit data as a CSV download, and add a simple weekly summary panel at the top showing which habit has the longest current streak and which was missed most this week.

---

## 5. Focus Timer with Session Log
**Problem it solves:** Losing track of how many focused work blocks you actually did today, and on what.
**Format:** Python (stdlib only, terminal or tkinter GUI)

**Prompt 1 — Build:**
> Build a single Python file called focus_timer.py using tkinter (standard library, no pip installs). It's a Pomodoro-style focus timer: a text box to label what you're working on, a 25-minute countdown with Start/Pause/Reset buttons, and a desktop-friendly window. When a session completes (or is stopped early), log it to a local sessions.csv file with timestamp, label, and duration in minutes. Show today's completed session count in the window.

**Iteration prompt 1:**
> Add a settings row to change the focus duration (default 25) and break duration (default 5), and after each focus session automatically start a break countdown with a distinct color, then prompt to start the next focus session.

**Iteration prompt 2:**
> Add a simple stats view (a button that opens a second window) showing total focused minutes today, this week, and a bar per day for the last 7 days, all computed from sessions.csv.

---

## 6. Downloads Folder Declutterer
**Problem it solves:** The Downloads folder becomes an unsorted dumping ground; this sorts it by file type automatically.
**Format:** Python (stdlib only, CLI)

**Prompt 1 — Build:**
> Build a Python CLI script called declutter.py using only the standard library. It scans a target folder (default: current directory, overridable with --path) and sorts files into subfolders by type: Images, Documents, Spreadsheets, Videos, Audio, Archives, Other, based on extension. Default to --dry-run mode that only prints what it would move; require an explicit --apply flag to actually move files. Print a summary count of files moved per category at the end.

**Iteration prompt 1:**
> Add an --older-than-days N flag that only moves files last modified more than N days ago, so recent downloads are left alone.

**Iteration prompt 2:**
> Add automatic handling of name collisions (append a number instead of overwriting) and a --undo flag that reads a log of the last run's moves and reverses them.

---

## 7. Duplicate File Finder
**Problem it solves:** Duplicate files (old exports, photo copies, downloaded twice) quietly eat disk space.
**Format:** Python (stdlib only, CLI)

**Prompt 1 — Build:**
> Build a Python CLI script called find_dupes.py using only the standard library. It takes a folder path as an argument, walks it recursively, and groups files by content using a hash (md5, read in chunks so large files are fine). Print groups of duplicate files with their sizes and total space that could be reclaimed. Do not delete anything yet — this version only reports.

**Iteration prompt 1:**
> Add an interactive mode: for each duplicate group, show the file paths numbered, let the user type which ones to delete (or "s" to skip the group), and confirm before deleting.

**Iteration prompt 2:**
> Add a --keep-newest flag that, combined with a --auto flag, automatically deletes all but the most recently modified file in each duplicate group without prompting, and logs every deletion to a dupes_removed.log file with timestamps.

---

## 8. Timesheet-to-Invoice Generator
**Problem it solves:** Freelancers/contractors turning a raw hours log into a clean invoice they can send.
**Format:** Python (stdlib only, CLI, generates an HTML invoice)

**Prompt 1 — Build:**
> Build a Python CLI script called make_invoice.py using only the standard library. It reads a CSV (columns: date, description, hours) and takes a --rate flag for hourly rate, plus --client and --invoice-number arguments. It generates a clean, printable HTML invoice (invoice_<number>.html) showing the line items in a table, subtotal, and total, styled simply with inline CSS so it prints well from a browser. Include today's date and a simple invoice header.

**Iteration prompt 1:**
> Add support for a flat "expenses" section (read from a second optional CSV: description, amount) that gets added to the invoice total separately from hours.

**Iteration prompt 2:**
> Add a --tax-rate flag that adds a tax line calculated on the subtotal, and generate a companion invoice_<number>.csv summary alongside the HTML for the user's own records.

---

## 9. Decision Matrix Tool
**Problem it solves:** Weighing a hard decision (which vendor, which apartment, which job offer) with gut feel instead of structure.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS weighted decision matrix. Let the user add options (rows) and criteria (columns), each criterion has an adjustable weight (1-5). For each option/criterion cell, let the user score 1-5. Automatically calculate a weighted total per option and highlight the highest-scoring option. Persist the whole matrix to localStorage. Keep it a clean, editable table.

**Iteration prompt 1:**
> Add a bar chart (plain CSS/SVG, no libraries) below the table visualizing each option's weighted total score, so the winner is visually obvious.

**Iteration prompt 2:**
> Add the ability to save and load named matrices (e.g. "Apartment search," "Vendor pick") from a dropdown, so the user can keep multiple decisions going at once, all in localStorage.

---

## 10. Automation Effort Calculator

Problem it solves: Deciding whether a repetitive task is actually worth automating, or if you're just procrastinating on real work by tinkering. Format: HTML/JS (single file)

**Prompt 1 — Build:**

>Build a single-file HTML/JS app called "Automation Effort Calculator." Three sliders: "Time per occurrence" (1-120 minutes), "How annoying/hard is it" (1-5, a difficulty/pain multiplier), and "How often you do it" (options like daily, a few times a week, weekly, monthly, with a numeric occurrences-per-month equivalent). As the sliders move, live-update a result panel showing: time spent per month on this task, and a recommended "budget" — the max hours you should reasonably spend building an automation for it to pay off within, say, 3 months, scaled by the pain multiplier (more painful tasks justify more upfront effort even at the same time cost). Show the math clearly (time/month, break-even effort in hours) so the reasoning isn't a black box. Clean, single-page layout, no external libraries.

**Iteration prompt 2:**

>Add an hourly rate input (defaulting to a reasonable number, editable) so time spent is converted to a dollar cost per month, and a dollar-value "worth automating up to $X" figure. Add a "how many people do this task" input that multiplies the monthly time/cost savings accordingly, since automating something 5 people do is 5x the ROI of automating something only you do.

**Iteration prompt 3:**

>Improve the whole tool: add a saved list of past calculations (name each one, e.g. "Weekly report formatting") stored in localStorage so multiple tasks can be compared side by side in a ranked table sorted by ROI. Add a simple visual (bar or scatter, plain SVG/CSS, no libraries) plotting all saved tasks by time-cost vs. recommended automation budget, so the best automation candidates are obvious at a glance. Polish the styling and make the result panel feel like a clear recommendation rather than just raw numbers.
---

## 11. Estimate vs Actual Tracker
**Problem it solves:** People routinely misjudge how long tasks will take; logging estimates against actuals turns that gut feeling into visible data on whether their estimation is improving or getting worse over time.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Estimate vs Actual Tracker." Let the user add a task with a name, an estimated duration (a number plus a minutes/hours unit selector), and an optional category/tag. Show active (not-yet-completed) tasks in a list, each with an inline field to record actual time spent (value + unit) and a "Mark complete" button. Once completed, move the task into a "Completed tasks" table showing task name, category, estimated time, actual time, and the variance (both as a percentage and an absolute time difference), color-coded green/red/blue depending on whether the task ran on-target, over, or under estimate. Add a category filter dropdown that filters the completed table. At the top, show summary stats: number of tasks completed, average variance percentage, and a simple "Improving / Getting worse / Steady" trend indicator (comparing estimation accuracy in the second half of completed tasks vs. the first half). Below that, add a trend chart built with plain inline SVG (no chart libraries) plotting the actual/estimated ratio for the last 20 completed tasks in chronological order, as a connected line with dots colored by accuracy, plus a dashed reference line at 1.0x for "on target." Persist everything in localStorage. Style it as a clean dark-themed single page (dark slate background, rounded cards, system-ui font), self-contained in one HTML file with no external libraries or CDNs.

---

## 12. Maintenance Schedule Tracker
**Problem it solves:** Recurring equipment maintenance gets missed or tracked in scattered spreadsheets, and the resulting costs are painful to hand off to accounting/invoicing software in a clean, importable format.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Maintenance Schedule Tracker." Let the user add equipment/assets with a name, a maintenance interval (a number plus a unit dropdown: days/weeks/months), and a last-serviced date. Automatically compute each asset's next-due date from the interval and last-serviced date, and show a dashboard of all assets sorted by urgency, color-coded and badged as Overdue (red), Due Soon within 7 days (amber), or On Track (green), with summary counts at the top. Each asset should have a "Log Maintenance" action that opens an inline form to enter a completion date, cost, and notes; saving it updates the asset's last-serviced date (recalculating next-due) and appends a record to a maintenance history log. Below the dashboard, show a table of the full maintenance history log (date, description, amount, reference) and an "Export CSV" button that downloads it in a simple Date/Description/Amount/Reference format suitable for importing into accounting or invoicing software. Persist everything in localStorage. Dark-themed styling (dark slate background, rounded card, system-ui font), no external libraries — plain HTML/CSS/JS in one file.

---

## 13. Image Batch Reformatter
**Problem it solves:** Publishing a batch of images to a content site means manually resizing/cropping/re-exporting each one to consistent dimensions and format — tedious and error-prone by hand.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Image Batch Reformatter." Let the user select or drag-and-drop multiple image files (no upload, everything happens client-side via the Canvas API). Provide an output preset dropdown (e.g. "Thumbnail 400x300," "Square 800x800," "Banner 1200x400," "Social 1200x630," plus a "Custom" option with width/height number inputs), a fit-mode toggle between Cover (crop to fill) and Contain (fit inside with a background fill color the user can pick), an output format dropdown (JPEG/PNG/WebP), and a quality slider that applies to JPEG/WebP. On clicking "Reformat images," process each file through an offscreen canvas at the target size/fit/format and render a preview grid of the results showing filename, original dimensions vs. new dimensions, and original file size vs. new file size (highlight whether it got smaller or larger). Give each processed image its own Download button (canvas.toBlob + object URL, no zipping needed). Style it as a clean dark-themed single page — no external libraries, no server, no build step.

---

## 14. Lending Rules Checker
**Problem it solves:** Turning a lender's or product's raw eligibility criteria (DTI limits, minimum deposit, credit score floor, LVR cap) into an instant pass/fail check against a specific applicant's numbers.
**Format:** HTML/JS (single file)

**Prompt 1 — Build:**
> Build a single-file HTML/JS app called "Lending Rules Checker." Let the user define a set of named lending eligibility rules, each with a label (e.g. "Maximum debt-to-income ratio," "Minimum deposit %," "Minimum credit score," "Maximum loan-to-value ratio"), a metric it applies to, a comparison type (min/max/equals), and a threshold value. Support saving multiple named rule sets (e.g. "Lender A — Standard," "Lender B — Low Deposit") in localStorage, selectable from a dropdown, with the ability to create, duplicate, rename, and delete rule sets. Below that, an applicant details form capturing annual income, total monthly debt payments, property value, deposit amount, and credit score (loan amount is implied as property value minus deposit). On clicking "Evaluate eligibility," compute each rule's underlying metric from the applicant's figures (debt-to-income ratio, deposit percentage, loan-to-value ratio, credit score, etc.), show a clear pass/fail row per rule with the applicant's actual value vs. the required threshold, and display an overall verdict at the top: "Eligible" or "Not eligible — N rules failed" listing which ones. Keep it a generic lending-rules tool, not tied to any specific bank. Dark-themed styling (dark slate background, rounded card, system-ui font), no external libraries, everything persisted to localStorage.

---

## 15. Course Publishing Checklist
**Problem it solves:** Course content sits in a CMS with no reliable check that every course is actually publish-ready before it goes live to students.
**Format:** Python (stdlib only, CLI)

**Prompt 1 — Build:**
> Build a Python CLI script called check_courses.py using only the standard library. It reads a folder of course definition files (default: ./courses, overridable with --path), one JSON file per course, each with fields: title, modules (a list, each with title, has_content bool, has_learning_objectives bool), has_syllabus bool, and assessment_weights (a dict of assessment name to percentage). For each course, check it against a publishing checklist: has a syllabus, has at least one module, every module has content, every module has learning objectives, and assessment weights sum to exactly 100. Print a per-course PASS/FAIL report to stdout, listing the specific issues for any FAIL (e.g. "Module 'Week 3' missing learning objectives"), then a final summary line like "3/5 courses ready to publish." Exit with a non-zero exit code if any course fails, so it can be used in a CI-style workflow.

---

### Facilitator notes
- Have participants pick one idea, paste Prompt 1 into Claude Code, and time how long it takes to get a working app.
- Iteration prompts are designed to be pasted one at a time, in order, after reviewing what Claude Code built — they compound rather than replace.
- All specs avoid API keys and external paid services so they run offline and work in any workshop network conditions.
- Apps 11–15 are generalized from real apps built by workshop attendees, kept to a single build iteration (no follow-up prompts) rather than three.
