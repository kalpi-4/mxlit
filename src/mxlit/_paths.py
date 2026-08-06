from pathlib import Path

PACKAGE_DIR   = Path(__file__).parent
STATIC_DIR    = PACKAGE_DIR / "static"
TEMPLATES_DIR = PACKAGE_DIR / "templates"
INPUT_CSS     = STATIC_DIR / "input.css"
OUTPUT_CSS    = STATIC_DIR / "style.css"
