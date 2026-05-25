# mxlit Codebase — DRY Violation Analysis & Refactor Plan

## Executive Summary

The audit found **four distinct categories** of DRY violations. None individually break correctness,
but together they mean that every future feature, bug-fix, or new component type must be applied in
multiple places simultaneously or risk silent divergence. The most impactful is the
component-registration boilerplate, which recurs **43 times** across six files; the second most
impactful is the duplicated script-execution block in `server.py`.

---

## Section 1 — Identified Violations

### 1A · Component Registration Boilerplate *(43 repetitions across 6 files)*

Every component function across `text.py`, `data.py`, `widgets.py`, `charts.py`, `media.py`, and
`status.py` opens with an identical three-part ritual:

```python
def write(*args, class_: str = ""):
    ctx = get_context()            # ① lookup  — repeated 43×
    if ctx:                        # ② guard   — repeated 43×
        ctx.add_component({...})   # ③ register — repeated 41×
    else:
        print(*args)               # ④ fallback — repeated ~40×
```

The only part that differs is the component dict payload. Adding cross-cutting behaviour (e.g.,
component IDs, render hooks, performance tracing) requires 43 edits.

**Sub-violation: duplicated `_generate_key` utility.**
The helper exists independently in `widgets.py` (line 5) and `charts.py` (line 4) with slightly
different signatures and reversed argument order.

---

### 1B · Theme Resolution Split *(3 sources of truth)*

**`server.py` lines 15–17** — thin helper called by both `/interact` and `/modify`:

```python
def _resolve_theme() -> dict:
    return {**_THEME_DEFAULTS, **session_state.get(THEME_KEY, {})}
```

**`components/theme.py` line 77** — the user-facing `mt.theme()` opens with the *identical* merge:

```python
current: dict[str, str] = {**_DEFAULTS, **session_state.get(THEME_KEY, {})}
```

`_THEME_DEFAULTS` and `_DEFAULTS` are the same object. The merge rule — and its precedence — lives
in two places.

**CSS layer divergence.** The theme's default values are hardcoded a third time in `static/input.css`
as 48 build-time CSS custom properties (24 light, 24 dark). These hex values already exist in
`theme.json`. They must be kept in sync manually whenever the Material palette seed changes.
The runtime override block in `components.html` (lines 1–29) then overrides *thirteen* of those
same variables, making the `:root {}` block in `input.css` partially redundant at runtime.

---

### 1C · Script Execution & Error Handling *(verbatim copy-paste between two endpoints)*

The following 12-line block is copy-pasted **without modification** between `/interact` (lines 95–110)
and `/modify` (lines 190–202):

```python
script_path = get_script_path()
ctx = AppContext()
token = _current_context.set(ctx)
try:
    runpy.run_path(script_path, run_name="__main__")
except Exception as e:
    if type(e).__name__ == "RerunException":
        pass
    else:
        ctx.add_component({"type": "write", "content": f"Error executing script: {e}"})
finally:
    _current_context.reset(token)
```

Two embedded problems:
1. **`type(e).__name__ == "RerunException"`** is a fragile string-comparison guard. `RerunException`
   is defined as a *local class* inside `mxlit.rerun()`, so it cannot be imported and caught
   normally. Any unrelated exception with that name would be silently swallowed.
2. The **form-value type-coercion block** (6 `isinstance` checks, 20 lines) is also copy-pasted
   between `/interact` (lines 65–86) and `/modify` (lines 167–188).

---

### 1D · Dual Package Manifests *(setup.py vs. pyproject.toml)*

`setup.py` and `pyproject.toml` both declare the package's name, version, description, authors,
license, `requires-python`, classifiers, `install_requires`/`dependencies`, and the `mxlit` entry
point. Every release requires updating both files atomically.

Additional inconsistency: `pytailwindcss` is listed as a `dev` extra in `setup.py` but is entirely
absent from `pyproject.toml`.

The `STATIC_DIR` path is also computed independently in two modules:

```python
_STATIC_DIR = Path(__file__).parent / "static"   # cli.py line 10
STATIC_DIR  = Path(__file__).parent / "static"   # server.py line 34
```

---

## Section 2 — Proposed Solutions

### Solution A: `register_component` Helper + `_registry.py`

Replace the 43-repetition boilerplate with a single function:

```python
# src/mxlit/components/_registry.py
from mxlit.context import get_context

def register_component(payload: dict, *, fallback=None) -> None:
    ctx = get_context()
    if ctx:
        ctx.add_component(payload)
    elif fallback is not None:
        fallback()
```

Every display-only component collapses from 5 lines to 2–3:

```python
def title(text: str, class_: str = ""):
    register_component(
        {"type": "title", "content": text, "class_": class_},
        fallback=lambda: print(f"# {text}"),
    )
```

Move the single canonical `_generate_key` here and import it from both `widgets.py` and `charts.py`.

---

### Solution B: `ThemeManager` in `constants/theme.py`

```python
class ThemeManager:
    def resolve(self) -> dict[str, str]:
        """Merge session overrides onto defaults. Used by templates."""
        return {**_DEFAULTS, **session_state.get(THEME_KEY, {})}

    def apply(self, tokens: dict | None = None) -> dict[str, str]:
        """Full apply: absorb widget keys, merge overrides, persist."""
        current = self.resolve()
        # … widget absorption + explicit override logic …
        session_state[THEME_KEY] = current
        return dict(current)

theme_manager = ThemeManager()
```

`server.py` drops `_resolve_theme()` and calls `theme_manager.resolve()`.
`components/theme.py::theme()` delegates to `theme_manager.apply()`.

**CSS sync:** Add a `mxlit sync-css-tokens` CLI sub-command that writes the `:root {}` and
`[data-theme="dark"] {}` blocks in `input.css` directly from `_DEFAULTS`, eliminating manual hex
maintenance.

---

### Solution C: `_run_script` & `_coerce_form_value` in `server.py`

```python
async def _run_script() -> AppContext:
    script_path = get_script_path()
    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except RerunException:         # caught by type, not string
        pass
    except Exception as e:
        ctx.add_component({"type": "write", "content": f"Error: {e}"})
    finally:
        _current_context.reset(token)
    return ctx

def _coerce_form_value(value: str, current) -> object:
    if isinstance(current, bool):
        return str(value).lower() in ("true", "1", "yes", "on")
    if isinstance(current, int):
        try: return int(value)
        except ValueError: return value
    if isinstance(current, float):
        try: return float(value)
        except ValueError: return value
    return value

async def _apply_form_data(form_data) -> None:
    for key, value in form_data.items():
        session_state[key] = _coerce_form_value(value, session_state.get(key, value))
```

**Fix `RerunException`:** Move the class to `src/mxlit/_exceptions.py` at module level as a
`BaseException` subclass (consistent with Python's control-flow signal convention — `SystemExit`,
`KeyboardInterrupt`). Import and catch it by type everywhere.

---

### Solution D: Retire `setup.py`, Consolidate Paths

- Delete `setup.py`; `pyproject.toml` (hatchling) is the active build config.
- Add `[project.optional-dependencies] dev = ["pytailwindcss"]` to `pyproject.toml`.
- Create `src/mxlit/_paths.py` with `PACKAGE_DIR`, `STATIC_DIR`, `TEMPLATES_DIR`, `INPUT_CSS`,
  `OUTPUT_CSS`; import from it in both `cli.py` and `server.py`.

---

## Section 3 — Implementation Roadmap

Tasks ordered by **impact-to-risk ratio** (highest isolation, lowest breakage risk first).

### Priority 1 — Immediate (Zero Behavioral Risk)

| Task | Action | Effort |
|------|--------|--------|
| 1.1 | Extract `_run_script` and `_coerce_form_value` / `_apply_form_data` in `server.py` | 1 h |
| 1.2 | Move `RerunException` to `src/mxlit/_exceptions.py`; catch by type | 30 min |
| 1.3 | Delete `setup.py`; add `pytailwindcss` dev extra to `pyproject.toml` | 15 min |
| 1.4 | Create `src/mxlit/_paths.py`; update `cli.py` and `server.py` imports | 20 min |

### Priority 2 — Short-Term (Cross-File, Low Risk)

| Task | Action | Effort |
|------|--------|--------|
| 2.1 | Create `src/mxlit/components/_registry.py` with `register_component` and unified `_generate_key` | 1 h |
| 2.2 | Migrate all display-only components (text, media, status, data, charts) to `register_component` | 2–3 h |
| 2.3 | Migrate widget functions (return-value functions) to use `register_component` inline | 1 h |

### Priority 3 — Medium-Term (Architectural)

| Task | Action | Effort |
|------|--------|--------|
| 3.1 | Introduce `ThemeManager`; retire `_resolve_theme()` in `server.py` | 2 h |
| 3.2 | Add `mxlit sync-css-tokens` CLI command to generate `:root {}` from `_DEFAULTS` | 3–4 h |

### Priority 4 — Long-Term (Structural)

| Task | Action | Effort |
|------|--------|--------|
| 4.1 | Add `ComponentMiddleware` hook in `register_component` for IDs, tracing, conditional rendering | variable |
| 4.2 | Move `runpy.run_path` to `asyncio.to_thread` to unblock the SSE event loop | 2 h |

---

## Dependency Map

```
Task 1.2 (RerunException)   ──► Task 1.1 (_run_script)
Task 1.4 (_paths.py)        ──► cli.py + server.py cleanup
Task 2.1 (_registry.py)     ──► Task 2.2, Task 2.3
Task 3.1 (ThemeManager)     ──► Task 1.1 (uses resolve() in _run_script)
Task 3.2 (sync-css-tokens)  ──► Task 3.1 (ThemeManager exposes _DEFAULTS)
```

---

## Quick-Reference: Violation → Solution Matrix

| # | Violation | Location | Repetitions | Solution | Tasks |
|---|-----------|----------|-------------|---------|-------|
| 1A | `get_context()` / `add_component` boilerplate | 6 component files | 43 | `register_component` helper | 2.1, 2.2, 2.3 |
| 1A | `_generate_key` duplicated | `widgets.py`, `charts.py` | 2 | Merge into `_registry.py` | 2.1 |
| 1B | `_resolve_theme` vs `theme()` merge logic | `server.py`, `theme.py` | 2 | `ThemeManager.resolve()` | 3.1 |
| 1B | CSS tokens hardcoded in `input.css` + `theme.json` | `input.css`, `theme.json` | 48 values | Generated `:root {}` block | 3.2 |
| 1C | `runpy` + `AppContext` + error handling block | `server.py` | 2 | `_run_script()` helper | 1.1 |
| 1C | Form value type-coercion block | `server.py` | 2 | `_coerce_form_value` + `_apply_form_data` | 1.1 |
| 1C | `type(e).__name__ == "RerunException"` string check | `server.py` | 2 | Module-level `RerunException` | 1.2 |
| 1D | Dual `setup.py` + `pyproject.toml` manifests | root | 2 | Delete `setup.py` | 1.3 |
| 1D | `STATIC_DIR` computed independently | `cli.py`, `server.py` | 2 | `_paths.py` shared constants | 1.4 |
