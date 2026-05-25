"""
mxlit.constants
===============
Public re-export surface for theme constants derived from the bundled
Material Theme Builder JSON (``constants/theme.json``).

Importing from this package is identical to importing from ``constants.theme``
directly, so all existing ``from mxlit.constants import …`` call-sites continue
to work without modification.
"""
from mxlit.constants.theme import (  # noqa: F401
    THEME_KEY,
    _DEFAULTS,
    _FLAT_KEYS,
    _RAW,
    _flatten_theme,
)

__all__ = ["THEME_KEY", "_DEFAULTS", "_FLAT_KEYS", "_RAW", "_flatten_theme"]
