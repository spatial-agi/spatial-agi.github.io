"""Approved Figure 8.1–8.25 frontend fragments used by the reader rebuild.

Regenerate editable source geometry with figures81_825.py, then update these
approved fragments after visual review. Reading them requires no source PDFs.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((ROOT / 'source/pipeline/figures81_825_sources.json').read_text())

def render(number):
    return (ROOT / f'source/pipeline/native/figure8{number}.html').read_text()
