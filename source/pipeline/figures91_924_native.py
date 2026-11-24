"""Approved Figure 9.1–9.24 fragments used by the website rebuild."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((ROOT / "source/pipeline/figures91_924_sources.json").read_text())
def render(number):
    return (ROOT / f"source/pipeline/native/figure9{number}.html").read_text()
