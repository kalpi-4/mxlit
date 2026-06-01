import argparse
import re
import subprocess
import sys
import os
import threading
from pathlib import Path

import uvicorn

from mxlit._paths import INPUT_CSS, OUTPUT_CSS, STATIC_DIR


def _build_css() -> None:
    """Rebuild style.css from input.css via pytailwindcss on every server start.

    Always runs unconditionally so the compiled CSS is guaranteed to reflect the
    current input.css and any scanned template/source changes.
    Fails gracefully — a missing pytailwindcss or a build error prints a warning
    but never prevents the server from starting.
    """
    print("Building style.css …", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytailwindcss",
             "-i", str(INPUT_CSS),
             "-o", str(OUTPUT_CSS)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print("  ✓ style.css rebuilt.", flush=True)
        else:
            msg = (result.stderr or result.stdout).strip()
            print(f"  ✗ CSS build failed (using existing style.css):\n    {msg}",
                  file=sys.stderr, flush=True)
    except FileNotFoundError:
        print(
            "  ⚠ pytailwindcss not installed — using existing style.css.\n"
            "    To enable auto-rebuild: pip install pytailwindcss",
            file=sys.stderr, flush=True,
        )
    except subprocess.TimeoutExpired:
        print("  ⚠ CSS build timed out — using existing style.css.",
              file=sys.stderr, flush=True)


def sync_css_tokens() -> None:
    """Parse oat.min.css and regenerate the :root / [data-theme="dark"] blocks in input.css.

    oat.min.css declares all semantic colour variables using ``light-dark(light, dark)``
    CSS functions inside a ``:root`` block.  This command extracts every variable name
    and its two values, then splices freshly generated light and dark :root blocks
    into ``input.css``, replacing everything between the sentinel comments::

        /* oat.ink default theme … */
        …generated content…
        /* ── Base font size …

    Variables that don't use ``light-dark()`` are included with the same value in
    both the light and dark blocks.

    Run manually after upgrading oat.min.css::

        mxlit sync-css-tokens
    """
    oat_css_path: Path = STATIC_DIR / "oat.min.css"
    if not oat_css_path.exists():
        print(f"  ✗ {oat_css_path} not found — nothing to sync.", file=sys.stderr)
        sys.exit(1)

    css_text = oat_css_path.read_text(encoding="utf-8")

    # ── Extract variables from :root { … } ──────────────────────────────────
    # Match the first :root block in the minified CSS (stops at the first '}'.
    # The block may contain light-dark() or plain hex values.
    root_match = re.search(r':root\s*\{([^}]+)\}', css_text)
    if not root_match:
        print("  ✗ No :root block found in oat.min.css.", file=sys.stderr)
        sys.exit(1)
    root_block = root_match.group(1)

    # Pattern: --name:light-dark(#light,#dark)   or   --name:#value
    ld_pattern    = re.compile(
        r'(--[\w-]+)\s*:\s*light-dark\(\s*(#[0-9A-Fa-f]{3,8})\s*,\s*(#[0-9A-Fa-f]{3,8})\s*\)'
    )
    plain_pattern = re.compile(r'(--[\w-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})')

    light_vars: dict[str, str] = {}
    dark_vars:  dict[str, str] = {}

    for m in ld_pattern.finditer(root_block):
        name, light, dark = m.group(1), m.group(2).upper(), m.group(3).upper()
        light_vars[name] = light
        dark_vars[name]  = dark

    for m in plain_pattern.finditer(root_block):
        name = m.group(1)
        if name not in light_vars:  # don't override light-dark() matches
            val = m.group(2).upper()
            light_vars[name] = val
            dark_vars[name]  = val

    if not light_vars:
        print("  ✗ No CSS custom properties found in :root.", file=sys.stderr)
        sys.exit(1)

    # ── Build replacement CSS blocks ─────────────────────────────────────────
    max_name_len = max(len(n) for n in light_vars)

    def _block(selector: str, var_dict: dict[str, str]) -> str:
        lines = [f"{selector} {{"]
        for name, value in var_dict.items():
            lines.append(f"  {name:<{max_name_len}}: {value};")
        lines.append("}")
        return "\n".join(lines)

    light_block = _block(":root", light_vars)
    dark_block  = _block('[data-theme="dark"]', dark_vars)

    new_section = (
        "/* ── oat.ink default theme ────────────────────────────────────────────────────\n"
        "   Values sourced directly from oat.min.css :root { light-dark(…) } declarations.\n"
        "   Light values are the first argument; dark values are the second.\n"
        "   Run `mxlit sync-css-tokens` after upgrading oat.min.css to regenerate.\n"
        "   ─────────────────────────────────────────────────────────────────────────── */\n\n"
        "/* Light (:root) ────────────────────────────────────────────────────────────── */\n"
        f"{light_block}\n\n"
        "/* Dark ─────────────────────────────────────────────────────────────────────── */\n"
        f"{dark_block}\n"
    )

    # ── Splice into input.css ────────────────────────────────────────────────
    input_text = INPUT_CSS.read_text(encoding="utf-8")

    # Sentinel markers: from "/* oat.ink default theme" up to "/* ── Base font size"
    start_sentinel = "/* ── oat.ink default theme"
    end_sentinel   = "/* ── Base font size"

    start_idx = input_text.find(start_sentinel)
    end_idx   = input_text.find(end_sentinel)

    if start_idx == -1 or end_idx == -1:
        print(
            f"  ✗ Could not find sentinel comments in input.css.\n"
            f"    Expected:\n"
            f"      '…{start_sentinel}…'\n"
            f"      '…{end_sentinel}…'",
            file=sys.stderr,
        )
        sys.exit(1)

    updated = input_text[:start_idx] + new_section + "\n" + input_text[end_idx:]
    INPUT_CSS.write_text(updated, encoding="utf-8")

    print(
        f"  ✓ Synced {len(light_vars)} CSS variables from oat.min.css → input.css.",
        flush=True,
    )


def run_server(script_path, host="127.0.0.1", port=8501):
    """
    Start the mxlit server for the given script.
    """
    abs_path = Path(script_path).resolve()
    if not abs_path.is_file():
        print(f"Error: Script '{script_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Rebuild style.css before the server starts (skipped when already up-to-date).
    _build_css()

    os.environ["MXLIT_SCRIPT"] = str(abs_path)

    config = uvicorn.Config(
        "mxlit.server:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    # Run uvicorn in a daemon thread so the main thread stays free to receive
    # Ctrl+C as a KeyboardInterrupt (on Windows, uvicorn's asyncio signal
    # handlers can swallow SIGINT when run directly on the main thread).
    thread = threading.Thread(target=server.run, daemon=True)

    print(f"Starting mxlit server for '{abs_path.name}' at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.should_exit = True
        thread.join(timeout=5)
        print("Stopped.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="mxlit CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run an mxlit app")
    run_parser.add_argument("script", help="Path to the python script to run")
    run_parser.add_argument("--port", type=int, default=8501, help="Port to run the server on")
    run_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")

    subparsers.add_parser(
        "sync-css-tokens",
        help=(
            "Parse oat.min.css and regenerate the :root / [data-theme=\"dark\"] "
            "blocks in input.css. Run after upgrading oat.min.css."
        ),
    )

    args = parser.parse_args()

    if args.command == "run":
        run_server(args.script, host=args.host, port=args.port)
    elif args.command == "sync-css-tokens":
        print("Syncing CSS tokens from oat.min.css …", flush=True)
        sync_css_tokens()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
