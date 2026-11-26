"""Shared paths for content builds; the book source is always read-only."""
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE_ROOT = HERE.parents[1]
_candidates = list(SITE_ROOT.parent.glob('Spatial_Intelligence_Book_2025_v*'))
_candidates = [p for p in _candidates if p.is_dir()]
_default = max(_candidates, key=lambda p: int(re.search(r'_v(\d+)$', p.name).group(1))) if _candidates else SITE_ROOT.parent / 'Spt-Intell-share-paper'
BOOK = Path(os.environ.get('BOOK_SOURCE', str(_default))).expanduser().resolve()
PDF = Path(os.environ.get('BOOK_PDF', str(SITE_ROOT.parent / 'spatial-intelligence-handbook.pdf'))).expanduser().resolve()
METADATA = HERE / 'build' / 'print_metadata'
DIST = Path(os.environ.get('SITE_OUTPUT', str(SITE_ROOT / 'source' / 'dist'))).expanduser().resolve()
