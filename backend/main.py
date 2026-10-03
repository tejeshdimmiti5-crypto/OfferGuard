from pathlib import Path
import sys

# Render starts from the repository root. Add backend/ so the existing
# internal package layout remains importable in local and hosted runs.
BACKEND_DIR = str(Path(__file__).resolve().parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from api.server import app

__all__ = ["app"]
