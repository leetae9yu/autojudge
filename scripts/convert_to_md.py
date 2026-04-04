#!/usr/bin/env python3
# pyright: reportUnusedCallResult=false
"""Compatibility wrapper for backend/scripts/convert_to_md.py."""

from __future__ import annotations

from pathlib import Path
import runpy


SCRIPT = Path(__file__).resolve().parents[1] / "backend" / "scripts" / "convert_to_md.py"
_ = runpy.run_path(str(SCRIPT), run_name="__main__")
