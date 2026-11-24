"""Approved Figures 10.1–11.16 used by the website rebuild."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((ROOT / 'source/pipeline/figures101_1116_sources.json').read_text())
def render(chapter, number):
    return (ROOT / f'source/pipeline/native/figure{chapter}{number}.html').read_text()
