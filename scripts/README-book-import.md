# Import the LaTeX book

From the website directory:

```bash
python3 -m pip install -r scripts/requirements-book.txt
python3 scripts/import_book.py
```

The default source is `../Spatial_Intelligence_Book_2025_v12`. To use another checkout:

```bash
python3 scripts/import_book.py --source /path/to/book
```

The importer follows `main.tex` recursively, generates the Contents reader and TOC,
copies raster/SVG figures, rasterizes PDF figures, and writes `book-import-report.json`.
Every `\cite{...}` is rendered as a clickable author/year reference. Activating it opens
a keyboard-accessible citation popover with BibTeX metadata and a link to the reference
list. Output is static HTML and works without a Python server after generation. Math
rendering uses the existing MathJax CDN script. Run the importer again after editing the book.

Generated files: `contents.html`, `book-assets/`, `book-import-report.json`.
Reader runtime: `contents-reader.js`, `contents-reader.css`.

## Known conversion limits

The current importer retains unsupported LaTeX in the generated HTML as code fallbacks
and lists them in the report. Complex TikZ, custom macros and some tables need additional
conversion work for publication-quality parity with the printed book. Citation bubbles and
the reference list are generated from `main.bib`; only entries cited in the manuscript are
included in the list.
Source references whose anchors Pandoc drops are reported and point to their reader page.
The bibliography and acknowledgements currently appear with the closing chapter.
