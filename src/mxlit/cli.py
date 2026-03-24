import argparse
import sys
import os
from pathlib import Path
import uvicorn

def run_server(script_path, host="127.0.0.1", port=8501):
    """
    Start the mxlit server for the given script.
    """
    abs_path = Path(script_path).resolve()
    if not abs_path.is_file():
        print(f"Error: Script '{script_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # Set the environment variable so the server knows which script to run
    os.environ["MXLIT_SCRIPT"] = str(abs_path)
    
    print(f"Starting mxlit server for '{abs_path.name}' at http://{host}:{port}")
    uvicorn.run("mxlit.server:app", host=host, port=port, reload=False, log_level="warning")

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
