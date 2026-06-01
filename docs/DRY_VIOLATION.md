# mxlit Codebase — DRY Violation Analysis & Refactor Plan

## Table of Contents

- [Executive Summary](#executive-summary)
- [Section 1 — Identified Violations](#section-1--identified-violations)
  - [1A · Component Registration Boilerplate ✅](#1a--component-registration-boilerplate-43-repetitions--resolved)
  - [1B · Theme Resolution Split ✅](#1b--theme-resolution-split-3-sources-of-truth--resolved)
  - [1C · Script Execution & Error Handling ✅](#1c--script-execution--error-handling-verbatim-copy-paste--resolved)
  - [1D · Path Constants & Package Manifest ✅](#1d--path-constants--package-manifest--fully-resolved)
  - [1E · Parallel Container Patterns ✅](#1e--parallel-container-patterns--fully-resolved)
- [Section 2 — Solutions](#section-2--proposed-solutions)
  - [Solution A: Decorator Architecture ✅](#solution-a-decorator-architecture-in-basepy--implemented--supersedes-original-proposal)
  - [Solution B: `ThemeManager` ✅](#solution-b-thememanager-in-constantsthemepy--implemented)
  - [Solution C: `_run_script` & helpers ✅](#solution-c-_run_script--_coerce_form_value--implemented-in-serverpy)
  - [Solution D: `_paths.py` ✅](#solution-d-_pathspy-shared-constants--implemented)
  - [Solution E: Migrate Containers ✅](#solution-e-migrate-containercontextmanager-to-compositecomponent--implemented)
- [Section 3 — Implementation Roadmap](#section-3--implementation-roadmap)
- [Dependency Map](#dependency-map)
- [Quick-Reference: Violation → Solution Matrix](#quick-reference-violation--solution-matrix)

---

## Executive Summary

The original audit found **four distinct categories** of DRY violations.  Since then, significant
refactoring has resolved the majority of them:

| Category | Original severity | Current status |
|---|---|---|
| 1A — Component registration boilerplate (43×) | Critical | ✅ **Fully resolved** |
| 1B — Theme resolution split (3 sources) | Medium | ✅ **Fully resolved** |
| 1C — Script execution & form-coercion copy-paste | High | ✅ **Fully resolved** |
| 1D — Path constants & package manifest | Low | ✅ **Fully resolved** |
| 1E — Parallel container patterns | Low | ✅ **Fully resolved** |

**All violations are now closed.** The codebase has zero instances of the original boilerplate patterns.

---

## Section 1 — Identified Violations

### 1A · Component Registration Boilerplate *(43 repetitions — ✅ RESOLVED)*

**Original violation:** Every component function opened with an identical three-part ritual:

```python
def write(*args, class_: str = ""):
    ctx = get_context()            # ① repeated 43×
    if ctx:                        # ② repeated 43×
        ctx.add_component({...})   # ③ repeated 41×
    else:
        print(*args)               # ④ repeated ~40×
```

**Resolution:** `src/mxlit/components/base.py` introduces two factory decorators and a base class
hierarchy that encapsulate the entire boilerplate:

| Class / Decorator | Replaces | Used by |
|---|---|---|
| `@component(ComponentType.X)` | ①②③④ for display components | `text.py`, `charts.py`, `data.py`, `media.py`, `status.py`, new OAT primitives in `layout.py` |
| `@widget_component(ComponentType.X, htmx=…, oat=…)` | ①②③ for stateful widgets | all 16 widget functions in `widgets.py` |
| `BaseComponent` dataclass | Manual dict construction + `ctx.add_component()` | `status.exception()`, composite factories |
| `CompositeComponent(BaseComponent)` | `ContainerContextManager` boilerplate for nested-child components | `card`, `dialog`, `grid`, `input_group` in `layout.py` |

**Current function counts (all boilerplate eliminated):**

| File | Functions | Pattern |
|------|-----------|---------|
| `text.py` | 12 | `@component` (3 via `_make_heading` factory) |
| `widgets.py` | 16 | `@widget_component` |
| `charts.py` | 4 | `@component` via `_make_chart` factory |
| `data.py` | 4 | `@component` |
| `media.py` | 4 | `@component` |
| `status.py` | 5 | 4 via `@component` + `_make_status_variant`; 1 (`exception`) via `BaseComponent` directly |
| `layout.py` | 14 OAT primitives | `@component` or `CompositeComponent` factory |
| **Total** | **59** | Zero instances of the old boilerplate |

**Sub-violation `_generate_key` — ✅ RESOLVED.**
`BaseComponent.generate_key(component_type, discriminator)` is the single canonical implementation.
Both `widgets.py` and `charts.py` import and call it from `base.py`.  The two incompatible private
`_generate_key` helpers no longer exist.

---

### 1B · Theme Resolution Split *(✅ FULLY RESOLVED)*

**Resolution:**

- **`server.py`** — the `_resolve_theme()` helper was removed. All three endpoints now call
  `theme_manager.resolve()` from `mxlit.constants`.
- **`components/theme.py`** — the inline merge + absorb + persist block was replaced with a single
  delegation call `return theme_manager.apply(tokens)`.
- **`constants/theme.py`** — `ThemeManager` is the single authoritative owner of the merge logic:
  `resolve()` for lightweight reads, `apply()` for the full absorb-merge-persist cycle.
- **`static/input.css`** — the 34 hardcoded CSS custom-property values are now regenerated from
  `oat.min.css` via `mxlit sync-css-tokens` (Task 3.2), eliminating the manual sync risk.

---

### 1C · Script Execution & Error Handling *(verbatim copy-paste — ✅ RESOLVED)*

**Original violation:** A 12-line block (runpy + AppContext + error handler) was copy-pasted
between `/interact` and `/modify`.  The form-value type-coercion block (3 `isinstance` checks,
22 lines) was also duplicated.  `RerunException` was a fragile local class caught by string name.

**Resolution:** Three helpers now live at the top of `server.py`:

```python
# src/mxlit/server.py

def _coerce_form_value(key: str, value: str) -> object:  # single canonical type coercion
    ...

def _apply_form_data(form_data) -> None:                 # single write-to-session call site
    for key, value in form_data.items():
        session_state[key] = _coerce_form_value(key, value)

def _run_script(script_path: str) -> AppContext:         # single canonical script executor
    reset_render_counts()
    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except RerunException:   # ← caught by type, not by string comparison
        pass
    except Exception as e:
        ctx.add_component({"type": "write", "content": f"Error executing script: {e}"})
    finally:
        _current_context.reset(token)
    return ctx
```

`RerunException` is a module-level `BaseException` subclass in `src/mxlit/_exceptions.py`,
imported by name in `server.py`.  All three endpoints (`/interact`, `/refresh/{id}`, `/modify`)
call `_apply_form_data` + `_run_script` without any duplication.

---

### 1D · Path Constants & Package Manifest *(✅ FULLY RESOLVED)*

- **Task 1.3 ✓** — `setup.py` deleted; `pyproject.toml` (hatchling) is the sole build config with
  `pytailwindcss` in `[project.optional-dependencies] dev`.

- **Task 1.4 ✓** — `src/mxlit/_paths.py` centralises all five path constants:

  ```python
  # src/mxlit/_paths.py
  PACKAGE_DIR   = Path(__file__).parent
  STATIC_DIR    = PACKAGE_DIR / "static"
  TEMPLATES_DIR = PACKAGE_DIR / "templates"
  INPUT_CSS     = STATIC_DIR / "input.css"
  OUTPUT_CSS    = STATIC_DIR / "style.css"
  ```

  `cli.py` imports `INPUT_CSS, OUTPUT_CSS`; `server.py` imports `STATIC_DIR, TEMPLATES_DIR`.
  No path is computed independently in any module.

---

### 1E · Parallel Container Patterns *(✅ FULLY RESOLVED)*

**Resolution:** `ContainerContextManager` has been deleted from `layout.py`. Every composite
container now uses `CompositeComponent`:

| Function | Type | Return |
|---|---|---|
| `columns(spec)` | `ComponentType.COLUMN` | `list[CompositeComponent]` |
| `tabs(labels)` | `ComponentType.TAB` | `list[CompositeComponent]` |
| `expander(label)` | `ComponentType.EXPANDER` | `CompositeComponent` |
| `container(horizontal)` | `ComponentType.CONTAINER` | `CompositeComponent` |
| `sidebar` singleton | `ComponentType.SIDEBAR` | `CompositeComponent` (via `Sidebar.__enter__`) |
| `card(header, footer)` | `ComponentType.CARD` | `CompositeComponent` |
| `dialog(title)` | `ComponentType.DIALOG` | `CompositeComponent` |
| `grid()` | `ComponentType.GRID` | `CompositeComponent` |
| `input_group(prefix)` | `ComponentType.INPUT_GROUP` | `CompositeComponent` |

`ComponentType.COLUMN = "column"` and `ComponentType.TAB = "tab"` were added to `base.py` so
all types are registered in the exhaustive enum.  `page_config()` retains its direct
`get_context()` call — it is not a container and has no equivalent in either pattern.

---

## Section 2 — Proposed Solutions

### Solution A: Decorator Architecture in `base.py` *(✅ IMPLEMENTED — supersedes original proposal)*

The original proposal was a `register_component` helper in `_registry.py`.  The actual
implementation is architecturally superior: `base.py` provides a full `BaseComponent` dataclass
hierarchy with two factory decorators.

```python
# src/mxlit/components/base.py  (implemented)

@dataclass
class BaseComponent:
    type: ComponentType
    props: dict
    _htmx: HtmxProps | None
    _oat:  OatProps  | None
    def __post_init__(self): self._register()   # single registration point

@dataclass
class CompositeComponent(BaseComponent):        # deferred registration via with block
    ...

def component(component_type, *, htmx=None, oat=None):
    """Decorator for display-only components."""
    ...

def widget_component(component_type, *, htmx=None, oat=None):
    """Decorator for stateful widgets (reads + writes session_state)."""
    ...
```

Key advantages over the original proposal:
- `HtmxProps` and `OatProps` dataclasses make HTMX/OAT attributes type-safe and discoverable
- `ComponentType(str, Enum)` is the authoritative registry of all component strings
- `BaseComponent.generate_key()` is the single canonical key generator
- `CompositeComponent` handles nested-children collection without any boilerplate

---

### Solution B: `ThemeManager` in `constants/theme.py` *(✅ IMPLEMENTED)*

Extracted the common merge rule from `_resolve_theme()` (server.py) and `theme()` (theme.py)
into a single object:

```python
# proposed: src/mxlit/constants/theme.py

class ThemeManager:
    def resolve(self) -> dict[str, str]:
        """Lightweight read used by server templates. No side effects."""
        return {**_DEFAULTS, **session_state.get(THEME_KEY, {})}

    def apply(self, tokens: dict | None = None) -> dict[str, str]:
        """Full apply: absorb color-picker widget keys, merge overrides, persist."""
        current = self.resolve()
        for flat_key, theme_key in _FLAT_KEYS.items():
            if flat_key in session_state:
                current[theme_key] = session_state[flat_key]
                del session_state[flat_key]
        if tokens:
            for key, value in tokens.items():
                if key not in _DEFAULTS:
                    raise ValueError(f"Unknown token key: {key!r}")
                current[key] = value
        session_state[THEME_KEY] = current
        return dict(current)

theme_manager = ThemeManager()
```

`server.py` replaced `_resolve_theme()` with `theme_manager.resolve()`.
`components/theme.py::theme()` delegates its merge + persist logic to `theme_manager.apply()`.

**CSS sync:** `mxlit sync-css-tokens` (Task 3.2) parses `oat.min.css` and regenerates the
`:root {}` and `[data-theme="dark"] {}` blocks in `input.css`, eliminating the 22+ hand-maintained
values. Run after upgrading `oat.min.css` to keep the fallback CSS in sync.

---

### Solution C: `_run_script` & `_coerce_form_value` *(✅ IMPLEMENTED in `server.py`)*

Implemented exactly as proposed.  See `server.py` lines 31–70.  All three endpoints call the
shared helpers; `RerunException` is caught by type via `_exceptions.py`.

---

### Solution D: `_paths.py` shared constants *(✅ IMPLEMENTED)*

`src/mxlit/_paths.py` exists with all five constants.  Both `cli.py` and `server.py` import from
it.  No module computes its own path constants.

---

### Solution E: Migrate `ContainerContextManager` to `CompositeComponent` *(✅ IMPLEMENTED)*

`ContainerContextManager` has been deleted.  All containers now use `CompositeComponent`:

- `columns(spec)` returns a **list** of `CompositeComponent(type=COLUMN)`.  Each element is an
  independent context manager; the template's look-ahead grouping logic is unchanged.
- `tabs(labels)` returns a **list** of `CompositeComponent(type=TAB)`.  Same pattern as columns.
- `expander(label)` returns a single `CompositeComponent(type=EXPANDER)`.
- `container(horizontal)` returns a single `CompositeComponent(type=CONTAINER)`.
- `sidebar` singleton delegates `__enter__` / `__exit__` to a fresh `CompositeComponent(type=SIDEBAR)`
  created per `with` block — no cross-request state on the singleton object.
- `ComponentType.COLUMN = "column"` and `ComponentType.TAB = "tab"` added to `base.py`.
- `page_config()` keeps its direct `get_context()` call — it is not a container.

---

## Section 3 — Implementation Roadmap

Tasks ordered by **impact-to-risk ratio**.

### Priority 1 — Immediate (Zero Behavioral Risk)

| Task | Action | Effort | Status |
|------|--------|--------|--------|
| ~~1.1~~ | ~~Extract `_run_script`, `_coerce_form_value`, `_apply_form_data` in `server.py`~~ | ~~1 h~~ | ✅ |
| ~~1.2~~ | ~~Move `RerunException` to `src/mxlit/_exceptions.py`; catch by type~~ | ~~30 min~~ | ✅ |
| ~~1.3~~ | ~~Delete `setup.py`; add `pytailwindcss` dev extra to `pyproject.toml`~~ | ~~15 min~~ | ✅ |
| ~~1.4~~ | ~~Create `src/mxlit/_paths.py`; update `cli.py` and `server.py` imports~~ | ~~20 min~~ | ✅ |

### Priority 2 — Short-Term (Cross-File, Low Risk)

| Task | Action | Effort | Status |
|------|--------|--------|--------|
| ~~2.1~~ | ~~`BaseComponent` + `@component` / `@widget_component` decorators in `base.py`~~ | ~~2 h~~ | ✅ |
| ~~2.2~~ | ~~Migrate display-only components (text, media, status, data, charts)~~ | ~~2–3 h~~ | ✅ |
| ~~2.3~~ | ~~Migrate widget functions to `@widget_component`~~ | ~~1 h~~ | ✅ |
| ~~2.4~~ | ~~Migrate `ContainerContextManager` usages to `CompositeComponent` (columns, tabs, expander, sidebar)~~ | ~~3–4 h~~ | ✅ |

### Priority 3 — Medium-Term (Architectural)

| Task | Action | Effort | Status |
|------|--------|--------|--------|
| ~~3.1~~ | ~~Introduce `ThemeManager`; retire `_resolve_theme()` in `server.py`~~ | ~~2 h~~ | ✅ |
| ~~3.2~~ | ~~Add `mxlit sync-css-tokens` CLI command to regenerate oat.ink CSS vars from code~~ | ~~3–4 h~~ | ✅ |

### Priority 4 — Long-Term (Structural)

| Task | Action | Effort | Status |
|------|--------|--------|--------|
| 4.1 | Add `ComponentMiddleware` hook in `BaseComponent._register()` for IDs, tracing, conditional rendering | variable | ○ |
| 4.2 | Move `runpy.run_path` to `asyncio.to_thread` to unblock the SSE event loop | 2 h | ○ |

---

## Dependency Map

```
Task 2.4 (ContainerContextManager migration) ──► requires CompositeComponent ✅
Task 3.1 (ThemeManager)     ──► can replace _resolve_theme() independently
Task 3.2 (sync-css-tokens)  ──► ThemeManager exposes _DEFAULTS cleanly (optional dep)
Task 4.1 (ComponentMiddleware) ──► requires Task 2.1 complete ✅
```

---

## Quick-Reference: Violation → Solution Matrix

| # | Violation | Location | Repetitions | Solution | Tasks | Status |
|---|-----------|----------|-------------|---------|-------|--------|
| ~~1A~~ | ~~`get_context()` / `add_component` boilerplate~~ | ~~7 files~~ | ~~43~~ | ~~`@component` / `@widget_component` decorators~~ | ~~2.1–2.3~~ | ✅ |
| ~~1A~~ | ~~`_generate_key` duplicated (incompatible signatures)~~ | ~~`widgets.py`, `charts.py`~~ | ~~2~~ | ~~`BaseComponent.generate_key()`~~ | ~~2.1~~ | ✅ |
| ~~1B~~ | ~~`_resolve_theme` vs `theme()` identical merge rule~~ | ~~`server.py`, `theme.py`~~ | ~~2~~ | ~~`ThemeManager.resolve()`~~ | ~~3.1~~ | ✅ |
| ~~1B~~ | ~~34 CSS custom property values hardcoded in `input.css`~~ | ~~`input.css`~~ | ~~34 values~~ | ~~Generated blocks via `mxlit sync-css-tokens`~~ | ~~3.2~~ | ✅ |
| ~~1C~~ | ~~`runpy` + AppContext + error handling block~~ | ~~`server.py`~~ | ~~2~~ | ~~`_run_script()` helper~~ | ~~1.1~~ | ✅ |
| ~~1C~~ | ~~Form value type-coercion block (3 checks, 22 lines)~~ | ~~`server.py`~~ | ~~2~~ | ~~`_coerce_form_value` + `_apply_form_data`~~ | ~~1.1~~ | ✅ |
| ~~1C~~ | ~~`type(e).__name__ == "RerunException"` string check~~ | ~~`server.py`~~ | ~~2~~ | ~~Module-level `RerunException` in `_exceptions.py`~~ | ~~1.2~~ | ✅ |
| ~~1D~~ | ~~Dual `setup.py` + `pyproject.toml` manifests~~ | ~~root~~ | ~~2~~ | ~~Delete `setup.py`~~ | ~~1.3~~ | ✅ |
| ~~1D~~ | ~~`STATIC_DIR` / `TEMPLATES_DIR` computed independently~~ | ~~`cli.py`, `server.py`~~ | ~~2–3~~ | ~~`_paths.py` shared constants~~ | ~~1.4~~ | ✅ |
| ~~1E~~ | ~~Parallel container patterns: `ContainerContextManager` alongside `CompositeComponent`~~ | ~~`layout.py`~~ | ~~2 patterns~~ | ~~Migrate legacy containers to `CompositeComponent`~~ | ~~2.4~~ | ✅ |
