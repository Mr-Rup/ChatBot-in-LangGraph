---
name: code-structure
description: Professional code structure, formatting, naming, documentation, and organization standard. Use this skill any time code is being WRITTEN from scratch on a new or existing project (functions, scripts, modules, classes) to apply consistent professional conventions from the first line — naming, docstrings, section headers, import grouping, type hints, error handling. ALSO use this skill whenever the user asks to "clean up", "refactor", "professionalize", "restructure", "reorganize", "upgrade", or "redesign" existing code, or improve its readability/formatting/documentation — in that case this skill enforces a strict behavior-preserving pass — same logic, same outputs, same algorithm, only the craftsmanship improves. Trigger this even if the user doesn't use the word "skill" — any request touching code quality, code organization, or code style falls under this.
---

# Code Structure & Quality Standard

One standard, two modes. Figure out which mode the request is in before touching anything.

| Signal in the request | Mode |
|---|---|
| "build", "write", "create", "add a function/script/module" — code doesn't exist yet | **A — New Code** |
| "clean up", "refactor", "professionalize", "reorganize", "redesign", "improve readability", "make this look better" on code that already runs | **B — Refactor (behavior-locked)** |
| Ambiguous / both in one request | Do A for the new parts, B for the pre-existing parts. Say so explicitly. |

Both modes share the same style rules (naming, docstrings, formatting — see "Shared Style Reference" below). They differ in how much freedom you have to change *structure and logic*.

---

## MODE A — Writing New Code

No existing behavior to protect, so apply the full standard proactively, without being asked each time:

- One clear responsibility per function; extract only when a sub-piece genuinely has its own purpose (don't extract just to have more functions).
- Descriptive names (`load_dataset`, `calculate_metrics`) — never `do_stuff`, `helper`, `process`, `func1`.
- Docstrings on every public function/class (see format below).
- Type hints where they aid clarity, not for show.
- Imports grouped: standard library → third-party → local.
- Constants pulled to the top (`UPPER_CASE`), not left as magic numbers inline.
- `try/except` only where a failure is expected and can be meaningfully handled — never a blanket `except Exception: pass`.
- Script-style code gets a `main()` + `if __name__ == "__main__":` entry point.
- Section headers (see below) once a file has more than ~2-3 logical blocks; skip them for short files — don't decorate a 20-line script.

Default to this standard silently, the way you'd default to correct syntax. Don't narrate that you're "applying the code-structure skill" — just write clean code.

---

## MODE B — Refactoring / Upgrading Existing Code

This is a **readability and organization pass, not a logic refactor.** The output must run identically to the input.

### The absolute rule

> The code must behave exactly as it did before.

Do not touch: algorithms, math/statistical operations, model architecture or training/eval logic, data transformations, preprocessing, feature engineering, hyperparameters, random seeds, control-flow decisions, conditions, order of operations where order affects behavior, or return values/API surface. This applies with extra weight to research/ML code, where the implementation is part of the scientific record — preprocessing, splits, loss functions, metrics, and seeds are not yours to "improve" here.

If you think something is a bug, inefficient, or outdated: **do not fix it silently.** Flag it separately (format below) and wait for a decision before touching it.

### What you ARE free to change

Formatting, whitespace, indentation, line organization, naming (when it can't break external references), comments, docstrings, type hints that don't alter runtime behavior, import order, constant placement, logical grouping, dead/unused-import removal (only when provably safe), section organization, PEP 8 / language-standard compliance.

Test for every edit: **"Am I changing what this code does, or only making the same code easier to read?"** If it's not clearly the latter, stop and ask.

### Guardrails against over-eagerness

- Don't turn `if/else` into a ternary, a `for` loop into a comprehension, or a loop into a vectorized call "because it's cleaner." Only make the swap if it is unambiguously behavior-identical AND clearly more readable — and lean toward leaving it if unsure.
- Don't introduce classes, design patterns, dependency injection, or new abstraction layers the project didn't already have.
- Don't rename a function/variable if it's referenced externally (other modules, notebooks, configs, APIs) unless you've confirmed it's safe — otherwise flag and ask.
- Don't split a function just because it's long; only extract a piece with a genuinely separate responsibility.
- Minimal diff wins: if a file only needs formatting, format it — don't rewrite the whole file because one function bugged you.

### Preserving the original on substantial rewrites

When a block is rewritten enough that the diff isn't trivially reviewable, keep the original directly below it, clearly separated and commented out:

```python
# ============================================================
# PROFESSIONAL IMPLEMENTATION
# ============================================================
... new version ...

# ============================================================
# LEGACY / ORIGINAL IMPLEMENTATION — kept for rollback/comparison.
# Do not execute.
# ============================================================
# ... original version, untouched ...
```

Skip this for pure formatting/whitespace/comment changes — only do it when the actual code shape changed enough that a reviewer would want the before/after side by side.

### When you spot something that looks wrong

Never fix it inline. Surface it like this, then keep going with everything else, and wait on this specific item:

```
Potential issue: <what and where>
Impact if left as-is: <why it might matter>
Suggested fix: <what you'd change>
Approval needed before I touch this: YES
```

### Before/after checklist

Before editing a file: know its inputs, outputs, side effects, and anything external that imports from it.
After editing: re-check imports, signatures, return values, control flow, and run whatever tests/syntax checks are available. Say plainly if something couldn't be verified — don't claim behavior is preserved on faith.

### Change report

Give one of these per file after a refactor pass:

```
FILE: <name>

CHANGES MADE:
- ...

BEHAVIOUR: Preserved / Potentially affected (say which and why)

LOGIC CHANGES: None  [this line should almost always say "None" — if it doesn't, that change needed approval first]

POTENTIAL ISSUES DISCOVERED:
- None
  or
- <see flag format above>

APPROVAL REQUIRED: No / Yes — <reason>
```

Keep this report short — a few bullets, not a wall of text — unless the user asks for detail.

---

## Shared Style Reference

**Naming (Python; adapt casing convention to the project's existing language if it's R/SQL/etc.):**
`snake_case` → functions, variables · `PascalCase` → classes · `UPPER_CASE` → constants.
Avoid abbreviations unless they're standard in the domain (`df`, `X_train` are fine; `tr_data`, `val_l` are not).

**Docstrings** (NumPy style, adjust to whatever the project already uses if one exists):

```python
def calculate_metrics(predictions, targets):
    """
    Calculate evaluation metrics for model predictions.

    Parameters
    ----------
    predictions : array-like
        Model-generated predictions.
    targets : array-like
        Ground-truth target values.

    Returns
    -------
    dict
        Calculated metrics.
    """
```

**Comments** explain *why*, not *what*. `# Increment counter` is noise; `# Track processed samples so progress logging stays in sync with iteration order` earns its line.

**Imports:**

```python
# Standard library
import os
from pathlib import Path

# Third-party
import numpy as np

# Local
from src.data.loader import load_dataset
```

**Section headers** (use sparingly — only when they actually help navigation in a longer file):

```python
# ============================================================
# Core Functions
# ============================================================
```

**Consistency**: once a convention is picked for a project, hold it across every file touched in that project — same docstring style, same header style, same error-handling posture. Don't let one file look hand-rolled and another look enterprise.

---

## ChatBot Project-Specific Architectural Standards

For this specific project, adhere strictly to the following structural and architectural rules derived from our recent refactoring efforts:

### 1. File Size & Sub-Packaging
- **Rule:** If a Python module exceeds ~150 lines, it must be split into a logical sub-package.
- **Implementation:** Create a directory (e.g., `backend/config/`), break the logic into focused sub-modules, and strictly re-export the public API via the `__init__.py`. 
- **Goal:** Zero changes required to external import statements when splitting a file.

### 2. Magic Strings & Constants
- **Rule:** No raw magic strings for state keys, roles, or event types anywhere in the application logic or UI.
- **Implementation:** Import all structural strings from `backend/constants.py` (e.g., `SESSION_THREAD_ID`, `ROLE_USER`, `MSG_TYPE_AI`).

### 3. Centralized Precision Logging
- **Rule:** `print()` statements are forbidden in application code.
- **Implementation:** Use Python's built-in `logging`. Every module must define `logger = logging.getLogger(__name__)` right after imports. The logger is configured centrally once in `app.py` via `backend.logger.setup_logging()`.

### 4. Auto-Discovery (Open/Closed Principle)
- **Rule:** Adding a new feature (like a tool) should not require modifying existing registry files or lists.
- **Implementation:** Use `pkgutil` auto-discovery where applicable. For example, adding a tool means dropping a `.py` file into `backend/tools/` and exposing a `TOOLS` list. The package `__init__.py` will automatically discover and bind it.

### 5. Fault Tolerance & Resiliency
- **Rule:** The app should fail gracefully and never crash silently.
- **Implementation:** 
  - Wrap potentially blocking database calls in exponential backoff retry logic (`execute_with_retry`) to handle SQLite WAL lock contention.
  - Use lazy factory instantiation (`@st.cache_resource` for the LangGraph bot) so misconfigurations cause visible, localized errors rather than silent module-level crashes.

---

## Quick decision rule

```
Does this change alter what the program does?
  NO  → proceed, it's a quality improvement
  YES / NOT SURE → stop, flag it, ask
```

Minimal change, maximum clarity, zero silent surprises.
