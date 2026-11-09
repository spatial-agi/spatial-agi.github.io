# Spatial Intelligence Handbook — website

Live site: https://spatial-agi.github.io

This branch holds the generated static site (served as is by GitHub Pages) and, under `source/`, everything needed to rebuild it from the LaTeX source of the handbook.

## What is generated from the book

| Output | Source |
|---|---|
| Reader pages (`/read/…`), one per numbered section, plus preface, part and chapter openings, notation, glossary, back matter | LaTeX → LaTeXML → post-processing (`source/pipeline/build_site.py`) |
| Section, figure, table, equation and citation numbers | `main.aux` of the print build (checked by `source/pipeline/verify_numbers.py` and `parity.py`) |
| Literature explorer, references | `main.bib` + `\bibcite` numbers |
| Datasets & benchmarks | the comparison tables of the book |
| Milestones | the TikZ source of Figure 1.3 |
| Figures | the book's figure files, rasterised to WebP |
| Tools & platforms | curated list `source/pipeline/tools_curated.yaml`; every repository is verified on each build |

## Rebuild

Requirements: TeX Live, LaTeXML ≥ 0.8.8, Ghostscript, Poppler (`pdftoppm`), Node (for Pagefind), Python 3.12 with `jinja2 lxml bibtexparser==1.4.3 pillow pyyaml`.

```bash
# the book (Overleaf clone) must sit next to the website folder as ../Spt-Intell-share-paper, compiled (main.pdf, main.aux)
cd source/pipeline
./make.sh            # full rebuild, ~5 minutes
./make.sh --skip-latex   # templates, styles and data only
```

Output goes to `dist/`, which is what this branch contains at its root.
