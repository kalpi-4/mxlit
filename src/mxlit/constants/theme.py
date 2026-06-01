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


# ── ThemeManager ───────────────────────────────────────────────────────────────

class ThemeManager:
    """Single authoritative owner of theme merge logic.

    Two consumers previously duplicated the same dict-merge rule:

    * ``server.py :: _resolve_theme()``  — a lightweight read used by the
      Jinja2 template on every HTTP response.
    * ``components/theme.py :: theme()`` — the user-facing API that also
      absorbs color-picker widget keys and persists the result.

    Both now delegate here, eliminating the duplication.
    """

    @staticmethod
    def _ss():
        """Lazy accessor for session_state (avoids circular import at module level)."""
        from mxlit.state import session_state  # noqa: PLC0415
        return session_state

    def resolve(self) -> dict[str, str]:
        """Lightweight read — merge session overrides onto defaults.

        No side effects: does **not** absorb widget keys, does **not** persist.
        Called by server endpoints on every HTTP response to build the
        ``theme_vars`` dict injected into the Jinja2 template context.

        Returns:
            Full resolved token dict (386 Material + any session overrides).
        """
        ss = self._ss()
        return {**_DEFAULTS, **ss.get(THEME_KEY, {})}

    def apply(self, tokens: dict[str, str] | None = None) -> dict[str, str]:
        """Full apply — absorb widget keys, merge explicit overrides, persist.

        This is the implementation of the user-facing ``mt.theme()`` API.

        Steps:
        1. Read current stored theme (or fall back to ``_DEFAULTS``).
        2. Absorb transient flat keys written by ``color_picker`` widgets.
        3. Merge explicit *tokens* argument (highest priority).
        4. Persist result back to ``session_state[THEME_KEY]``.
        5. Return the complete resolved dict.

        Args:
            tokens: Optional ``{dot.notation.path: "#RRGGBB"}`` overrides.
                    Unknown keys raise :class:`ValueError`.

        Returns:
            Full resolved token dict after all merges and persistence.

        Raises:
            ValueError: If *tokens* contains a key not in ``_DEFAULTS``.
        """
        ss = self._ss()
        current: dict[str, str] = {**_DEFAULTS, **ss.get(THEME_KEY, {})}

        # Absorb transient flat keys (color-picker widget side-effects)
        for flat_key, theme_key in _FLAT_KEYS.items():
            if flat_key in ss:
                current[theme_key] = ss[flat_key]
                del ss[flat_key]

        # Merge explicit caller overrides (highest priority)
        if tokens:
            for key, value in tokens.items():
                if key not in _DEFAULTS:
                    raise ValueError(
                        f"mt.theme(): unknown key {key!r}. "
                        f"Valid keys: {sorted(_DEFAULTS)}"
                    )
                current[key] = value

        ss[THEME_KEY] = current
        return dict(current)


#: Module-level singleton — import this from ``mxlit.constants``.
theme_manager = ThemeManager()
