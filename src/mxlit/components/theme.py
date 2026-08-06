from mxlit.constants import THEME_KEY, _DEFAULTS, _FLAT_KEYS, theme_manager  # noqa: F401


def theme(tokens: dict | None = None) -> dict[str, str]:
    """Merge token overrides into the global theme and return the resolved dict.

    The theme is stored as a single dict at ``session_state[THEME_KEY]`` and
    seeded from the 386-token Material Theme Builder palette in
    ``mxlit/constants/theme.json``.  CSS variable overrides are emitted
    automatically by the Jinja2 template on every HTMX response — no manual
    ``mt.html()`` injection is needed.

    **Token keys** use dot-notation paths that mirror the JSON structure, e.g.
    ``"schemes.light.primary"``.  Any of the 386 hex-colour entries in
    ``_DEFAULTS`` is a valid key; passing an unrecognised key raises
    :class:`ValueError`.

    The **four core rendering tokens** drive all oat.ink CSS variables:

    +--------------------------------------+---------------------------------------------+-------------------+
    | Token key                            | CSS variables affected                      | Material default  |
    +======================================+=============================================+===================+
    | ``"schemes.light.primary"``          | ``--primary``, ``--ring``, ``--accent``     | ``#415F91``       |
    +--------------------------------------+---------------------------------------------+-------------------+
    | ``"schemes.light.secondary"``        | ``--secondary``, ``--secondary-foreground`` | ``#565F71``       |
    +--------------------------------------+---------------------------------------------+-------------------+
    | ``"schemes.light.background"``       | ``--background``, ``--card``                | ``#F9F9FF``       |
    +--------------------------------------+---------------------------------------------+-------------------+
    | ``"schemes.light.onBackground"``     | ``--foreground``, ``--card-foreground``     | ``#191C20``       |
    +--------------------------------------+---------------------------------------------+-------------------+

    Any other ``schemes.*``, ``palettes.*``, or ``coreColors.*`` token can also
    be overridden and is available in the returned dict for use in Python code.

    **Widget absorption** — color-picker widgets write transient flat keys back
    to ``session_state`` using the auto-generated alias format::

        "theme_" + token_key.replace(".", "_")

    For example, a picker with ``key="theme_schemes_light_primary"`` writes
    ``session_state["theme_schemes_light_primary"]``.  On the next call
    ``mt.theme()`` absorbs and deletes those transient keys, merging the value
    into ``session_state[THEME_KEY]`` before returning.

    Args:
        tokens: Optional ``{dot.notation.path: "#RRGGBB"}`` overrides.
                Unrecognised keys raise :class:`ValueError`.
                Omitted keys keep their current session value or the Material
                Design default.

    Returns:
        The full resolved theme dict — all 386 Material tokens merged with any
        session-state overrides and the *tokens* argument.  Index the four core
        keys to drive the UI::

            _t = mt.theme()
            primary_hex = _t["schemes.light.primary"]

    Raises:
        ValueError: If *tokens* contains a key that is not in ``_DEFAULTS``.

    Examples::

        mt.theme()                                      # initialise / re-apply defaults

        mt.theme({"schemes.light.primary": "#9333ea"}) # purple primary, rest unchanged

        mt.theme({
            "schemes.light.primary":    "#0f172a",
            "schemes.light.secondary":  "#10b981",
            "schemes.light.background": "#f8fafc",
            "schemes.light.onBackground": "#1e293b",
        })
    """
    # Delegate all merge/absorb/persist logic to the canonical ThemeManager.
    # This eliminates the duplication that previously existed between here and
    # server.py's _resolve_theme() helper.
    return theme_manager.apply(tokens)
