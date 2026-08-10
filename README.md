# Claude Workshop 3 — Code

A hands-on workshop repository for learning to build software with
**Claude Code**, Anthropic's agentic coding tool. This repo is the starting
point for the exercises: it comes pre-configured so you can jump straight into
writing code, running agents, and shipping changes.

---

## What is this?

This is a sandbox project used during the workshop. You'll use it to practice:

- Driving Claude Code from the terminal, IDE, and the web
- Writing effective prompts and breaking work into reviewable changes
- Configuring agent behavior with `AGENTS.md`
- Working with branches, commits, and pull requests through an agent
- Running tests and linters as part of the loop

No prior experience with Claude Code is required — just curiosity and a
GitHub account.

---

## Prerequisites

Before the workshop, make sure you have the following installed:

| Tool | Version | Notes |
|------|---------|-------|
| [Python](https://www.python.org/downloads/) | 3.10+ | The project is Python-based |
| [Git](https://git-scm.com/) | 2.30+ | For version control |
| [Claude Code](https://claude.com/claude-code) | latest | The agent itself |
| A GitHub account | — | To clone, branch, and open PRs |

Optional but recommended:

- A code editor such as [VS Code](https://code.visualstudio.com/) or a
  JetBrains IDE (both have Claude Code extensions)
- [`uv`](https://github.com/astral-sh/uv) or `venv` for managing a Python
  virtual environment

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/8bitnz/claude-workshop-3.git
cd claude-workshop-3
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

Dependencies will be added during the workshop. When a `requirements.txt` or
`pyproject.toml` is present, install with:

```bash
pip install -r requirements.txt   # or: uv sync
```

### 4. Launch Claude Code

From the project root:

```bash
claude
```

Then try your first prompt — for example:

> "Give me an overview of this repository and suggest a first exercise."

---

## Project layout

```
claude-workshop-3/
├── AGENTS.md        # Guidance for AI coding agents working in this repo
├── LICENSE          # MIT license
├── README.md        # You are here
└── .gitignore       # Python-oriented ignore rules
```

As you work through the exercises, source code, tests, and configuration
files will grow this tree.

---

## Workshop exercises

Each exercise builds on the last. Work through them in order.

1. **Explore** — Ask Claude to summarize the repo and explain the tooling.
2. **First change** — Add a small module (e.g. a `hello()` function) with a
   test, and let Claude run the test.
3. **Refactor** — Introduce a deliberate bit of messy code and ask Claude to
   clean it up while keeping tests green.
4. **Branch & PR** — Have Claude create a feature branch, commit, push, and
   open a pull request.
5. **Review loop** — Request a code review, then apply and discuss the
   feedback.

> Tip: keep changes small and reviewable. The best agent workflows look like
> a series of tidy commits, not one giant diff.

---

## Working with Claude Code

A few practices that make agent-assisted development smoother:

- **Be specific.** State the goal, the constraints, and how you'll verify
  success.
- **Work in branches.** Let the agent create a feature branch rather than
  committing to `main`.
- **Review every diff.** You are the author of record — read what the agent
  produces before merging.
- **Keep `AGENTS.md` current.** It's the fastest way to teach the agent your
  conventions. See [AGENTS.md](./AGENTS.md).

---

## Contributing

This is a workshop repo, so feel free to experiment. If you're collaborating:

1. Create a feature branch: `git checkout -b your-name/short-description`
2. Make focused commits with clear messages
3. Push and open a pull request
4. Ask for a review (from a human or from Claude!)

---

## License

Released under the [MIT License](./LICENSE).
