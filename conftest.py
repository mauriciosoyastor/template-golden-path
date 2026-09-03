"""Ancla pytest rootdir — no borrar (ver docs/adr/0002)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
