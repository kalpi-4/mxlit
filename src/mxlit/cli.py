import argparse
import subprocess
import sys
import os
import threading
from pathlib import Path
import uvicorn

# Paths are relative to this file — works whether mxlit is installed or editable.
_STATIC_DIR = Path(__file__).parent / "static"
_INPUT_CSS  = _STATIC_DIR / "input.css"
_OUTPUT_CSS = _STATIC_DIR / "style.css"


def _build_css() -> None:
    """Rebuild style.css from input.css via pytailwindcss.

    Skipped entirely when style.css is already up-to-date (mtime comparison),
    so repeated ``mxlit run`` calls add < 1 ms overhead after the first build.
    Fails gracefully — a missing pytailwindcss or a build error prints a warning
    but never prevents the server from starting.
    """
    # Only rebuild when input.css is newer than the current output.
    if (
        _OUTPUT_CSS.exists()
        and _OUTPUT_CSS.stat().st_mtime >= _INPUT_CSS.stat().st_mtime
    ):
        return

    print("Building style.css from input.css …", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytailwindcss",
             "-i", str(_INPUT_CSS),
             "-o", str(_OUTPUT_CSS)],
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
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_server(args.script, host=args.host, port=args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
