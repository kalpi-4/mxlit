"""
constants/theme.py
==================
Loads the bundled Material Theme Builder JSON at import time and derives:

    _DEFAULTS   – flat {dot.notation.path: "#RRGGBB"} for every hex token
    _FLAT_KEYS  – {session_state_alias: dot.notation.path} for widget absorption
    THEME_KEY   – the single session_state key that owns the live theme dict

The four *core* rendering tokens are:
    "schemes.light.primary"       → --primary
    "schemes.light.secondary"     → --secondary
    "schemes.light.background"    → --background / --card
    "schemes.light.onBackground"  → --foreground / --card-foreground
"""
from __future__ import annotations

import json
from pathlib import Path

# ── Load bundled JSON ──────────────────────────────────────────────────────────
_THEME_JSON_PATH: Path = Path(__file__).parent / "theme.json"

with _THEME_JSON_PATH.open(encoding="utf-8") as _f:
    _RAW: dict = json.load(_f)


# ── Recursive flattener ────────────────────────────────────────────────────────
def _flatten_theme(data: dict, path: str = "") -> dict[str, str]:
    """Recursively flatten *data* into a dot-notation dict of hex colour strings.

    Only leaf values that are hex colour strings (starting with ``#``) are
    included.  Non-colour strings (e.g. ``description``), lists
    (e.g. ``extendedColors``), and non-string scalars are silently skipped.

    Args:
        data:  A (possibly nested) dict to traverse.
        path:  Dot-notation prefix accumulated by recursion; callers leave this
               at its default empty string.

    Returns:
        Flat ``{dot.notation.path: "#RRGGBB"}`` dict.

    Example::

        _flatten_theme({"schemes": {"light": {"primary": "#415F91"}}})
        # → {"schemes.light.primary": "#415F91"}
    """
    result: dict[str, str] = {}
    for key, value in data.items():
        full_key = f"{path}.{key}" if path else key
        if isinstance(value, dict):
            result.update(_flatten_theme(value, full_key))
        elif isinstance(value, str) and value.startswith("#"):
            result[full_key] = value
    return result


# ── Derived constants ──────────────────────────────────────────────────────────

#: Single session_state key that owns the entire live theme dict.
THEME_KEY: str = "__mxlit_theme__"

#: Every hex colour token from the JSON, keyed by its dot-notation path.
#: Covers all scheme variants (light / dark / contrast) and all palette steps.
_DEFAULTS: dict[str, str] = _flatten_theme(_RAW)

#: session_state alias  →  dot-notation path
#: Generated automatically: dots become underscores, prefixed with "theme_".
#:
#: e.g.  "theme_schemes_light_primary"  →  "schemes.light.primary"
_FLAT_KEYS: dict[str, str] = {
    f"theme_{key.replace('.', '_')}": key
    for key in _DEFAULTS
}
