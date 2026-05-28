# mxlit Component Architecture — Refactor Plan

> **Prerequisite reading:** `docs/DRY_VIOLATION.md` — Section 1A documents the 43 instances of
> `get_context() / if ctx: / ctx.add_component()` boilerplate this plan eliminates.

---

## Table of Contents

1. [Overview & Goals](#1-overview--goals)
2. [Architecture Specification](#2-architecture-specification)
   - [2.1 Module Layout After Refactor](#21-module-layout-after-refactor)
   - [2.2 `HtmxProps` — Full HTMX Attribute Schema](#22-htmxprops--full-htmx-attribute-schema)
     - [2.2.1 Type Aliases and Literals](#221-type-aliases-and-literals)
     - [2.2.2 Full `HtmxProps` Dataclass](#222-full-htmxprops-dataclass)
     - [2.2.3 Attribute-to-Field Quick Reference](#223-attribute-to-field-quick-reference)
     - [2.2.4 Usage Examples](#224-usage-examples)
     - [2.2.5 Jinja2 Template Integration](#225-jinja2-template-integration)
   - [2.3 `ComponentType` Enum + `BaseComponent` — Full Definitions](#23-componenttype-enum--basecomponent--full-definitions)
     - [2.3.1 `ComponentType` Enum](#231-componenttype-enum)
     - [2.3.2 `BaseComponent` — Full Class Definition](#232-basecomponent--full-class-definition)
   - [2.4 Design Decisions](#24-design-decisions)
   - [2.5 `OatProps` — OAT Semantic Attribute Schema](#25-oatprops--oat-semantic-attribute-schema)
   - [2.6 Component Factory Pattern](#26-component-factory-pattern)
     - [2.6.1 Problem: Residual Boilerplate After `BaseComponent`](#261-problem-residual-boilerplate-after-basecomponent)
     - [2.6.2 `@component` — Display Components](#262-component--display-components)
     - [2.6.3 `@widget_component` — Interactive Widgets](#263-widget_component--interactive-widgets)
     - [2.6.4 Decorator Wiring Summary](#264-decorator-wiring-summary)
   - [2.7 Atomic Composition](#27-atomic-composition)
     - [2.7.1 Problem: Repeated Parametric Variants](#271-problem-repeated-parametric-variants)
     - [2.7.2 Status Variant Factory](#272-status-variant-factory)
     - [2.7.3 Heading Atom Factory](#273-heading-atom-factory)
     - [2.7.4 Chart Atom Factory](#274-chart-atom-factory)
     - [2.7.5 Composition vs. Subclassing](#275-composition-vs-subclassing)
3. [Refactoring Examples](#3-refactoring-examples)
   - [3.1 Simple Component — `mt.title`](#31-simple-component--mttitle)
   - [3.2 Complex Widget — `mt.text_input`](#32-complex-widget--mttext_input)
   - [3.3 Status Variants — Atomic Composition in Practice](#33-status-variants--atomic-composition-in-practice)
4. [Template Update Strategy](#4-template-update-strategy)
   - [4.1 Current State](#41-current-state)
   - [4.2 Phase 1 — Additive: `htmx_attrs` Jinja2 Macro](#42-phase-1--additive-htmx_attrs-jinja2-macro)
   - [4.3 Phase 2 — Cleanup (Post Full Migration)](#43-phase-2--cleanup-post-full-migration)
   - [4.4 OAT Data Attribute Strategy — Phase 2](#44-oat-data-attribute-strategy--phase-2)
5. [OAT Component Catalog](#5-oat-component-catalog)
   - [5.1 Existing mxlit Components → OAT Mapping](#51-existing-mxlit-components--oat-mapping)
   - [5.2 New Components Enabled by OAT](#52-new-components-enabled-by-oat)
     - [5.2.1 New UI Primitives (not yet in mxlit at all)](#521-new-ui-primitives-not-yet-in-mxlit-at-all)
     - [5.2.2 Missing Form Input Variants](#522-missing-form-input-variants)
   - [5.3 OAT Attribute Quick Reference](#53-oat-attribute-quick-reference)
   - [5.4 Gap Analysis — Missing Components (oat.ink parity)](#54-gap-analysis--missing-components-oatink-parity)
6. [Composite Design Pattern](#6-composite-design-pattern)
   - [6.1 Problem with Current `ContainerContextManager`](#61-problem-with-current-containercontextmanager)
   - [6.2 `CompositeComponent` — Extended Definition](#62-compositecomponent--extended-definition)
   - [6.3 Template Support for Composite Children](#63-template-support-for-composite-children)
   - [6.4 Worked Example — `mt.card`](#64-worked-example--mtcard)
   - [6.5 Migrating Existing Layout Containers](#65-migrating-existing-layout-containers)
7. [Migration Checklist](#7-migration-checklist)
   - [7.1 Create `src/mxlit/components/base.py`](#71-create-srcmxlitcomponentsbasepy)
   - [7.2 Template — Phase 1 (do this before any Python changes)](#72-template--phase-1-do-this-before-any-python-changes)
   - [7.3 Migrate Display-Only Components (no return value)](#73-migrate-display-only-components-no-return-value)
   - [7.4 Migrate Widget Components (return value preserved)](#74-migrate-widget-components-return-value-preserved)
   - [7.5 Migrate Layout Containers to `CompositeComponent`](#75-migrate-layout-containers-to-compositecomponent)
   - [7.6 Template — Phase 2 (after all widgets migrated)](#76-template--phase-2-after-all-widgets-migrated)
   - [7.7 Final Cleanup](#77-final-cleanup)
8. [Compatibility Notes](#8-compatibility-notes)
9. [File Change Summary](#9-file-change-summary)
   - [9.1 Per-file Breakdown](#91-per-file-breakdown)
   - [9.2 Boilerplate Elimination Summary](#92-boilerplate-elimination-summary)
10. [Full-Page Refresh Bug — Diagnosis & Targeted-Update Plan](#10-full-page-refresh-bug--diagnosis--targeted-update-plan)
    - [10.1 Root-Cause Breakdown (5 compounding problems)](#101-root-cause-breakdown-5-compounding-problems)
    - [10.2 Summary Table](#102-summary-table)
    - [10.3 Target Architecture — Targeted Per-Component Updates](#103-target-architecture--targeted-per-component-updates)
    - [10.4 Work Items](#104-work-items)

---

## 1. Overview & Goals

This plan introduces a `BaseComponent` dataclass in `src/mxlit/components/base.py` as the single,
canonical registration choke-point for all mxlit components. Every component function is then
reduced to constructing a typed object; registration, serialization, and fallback output happen
automatically inside the class.

**In scope**

- `ComponentType` Enum — exhaustive typed registry of all component type identifiers (replaces raw strings)
- `BaseComponent` + `HtmxProps` + `OatProps` class definitions (`base.py`)
- Component Factory Pattern — `@component` / `@widget_component` decorators that eliminate per-function registration boilerplate
- Atomic Composition — generating families of related components (e.g., all status variants) from a single factory function
- Refactored `title`, `text_input`, and status components as worked examples
- Jinja2 template update strategy for HTMX attribute deduplication
- OAT component catalog — semantic HTML mapping + new component opportunities
- Composite design pattern — `CompositeComponent` for tree-structured nesting
- Migration checklist

**Out of scope for this plan** (tracked in `docs/DRY_VIOLATION.md`)

- Tasks 1.1 & 1.2 — `_run_script` / `_coerce_form_value` extraction and `RerunException` move (`server.py`) — see §7.0 prerequisite checklist
- Task 1.4 — `_paths.py` shared path constants — see §7.0
- ~~Task 1.3~~ — ✓ Completed: `setup.py` deleted; `pytailwindcss` added to `pyproject.toml` as dev extra
- Task 3.1 — `ThemeManager` consolidation (`DRY_VIOLATION.md` §Solution B)
- Task 3.2 — `mxlit sync-css-tokens` CLI sub-command
- Multi-user session isolation (architectural concern independent of component rendering)

---

## 2. Architecture Specification

### 2.1 Module Layout After Refactor

```
src/mxlit/components/
├── base.py           ← NEW  : ComponentType, HtmxProps, OatProps, BaseComponent,
│                              CompositeComponent, @component, @widget_component
├── text.py           ← UPDATE: use @component; remove boilerplate; headings via _make_heading
├── data.py           ← UPDATE: use @component; remove boilerplate
├── widgets.py        ← UPDATE: use @widget_component + HtmxProps; remove boilerplate + hashlib
├── charts.py         ← UPDATE: use @widget_component; remove boilerplate + hashlib
├── media.py          ← UPDATE: use @component; remove boilerplate
├── status.py         ← UPDATE: use _make_status_variant factory; 4 functions → 4 lines
└── layout.py         ← UNCHANGED (ContainerContextManager manages its own ctx lifecycle)
```

`layout.py` is explicitly excluded because `ContainerContextManager` uses `ctx.current_target`
directly to implement the `with` block nesting protocol — a concern that `BaseComponent` does not
address and should not absorb.

---

### 2.2 `HtmxProps` — Full HTMX Attribute Schema

Source: <https://htmx.org/reference/>

#### 2.2.1 Type Aliases and Literals

Before the dataclass, declare shared type aliases so every field is
self-documenting and checked by mypy / pyright:

```python
# src/mxlit/components/base.py
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

# ── HTMX type aliases ──────────────────────────────────────────────────────────

# hx-swap values (https://htmx.org/attributes/hx-swap/)
SwapStrategy = Literal[
    "innerHTML",
    "outerHTML",
    "textContent",
    "beforebegin",
    "afterbegin",
    "beforeend",
    "afterend",
    "delete",
    "none",
]

# hx-trigger modifier suffixes that can be appended to any event name,
# e.g. "click once", "keyup changed delay:500ms", "every 2s"
# (free-form string — no Literal constraint, but documented here)
TriggerSpec = str

# hx-params values
ParamsSpec = Literal["*", "none"] | str   # "*" = all, "none" = none, CSV for explicit list

# hx-sync strategies
SyncStrategy = Literal["drop", "abort", "replace", "queue", "queue first",
                        "queue last", "queue all"]

# hx-encoding
EncodingType = Literal["multipart/form-data", "application/x-www-form-urlencoded"]

# hx-history
HistorySpec = Literal["false"]
```

#### 2.2.2 Full `HtmxProps` Dataclass

```python
@dataclass
class HtmxProps:
    """Strongly-typed container for every HTMX attribute.

    Every field maps 1-to-1 to an ``hx-*`` HTML attribute.
    Fields left at ``None`` / ``False`` are excluded from ``to_attrs()``
    output so component dicts stay minimal.

    Defaults (post, target, swap, trigger) match the global <form> in
    base.html so that widget components need only override what differs
    from the standard mxlit interaction pattern.

    ── HTTP method ──────────────────────────────────────────────────────────
    post:    hx-post    — POST to this URL (mxlit default endpoint).
    get:     hx-get     — GET to this URL.
    put:     hx-put     — PUT to this URL.
    patch:   hx-patch   — PATCH to this URL.
    delete:  hx-delete  — DELETE to this URL.

    ── Targeting & swapping ─────────────────────────────────────────────────
    target:     hx-target     — CSS selector for the swap target.
    swap:       hx-swap       — Swap strategy + optional modifiers.
    swap_oob:   hx-swap-oob   — Out-of-band swap selector / "true".
    select:     hx-select     — CSS selector to pluck from response HTML.
    select_oob: hx-select-oob — Out-of-band select (CSS selector list).

    ── Triggering ───────────────────────────────────────────────────────────
    trigger:  hx-trigger  — DOM event(s) that fire the request.
    boost:    hx-boost    — Progressive-enhance <a>/<form> to AJAX.
    validate: hx-validate — Force HTML5 validation before sending.

    ── Request customisation ────────────────────────────────────────────────
    vals:         hx-vals         — Extra values merged into request body (dict → JSON).
    headers:      hx-headers      — Extra headers merged into request (dict → JSON).
    include:      hx-include      — CSS selector of extra elements to include.
    params:       hx-params       — Filter which params are sent ("*" | "none" | CSV).
    encoding:     hx-encoding     — Request encoding type override.
    request:      hx-request      — Low-level request config (timeout, credentials…).
    sync:         hx-sync         — Cross-element request synchronisation strategy.
    disabled_elt: hx-disabled-elt — CSS selector of elements to disable during request.
    indicator:    hx-indicator    — CSS selector of spinner element.
    confirm:      hx-confirm      — Confirmation dialog text before sending.
    prompt:       hx-prompt       — prompt() dialog; value is sent as HX-Prompt header.
    ext:          hx-ext          — Comma-separated extension names to activate.

    ── History & URL ─────────────────────────────────────────────────────────
    push_url:     hx-push-url     — Push this URL into the browser history stack.
    replace_url:  hx-replace-url  — Replace current URL without a new history entry.
    history:      hx-history      — Set to "false" to exclude from history cache.
    history_elt:  hx-history-elt  — Mark element as the snapshot root for history.

    ── Inheritance control ───────────────────────────────────────────────────
    boost:       hx-boost       — (also listed under Triggering)
    disable:     hx-disable     — Opt element (and children) out of htmx processing.
    disinherit:  hx-disinherit  — Disable attribute inheritance for listed attrs.
    inherit:     hx-inherit     — Re-enable inheritance for listed attrs.
    preserve:    hx-preserve    — Keep element unchanged between swaps.
    """

    # ── HTTP method (exactly one should be set) ──────────────────────────────
    post:   str | None = "/interact"   # mxlit default
    get:    str | None = None
    put:    str | None = None
    patch:  str | None = None
    delete: str | None = None

    # ── Targeting & swapping ─────────────────────────────────────────────────
    target:     str | None = "#app-root"          # mxlit default
    swap:       str | None = "innerHTML settle:0"  # mxlit default
    swap_oob:   str | None = None
    select:     str | None = None
    select_oob: str | None = None

    # ── Triggering ───────────────────────────────────────────────────────────
    trigger:  TriggerSpec | None = "change"   # mxlit default
    boost:    bool              = False
    validate: bool              = False

    # ── Request customisation ─────────────────────────────────────────────────
    vals:         dict[str, Any] | str | None = None
    headers:      dict[str, str] | str | None = None
    include:      str | None                  = None
    params:       ParamsSpec | None           = None
    encoding:     EncodingType | None         = None
    request:      dict[str, Any] | str | None = None
    sync:         str | None                  = None   # "{selector}:{strategy}"
    disabled_elt: str | None                  = None
    indicator:    str | None                  = None
    confirm:      str | None                  = None
    prompt:       str | None                  = None
    ext:          str | None                  = None

    # ── History & URL ─────────────────────────────────────────────────────────
    push_url:    str | bool | None = None
    replace_url: str | bool | None = None
    history:     HistorySpec | None = None
    history_elt: bool               = False

    # ── Inheritance control ────────────────────────────────────────────────────
    disable:    bool        = False
    disinherit: str | None  = None
    inherit:    str | None  = None
    preserve:   bool        = False

    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _json_or_str(value: dict | str) -> str:
        """Serialise dict → compact JSON string, pass str through unchanged."""
        return json.dumps(value, separators=(",", ":")) if isinstance(value, dict) else value

    @staticmethod
    def _bool_url(value: str | bool) -> str:
        """hx-push-url / hx-replace-url: True → 'true', False → 'false', str → str."""
        if isinstance(value, bool):
            return "true" if value else "false"
        return value

    def to_attrs(self) -> dict[str, str]:
        """Serialise to a flat ``hx-*`` dict merged by ``BaseComponent.to_dict()``.

        Rules
        -----
        * ``None`` fields → omitted entirely.
        * ``bool`` fields (boost, validate, …) → emitted as ``""`` (bare attribute)
          when ``True``; omitted when ``False``.
        * ``dict`` fields (vals, headers, request) → compact JSON string.
        * ``str | bool`` fields (push_url, replace_url) → ``"true"`` / ``"false"``
          for booleans, URL string as-is.
        """
        d: dict[str, str] = {}

        # ── HTTP method ──────────────────────────────────────────────────────
        if self.post    is not None: d["hx-post"]   = self.post
        if self.get     is not None: d["hx-get"]    = self.get
        if self.put     is not None: d["hx-put"]    = self.put
        if self.patch   is not None: d["hx-patch"]  = self.patch
        if self.delete  is not None: d["hx-delete"] = self.delete

        # ── Targeting & swapping ─────────────────────────────────────────────
        if self.target     is not None: d["hx-target"]     = self.target
        if self.swap       is not None: d["hx-swap"]       = self.swap
        if self.swap_oob   is not None: d["hx-swap-oob"]   = self.swap_oob
        if self.select     is not None: d["hx-select"]     = self.select
        if self.select_oob is not None: d["hx-select-oob"] = self.select_oob

        # ── Triggering ───────────────────────────────────────────────────────
        if self.trigger  is not None: d["hx-trigger"]  = self.trigger
        if self.boost:                d["hx-boost"]    = ""
        if self.validate:             d["hx-validate"] = ""

        # ── Request customisation ─────────────────────────────────────────────
        if self.vals         is not None: d["hx-vals"]         = self._json_or_str(self.vals)
        if self.headers      is not None: d["hx-headers"]      = self._json_or_str(self.headers)
        if self.include      is not None: d["hx-include"]      = self.include
        if self.params       is not None: d["hx-params"]       = self.params
        if self.encoding     is not None: d["hx-encoding"]     = self.encoding
        if self.request      is not None: d["hx-request"]      = self._json_or_str(self.request)
        if self.sync         is not None: d["hx-sync"]         = self.sync
        if self.disabled_elt is not None: d["hx-disabled-elt"] = self.disabled_elt
        if self.indicator    is not None: d["hx-indicator"]    = self.indicator
        if self.confirm      is not None: d["hx-confirm"]      = self.confirm
        if self.prompt       is not None: d["hx-prompt"]       = self.prompt
        if self.ext          is not None: d["hx-ext"]          = self.ext

        # ── History & URL ─────────────────────────────────────────────────────
        if self.push_url    is not None: d["hx-push-url"]    = self._bool_url(self.push_url)
        if self.replace_url is not None: d["hx-replace-url"] = self._bool_url(self.replace_url)
        if self.history     is not None: d["hx-history"]     = self.history
        if self.history_elt:             d["hx-history-elt"] = ""

        # ── Inheritance control ────────────────────────────────────────────────
        if self.disable:                d["hx-disable"]    = ""
        if self.disinherit is not None: d["hx-disinherit"] = self.disinherit
        if self.inherit    is not None: d["hx-inherit"]    = self.inherit
        if self.preserve:               d["hx-preserve"]   = ""

        return d
```

`HtmxProps` is a pure data object — no template logic. `to_attrs()` produces a flat dict that
`BaseComponent.to_dict()` merges at the top level, so the Jinja2 template reads `comp['hx-trigger']`
exactly as it already reads `comp.type` or `comp.class_`.

#### 2.2.3 Attribute-to-Field Quick Reference

| HTML attribute | Python field | Type | Serialisation rule |
|----------------|-------------|------|--------------------|
| `hx-post` | `post` | `str \| None` | as-is |
| `hx-get` | `get` | `str \| None` | as-is |
| `hx-put` | `put` | `str \| None` | as-is |
| `hx-patch` | `patch` | `str \| None` | as-is |
| `hx-delete` | `delete` | `str \| None` | as-is |
| `hx-target` | `target` | `str \| None` | as-is |
| `hx-swap` | `swap` | `str \| None` | as-is (free-form with modifiers) |
| `hx-swap-oob` | `swap_oob` | `str \| None` | as-is |
| `hx-select` | `select` | `str \| None` | as-is |
| `hx-select-oob` | `select_oob` | `str \| None` | as-is |
| `hx-trigger` | `trigger` | `str \| None` | as-is (event spec string) |
| `hx-boost` | `boost` | `bool` | `True` → `""` (bare attr) |
| `hx-validate` | `validate` | `bool` | `True` → `""` |
| `hx-vals` | `vals` | `dict \| str \| None` | dict → compact JSON |
| `hx-headers` | `headers` | `dict \| str \| None` | dict → compact JSON |
| `hx-include` | `include` | `str \| None` | CSS selector |
| `hx-params` | `params` | `str \| None` | `"*"` / `"none"` / CSV |
| `hx-encoding` | `encoding` | `str \| None` | MIME type string |
| `hx-request` | `request` | `dict \| str \| None` | dict → compact JSON |
| `hx-sync` | `sync` | `str \| None` | `"{selector}:{strategy}"` |
| `hx-disabled-elt` | `disabled_elt` | `str \| None` | CSS selector |
| `hx-indicator` | `indicator` | `str \| None` | CSS selector |
| `hx-confirm` | `confirm` | `str \| None` | dialog text |
| `hx-prompt` | `prompt` | `str \| None` | dialog text |
| `hx-ext` | `ext` | `str \| None` | comma-separated extension names |
| `hx-push-url` | `push_url` | `str \| bool \| None` | bool → `"true"`/`"false"`, str → URL |
| `hx-replace-url` | `replace_url` | `str \| bool \| None` | bool → `"true"`/`"false"`, str → URL |
| `hx-history` | `history` | `Literal["false"] \| None` | as-is |
| `hx-history-elt` | `history_elt` | `bool` | `True` → `""` |
| `hx-disable` | `disable` | `bool` | `True` → `""` |
| `hx-disinherit` | `disinherit` | `str \| None` | space-separated attr names or `"*"` |
| `hx-inherit` | `inherit` | `str \| None` | space-separated attr names |
| `hx-preserve` | `preserve` | `bool` | `True` → `""` |

> **Note — `hx-on*`:** The `hx-on:event-name` family is an inline-script feature
> (e.g. `hx-on:click="doSomething()"`). It is intentionally excluded from
> `HtmxProps` because mxlit does not allow arbitrary inline JS. Use HTMX events
> via the SSE channel or `hx-trigger` instead.
>
> **Note — `hx-vars`:** Deprecated by HTMX in favour of `hx-vals`. Not included.

#### 2.2.4 Usage Examples

**Minimal widget (mxlit default endpoint):**

```python
# All four mxlit defaults — equivalent to HtmxProps() with no overrides
HtmxProps()
# → {"hx-post": "/interact", "hx-target": "#app-root",
#    "hx-swap": "innerHTML settle:0", "hx-trigger": "change"}
```

**Debounced text input with extra values:**

```python
HtmxProps(
    trigger = "keyup changed delay:300ms",
    vals    = {"component_type": "text_input", "extra_flag": True},
)
# → {"hx-post": "/interact", "hx-target": "#app-root",
#    "hx-swap": "innerHTML settle:0",
#    "hx-trigger": "keyup changed delay:300ms",
#    "hx-vals": '{"component_type":"text_input","extra_flag":true}'}
```

**File upload form (multipart encoding, indicator, confirm):**

```python
HtmxProps(
    post      = "/upload",
    encoding  = "multipart/form-data",
    indicator = "#upload-spinner",
    confirm   = "Upload this file?",
    swap      = "outerHTML",
)
```

**DELETE button with confirmation and out-of-band counter update:**

```python
HtmxProps(
    post      = None,          # clear the default POST
    delete    = "/item/42",
    confirm   = "Delete this item permanently?",
    target    = "#item-42",
    swap      = "outerHTML",
    swap_oob  = "#item-count",
)
```

**Infinite scroll trigger:**

```python
HtmxProps(
    get     = "/items?page=2",
    trigger = "revealed",      # fires when element scrolls into view
    swap    = "beforeend",
    target  = "#item-list",
)
```

**Read-only display with boosted navigation:**

```python
HtmxProps(
    post    = None,
    get     = "/dashboard",
    boost   = True,
    push_url = True,
)
```

**Cross-element sync (prevent overlapping requests):**

```python
HtmxProps(
    post = "/search",
    sync = "#search-form:replace",   # drop in-flight request, send new one
)
```

#### 2.2.5 Jinja2 Template Integration

The `htmx_attrs(comp)` macro (§4) already handles the `hx-post / target / swap / trigger`
quartet. With the expanded `HtmxProps`, `to_attrs()` can emit any of the 32 fields above,
and the macro needs no changes — it emits whatever keys are present in the dict:

```jinja2
{# components.html — generic htmx attribute emitter #}
{% macro htmx_attrs(comp) %}
  {% for attr, val in comp.items() %}
    {% if attr.startswith('hx-') %}
      {{ attr }}{% if val %}="{{ val }}"{% endif %}
    {% endif %}
  {% endfor %}
{% endmacro %}
```

Boolean bare attributes (`hx-boost`, `hx-validate`, `hx-disable`, `hx-preserve`,
`hx-history-elt`) are serialised as `""` by `to_attrs()`, so the `{% if val %}` branch
is `False` and the attribute is emitted without a value — exactly the correct HTML form.

---

### 2.3 `ComponentType` Enum + `BaseComponent` — Full Definitions

#### 2.3.1 `ComponentType` Enum

```python
# src/mxlit/components/base.py (continued)
from enum import Enum

class ComponentType(str, Enum):
    """Exhaustive typed registry of every mxlit component type identifier.

    Inheriting from ``str`` means ``ComponentType.TITLE == "title"`` is True,
    the value serialises to JSON unchanged, and Jinja2 ``comp.type == 'title'``
    comparisons still hold — zero template changes required.

    The enum serves three purposes:
    1. Eliminates bare string literals scattered across 43+ component functions.
    2. Makes the complete component surface area discoverable via IDE autocomplete.
    3. Provides a single place to add new component types (no hunting across files).
    """
    # ── Text ─────────────────────────────────────────────────────────────────
    WRITE        = "write"
    TITLE        = "title"
    HEADER       = "header"
    SUBHEADER    = "subheader"
    TEXT         = "text"
    MARKDOWN     = "markdown"
    CODE         = "code"
    HTML         = "html"
    LATEX        = "latex"
    BADGE        = "badge"
    NER          = "ner"
    WRITE_STREAM = "write_stream"

    # ── Data ─────────────────────────────────────────────────────────────────
    DATAFRAME    = "dataframe"
    TABLE        = "table"
    JSON         = "json"
    METRIC       = "metric"

    # ── Widgets ───────────────────────────────────────────────────────────────
    BUTTON       = "button"
    TEXT_INPUT   = "text_input"
    CHECKBOX     = "checkbox"
    SLIDER       = "slider"
    NUMBER_INPUT = "number_input"
    TEXT_AREA    = "text_area"
    RADIO        = "radio"
    SELECTBOX    = "selectbox"
    TOGGLE       = "toggle"
    COLOR_PICKER = "color_picker"
    DATE_INPUT   = "date_input"

    # ── Layout ────────────────────────────────────────────────────────────────
    CONTAINER    = "container"
    SIDEBAR      = "sidebar"
    COLUMNS      = "columns"
    TABS         = "tabs"
    EXPANDER     = "expander"
    CARD         = "card"

    # ── Media ─────────────────────────────────────────────────────────────────
    IMAGE        = "image"
    AUDIO        = "audio"
    VIDEO        = "video"
    LOGO         = "logo"

    # ── Charts ────────────────────────────────────────────────────────────────
    LINE_CHART    = "line_chart"
    BAR_CHART     = "bar_chart"
    AREA_CHART    = "area_chart"
    SCATTER_CHART = "scatter_chart"

    # ── Status ────────────────────────────────────────────────────────────────
    STATUS       = "status"

    # ── OAT additions (Phase 2+) ──────────────────────────────────────────────
    SPINNER      = "spinner"
    SKELETON     = "skeleton"
    PROGRESS     = "progress"
    METER        = "meter"
    AVATAR       = "avatar"
    AVATAR_GROUP = "avatar_group"
    DIALOG       = "dialog"
    DROPDOWN     = "dropdown"
    BREADCRUMB   = "breadcrumb"
    BUTTON_GROUP = "button_group"
    GRID         = "grid"
```

#### 2.3.2 `BaseComponent` — Full Class Definition

```python
@dataclass
class BaseComponent:
    """Root of the mxlit component hierarchy.

    Lifecycle
    ---------
    1. A component function constructs a BaseComponent subclass instance.
    2. dataclass __init__ fires, populating all fields.
    3. __post_init__ immediately calls _register().
    4. _register() looks up the active AppContext via get_context():
         • Context found  → ctx.add_component(self.to_dict()) appends to the
                            current render target (respects ContainerContextManager).
         • Context absent → _fallback_fn() is called if provided (console / tests).

    Serialization
    -------------
    to_dict() produces the flat dict format consumed by the Jinja2
    render_component macro in components.html.  It merges five sources:
      {"type": self.type, "id": self.id, "class_": self.className}  — always present
      self.props                                       — component payload
      self._htmx.to_attrs()                            — only for widgets
      self._oat.to_attrs()                             — OAT semantic attrs

    Naming
    ------
    id           Deterministic HTML element id used for targeted HTMX updates
                 (Section 10 targeted-update strategy).  The rendered wrapper
                 element becomes ``<div id="mx-<id>">``, which lets widgets
                 address themselves via ``hx-target="#mx-<id>"`` and
                 ``hx-swap="outerHTML"`` instead of replacing all of
                 ``#app-root``.  Must be stable across script re-runs:
                 • Widgets  — derived from ``generate_key()`` (MD5 of
                              ``"{type}-{discriminator}"``), same value as
                              ``props["key"]``.
                 • Display  — derived from type + sequential render-order index
                              (e.g. ``"title-0"``, ``"text-1"``), assigned by
                              the ``@component`` decorator at registration time.
    className    The only CSS class parameter.  `class_` is not accepted;
                 scripts must use `className` exclusively.  Serialized as
                 "class_" in to_dict() so the Jinja2 template reads
                 {{ comp.class_ }} without changes.
    props        Flat dict of component-specific keys (content, label, value,
                 key, min_value …).  Kept generic on the base class so that
                 BaseComponent stays a thin shell; concrete component functions
                 pass the full payload directly.
    _htmx        Set to an HtmxProps instance only for interactive widgets.
                 Display components leave it None; to_dict() skips it cleanly.
    _oat         Optional OatProps for semantic OAT HTML attributes
                 (data-variant, role, aria-busy, data-spinner, title …).
    _fallback_fn A zero-argument callable invoked when no AppContext is active.
                 Passed as a lambda at construction time; no subclass override
                 needed for the simple print() case.
    """
    type:         ComponentType
    id:           str                = ""
    className:    str                = ""
    props:        dict[str, Any]     = field(default_factory=dict)
    _htmx:        HtmxProps | None  = field(default=None, repr=False)
    _oat:         OatProps  | None  = field(default=None, repr=False)
    _fallback_fn: Callable  | None  = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._register()

    # ── Registration ──────────────────────────────────────────────────────────

    def _register(self) -> None:
        """Append self to the active AppContext, or invoke the fallback."""
        from mxlit.context import get_context          # local import avoids circular
        ctx = get_context()
        if ctx:
            ctx.add_component(self.to_dict())
        elif self._fallback_fn is not None:
            self._fallback_fn()

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Produce the flat dict that render_component in components.html reads.

        Key mapping:
          type      → str value (ComponentType inherits str, so no .value needed)
          id        → "id"       Resolved HTML element id (see resolution order
                                 below).  Jinja2 reads {{ comp.id }}.  Used by
                                 components.html to render the outer wrapper as
                                 ``<div id="mx-{{ comp.id }}">``, enabling
                                 per-component HTMX targeting via
                                 ``hx-target="#mx-{{ comp.id }}"`` (Section 10).
          className → "class_"   Jinja2 reads {{ comp.class_ }}
          props     → merged at the top level  (comp.content, comp.label, …)
          _htmx     → "hx-post", "hx-target", "hx-swap", "hx-trigger" if set
          _oat      → "data-variant", "role", "aria-busy", etc. if set

        id resolution order
        -------------------
        1. ``self.id``  — non-empty string supplied by the caller via
           ``id="my-widget"`` kwarg.  Takes absolute priority; the value is
           used verbatim in the rendered HTML (``id="mx-my-widget"``).
        2. ``props["key"]`` — present for all widgets; the MD5 hash produced by
           ``generate_key()``.  Guarantees stable HTMX targets across re-runs
           even when the user does not supply a custom id.
        3. ``""``  — display components with neither a custom id nor a
           ``props["key"]`` emit an empty id; the ``@component`` decorator is
           responsible for pre-filling ``id`` with a type+index string
           (e.g. ``"title-0"``) before construction so this branch is never
           reached in practice.

        Because ComponentType(str, Enum), ``self.type == "title"`` is True and
        serialisation to JSON / Jinja2 comparison both work without .value.
        """
        resolved_id = self.id or self.props.get("key", "")
        d: dict[str, Any] = {"type": self.type, "id": resolved_id, "class_": self.className}
        d.update(self.props)
        if self._htmx is not None:
            d.update(self._htmx.to_attrs())
        if self._oat is not None:
            d.update(self._oat.to_attrs())
        return d

    # ── Key generation ────────────────────────────────────────────────────────

    @staticmethod
    def generate_key(component_type: ComponentType | str, discriminator: str) -> str:
        """Stable MD5-based widget key.

        Replaces the two divergent _generate_key helpers in widgets.py (where
        the argument order was label, component_type) and charts.py (where it
        was component_type, data).  Both are now unified here.

        Because ComponentType inherits from str, passing a ComponentType value
        directly (e.g. ComponentType.TEXT_INPUT) produces the same hash as
        passing the raw string "text_input" — no existing keys are invalidated.

        Args:
            component_type:  ComponentType enum member or plain str fallback.
            discriminator:   label string for widgets; str(data) for charts.
        """
        import hashlib
        type_str = component_type.value if isinstance(component_type, ComponentType) else component_type
        return hashlib.md5(
            f"{type_str}-{discriminator}".encode()
        ).hexdigest()
```

---

### 2.4 Design Decisions

| Decision | Rationale |
|----------|-----------|
| `ComponentType(str, Enum)` — inherits `str` | `comp.type == "title"` stays True in Jinja2 and JSON; `ComponentType.TITLE == "title"` is True in Python — zero template changes; IDE autocomplete over the entire surface area |
| `@component` / `@widget_component` decorators | Reduces every component function to a pure props-builder; registration, key-extraction, `BaseComponent` construction, and fallback are handled once inside the decorator — not 43 times |
| Atomic composition via factory functions | Families of related components (status variants, heading levels) share one factory; adding a new variant is one line instead of one full function definition |
| `@dataclass` over plain class | `field()` gives zero-cost defaults; auto `__repr__` aids debugging; type checkers understand it natively |
| `__post_init__` fires registration | All fields are populated before `to_dict()` serializes them — no partially-constructed component dicts reach the context |
| `props` as a flat `dict` (not typed sub-fields) | `to_dict()` does a single `d.update(self.props)` and the template continues to read `comp.content`, `comp.label`, etc. with zero template changes |
| `className` only — no `class_` alias | Clean break. `class_` was a Python workaround for a reserved keyword; `className` is the correct modern name. No alias means no ambiguity, no dual code paths, no deprecation lifecycle to manage |
| `_htmx: HtmxProps \| None` | Display-only components set this to `None`; `to_dict()` skips the merge with a single `if` check — no HTMX keys pollute display component dicts |
| `_oat: OatProps \| None` | Separates OAT semantic attributes (`data-variant`, `role`, `aria-busy` …) from component payload, making the OAT contract explicit and discoverable without hunting through props dicts |
| `_fallback_fn: Callable \| None` | Avoids an `_fallback()` override in every subclass; callers pass `lambda: print(...)` at construction time |
| `generate_key` as a `@staticmethod` | Callable from any component function without an instance; single canonical MD5 implementation replaces two divergent private helpers |
| Local import of `get_context` inside `_register` | Prevents the circular import chain `base.py → context.py → (anything in mxlit) → base.py` |

---

### 2.5 `OatProps` — OAT Semantic Attribute Schema

OAT styles elements through semantic HTML attributes rather than class names. Every OAT attribute
that mxlit components currently hardcode in the Jinja2 template (`data-variant`, `role`,
`data-field`, `aria-busy`, `data-spinner`, `title`) can be captured in a typed dataclass so the
Python layer owns the contract — not the template.

```python
# src/mxlit/components/base.py (continued)

@dataclass
class OatProps:
    """Typed carrier for OAT semantic HTML attributes.

    Any field left at its default (None / False) is excluded from to_attrs()
    output so component dicts stay minimal.

    Attributes:
        variant:  data-variant → OAT colour role.
                  Values: "success" | "warning" | "error" | "danger" | "secondary"
        role:     ARIA role attribute.
                  Values: "alert" | "switch" | "status" | "tablist" | "tabpanel" | …
        field:    data-field for form field styling.
                  True  → data-field=""  (standard styled field wrapper)
                  "error" → data-field="error"  (error state with red border)
        busy:     aria-busy="true" — triggers OAT spinner overlay.
        spinner:  data-spinner size modifier.
                  Values: "small" | "large" | "overlay"
        tooltip:  title attribute — OAT renders this as a smooth tooltip on hover.
    """
    variant: str | None       = None
    role:    str | None       = None
    field:   str | bool | None = None
    busy:    bool             = False
    spinner: str | None       = None
    tooltip: str | None       = None

    def to_attrs(self) -> dict[str, str]:
        """Serialize to flat attribute dict merged by BaseComponent.to_dict()."""
        d: dict[str, str] = {}
        if self.variant:
            d["data-variant"] = self.variant
        if self.role:
            d["role"] = self.role
        if self.field is not None:
            d["data-field"] = "" if self.field is True else str(self.field)
        if self.busy:
            d["aria-busy"] = "true"
        if self.spinner:
            d["data-spinner"] = self.spinner
        if self.tooltip:
            d["title"] = self.tooltip
        return d
```

**Usage examples:**

```python
# status.py — error variant (replaces hardcoded data-variant in template)
BaseComponent(
    type      = ComponentType.STATUS,
    className = className,
    props     = {"content": body, "status_type": "error"},
    _oat      = OatProps(variant="error", role="alert"),
)

# New spinner component
BaseComponent(
    type      = ComponentType.SPINNER,
    className = className,
    props     = {},
    _oat      = OatProps(busy=True, spinner="large"),
)

# Button with tooltip
BaseComponent(
    type      = ComponentType.BUTTON,
    className = className,
    props     = {"label": label, "key": widget_key},
    _oat      = OatProps(variant="secondary", tooltip="Click to submit"),
    _htmx     = HtmxProps(trigger="click"),
)
```

---

### 2.6 Component Factory Pattern

#### 2.6.1 Problem: Residual Boilerplate After `BaseComponent`

Even with `BaseComponent`, each component function still manually:

1. Pops `className` out of its parameter list
2. Builds the `props` dict by name
3. Calls `BaseComponent(type=..., className=..., props=..., _htmx=..., _oat=..., _fallback_fn=...)`

With 43 component functions this pattern recurs 43 times. A decorator abstraction eliminates it
entirely: each function becomes a pure *props-builder* — it receives its domain arguments and
returns a `(props, fallback_fn)` or `(props, return_value)` tuple. All construction and
registration happen inside the decorator.

#### 2.6.2 `@component` — Display Components

```python
# src/mxlit/components/base.py (continued)
import functools
from typing import TypeVar

F = TypeVar("F")


def component(
    component_type: ComponentType,
    *,
    htmx: HtmxProps | None = None,
    oat:  OatProps  | None = None,
) -> Callable[[F], F]:
    """Decorator that turns a props-builder into a registered display component.

    The decorated function signature must:
    - Accept any domain arguments (text, label, body, data …)
    - NOT include ``className`` or ``id`` — the decorator extracts both from
      kwargs automatically
    - Return a 2-tuple: ``(props: dict[str, Any], fallback_fn: Callable | None)``

    The decorator:
    1. Pops ``id`` from the call-site kwargs (defaults to ``""``).
    2. Pops ``className`` from the call-site kwargs (defaults to ``""``).
    3. Calls the wrapped function with remaining args/kwargs to get ``props``.
    4. Constructs a ``BaseComponent`` — registration fires in ``__post_init__``.
    5. Returns ``None`` to the call site (display components have no return value).

    The ``id`` kwarg lets callers pin a stable, human-readable selector to any
    display component::

        mt.title("Overview", id="overview-heading")
        # renders: <div id="mx-overview-heading"> … </div>
        # HTMX target: hx-target="#mx-overview-heading"

    If ``id`` is omitted the decorator falls back to a type+index string
    (e.g. ``"title-0"``) so every component still has a non-empty wrapper id.

    Args:
        component_type: The ``ComponentType`` enum member for this component.
        htmx:  Shared ``HtmxProps`` applied to every instance (or ``None``).
        oat:   Shared ``OatProps``  applied to every instance (or ``None``).

    Usage::

        @component(ComponentType.TITLE)
        def title(text: str) -> tuple[dict, Callable]:
            return {"content": text}, lambda: print(f"# {text}")
    """
    _render_counts: dict[str, int] = {}   # tracks per-type render index

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> None:
            custom_id = kwargs.pop("id", "")
            className = kwargs.pop("className", "")
            props, fallback_fn = fn(*args, **kwargs)
            # Resolve id: user-supplied → type+index auto-assign
            if custom_id:
                resolved_id = custom_id
            else:
                idx = _render_counts.get(component_type, 0)
                _render_counts[component_type] = idx + 1
                resolved_id = f"{component_type}-{idx}"
            BaseComponent(
                type         = component_type,
                id           = resolved_id,
                className    = className,
                props        = props,
                _htmx        = htmx,
                _oat         = oat,
                _fallback_fn = fallback_fn,
            )
        return wrapper  # type: ignore[return-value]
    return decorator
```

#### 2.6.3 `@widget_component` — Interactive Widgets

Widget components differ in two ways: they read session state *before* registration and they
return a value to the caller *after* registration. The decorator handles both:

```python
def widget_component(
    component_type: ComponentType,
    *,
    htmx: HtmxProps | None = None,
    oat:  OatProps  | None = None,
) -> Callable[[F], F]:
    """Decorator that registers a stateful widget and preserves its return value.

    The decorated function signature must:
    - Accept domain arguments (label, value, key, …)
    - NOT include ``className`` or ``id`` — both are extracted by the decorator
    - Return a 2-tuple: ``(props: dict[str, Any], return_value: Any)``
      where ``return_value`` is what the caller of ``mt.text_input(...)`` receives.

    The decorator:
    1. Pops ``id`` from kwargs (defaults to ``""``).
    2. Pops ``className`` from kwargs.
    3. Calls the wrapped function — session state is read inside.
    4. Constructs ``BaseComponent`` (registration fires immediately).
    5. Returns ``return_value`` to the caller.

    The ``id`` kwarg lets callers override the default MD5-based wrapper id with
    a human-readable one::

        name = mt.text_input("Name", id="name-field")
        # renders: <div id="mx-name-field"> … </div>
        # widget hx-target: "#mx-name-field"

    When ``id`` is omitted, ``to_dict()`` resolves the id from ``props["key"]``
    (the MD5 hash) so the HTMX target is always stable even without a custom id.

    Args:
        component_type: The ``ComponentType`` enum member for this widget.
        htmx:  ``HtmxProps`` instance shared across every call (set trigger here).
        oat:   ``OatProps``  instance shared across every call.

    Usage::

        @widget_component(
            ComponentType.TEXT_INPUT,
            htmx = HtmxProps(trigger="change"),
            oat  = OatProps(field=True),
        )
        def text_input(label: str, value: str = "", key: str = None) -> tuple[dict, str]:
            widget_key    = key or BaseComponent.generate_key(ComponentType.TEXT_INPUT, label)
            current_value = session_state.get(widget_key, value)
            return (
                {"label": label, "value": current_value, "key": widget_key},
                current_value,
            )
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            custom_id = kwargs.pop("id", "")
            className = kwargs.pop("className", "")
            props, return_value = fn(*args, **kwargs)
            # custom_id overrides the MD5 key; to_dict() falls back to
            # props["key"] automatically when custom_id is empty.
            BaseComponent(
                type      = component_type,
                id        = custom_id,
                className = className,
                props     = props,
                _htmx     = htmx,
                _oat      = oat,
            )
            return return_value
        return wrapper
    return decorator
```

#### 2.6.4 Decorator Wiring Summary

**Case A — default id (auto-assigned)**

```
Call site: mt.title("Hello", className="text-xl")
                │
                ▼
@component(ComponentType.TITLE) wrapper
  ├─ pops id=""          (not supplied → empty)
  ├─ pops className="text-xl"
  ├─ calls title("Hello")
  │         └─ returns ({"content": "Hello"}, lambda: print("# Hello"))
  ├─ resolves id: "" → auto-assign "title-0"  (type + render-order index)
  └─ constructs BaseComponent(
         type         = ComponentType.TITLE,   # "title"
         id           = "title-0",
         className    = "text-xl",
         props        = {"content": "Hello"},
         _fallback_fn = lambda: print("# Hello"),
     )
         └─ __post_init__ → _register() → ctx.add_component(to_dict())

to_dict() output:
  {"type": "title", "id": "title-0", "class_": "text-xl", "content": "Hello"}
```

**Case B — user-supplied custom id**

```
Call site: mt.title("Hello", id="overview-heading", className="text-xl")
                │
                ▼
@component(ComponentType.TITLE) wrapper
  ├─ pops id="overview-heading"
  ├─ pops className="text-xl"
  ├─ calls title("Hello")
  │         └─ returns ({"content": "Hello"}, lambda: print("# Hello"))
  ├─ resolved id: "overview-heading"  (user-supplied → used verbatim)
  └─ constructs BaseComponent(
         type         = ComponentType.TITLE,
         id           = "overview-heading",
         className    = "text-xl",
         props        = {"content": "Hello"},
         _fallback_fn = lambda: print("# Hello"),
     )

to_dict() output:
  {"type": "title", "id": "overview-heading", "class_": "text-xl", "content": "Hello"}
  ↓
  Jinja2 renders: <div id="mx-overview-heading" class="mx-component text-xl"> … </div>
  HTMX target:    hx-target="#mx-overview-heading"
```

**Case C — widget with default id (falls back to MD5 key)**

```
Call site: mt.text_input("Name")
                │
                ▼
@widget_component(ComponentType.TEXT_INPUT, htmx=HtmxProps(trigger="change")) wrapper
  ├─ pops id=""          (not supplied → empty)
  ├─ pops className=""
  ├─ calls text_input("Name")
  │         └─ generates widget_key = md5("text_input-Name") = "a1b2c3…"
  │         └─ returns ({"label": "Name", "value": "…", "key": "a1b2c3…"}, "…")
  └─ constructs BaseComponent(id="", props={"key": "a1b2c3…", …})

to_dict() output:
  resolved_id = self.id or self.props.get("key") → "a1b2c3…"
  {"type": "text_input", "id": "a1b2c3…", "class_": "", "label": "Name", …}
  ↓
  Jinja2 renders: <div id="mx-a1b2c3…" …>
  Widget hx-target: hx-target="#mx-a1b2c3…"   hx-swap="outerHTML"
```

**Case D — widget with user-supplied custom id**

```
Call site: mt.text_input("Name", id="name-field")
                │
                ▼
  ├─ pops id="name-field"
  └─ constructs BaseComponent(id="name-field", props={"key": "a1b2c3…", …})

to_dict() output:
  resolved_id = self.id or self.props.get("key") → "name-field"  (self.id wins)
  {"type": "text_input", "id": "name-field", "class_": "", "label": "Name", …}
  ↓
  Jinja2 renders: <div id="mx-name-field" …>
  Widget hx-target: hx-target="#mx-name-field"   hx-swap="outerHTML"
```

---

### 2.7 Atomic Composition

#### 2.7.1 Problem: Repeated Parametric Variants

Some component families are structurally identical except for one preset parameter:

| Family | Shared structure | Varying parameter |
|--------|-----------------|-------------------|
| `error / warning / success / info` | `type=STATUS`, `role="alert"` | `variant` in `OatProps` |
| `title / header / subheader` | `type=TITLE/HEADER/SUBHEADER`, `props={"content": text}` | component type + fallback prefix |
| `line_chart / bar_chart / area_chart / scatter_chart` | `type=*_CHART`, `props={"data": data}` | component type |

Instead of writing N separate functions, a **factory function** generates them. The factory is an
internal implementation detail; the public API (`mt.error`, `mt.title`, …) is unchanged.

#### 2.7.2 Status Variant Factory

```python
# src/mxlit/components/status.py — after migration

from mxlit.components.base import (
    BaseComponent, ComponentType, OatProps, component,
)


def _make_status_variant(status_type: str) -> Callable:
    """Generate a status display function for the given OAT variant.

    Each generated function is a @component-decorated props-builder pre-wired
    with OatProps(variant=status_type, role="alert"). The status_type string
    also populates props["status_type"] so the Jinja2 template branch still
    reads comp.status_type for CSS class decisions during Phase 1.

    Args:
        status_type: OAT variant name — "error" | "warning" | "success" | "info"
    """
    preset_oat = OatProps(variant=status_type, role="alert")

    @component(ComponentType.STATUS, oat=preset_oat)
    def _fn(body: str) -> tuple[dict, Callable]:
        return (
            {"content": body, "status_type": status_type},
            lambda: print(f"[{status_type.upper()}] {body}"),
        )

    _fn.__name__     = status_type
    _fn.__qualname__ = f"mxlit.components.status.{status_type}"
    return _fn


# Four public functions — four lines
error   = _make_status_variant("error")
warning = _make_status_variant("warning")
success = _make_status_variant("success")
info    = _make_status_variant("info")
```

**Line delta:** The old `status.py` had ~50 lines for 5 functions (4 variants + `exception`).
The new version is ~20 lines for the factory + 4 assignment lines. `exception` keeps its own
function because it requires a `traceback` argument and different fallback logic.

#### 2.7.3 Heading Atom Factory

```python
# src/mxlit/components/text.py — after migration (heading group)

from mxlit.components.base import ComponentType, component


def _make_heading(component_type: ComponentType, fallback_prefix: str) -> Callable:
    """Generate a heading display function for the given heading level.

    Args:
        component_type:  ComponentType.TITLE | HEADER | SUBHEADER
        fallback_prefix: Markdown-style prefix printed when no context is active.
    """
    @component(component_type)
    def _fn(text: str) -> tuple[dict, Callable]:
        return (
            {"content": text},
            lambda: print(f"{fallback_prefix} {text}"),
        )

    _fn.__name__     = component_type.value        # "title" / "header" / "subheader"
    _fn.__qualname__ = f"mxlit.components.text.{component_type.value}"
    return _fn


title     = _make_heading(ComponentType.TITLE,     "#")
header    = _make_heading(ComponentType.HEADER,    "##")
subheader = _make_heading(ComponentType.SUBHEADER, "###")
```

#### 2.7.4 Chart Atom Factory

```python
# src/mxlit/components/charts.py — after migration

from mxlit.components.base import BaseComponent, ComponentType, component


def _make_chart(component_type: ComponentType) -> Callable:
    """Generate a chart display function for the given chart type."""
    @component(component_type)
    def _fn(data, title: str = "") -> tuple[dict, Callable]:
        chart_key = BaseComponent.generate_key(component_type, str(data))
        return (
            {"data": data, "title": title, "key": chart_key},
            lambda: print(f"[Chart: {component_type.value}] {title}"),
        )

    _fn.__name__     = component_type.value
    _fn.__qualname__ = f"mxlit.components.charts.{component_type.value}"
    return _fn


line_chart    = _make_chart(ComponentType.LINE_CHART)
bar_chart     = _make_chart(ComponentType.BAR_CHART)
area_chart    = _make_chart(ComponentType.AREA_CHART)
scatter_chart = _make_chart(ComponentType.SCATTER_CHART)
```

#### 2.7.5 Composition vs. Subclassing

Atomic composition via factory functions should be preferred over subclassing `BaseComponent`
for component variants. The comparison:

| Approach | Pros | Cons |
|----------|------|------|
| Factory function (`_make_status_variant`) | Zero inheritance; introspectable `__name__`; trivial to add variants | Requires `__name__` assignment for clean tracebacks |
| `BaseComponent` subclass per variant | IDE sees class hierarchy | 5× boilerplate per variant; subclasses rarely add behaviour |
| Direct `BaseComponent(...)` per function | Explicit | Repeats all 6 constructor args 43× — the problem we're solving |

The factory approach is the correct choice whenever variants share identical constructor arguments
except for one or two preset values.

---

## 3. Refactoring Examples

### 3.1 Simple Component — `mt.title`

`title` is the canonical display component: no state read, no return value, no HTMX.

**Before** (`src/mxlit/components/text.py` lines 18–29 — identical pattern repeated 12× in this
file alone):

```python
def title(text: str, class_: str = "") -> None:
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "title", "content": text, "class_": class_})
    else:
        print(f"# {text}")
```

**After — Phase 1 (`BaseComponent` only):**

```python
from mxlit.components.base import BaseComponent, ComponentType

def title(text: str, className: str = "") -> None:
    """Display text in title formatting."""
    BaseComponent(
        type         = ComponentType.TITLE,
        className    = className,
        props        = {"content": text},
        _fallback_fn = lambda: print(f"# {text}"),
    )
```

**After — Phase 2 (`@component` decorator):**

```python
from mxlit.components.base import ComponentType, component

@component(ComponentType.TITLE)
def title(text: str) -> tuple[dict, Callable]:
    """Display text in title formatting.

    Args:
        text:      The title string.
        className: Tailwind utility classes applied to the <h1> element.
                   (Extracted from kwargs by the @component decorator — not listed here.)
    """
    return {"content": text}, lambda: print(f"# {text}")
```

**After — Phase 3 (atomic composition, entire heading group):**

```python
from mxlit.components.base import ComponentType
from mxlit.components.text import _make_heading   # internal factory

title     = _make_heading(ComponentType.TITLE,     "#")
header    = _make_heading(ComponentType.HEADER,    "##")
subheader = _make_heading(ComponentType.SUBHEADER, "###")
```

**Line delta across phases:**

| Phase | Lines for `title` | Lines for all 3 headings |
|-------|-------------------|--------------------------|
| Before | 6 | 18 |
| Phase 1 (`BaseComponent`) | 5 | 15 |
| Phase 2 (`@component`) | 4 | 12 |
| Phase 3 (factory) | 1 | **3** |

**`to_dict()` output** (identical across all phases — template unchanged):

```python
{"type": "title", "class_": "text-xl", "content": "Hello"}
```

---

### 3.2 Complex Widget — `mt.text_input`

`text_input` adds three concerns on top of the display pattern:
1. **State read** — `session_state.get(widget_key, value)` before registration
2. **Return value** — the function must hand `current_value` back to the caller
3. **HTMX triggers** — the rendered `<input>` must fire `/interact` on `change`

**Before** (`src/mxlit/components/widgets.py` lines 26–41):

```python
from mxlit.context import get_context
from mxlit.state import session_state
import hashlib

def _generate_key(label: str, component_type: str) -> str:
    return hashlib.md5(f"{component_type}-{label}".encode()).hexdigest()

def text_input(label: str, value: str = "", key: str = None, class_: str = "") -> str:
    ctx = get_context()
    widget_key    = key or _generate_key(label, "text_input")
    current_value = session_state.get(widget_key, value)
    if ctx:
        ctx.add_component({"type": "text_input", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value
```

**After — Phase 1 (`BaseComponent` + `ComponentType`):**

```python
from mxlit.components.base import BaseComponent, ComponentType, HtmxProps, OatProps
from mxlit.state import session_state

def text_input(label: str, value: str = "", key: str = None, className: str = "") -> str:
    widget_key    = key or BaseComponent.generate_key(ComponentType.TEXT_INPUT, label)
    current_value = session_state.get(widget_key, value)
    BaseComponent(
        type         = ComponentType.TEXT_INPUT,
        className    = className,
        props        = {"label": label, "value": current_value, "key": widget_key},
        _htmx        = HtmxProps(trigger="change"),
        _oat         = OatProps(field=True),
        _fallback_fn = lambda: None,
    )
    return current_value
```

**After — Phase 2 (`@widget_component` decorator):**

```python
from mxlit.components.base import (
    BaseComponent, ComponentType, HtmxProps, OatProps, widget_component,
)
from mxlit.state import session_state

@widget_component(
    ComponentType.TEXT_INPUT,
    htmx = HtmxProps(trigger="change"),
    oat  = OatProps(field=True),
)
def text_input(label: str, value: str = "", key: str = None) -> tuple[dict, str]:
    """Display a single-line text input widget.

    Args:
        label:     Field label shown above the input.
        value:     Default value when no session state exists for this key.
        key:       Optional unique widget key.  Auto-generated from label when omitted.
        className: Tailwind classes applied to the <label> wrapper.
                   (Extracted from kwargs by the @widget_component decorator.)

    Returns:
        The current value from session_state, or *value* if not yet set.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.TEXT_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return (
        {"label": label, "value": current_value, "key": widget_key},
        current_value,
    )
```

**`to_dict()` output** (flat dict, backward-compatible with `components.html`):

```python
{
    "type":       "text_input",   # ComponentType.TEXT_INPUT == "text_input" ✓
    "class_":     "",
    "label":      "Name",
    "value":      "Alice",
    "key":        "a3f9…",
    "hx-post":    "/interact",
    "hx-target":  "#app-root",
    "hx-swap":    "innerHTML settle:0",
    "hx-trigger": "change",
    "data-field":  "",
}
```

**Key observations:**

- `ComponentType.TEXT_INPUT.value == "text_input"` → `generate_key` produces the identical MD5
  as the old `_generate_key(label, "text_input")` — **all existing widget keys are preserved**.
- `hashlib` is no longer imported in `widgets.py` — it moves inside `generate_key` in `base.py`.
- `className` no longer appears in the function signature — the decorator pops it automatically.
  Callers still pass `mt.text_input("Name", className="w-full")` unchanged.
- `_htmx` and `_oat` are declared once at the decorator, not inside the function — shared across
  every call without per-call object creation overhead.

**Trigger customisation — `slider` and `checkbox` with `@widget_component`:**

```python
@widget_component(
    ComponentType.SLIDER,
    htmx = HtmxProps(trigger="change, input delay:500ms"),
    oat  = OatProps(field=True),
)
def slider(label: str, min_value: int = 0, max_value: int = 100,
           value: int = None, key: str = None) -> tuple[dict, int]:
    widget_key    = key or BaseComponent.generate_key(ComponentType.SLIDER, label)
    default_val   = value if value is not None else min_value
    current_value = int(session_state.get(widget_key, default_val))
    return (
        {"label": label, "min_value": min_value, "max_value": max_value,
         "value": current_value, "key": widget_key},
        current_value,
    )


@widget_component(
    ComponentType.CHECKBOX,
    htmx = HtmxProps(trigger="click, change"),
    oat  = OatProps(field=True),
)
def checkbox(label: str, value: bool = False, key: str = None) -> tuple[dict, bool]:
    widget_key    = key or BaseComponent.generate_key(ComponentType.CHECKBOX, label)
    state_val     = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    return (
        {"label": label, "value": current_value, "key": widget_key},
        current_value,
    )
```

The `HtmxProps` trigger is declared at the decorator — `slider` and `checkbox` each deviate from
the default `"change"` once, at definition time, rather than once per call.

---

### 3.3 Status Variants — Atomic Composition in Practice

The four status functions (`error`, `warning`, `success`, `info`) are structurally identical.
Before migration, each required a full function body:

**Before (×4 in `status.py`):**

```python
def error(body: str, class_: str = "") -> None:
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "content": body,
                           "status_type": "error", "class_": class_})
    else:
        print(f"[ERROR] {body}")
```

**After — atomic composition:**

```python
from mxlit.components.base import ComponentType, OatProps, component


def _make_status_variant(status_type: str) -> Callable:
    preset_oat = OatProps(variant=status_type, role="alert")

    @component(ComponentType.STATUS, oat=preset_oat)
    def _fn(body: str) -> tuple[dict, Callable]:
        return (
            {"content": body, "status_type": status_type},
            lambda: print(f"[{status_type.upper()}] {body}"),
        )

    _fn.__name__     = status_type
    _fn.__qualname__ = f"mxlit.components.status.{status_type}"
    return _fn


error   = _make_status_variant("error")    # mt.error("Not found")
warning = _make_status_variant("warning")  # mt.warning("Check input")
success = _make_status_variant("success")  # mt.success("Saved!")
info    = _make_status_variant("info")     # mt.info("Loading…")
```

**Net line count for the 4 status functions:**

| Phase | Lines |
|-------|-------|
| Before | 28 (4 × 7 lines) |
| After (factory) | **8** (4-line factory body + 4 assignment lines) |

**`to_dict()` output for `mt.error("File not found", className="mt-4")`:**

```python
{
    "type":         "status",
    "class_":       "mt-4",
    "content":      "File not found",
    "status_type":  "error",
    "data-variant": "error",
    "role":         "alert",
}
```

The template reads `comp.status_type` exactly as before — **zero template changes** during Phase 1.

---

## 4. Template Update Strategy

### 4.1 Current State

The `render_component` macro in `components.html` hardcodes the four HTMX attributes directly
inside every interactive widget block. The same four lines appear **10 times** across lines
138–274:

```html
hx-post="/interact"
hx-target="#app-root"
hx-swap="innerHTML settle:0"
hx-trigger="change"
```

Each widget type also has a hard-coded trigger variant (`"click, change"` for checkbox,
`"change, input delay:500ms"` for slider), embedded invisibly inside the repetition.

### 4.2 Phase 1 — Additive: `htmx_attrs` Jinja2 Macro

Add a single macro at the top of the `render_component` section that reads from the component
dict when the `hx-*` keys are present, and falls back to safe defaults when they are not.
This keeps old component dicts (rendered before migration) working alongside new ones.

```jinja2
{# components.html — add immediately before the render_component macro definition #}

{# ── HTMX attribute helper ─────────────────────────────────────────────────── #}
{# Reads hx-* keys written by BaseComponent.to_dict().                          #}
{# Falls back to the standard /interact pattern when keys are absent            #}
{# (backward compat: component dicts created before the BaseComponent migration #}
{#  do not carry these keys).                                                    #}
{% macro htmx_attrs(comp) %}
    hx-post="{{ comp['hx-post'] | default('/interact') }}"
    hx-target="{{ comp['hx-target'] | default('#app-root') }}"
    hx-swap="{{ comp['hx-swap'] | default('innerHTML settle:0') }}"
    hx-trigger="{{ comp['hx-trigger'] | default('change') }}"
{% endmacro %}
```

Each widget block then replaces its four hardcoded lines with a single macro call:

```jinja2
{# Before (text_input, components.html lines 134–141) #}
<input type="text"
       id="{{ comp.key }}"
       name="{{ comp.key }}"
       value="{{ comp.value }}"
       hx-post="/interact"
       hx-target="#app-root"
       hx-swap="innerHTML settle:0"
       hx-trigger="change">

{# After — Phase 1 #}
<input type="text"
       id="{{ comp.key }}"
       name="{{ comp.key }}"
       value="{{ comp.value }}"
       {{ htmx_attrs(comp) }}>
```

Apply the same substitution to all 10 interactive widget blocks:
`text_input`, `text_area`, `number_input`, `date_input`, `color_picker`,
`checkbox`, `toggle`, `slider`, `radio`, `selectbox`.

**Backward compatibility:** Old dicts without `hx-*` keys render identically to today because
`default('/interact')` etc. reproduce the previously hardcoded values exactly.

### 4.3 Phase 2 — Cleanup (Post Full Migration)

Once every widget function has been migrated to `BaseComponent`, the `default()` fallbacks
in `htmx_attrs` become dead code. Remove them and lock the macro to require the keys:

```jinja2
{% macro htmx_attrs(comp) %}
    hx-post="{{ comp['hx-post'] }}"
    hx-target="{{ comp['hx-target'] }}"
    hx-swap="{{ comp['hx-swap'] }}"
    hx-trigger="{{ comp['hx-trigger'] }}"
{% endmacro %}
```

This makes it immediately obvious in a template error if a new interactive component forgets
to set `_htmx` — rather than silently falling back to `"change"` and producing hard-to-debug
interaction behavior.

### 4.4 OAT Data Attribute Strategy — Phase 2

In Phase 2 (post-migration), OAT attributes that the template currently hard-codes per component
branch (`data-variant`, `role`, `data-field`) move into `OatProps` on the Python side. The
template then reads them generically from the component dict, collapsing multiple if-branches
into direct attribute pass-through.

**Phase 2 status component rewrite:**

```jinja2
{# Before: 4 separate branches for each status_type #}
{% elif comp.type == 'status' %}
    {% if comp.status_type == 'error' %}
        <div role="alert" data-variant="error" class="{{ comp.class_ | default('') }}">…</div>
    {% elif comp.status_type == 'warning' %}
        <div role="alert" data-variant="warning" class="{{ comp.class_ | default('') }}">…</div>
    …
    {% endif %}

{# After: single branch reads OatProps output from the dict #}
{% elif comp.type == 'status' %}
    <div {{ comp.role | render_attr('role') }}
         {{ comp['data-variant'] | render_attr('data-variant') }}
         class="{{ comp.class_ | default('') }}">{{ comp.content }}</div>
```

This is **explicitly Phase 2** — Phase 1 retains existing template branch logic untouched.
The `render_attr` helper macro (`{% macro render_attr(val, name) %}{{ name }}="{{ val }}"{% if val %}{% endmacro %}`)
can be defined alongside `htmx_attrs`.

---

## 5. OAT Component Catalog

Source: [oat.ink/components](https://oat.ink/components/)

### 5.1 Existing mxlit Components → OAT Mapping

| mxlit function | OAT element / attributes | Notes |
|----------------|--------------------------|-------|
| `mt.title/header/subheader` | `<h1>` / `<h2>` / `<h3>` — styled automatically | No class needed |
| `mt.write` / `mt.text` | `<p>` — styled automatically | |
| `mt.code` | `<pre><code>` — styled automatically | |
| `mt.badge` | `<span class="badge">` + `data-variant` | Supports `outline` class modifier |
| `mt.error/warning/info/success` | `<div role="alert">` + `data-variant="error\|warning\|success"` | OatProps carries this |
| `mt.button` | `<button>` + `data-variant="secondary"` | Supports `outline`, `ghost`, `small`, `large` |
| `mt.checkbox` | `<input type="checkbox">` in `<label data-field>` | |
| `mt.toggle` | `<input type="checkbox" role="switch">` | OAT switch component |
| `mt.slider` | `<input type="range">` in `<label data-field>` | |
| `mt.selectbox` | `<select>` in `<div data-field>` | |
| `mt.text_input/text_area/number_input/date_input/color_picker` | `<input>` in `<label data-field>` | OatProps(field=True) |
| `mt.expander` | `<details><summary>` — styled automatically | OAT accordion |
| `mt.tabs` | `<ot-tabs>` WebComponent | Already uses `role="tablist/tab/tabpanel"` |
| `mt.sidebar` | `<aside data-sidebar>` in `[data-sidebar-layout]` | |
| `mt.dataframe/table` | `<div class="table"><table>` | Responsive scroll wrapper |

### 5.2 New Components Enabled by OAT

These can all be implemented as `BaseComponent` (leaves) or `CompositeComponent` (containers):

#### 5.2.1 New UI Primitives (not yet in mxlit at all)

| New function | OAT pattern | Type | Key attributes |
|--------------|-------------|------|----------------|
| `mt.card(header, footer)` | `<article class="card">` | Composite | `<header>`, `<footer>` slots |
| `mt.avatar(src, initials, size)` | `<figure data-variant="avatar">` | Leaf | `class="small\|large"`, `aria-label` |
| `mt.avatar_group(size)` | `<figure data-variant="avatar" role="group">` | Composite | size controls all nested avatars |
| `mt.dialog(dialog_id, title)` | `<dialog closedby="any">` + `commandfor/command` trigger | Composite | zero-JS focus trapping + Escape key |
| `mt.dropdown(label)` | `<ot-dropdown>` WebComponent | Composite | `popovertarget` / `popover` |
| `mt.spinner(size)` | `<div aria-busy="true">` | Leaf | `data-spinner="small\|large\|overlay"` |
| `mt.skeleton(variant)` | `<div role="status" class="skeleton line\|box">` | Leaf | `role="status"` |
| `mt.progress(value, max)` | `<progress value max>` | Leaf | Native `<progress>`; indeterminate when `value` omitted |
| `mt.meter(value, min, max, low, high, optimum)` | `<meter>` | Leaf | Browser semantic colors via `low/high/optimum` |
| `mt.breadcrumb(items)` | `<nav aria-label="Breadcrumb"><ol class="unstyled hstack">` | Leaf | `aria-current="page"` on last item |
| `mt.button_group(labels, on_click)` | `<menu class="buttons">` | Composite | Connected / segmented button styling |
| `mt.grid(cols)` | `<div class="container"><div class="row">` | Composite | `.col-{1-12}`, `.offset-{n}`, `.col-end` |
| `mt.toast(message, title, variant, placement, duration)` | `ot.toast()` JS call emitted via SSE | Leaf | variant: success\|danger\|warning; placement: top-right\|… |
| `mt.pagination(total_pages, current_page)` | `<nav aria-label="Pagination"><menu class="buttons">` | Widget | `aria-current="page"` on active item; returns new page number |

#### 5.2.2 Missing Form Input Variants

oat.ink supports these `<input>` types that mxlit does not yet expose as dedicated Python functions:

| New function | OAT pattern | Type | Notes |
|--------------|-------------|------|-------|
| `mt.email_input(label, value, key)` | `<input type="email">` in `<label data-field>` | Widget | Browser-native email validation |
| `mt.password_input(label, key)` | `<input type="password">` in `<label data-field>` | Widget | Value never stored in session state |
| `mt.file_input(label, accept, key)` | `<input type="file">` in `<label data-field>` | Widget | Returns uploaded filename; multipart encoding needed |
| `mt.datetime_input(label, value, key)` | `<input type="datetime-local">` in `<label data-field>` | Widget | Returns ISO datetime string |
| `mt.input_group(prefix, suffix)` | `<fieldset class="group">` with input + button/select | Composite | Combines input with prefix label or action button |

### 5.3 OAT Attribute Quick Reference

Drawn directly from the oat.ink spec for use in `OatProps`:

| Python field | HTML attribute | Values | Used by |
|-------------|----------------|--------|---------|
| `variant` | `data-variant` | `"success"` `"warning"` `"error"` `"danger"` `"secondary"` | alert, badge, button, avatar |
| `role` | `role` | `"alert"` `"switch"` `"status"` `"tablist"` `"tab"` `"tabpanel"` `"group"` `"menuitem"` | status, toggle, tabs, avatar group |
| `field` | `data-field` | `True` → `""`, `"error"` → `"error"` | all form field wrappers |
| `busy` | `aria-busy` | `"true"` | spinner, loading overlay |
| `spinner` | `data-spinner` | `"small"` `"large"` `"overlay"` | spinner, card loading |
| `tooltip` | `title` | any string | any element — OAT renders as smooth tooltip |
| `tooltip_placement` | `data-tooltip-placement` | `"top"` `"bottom"` `"left"` `"right"` | any element with a `title` attribute |

---

### 5.4 Gap Analysis — Missing Components (oat.ink parity)

Audited against [oat.ink/components](https://oat.ink/components/) on 2026-05-28.

#### Currently implemented ✅ (18 oat.ink sections covered)

| oat.ink section | mxlit function(s) |
|-----------------|-------------------|
| Typography | `write`, `title`, `header`, `subheader`, `text`, `markdown`, `code`, `html`, `latex`, `ner_text`, `badge`, `write_stream` |
| Accordion | `expander` |
| Alert | `error`, `warning`, `info`, `success` |
| Badge | `badge` |
| Button | `button` |
| Form elements (core) | `text_input`, `number_input`, `text_area`, `date_input`, `color_picker`, `checkbox`, `radio`, `slider`, `selectbox`, `toggle` |
| Sidebar | `sidebar` |
| Switch | `toggle` |
| Table | `dataframe`, `table` |
| Tabs | `tabs` |
| Media | `image`, `audio`, `video`, `logo` |
| Charts (custom) | `line_chart`, `bar_chart`, `area_chart`, `scatter_chart` |
| Data display (custom) | `dataframe`, `table`, `json`, `metric` |
| Layout containers | `container`, `columns` |

#### Missing — New UI Primitives ❌ (14 items)

| # | Function | Priority | Complexity |
|---|----------|----------|------------|
| 1 | `mt.card(header, footer)` | 🔴 High | Medium — CompositeComponent |
| 2 | `mt.spinner(size)` | 🔴 High | Low — single div + aria-busy |
| 3 | `mt.progress(value, max)` | 🔴 High | Low — native `<progress>` |
| 4 | `mt.skeleton(variant)` | 🟡 Medium | Low — CSS class on div |
| 5 | `mt.avatar(src, initials, size)` | 🟡 Medium | Low — figure element |
| 6 | `mt.avatar_group(size)` | 🟡 Medium | Medium — CompositeComponent |
| 7 | `mt.meter(value, min, max, low, high, optimum)` | 🟡 Medium | Low — native `<meter>` |
| 8 | `mt.breadcrumb(items)` | 🟡 Medium | Low — nav + ordered list |
| 9 | `mt.button_group(labels, on_click)` | 🟡 Medium | Medium — menu + HTMX |
| 10 | `mt.toast(message, title, variant, placement, duration)` | 🟡 Medium | Medium — SSE → `ot.toast()` JS call |
| 11 | `mt.pagination(total_pages, current_page)` | 🟡 Medium | Medium — widget + HTMX |
| 12 | `mt.dialog(dialog_id, title)` | 🟠 Low | High — CompositeComponent + JS interop |
| 13 | `mt.dropdown(label)` | 🟠 Low | High — `<ot-dropdown>` WebComponent |
| 14 | `mt.grid(cols)` | 🟠 Low | Medium — CompositeComponent, 12-col system |

#### Missing — Form Input Variants ❌ (5 items)

| # | Function | Priority | Notes |
|---|----------|----------|-------|
| 15 | `mt.email_input(label, value, key)` | 🔴 High | `type="email"` — browser validation built-in |
| 16 | `mt.password_input(label, key)` | 🔴 High | `type="password"` — value never stored in session |
| 17 | `mt.datetime_input(label, value, key)` | 🟡 Medium | `type="datetime-local"` — returns ISO string |
| 18 | `mt.file_input(label, accept, key)` | 🟡 Medium | `type="file"` — needs multipart form encoding |
| 19 | `mt.input_group(prefix, suffix)` | 🟠 Low | `<fieldset class="group">` — combines input + button |

#### Summary counts

| Category | Total in oat.ink | Implemented | **Missing** |
|----------|-----------------|-------------|-------------|
| Core UI primitives | 22 sections | 14 | **8** |
| New UI primitives (§5.2.1) | 14 | 0 | **14** |
| Form input variants (§5.2.2) | 5 | 0 | **5** |
| **Total** | **41** | **14** | **27** |

> **Recommended implementation order:** High-priority items first (card, spinner, progress,
> email_input, password_input), then medium-priority (skeleton, avatar, meter, breadcrumb,
> button_group, toast, pagination, datetime_input, file_input), then low-priority (dialog,
> dropdown, grid, input_group). Each high-priority item is a leaf component that can be
> delivered in a single PR with no dependency on `CompositeComponent`.

---

## 6. Composite Design Pattern

### 6.1 Problem with Current `ContainerContextManager`

`layout.py` implements nesting via `ContainerContextManager` — a separate class that manages
`ctx.current_target` switching in `__enter__` / `__exit__`. Every new container component (card,
dialog, dropdown) must duplicate this class or subclass it. `BaseComponent` has no awareness of
children, so leaf and container components share no implementation.

The Composite pattern solves this by giving every `BaseComponent` the *option* to hold children,
making the class simultaneously a Leaf (registers immediately) and a Composite (defers
registration until `__exit__` collects children).

### 6.2 `CompositeComponent` — Extended Definition

```python
# src/mxlit/components/base.py (addition)

@dataclass
class CompositeComponent(BaseComponent):
    """A BaseComponent that can nest children via a `with` block.

    Lifecycle difference from BaseComponent
    ----------------------------------------
    BaseComponent:   __post_init__ → _register() immediately.
    CompositeComponent: __post_init__ skips registration.  Registration is
                        deferred until __exit__, after the `with` block has
                        finished and all children have added themselves to
                        self._children via the redirected ctx.current_target.

    Usage
    -----
        with mt.card("Revenue") as card:
            mt.metric("MRR", "$12,400")
            mt.metric("Churn", "2.1%")

    Tree structure in ctx.components after __exit__:
        {"type": "card", "class_": "", "props": {"header": "Revenue"},
         "children": [
             {"type": "metric", "label": "MRR",   "value": "$12,400", …},
             {"type": "metric", "label": "Churn",  "value": "2.1%",   …},
         ]}
    """
    # Private mutable state — not dataclass init fields
    _children:    list     = field(default_factory=list, repr=False, init=False)
    _saved_target: list | None = field(default=None,      repr=False, init=False)
    _active_ctx:  object | None = field(default=None,     repr=False, init=False)

    def __post_init__(self) -> None:
        # Deliberately skip BaseComponent.__post_init__ — do NOT register yet.
        pass

    def __enter__(self) -> "CompositeComponent":
        from mxlit.context import get_context
        ctx = get_context()
        if ctx:
            self._active_ctx  = ctx
            self._saved_target = ctx.current_target
            ctx.current_target = self._children   # redirect child registrations here
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._active_ctx:
            # Restore parent render target before registering self
            self._active_ctx.current_target = self._saved_target
            self._active_ctx = None
        # Now register self — children list is fully populated
        self._register()
        return False   # never suppress exceptions

    def to_dict(self) -> dict[str, Any]:
        """Extends BaseComponent.to_dict() to include the children list."""
        d = super().to_dict()
        d["children"] = list(self._children)   # shallow copy of already-serialized dicts
        return d
```

### 6.3 Template Support for Composite Children

The `render_component` macro already handles children recursively for `container`, `expander`,
`column`, and `tab` types. Any new composite component type simply needs a branch that iterates
`comp.children`:

```jinja2
{# components.html — generic composite rendering (works for card, dialog, dropdown …) #}
{% elif comp.type == 'card' %}
    <article class="card {{ comp.class_ | default('') }}">
        {% if comp.props.header %}
            <header><h3>{{ comp.props.header }}</h3></header>
        {% endif %}
        {% for child in comp.children %}
            {{ render_component(child) }}
        {% endfor %}
        {% if comp.props.footer %}
            <footer>{{ comp.props.footer }}</footer>
        {% endif %}
    </article>
```

No Python changes are needed in the template loop — `comp.children` is a plain list of dicts,
the same format that `container` and `expander` already use.

### 6.4 Worked Example — `mt.card`

**Python implementation (`src/mxlit/components/layout.py`):**

```python
from mxlit.components.base import CompositeComponent, OatProps

def card(header: str = "", footer: str = "", className: str = "") -> CompositeComponent:
    """Create a card container using OAT's <article class="card"> pattern.

    Args:
        header:    Optional heading text rendered in <header>.
        footer:    Optional text rendered in <footer>.
        className: Tailwind classes applied to the <article> element.

    Usage::

        with mt.card("Sales Summary"):
            mt.metric("Revenue", "$42k", delta="+8%")
            mt.metric("Orders", 318)
    """
    return CompositeComponent(
        type      = "card",
        className = className,
        props     = {"header": header, "footer": footer},
    )
```

**User script:**

```python
import mxlit as mt

with mt.card("Monthly Metrics", className="max-w-xl"):
    mt.metric("Revenue", "$42,000", delta="+8%")
    mt.metric("Churn",   "2.1%",   delta="-0.3%")
    with mt.container(horizontal=True):
        mt.button("Export CSV")
        mt.button("View Details")
```

**`ctx.components` after rendering:**

```python
[{
    "type":      "card",
    "class_":    "max-w-xl",
    "header":    "Monthly Metrics",
    "footer":    "",
    "children":  [
        {"type": "metric", "label": "Revenue", "value": "$42,000", "delta": "+8%", …},
        {"type": "metric", "label": "Churn",   "value": "2.1%",   "delta": "-0.3%", …},
        {"type": "container", "horizontal": True, "children": [
            {"type": "button", "label": "Export CSV", …},
            {"type": "button", "label": "View Details", …},
        ]},
    ]
}]
```

Arbitrary nesting depth is supported because `render_component` in the template calls itself
recursively for every `comp.children` list.

### 6.5 Migrating Existing Layout Containers

The existing `ContainerContextManager` in `layout.py` can be gradually replaced by
`CompositeComponent` subclasses. No user-facing change is required — the container functions
(`mt.expander`, `mt.container`, `mt.columns`) continue to return context managers; only the
implementation changes.

| Current | After migration | Effort |
|---------|----------------|--------|
| `ContainerContextManager("container", …)` | `CompositeComponent(type="container", …)` | Swap constructor |
| `ContainerContextManager("expander", …)` | `CompositeComponent(type="expander", …)` | Swap constructor |
| `Sidebar` (custom class with override) | `CompositeComponent(type="sidebar", …)` | Simplify class |
| `columns()` list of `ContainerContextManager` | list of `CompositeComponent` | Swap constructor |

`ContainerContextManager` can be retained as a thin alias during transition:

```python
# layout.py — transition shim
def ContainerContextManager(container_type, **kwargs):
    return CompositeComponent(type=container_type, props=kwargs)
```

---

## 7. Migration Checklist

Tasks are sequenced to match the Priority 1–2 items from `docs/DRY_VIOLATION.md`. Priority 1
tasks (§7.0) are independent of the component architecture work and can be executed in any order
relative to it; Priority 2 tasks (§7.1–§7.7) can be executed file-by-file once `base.py` exists.

### 7.0 Priority 1 — Prerequisite Server-Side Refactors (`DRY_VIOLATION.md`)

These tasks eliminate DRY violations in `server.py`, `cli.py`, and the package structure. They
carry zero behavioral risk and unblock `ThemeManager` (Task 3.1) which depends on Task 1.1.

- [ ] **Task 1.2** — Create `src/mxlit/_exceptions.py`; move `RerunException` to module level
      as a `BaseException` subclass; replace `type(e).__name__ == "RerunException"` string checks
      in `server.py` with a proper `except RerunException:` clause (30 min)
- [ ] **Task 1.1** — Extract `_run_script()` (the 12-line `runpy` + `AppContext` + error-handling
      block, duplicated between `/interact` and `/modify`) and `_coerce_form_value()` /
      `_apply_form_data()` (the 22-line form type-coercion block, also duplicated) as named helpers
      in `server.py` (1 h, depends on Task 1.2)
- [ ] **Task 1.4** — Create `src/mxlit/_paths.py` with `PACKAGE_DIR`, `STATIC_DIR`,
      `TEMPLATES_DIR`, `INPUT_CSS`, `OUTPUT_CSS`; update `cli.py` and `server.py` to import from
      it instead of recomputing `Path(__file__).parent / "static"` independently (20 min)
- [x] ~~**Task 1.3**~~ — ✓ Completed: `setup.py` deleted; `pytailwindcss` declared as dev extra in
      `pyproject.toml`

### 7.1 Create `src/mxlit/components/base.py`

- [ ] Implement `ComponentType(str, Enum)` with all 50+ type identifiers (§2.3.1)
- [ ] Implement type aliases: `SwapStrategy`, `TriggerSpec`, `ParamsSpec`, `EncodingType` (§2.2.1)
- [ ] Implement `HtmxProps` dataclass with all 33 HTMX fields + `to_attrs()` (§2.2.2)
- [ ] Implement `OatProps` dataclass with `variant`, `role`, `field`, `busy`, `spinner`, `tooltip`
- [ ] Implement `BaseComponent` dataclass with `type: ComponentType`, `className`, `props`,
      `_htmx`, `_oat`, `_fallback_fn`
- [ ] Implement `__post_init__` → `_register()` lifecycle
- [ ] Implement `to_dict()`: merges `{"type", "class_"}` + `props` + `_htmx` + `_oat`
- [ ] Implement `generate_key(ComponentType | str, discriminator)` static method
- [ ] Implement `CompositeComponent(BaseComponent)` with `__enter__` / `__exit__` / `to_dict()`
- [ ] Implement `@component(component_type, *, htmx, oat)` decorator (§2.6.2)
- [ ] Implement `@widget_component(component_type, *, htmx, oat)` decorator (§2.6.3)
- [ ] Verify local import of `get_context` inside `_register` avoids circular imports

### 7.2 Template — Phase 1 (do this before any Python changes)

- [ ] Add `htmx_attrs(comp)` macro to `components.html` above `render_component`
- [ ] Replace hardcoded `hx-post/target/swap/trigger` in all 10 widget blocks with
      `{{ htmx_attrs(comp) }}`
- [ ] Add new composite branches for `card`, `spinner`, `skeleton`, `progress`, `meter`
- [ ] Run all sample apps in `samples/` and confirm no visual or behavioral regression
- [ ] Confirm `checkbox` block's `"click, change"` and `slider`'s `"change, input delay:500ms"`
      are preserved as `default()` values in the macro

### 7.3 Migrate Display-Only Components (no return value)

Recommended order: `status.py` → `media.py` → `data.py` → `text.py` → `charts.py`

**Phase 1 — `BaseComponent` + `ComponentType` (prerequisite for Phase 2):**

- [ ] Replace `from mxlit.context import get_context` with
      `from mxlit.components.base import BaseComponent, ComponentType, OatProps`
- [ ] Replace every manual boilerplate block with `BaseComponent(type=ComponentType.X, ...)`
- [ ] Assign `_oat=OatProps(...)` where the component has a fixed OAT role

**Phase 2 — `@component` decorator (apply after Phase 1 is verified):**

- [ ] Add `component` to the import from `base`
- [ ] Decorate each function with `@component(ComponentType.X, oat=...)` and strip the function
      body down to `return (props_dict, fallback_fn)`
- [ ] Apply `_make_status_variant` factory to collapse `error/warning/success/info` → 4 lines
- [ ] Apply `_make_heading` factory to collapse `title/header/subheader` → 3 lines
- [ ] Apply `_make_chart` factory to collapse the 4 chart functions → 4 lines
- [ ] Remove `import hashlib` from `charts.py` after `_generate_key` calls are replaced

### 7.4 Migrate Widget Components (return value preserved)

Files: `widgets.py`, `data.py::metric`, `text.py::write_stream`

**Phase 1 — `BaseComponent` + `ComponentType`:**

- [ ] Replace `_generate_key(label, type)` with `BaseComponent.generate_key(ComponentType.X, label)`
- [ ] Replace `if ctx: ctx.add_component({...})` with `BaseComponent(..., _htmx=HtmxProps(...))`
- [ ] Assign triggers: `checkbox → "click, change"`, `slider → "change, input delay:500ms"`,
      all others → `HtmxProps()` default
- [ ] Assign `_oat=OatProps(field=True)` to all form field widgets
- [ ] Remove standalone `_generate_key` functions and `import hashlib`

**Phase 2 — `@widget_component` decorator:**

- [ ] Add `widget_component` to the import from `base`
- [ ] Decorate each function with `@widget_component(ComponentType.X, htmx=..., oat=...)`
- [ ] Strip the function body to session-state read + `return (props_dict, return_value)`
- [ ] Move `HtmxProps(trigger=...)` and `OatProps(field=True)` to the decorator arguments
      (one declaration per function, not one per call)
- [ ] Confirm the function no longer contains `className` in its signature

### 7.5 Migrate Layout Containers to `CompositeComponent`

- [ ] Implement `mt.card(header, footer, className)` using `CompositeComponent`
- [ ] Add `card` rendering branch to `components.html`
- [ ] Replace `ContainerContextManager("container", …)` with `CompositeComponent` in `layout.py`
- [ ] Replace `ContainerContextManager("expander", …)` with `CompositeComponent` in `layout.py`
- [ ] Add transition shim `ContainerContextManager = CompositeComponent` if any external code references it
- [ ] Add new OAT-backed components: `mt.spinner`, `mt.skeleton`, `mt.progress`, `mt.meter`

### 7.6 Template — Phase 2 (after all widgets migrated)

- [ ] Remove `default(...)` fallbacks from `htmx_attrs` macro
- [ ] Add `render_attr` macro; update `status` branch to read `data-variant` / `role` from dict
      (replaces the `{% if comp.status_type == 'error' %}` branching chain — see §4.4)

### 7.7 Final Cleanup

- [ ] Remove `from mxlit.context import get_context` from all component files
      (only `layout.py` retains this import during the `ContainerContextManager` transition)
- [ ] Confirm no remaining `import hashlib` in component files

---

## 8. Compatibility Notes

| Surface | Before | After | Breaking? |
|---------|--------|-------|-----------|
| `mt.title("x", class_="y")` | positional param | **removed** | **Yes** — use `className=` |
| `mt.title("x", className="y")` | not accepted | primary param | No (additive) |
| `ctx.components` items | flat dicts | flat dicts, same keys | **No** |
| `comp.class_` in Jinja2 template | string | string (from `to_dict`) | **No** |
| `comp.content` / `comp.label` in template | string | string | **No** |
| `hx-post` in rendered HTML | hardcoded in template | from dict via `htmx_attrs` macro | **No** |
| Widget keys (MD5 hashes) | `md5("{type}-{label}")` | `md5("{type}-{discriminator}")` | **No** — hash string identical |
| `BaseComponent` / `CompositeComponent` imports | do not exist | new public classes | No (additive) |
| `ContainerContextManager` in `layout.py` | concrete class | shim alias → `CompositeComponent` | **No** |

`class_` is a **hard removal** — no alias, no deprecation period. Scripts using `class_=` must
be updated to `className=`. Since mxlit is pre-1.0, this is within the normal semver contract.

---

## 9. File Change Summary

### 9.1 Per-file Breakdown

**Priority 1 — Server-side prereqs (DRY_VIOLATION.md Tasks 1.1, 1.2, 1.4)**

| File | Action | Δ | DRY Task |
|------|--------|---|----------|
| `src/mxlit/_exceptions.py` | **CREATE** | +10 | 1.2 — `RerunException` at module level |
| `src/mxlit/_paths.py` | **CREATE** | +10 | 1.4 — shared `STATIC_DIR`, `TEMPLATES_DIR`, CSS paths |
| `src/mxlit/server.py` | UPDATE | −20 | 1.1 — `_run_script` + `_coerce_form_value`; 1.2 — catch by type |
| `src/mxlit/cli.py` | UPDATE | −5 | 1.4 — import paths from `_paths.py` |

**Priority 2 — Component architecture (this plan)**

| File | Action | Phase 1 Δ | Phase 2 Δ | Notes |
|------|--------|-----------|-----------|-------|
| `src/mxlit/components/base.py` | **CREATE** | +280 | — | `ComponentType` enum (+80), `HtmxProps` full (+60), `OatProps` (+25), `BaseComponent` (+35), `CompositeComponent` (+40), `@component` (+20), `@widget_component` (+20) |
| `src/mxlit/components/layout.py` | UPDATE | +15 | — | `card`, shims for existing containers |
| `src/mxlit/components/text.py` | UPDATE | −45 | −15 | Phase 2: `_make_heading` factory collapses 3 heading fns to 3 lines |
| `src/mxlit/components/data.py` | UPDATE | −18 | −4 | |
| `src/mxlit/components/widgets.py` | UPDATE | −45 | −20 | Phase 2: `className` removed from 11 signatures; `HtmxProps` moved to decorators |
| `src/mxlit/components/charts.py` | UPDATE | −18 | −12 | Phase 2: `_make_chart` factory collapses 4 chart fns to 4 lines |
| `src/mxlit/components/media.py` | UPDATE | −15 | −5 | |
| `src/mxlit/components/status.py` | UPDATE | −20 | −22 | Phase 2: `_make_status_variant` collapses 4 status fns to 4 lines |
| `src/mxlit/templates/components.html` | UPDATE | −10 | +30 | Phase 1: HTMX macro; Phase 2: OAT component branches |
| **Total (P2)** | | **≈ +140 net** | **≈ −78 additional** | Phase 1 adds the new module; Phase 2 nets down |

### 9.2 Boilerplate Elimination Summary

| Boilerplate type | Before | After Phase 1 | After Phase 2 |
|-----------------|--------|---------------|---------------|
| `ctx = get_context()` occurrences | 43 | 0 | 0 |
| `if ctx: ctx.add_component(...)` blocks | 43 | 0 | 0 |
| `else: print(...)` fallback lines | ~40 | 0 (in `_fallback_fn`) | 0 (in decorator return tuple) |
| `import hashlib` in component files | 2 | 0 | 0 |
| `_generate_key` private functions | 2 | 0 | 0 |
| Bare string type literals (`"title"`, etc.) | 43+ | 0 (`ComponentType` enum) | 0 |
| `className` in function signatures | 43 | 43 (Phase 1 keeps it) | **0** (decorator pops it) |
| Manual `HtmxProps(trigger=...)` per call | — | 43 calls | **11** (one per function at decoration) |

Phase 1 eliminates the registration boilerplate (43 instances). Phase 2 eliminates the remaining
structural repetition: `className` disappears from signatures, and `HtmxProps`/`OatProps`
construction moves from per-call to per-function-definition.

The net result is that adding a new mxlit component in Phase 2 requires:
1. One `ComponentType` enum entry
2. One `@component` or `@widget_component` decorated call
3. A function body containing only the domain logic (state reads, data transforms)

Zero registration code. Zero boilerplate.

---

## 10. Full-Page Refresh Bug — Diagnosis & Targeted-Update Plan

> **Observed symptom:** Every interaction with any widget in a mxlit app (button click, color
> picker change, text input change, slider move) causes the entire visible UI — sidebar and all
> main content — to flash and re-render. It is visually indistinguishable from a native browser
> page reload.
>
> **Investigated files:** `src/mxlit/server.py`, `src/mxlit/templates/base.html`,
> `src/mxlit/templates/components.html`, `samples/class_styling_demo.py`.

---

### 10.1 Root-Cause Breakdown (5 compounding problems)

#### Problem 1 — `<button type="submit">` carries no HTMX attributes (`components.html`)

```html
<button type="submit"
        data-variant="secondary"
        name="{{ comp.key }}"
        value="true">{{ comp.label }}</button>
```

The button has **no `hx-post`, `hx-target`, `hx-trigger`, or `hx-include`**. Clicking it fires
the browser's native `submit` event, which bubbles up to the outer `<form>` in `base.html`.
HTMX intercepts the form-level submit — not a targeted widget-level request — so the response
replaces `#app-root` in its entirety.

#### Problem 2 — Duplicate HTMX triggers on `<form>` and `#app-root` both targeting `#app-root` (`base.html`)

```html
<form hx-post="/interact"
      hx-target="#app-root"
      hx-swap="innerHTML settle:0">

    <div id="app-root"
         hx-trigger="load"
         hx-post="/interact"
         hx-target="#app-root"
         hx-swap="innerHTML settle:0"
         ...>
```

Two overlapping HTMX event sources — the `<form>` (fires on button submit) and `#app-root`
(fires on `load`) — both target `#app-root` with `innerHTML` swap. Every button click therefore
causes the **full innerHTML of `#app-root` to be replaced**, which contains the entire sidebar
and main content — 100 % of the visible UI.

#### Problem 3 — Every individual widget targets `#app-root` with `innerHTML` swap (`components.html`)

```html
<input type="text"
       hx-post="/interact"
       hx-target="#app-root"
       hx-swap="innerHTML settle:0"
       hx-trigger="change">
```

All interactive widgets (`text_input`, `color_picker`, `slider`, `select`, `toggle`, `checkbox`,
`radio`, `number_input`, `date_input`) individually POST to `/interact` and replace the entire
`#app-root` innerHTML. A single color picker change in the sidebar re-renders the sidebar itself,
all main content sections, all charts, all tables — everything.

#### Problem 4 — `server.py /interact` re-runs the full script and returns the complete component tree

```python
runpy.run_path(script_path, run_name="__main__")   # full script, every time
return templates.TemplateResponse(
    "components.html",
    {"components": ctx.components, ...}             # all components always returned
)
```

The `/interact` endpoint has no concept of partial rendering. It always re-executes the entire
user script and returns every component in one response. There is no mechanism to identify which
component changed or to return only the affected subtree.

#### Problem 5 — `hx-swap="innerHTML settle:0"` (zero settle time) makes every swap look like a hard reload

`settle:0` tells HTMX to skip the settle phase — the brief window where old and new DOM nodes
coexist and CSS transitions can animate between states. With a zero settle delay the old content
disappears and the new content appears instantaneously with no visual transition, making the full
replacement indistinguishable from a native browser page reload.

---

### 10.2 Summary Table

| # | File | What | Effect |
|---|------|------|--------|
| 1 | `components.html` | `<button type="submit">` with no HTMX attrs | Triggers parent form submit → full `#app-root` replacement |
| 2 | `base.html` | `<form>` + `#app-root` both have `hx-post` → `#app-root` | Two overlapping triggers; button click fires form-level full swap |
| 3 | `components.html` | All widget inputs target `#app-root` with `innerHTML` | Any single widget change replaces 100 % of the visible UI |
| 4 | `server.py` | `/interact` always runs full script, returns full tree | Server always produces a complete page worth of HTML per request |
| 5 | `base.html` | `hx-swap="innerHTML settle:0"` (zero settle time) | No transition animation → full replacement looks like a hard reload |

---

### 10.3 Target Architecture — Targeted Per-Component Updates

The goal is that interacting with a widget sends a POST to `/interact`, the server re-runs the
script, and only the **single component whose state changed** is swapped in the DOM. All other
components remain untouched.

#### 10.3.1 Component ID Strategy

Every rendered component needs a stable, deterministic DOM `id` so HTMX can target it precisely.
The existing `widget_key` (MD5 of `"{type}-{label}"`) is already stable across re-runs and can
serve as the component id:

```html
<!-- rendered component wrapper -->
<div id="mx-{{ comp.id }}" class="mx-component">
    ...widget HTML...
</div>
```

`comp.id` is always non-empty: for widgets it is the user-supplied id or the MD5 key; for
display components it is the user-supplied id or the auto-assigned type+index string — both
resolved by the decorator before the component dict reaches the template.  No conditional
logic is needed in Jinja2.

#### 10.3.2 Widget HTMX Changes (`components.html`)

Each widget stops targeting `#app-root` and instead targets its own wrapper `id` using
`hx-swap="outerHTML"`:

```html
<!-- text_input — targeted self-swap -->
<div id="mx-{{ comp.id }}" class="mx-component">
    <label data-field for="{{ comp.key }}">
        {{ comp.label }}
        <input type="text"
               id="{{ comp.key }}"
               name="{{ comp.key }}"
               value="{{ comp.value }}"
               hx-post="/interact"
               hx-target="#mx-{{ comp.id }}"
               hx-swap="outerHTML settle:100ms"
               hx-trigger="change"
               hx-include="[name]">
    </label>
</div>
```

Note: `comp.id` is used for the **wrapper div** and **hx-target** (the resolved, human-readable
or auto-assigned id); `comp.key` is still used for `<input name>` and `<label for>` since form
field names must remain the stable MD5 key so session state lookups on the server are unaffected.

Key changes per widget:
- `hx-target` → `#mx-{key}` (own wrapper, not `#app-root`)
- `hx-swap` → `outerHTML settle:100ms` (replaces the wrapper div; settle gives a fade transition)
- `hx-include="[name]"` → includes all named inputs in the enclosing form so session state has
  the full current values of all sibling widgets, not just the one that changed

#### 10.3.3 Button HTMX Changes (`components.html`)

Buttons gain their own HTMX attributes and use `hx-swap="none"` since a button click triggers
a full re-render of dependent output components (not the button itself):

```html
<button type="button"
        data-variant="secondary"
        name="{{ comp.key }}"
        value="true"
        hx-post="/interact"
        hx-target="#mx-main"
        hx-swap="innerHTML settle:100ms"
        hx-include="[name]"
        class="{{ comp.class_ | default('') }}">{{ comp.label }}</button>
```

`type="button"` prevents the native form submit from firing at all. The button targets `#mx-main`
(the main content region) rather than its own id, because a button click typically changes
application-level state that affects multiple display components.

#### 10.3.4 Outer `<form>` and `#app-root` Changes (`base.html`)

The outer `<form>` retains `hx-post="/interact"` as a fallback for browsers without JS but
**loses `hx-target` and `hx-swap`** — those are now per-widget. `#app-root`'s duplicate
`hx-post` is removed entirely; only `hx-trigger="load"` stays for the initial render:

```html
<form style="margin:0; padding:0; width:100%;">

    <div id="app-root"
         data-sidebar-layout
         hx-trigger="load"
         hx-post="/interact"
         hx-target="#app-root"
         hx-swap="innerHTML settle:0"
         hx-ext="sse"
         sse-connect="/events"
         sse-swap="message">
        <p class="mx-loading">Loading app&hellip;</p>
    </div>
</form>
```

The initial `load` trigger still swaps the full `#app-root` innerHTML to populate the page on
first render. Subsequent interactions use per-widget targets.

#### 10.3.5 Server-Side Changes (`server.py`)

The `/interact` endpoint needs to know **which component was the trigger** so it can return only
that component's updated HTML. HTMX sends the triggering element's `id` in the `HX-Trigger`
request header automatically:

```python
@app.post("/interact", response_class=HTMLResponse)
async def interact(request: Request):
    hx_trigger = request.headers.get("HX-Trigger", "")   # e.g. "mx-<key>"
    is_initial_load = not hx_trigger                       # load trigger has no HX-Trigger

    # ... update session_state from form_data as before ...

    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        ...
    finally:
        _current_context.reset(token)

    if is_initial_load:
        # Full render on first load
        return templates.TemplateResponse("components.html", {...})
    else:
        # Find only the component(s) whose key matches the trigger and return them
        triggered_key = hx_trigger.removeprefix("mx-")
        changed = [c for c in ctx.components if c.get("key") == triggered_key]
        return templates.TemplateResponse(
            "component_fragment.html",   # new: renders a single component
            {"component": changed[0], ...}
        )
```

A new `component_fragment.html` template (or a Jinja2 macro call) renders just the one
`<div id="mx-{key}">` wrapper so the `outerHTML` swap replaces exactly the right element.

---

### 10.4 Work Items

| # | Area | Task |
|---|------|------|
| W1 | `components.html` | Wrap every `render_component` output in `<div id="mx-{{ comp.id }}">` (`comp.id` is always resolved by decorator/`to_dict()`) |
| W2 | `components.html` | Change all widget `hx-target` from `#app-root` to `#mx-{{ comp.id }}` |
| W3 | `components.html` | Change all widget `hx-swap` from `innerHTML` to `outerHTML settle:100ms` |
| W4 | `components.html` | Add `hx-include="[name]"` to all widget inputs |
| W5 | `components.html` | Change `<button type="submit">` to `type="button"` and add own `hx-*` attrs |
| W6 | `base.html` | Remove `hx-post / hx-target / hx-swap` from outer `<form>` (keep as plain form) |
| W7 | `base.html` | Remove duplicate `hx-post / hx-target / hx-swap` from `#app-root` (keep `hx-trigger="load"` only) |
| W8 | `server.py` | Read `HX-Trigger` header to identify the changed component |
| W9 | `server.py` | Return single-component fragment HTML when `HX-Trigger` is present |
| W10 | `templates/` | Create `component_fragment.html` (or macro) for single-component renders |
| W11 | `server.py` | Add named region ids (`#mx-sidebar`, `#mx-main`) for button targets that affect multiple components |
