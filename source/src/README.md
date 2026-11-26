# Spatial Intelligence: A Handbook — website

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

## Content update from a final PDF (November 2026)

The current source is selected from the adjacent `Spatial_Intelligence_Book_2025_v*`
folders. Set `BOOK_SOURCE` and `BOOK_PDF` to use explicit paths. The PDF is the
source of citation numbering and pagination; its named destinations are read by
`pdf_metadata.py`, so no print LaTeX compilation is needed. Install Python
requirements from `source/pipeline/requirements.txt`; LaTeXML 0.8.8, Ghostscript,
Node.js and Pagefind 1.3.0 are also required.

```bash
cd source/pipeline
./make.sh                  # outputs source/dist
./make.sh --skip-latex     # reuses the XML/HTML conversion
python3 verify_content.py  # checks content links, numbering and approved figures
python3 publish_content.py # copies verified content into the served website
```

`PYTHON`, `LATEXML`, `LATEXMLPOST`, `PAGEFIND` and `SITE_OUTPUT` can select local
runtimes/output paths. `data/approved_figure_bodies.json` preserves all approved
figure renderings while allowing captions to be regenerated. The v14 update only
changes terminology text inside Figures 4.5, 6.12 and 6.17; their geometry and
interactions are preserved. Visual
assets must match the served site before `publish_content.py` will publish a
content-only build. Author profiles and verified tools are retained in pipeline
metadata. The book source, site styles and native figure code are read-only
inputs to this workflow.
