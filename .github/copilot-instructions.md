# Copilot / AI agent instructions — Math-and-Furious

Short, actionable notes to help an AI editing agent be productive quickly.

## Quick facts
- Language: Python (but source files currently have no `.py` extension).
- Repo shape: single simple CLI game. Key files:
  - `main` — the runnable game script (no file extension).
  - `Example` — a tiny sample showing arithmetic expressions.
  - `README.md` — one-line project description.

## How to run (local dev)
- Run the main script with the system Python 3 interpreter:

```bash
python3 main
```

- For debugging with pdb:

```bash
python3 -m pdb main
```

Notes: there is no `requirements.txt` or packaging. If you add dependencies, create a `requirements.txt` and recommend a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Big picture / data flow (what to read first)
- `main` is the entire game logic. It:
  1. generates two addition numbers (addx, addy) and two subtraction numbers (subx, suby) at the top
  2. computes `add_total` and `sub_total`
  3. asks the user whether they want to play
  4. enters a `while` loop that prompts the user for answers and prints results

- Important: random numbers are created once at start, so the same questions repeat every loop iteration. (`addx`, `addy`, `subx`, `suby` are not regenerated inside the loop.)

## Project-specific conventions & gotchas
- Files currently lack `.py` extensions. Expect editors/linters to treat them as plain text unless you add an extension or a shebang.
- Variable naming is mostly snake_case (e.g., `add_total`) but check for inconsistent usage (`player_plays` used both as boolean and compared to string in code).
- There are no automated tests or CI. Changes should be validated by running `python3 main` and simple manual QA.

## Concrete examples / common edits an agent will do
- Refresh questions each round: move the `random.randint(...)` calls and the `*_total` calculations into the loop so each iteration uses new numbers.

- Fix boolean check bug: the code sets `player_plays = input(...).lower() == "yes"` (a boolean) then later compares `if player_plays == "yes":` — update logic to use the boolean consistently.

- Make the script executable/clearer: add a `.py` extension and a shebang line (`#!/usr/bin/env python3`) if you intend the file to be run directly.

## Integration points & external dependencies
- None detected. No external services, files, or environment variables are referenced.

## Debugging and tests
- No test framework present. For unit tests, create `tests/test_game.py` and use `pytest`.
- Quick smoke test: run `python3 main` and exercise both correct and incorrect inputs.

## Where to look when making changes
- Start at `main` for any game-behavior changes.
- Use `Example` for minimal arithmetic examples (note: also lacks extension).

## Minimal rules for edits by an automated agent
1. Preserve human-readable prompts and not change user-facing text unless improving clarity.
2. Run `python3 main` after modifications and include the observed smoke-test outcome in the commit message.
3. If adding files, keep them under the repository root and update `README.md` with usage notes.

---
If any of the above is unclear or you want the agent to follow stricter rules (naming, tests, CI), tell me which areas to expand and I'll iterate.
