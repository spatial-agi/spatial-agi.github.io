"""Approved Figures 12.1–14.5 used by the website rebuild."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((ROOT / 'source/pipeline/figures121_145_sources.json').read_text())
def render(chapter, number):
    return (ROOT / f'source/pipeline/native/figure{chapter}{number}.html').read_text()
