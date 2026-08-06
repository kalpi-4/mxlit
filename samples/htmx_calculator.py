"""
htmx_calculator.py — Calculator with history.
Kitchen sink for every HtmxProps pattern in mxlit.

HtmxProps patterns demonstrated (src/mxlit/components/base.py :: HtmxProps):
══════════════════════════════════════════════════════════════════════════════
 A  Full page re-render
    hx-post="/interact"  hx-target="#app-root"  hx-swap="innerHTML settle:0"
    ↳ Every mt.button() — digit, operator, = , CE, M* keys trigger this.
      The whole script re-runs top-to-bottom; new session_state drives the UI.
      Pre-processing reads button state BEFORE rendering so the display is
      always correct on the same pass that triggered the click.

 B  Targeted self-update
    hx-target="#mx-{comp.id}"  hx-swap="outerHTML settle:100ms"
    ↳ Every widget (selectbox, select_slider, text_input, toggle, …)
      Only the component's own wrapper <div id="mx-…"> is replaced.
      Sidebar settings demonstrate this — the calculator panel is untouched.

 C  Named-field include
    hx-include="[name]"
    ↳ All elements with a `name` attribute in the DOM are collected and sent
      with every widget POST. The pagination widget below sends its page number
      alongside any other [name] fields that happen to be in scope.

 D  Keyup-delay trigger
    hx-trigger="keyup delay:300ms"  (overrides default "change")
    ↳ The direct-expression text_input fires 300 ms after the last keystroke,
      so the targeted self-update runs without waiting for blur / Tab.

 E  Auto-poll trigger
    hx-trigger="every {N}s"
    ↳ setInterval(sync_time=N) wraps the live session clock.
      The polled component's wrapper fires hx-get="/refresh/{id}" every N s —
      no WebSocket, no JS, just HTMX polling.

 F  Swap strategy variety
    ↳ outerHTML settle:100ms  — widget targeted swaps
      innerHTML settle:0      — full #app-root replace (button clicks)
      outerHTML settle:0      — auto-refresh polled components

 G  hx-confirm analogue via mt.dialog()
    ↳ Destructive "All Clear" action is wrapped in a confirmation dialog
      instead of firing immediately — same intent as hx-confirm="Are you sure?".

Pattern flow per button click:
  1. Browser fires hx-post="/interact" with {btn_key: "true"} in POST body.
  2. server._apply_form_data() writes session_state[btn_key] = "true".
  3. Script re-runs from top.
  4. Pre-processing (top of script) reads & clears session_state[btn_key].
  5. New expr / display is written to session_state.
  6. Display card renders the updated state.
  7. Buttons render — their own session_state values are already "false", so
     mt.button() returns False and the if-blocks are no-ops (no double-process).

Run:  mxlit run samples/htmx_calculator.py
"""

import math
import time

import mxlit as mt
from mxlit.state import session_state

# ── State bootstrap ───────────────────────────────────────────────────────────
_DEFAULTS = {
    "calc_expr":      "",
    "calc_display":   "0",
    "calc_history":   [],
    "calc_memory":    0.0,
    "calc_precision": "2",
    "calc_mode":      "Standard",
    "calc_angle":     "Degrees",
}
for _k, _v in _DEFAULTS.items():
    if _k not in session_state:
        session_state[_k] = _v

# ── Helpers ───────────────────────────────────────────────────────────────────
def _fmt(val, prec: int) -> str:
    try:
        f = float(val)
        return str(int(f)) if f == int(f) else f"{f:.{prec}f}"
    except (TypeError, ValueError):
        return str(val)


_SAFE_NAMES = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "log2": math.log2, "exp": math.exp, "abs": abs,
    "pi": math.pi, "e": math.e, "tau": math.tau,
    "pow": pow, "round": round,
}


def _eval_expr(expression: str, angle: str = "Degrees") -> str:
    safe = dict(_SAFE_NAMES)
    if angle == "Degrees":
        for fn in ("sin", "cos", "tan"):
            safe[fn] = lambda x, _f=getattr(math, fn): _f(math.radians(x))
    try:
        return str(eval(expression, {"__builtins__": {}}, safe))  # noqa: S307
    except Exception as exc:
        return f"Error: {exc}"


def _push_history(expression: str, result: str) -> None:
    h = session_state["calc_history"]
    h.append({"expr": expression, "result": result})
    session_state["calc_history"] = h[-40:]


# ══════════════════════════════════════════════════════════════════════════════
# PATTERN A — Pre-process button actions (Pattern A explanation in docstring)
# Read current state, detect which button was pressed last POST, update state,
# then clear the button flag so mt.button() renders without double-processing.
# ══════════════════════════════════════════════════════════════════════════════

expr    = session_state["calc_expr"]
display = session_state["calc_display"]
memory  = float(session_state["calc_memory"])
prec    = int(session_state["calc_precision"])
mode    = session_state["calc_mode"]
angle   = session_state["calc_angle"]

_changed = False

# Digits & decimal
for _d in "0123456789.":
    _k = f"calc_d_{_d}"
    if session_state.get(_k) == "true":
        session_state[_k] = "false"
        if display in ("0", "Error"):
            expr = _d
        else:
            expr = expr + _d
        display = expr
        _changed = True
        break

# Operators
_OPS = {"calc_op_add": "+", "calc_op_sub": "-",
        "calc_op_mul": "*", "calc_op_div": "/",
        "calc_op_pow": "**", "calc_op_mod": "%",
        "calc_op_lp":  "(",  "calc_op_rp":  ")"}
for _k, _op in _OPS.items():
    if session_state.get(_k) == "true":
        session_state[_k] = "false"
        expr = expr + _op
        display = expr
        _changed = True
        break

# Scientific functions (append to expression, user closes with digit + "=")
_SCI = {
    "calc_fn_sin": "sin(", "calc_fn_cos": "cos(", "calc_fn_tan": "tan(",
    "calc_fn_sqrt": "sqrt(", "calc_fn_log": "log(", "calc_fn_exp": "exp(",
    "calc_fn_pi": str(math.pi), "calc_fn_e": str(math.e),
}
for _k, _token in _SCI.items():
    if session_state.get(_k) == "true":
        session_state[_k] = "false"
        expr = expr + _token
        display = expr
        _changed = True
        break

# Backspace
if session_state.get("calc_btn_back") == "true":
    session_state["calc_btn_back"] = "false"
    expr = expr[:-1]
    display = expr or "0"
    _changed = True

# CE — clear expression only
if session_state.get("calc_btn_CE") == "true":
    session_state["calc_btn_CE"] = "false"
    expr = ""
    display = "0"
    _changed = True

# ± toggle sign
if session_state.get("calc_btn_sign") == "true":
    session_state["calc_btn_sign"] = "false"
    if expr.startswith("-"):
        expr = expr[1:]
    elif expr:
        expr = "-" + expr
    display = expr or "0"
    _changed = True

# = evaluate
if session_state.get("calc_btn_eq") == "true":
    session_state["calc_btn_eq"] = "false"
    raw = _eval_expr(expr or "0", angle)
    if raw.startswith("Error"):
        display = "Error"
        expr = ""
    else:
        display = _fmt(raw, prec)
        _push_history(expr, display)
        expr = display
    _changed = True

# Memory operations
if session_state.get("calc_btn_MC") == "true":
    session_state["calc_btn_MC"] = "false"
    memory = 0.0
    session_state["calc_memory"] = 0.0

if session_state.get("calc_btn_MR") == "true":
    session_state["calc_btn_MR"] = "false"
    expr = _fmt(memory, prec)
    display = expr
    _changed = True

if session_state.get("calc_btn_Mplus") == "true":
    session_state["calc_btn_Mplus"] = "false"
    raw = _eval_expr(expr or "0", angle)
    if not raw.startswith("Error"):
        memory = memory + float(raw)
        session_state["calc_memory"] = memory

if session_state.get("calc_btn_Mminus") == "true":
    session_state["calc_btn_Mminus"] = "false"
    raw = _eval_expr(expr or "0", angle)
    if not raw.startswith("Error"):
        memory = memory - float(raw)
        session_state["calc_memory"] = memory

# All Clear (from dialog confirmation)
if session_state.get("calc_btn_AC") == "true":
    session_state["calc_btn_AC"] = "false"
    expr = ""
    display = "0"
    session_state["calc_history"] = []
    session_state["calc_memory"]  = 0.0
    memory = 0.0
    _changed = True

# Persist updated state
if _changed:
    session_state["calc_expr"]    = expr
    session_state["calc_display"] = display

# ── Page config ───────────────────────────────────────────────────────────────
mt.page_config(main_class="p-4 max-w-5xl mx-auto")

# ════════════════════════════════════════════════════════════════════════════
# PATTERN B — Sidebar widgets: targeted self-update only
# Each widget uses hx-target="#mx-{id}" + hx-swap="outerHTML settle:100ms"
# Sidebar widgets don't touch the calculator panel or history column.
# ════════════════════════════════════════════════════════════════════════════
with mt.sidebar():
    mt.title("⚙ Settings")
    mt.markdown("---")

    # Pattern B: selectbox — targeted update of its own wrapper only
    mode = mt.selectbox(
        "Mode",
        ["Standard", "Scientific"],
        key="calc_mode",
    )

    # Pattern B: select_slider — targeted update + Pattern C named include
    prec_sel = mt.select_slider(
        "Decimal places",
        options=["0", "1", "2", "4", "6", "8"],
        value=session_state["calc_precision"],
        key="calc_precision",
    )
    prec = int(prec_sel)
    session_state["calc_precision"] = prec_sel

    if mode == "Scientific":
        angle = mt.radio(
            "Angle unit",
            ["Degrees", "Radians"],
            key="calc_angle",
        )
        session_state["calc_angle"] = angle

    mt.markdown("---")
    mt.write("**Memory register**", className="text-sm font-semibold")
    mt.metric("M", _fmt(memory, prec))
    if memory != 0:
        mt.badge(f"M = {_fmt(memory, prec)}")

    mt.markdown("---")
    mt.write("**HtmxProps patterns active**", className="text-xs font-semibold uppercase tracking-wide")
    for _lbl in [
        "A · Full re-render  → buttons",
        "B · Targeted update → widgets",
        "C · Named include   → pagination",
        "D · Keyup delay     → expr input",
        "E · Auto-poll       → live clock",
        "F · Swap strategies → outerHTML/innerHTML",
        "G · Confirm dialog  → AC button",
    ]:
        mt.write(_lbl, className="text-xs font-mono")

# ── Page header ───────────────────────────────────────────────────────────────
mt.title("🧮 Calculator · HtmxProps Kitchen Sink")
mt.write(
    "Every HTMX behaviour available in mxlit — demonstrated through a working "
    f"{'scientific ' if mode == 'Scientific' else ''}calculator."
)
mt.markdown("---")

with mt.grid():
    with mt.row():

        # ════════════════════════════════════════════════════════════════════════════
        # Calculator column
        # ════════════════════════════════════════════════════════════════════════════
        with mt.col(7):

            # ── Display card ──────────────────────────────────────────────────────────
            # Shows UPDATED state because pre-processing ran before this render.
            with mt.card():
                mt.write(expr or "—", className="font-mono text-sm text-gray-400 min-h-5")
                disp_cls = (
                    "font-mono text-4xl text-right text-red-600"
                    if display.startswith("Error")
                    else "font-mono text-4xl text-right"
                )
                mt.title(display, className=disp_cls)
                _badge_row = mt.columns([1, 1, 1])
                with _badge_row[0]:
                    if memory != 0.0:
                        mt.badge(f"M={_fmt(memory, prec)}")
                with _badge_row[1]:
                    mt.badge(f"{prec}dp")
                with _badge_row[2]:
                    if mode == "Scientific":
                        mt.badge(angle[:3])

            mt.space()

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN D — Keyup-delay targeted update
            # hx-trigger="keyup delay:300ms" on the text_input's <input> element.
            # Fires 300 ms after the last keystroke → targeted outerHTML swap of
            # just this component, not the full #app-root.
            # ════════════════════════════════════════════════════════════════════════
            with mt.expander("Pattern D · Direct expression entry (keyup delay:300ms)", className="border rounded-lg mb-2"):
                mt.write(
                    "Type a full expression — evaluates on keystroke (300 ms debounce). "
                    "Only this widget's wrapper is swapped, the keypad is untouched.",
                    className="text-xs",
                )
                direct = mt.text_input(
                    "Expression",
                    value=expr,
                    key="calc_expr_direct",
                    className="font-mono w-full",
                )
                if direct and direct != session_state.get("calc_expr"):
                    raw = _eval_expr(direct, angle)
                    if not raw.startswith("Error"):
                        result_str = _fmt(raw, prec)
                        _push_history(direct, result_str)
                        session_state["calc_expr"]    = direct
                        session_state["calc_display"] = result_str

            mt.space()

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN A — Full page re-render (memory buttons)
            # hx-post="/interact"  hx-target="#app-root"  hx-swap="innerHTML settle:0"
            # Clicking any of these runs the script from the top; the pre-processing
            # block at the top detects which key was clicked and updates state.
            # ════════════════════════════════════════════════════════════════════════
            mt.write("**Pattern A · Memory — full re-render buttons**", className="text-xs font-semibold uppercase tracking-wide")
            with mt.grid():
                with mt.row():
                    with mt.col(3): mt.button("MC",  key="calc_btn_MC",     className="w-full")
                    with mt.col(3): mt.button("MR",  key="calc_btn_MR",     className="w-full")
                    with mt.col(3): mt.button("M+",  key="calc_btn_Mplus",  className="w-full")
                    with mt.col(3): mt.button("M−",  key="calc_btn_Mminus", className="w-full")

            mt.space()

            # ── Scientific row (visible in Scientific mode) ───────────────────────────
            if mode == "Scientific":
                mt.write("**Scientific functions**", className="text-xs font-semibold uppercase tracking-wide")
                _sci_btns = [
                    ("sin",  "calc_fn_sin"),  ("cos",  "calc_fn_cos"),
                    ("tan",  "calc_fn_tan"),  ("√",    "calc_fn_sqrt"),
                ]
                _sci2 = [
                    ("log",  "calc_fn_log"),  ("exp",  "calc_fn_exp"),
                    ("π",    "calc_fn_pi"),   ("e",    "calc_fn_e"),
                ]
                with mt.grid():
                    with mt.row():
                        for _lbl, _k in _sci_btns:
                            with mt.col(3): mt.button(_lbl, key=_k, className="w-full")
                    with mt.row():
                        for _lbl, _k in _sci2:
                            with mt.col(3): mt.button(_lbl, key=_k, className="w-full")

                mt.space()

            # ── Main keypad ───────────────────────────────────────────────────────────
            _ROWS: list[list[tuple[str, str, str]]] = [
                [("CE", "calc_btn_CE", ""),   ("±", "calc_btn_sign", ""), ("(", "calc_op_lp", ""), (")", "calc_op_rp", ""), ("÷", "calc_op_div", "op")],
                [("7",  "calc_d_7",   ""),    ("8", "calc_d_8",    ""),   ("9", "calc_d_9",    ""), ("×", "calc_op_mul", "op")],
                [("4",  "calc_d_4",   ""),    ("5", "calc_d_5",    ""),   ("6", "calc_d_6",    ""), ("−", "calc_op_sub", "op")],
                [("1",  "calc_d_1",   ""),    ("2", "calc_d_2",    ""),   ("3", "calc_d_3",    ""), ("+", "calc_op_add", "op")],
                [("0",  "calc_d_0",   ""),    (".", "calc_d_.", ""),       ("⌫", "calc_btn_back",""), ("=", "calc_btn_eq", "eq")],
            ]
            if mode == "Scientific":
                _ROWS[0].append(("%", "calc_op_mod", "op"))

            with mt.grid():
                for _row in _ROWS:
                    _n    = len(_row)
                    _span = 12 // _n
                    _last = 12 - _span * (_n - 1)
                    with mt.row():
                        for _i, (_label, _key, _role) in enumerate(_row):
                            _col_span = _last if _i == _n - 1 else _span
                            _cls = (
                                "w-full bg-blue-600 text-white font-bold" if _role == "eq"
                                else "w-full bg-orange-400 text-white"    if _role == "op"
                                else "w-full"
                            )
                            with mt.col(_col_span):
                                # Return value ignored — pre-processing already handled the state.
                                mt.button(_label, key=_key, className=_cls)

            mt.space()

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN G — Confirmation dialog (hx-confirm analogue)
            # Instead of hx-confirm="Are you sure?" on the button (which would need
            # a custom component), we wrap the destructive action in mt.dialog().
            # The dialog trigger fires a full re-render; "Yes" button inside also
            # fires a full re-render which the pre-processing block handles via
            # calc_btn_AC key.
            # ════════════════════════════════════════════════════════════════════════
            mt.write("**Pattern G · Destructive confirm via mt.dialog()**", className="text-xs font-semibold uppercase tracking-wide")
            mt.write("Analogue of `hx-confirm=\"…\"` — wraps the action in a native `<dialog>` element.", className="text-xs")
            with mt.dialog("All Clear — reset calculator and history?", trigger_label="AC · All Clear"):
                mt.warning("This permanently erases all history and resets the memory register to 0.")
                mt.button("Yes, reset everything", key="calc_btn_AC", className="w-full")

        # ════════════════════════════════════════════════════════════════════════════
        # History column
        # ════════════════════════════════════════════════════════════════════════════
        with mt.col(5):

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN E — Auto-poll via setInterval
            # setInterval(sync_time=5) emits:
            #   hx-trigger="every 5s"  hx-get="/refresh/{id}"  hx-swap="outerHTML"
            # on the wrapped component's div.  The browser fires GET /refresh/{id}
            # every 5 s; server re-runs the script and returns just this component.
            # ════════════════════════════════════════════════════════════════════════
            mt.subheader("Pattern E · Auto-poll (setInterval)")
            mt.write(
                "`hx-trigger=\"every 5s\"` on the clock metric — no WebSocket, no JS thread.",
                className="text-xs",
            )
            with mt.setInterval(sync_time=5):
                mt.metric("Session clock", time.strftime("%H:%M:%S"), id="calc_clock")

            mt.markdown("---")

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN C — Named-field include
            # The pagination widget has name="calc_hist_page" in the DOM.
            # hx-include="[name]" on every widget collects all [name] elements and
            # sends them with the POST, so page changes carry all form state.
            # ════════════════════════════════════════════════════════════════════════
            mt.subheader("History")
            mt.write(
                "**Pattern C**: pagination sends `name=\"calc_hist_page\"` with every POST "
                "via `hx-include=\"[name]\"`.",
                className="text-xs",
            )

            history: list = session_state["calc_history"]

            if not history:
                mt.info("No calculations yet — use the keypad or the expression input.")
            else:
                _per = 6
                _total = max(1, (len(history) + _per - 1) // _per)
                _page = mt.pagination(total_pages=_total, current_page=1, key="calc_hist_page")
                _start = (_page - 1) * _per
                _items = list(reversed(history))[_start: _start + _per]

                for _entry in _items:
                    with mt.card():
                        mt.write(_entry["expr"], className="font-mono text-xs text-gray-500")
                        mt.write(_entry["result"], className="font-mono text-lg font-bold")

            mt.markdown("---")

            # ════════════════════════════════════════════════════════════════════════
            # PATTERN F — Swap strategy quick reference
            # ════════════════════════════════════════════════════════════════════════
            with mt.expander("Pattern F · Swap strategy reference", className="border rounded-lg"):
                mt.write("**Trigger source → hx-swap value used**", className="text-xs font-semibold")
                _rows = [
                    ("Button click",        "innerHTML settle:0",        "#app-root"),
                    ("Widget change",       "outerHTML settle:100ms",    "#mx-{id}"),
                    ("setInterval poll",    "outerHTML settle:0",        "#mx-{id}"),
                    ("setTimeout one-shot", "outerHTML settle:0",        "#mx-{id}"),
                    ("Direct expr input",   "outerHTML settle:100ms",    "#mx-{id}"),
                ]
                mt.dataframe(
                    {
                        "Source":    [r[0] for r in _rows],
                        "hx-swap":   [r[1] for r in _rows],
                        "hx-target": [r[2] for r in _rows],
                    },
                    className="text-xs w-full",
                )
