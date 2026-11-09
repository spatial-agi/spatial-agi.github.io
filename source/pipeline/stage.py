"""Stage the book source for LaTeXML: copy the .tex tree, apply web-only rewrites, write book_web.tex.
The Overleaf clone is never modified."""
import re
import shutil
from pathlib import Path

BOOK = Path(__file__).resolve().parents[2] / "Spt-Intell-share-paper"
STAGE = Path(__file__).resolve().parent / "stage"
if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir()

REWRITES = [
    # TikZ milestone chart: the reader uses an interactive redraw; LaTeXML gets a raster fallback
    (r"\\input\{figures/part1/si_milestones_tikz\}", r"\\includegraphics[width=\\linewidth]{figures/web/si_milestones_tikz.pdf}"),
    # inline TikZ figure of Sec. 8.6: compiled standalone by tikz_figs.py
    (r"\\resizebox\{\\linewidth\}\{!\}\{%\s*\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}%?\s*\}",
     r"\\includegraphics[width=\\linewidth]{figures/web/world_modeling_tikz.pdf}"),
    # Part-opener numbering hack (handled from main.aux)
    (r"\\renewcommand\{\\thefigure\}\{\\Roman\{part\}\}%[^\n]*", ""),
]

for src in BOOK.rglob("*.tex"):
    rel = src.relative_to(BOOK)
    if rel.parts[0] in ("figures",) and "tikz" not in rel.name:
        continue
    text = src.read_text(encoding="utf-8", errors="replace")
    for pat, rep in REWRITES:
        text = re.sub(pat, rep, text, flags=re.S)
    out = STAGE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

# Notation and Glossary: tabularray longtblr -> plain longtable in an unnumbered chapter (LaTeXML has no tabularray)
for name in ("notations.tex", "glossary.tex"):
    t = (STAGE / name).read_text()
    t = re.sub(r"\\section\*\{(Notation|Glossary)\}", r"\\chapter*{\1}", t)
    t = re.sub(r"\\DefTblrTemplate\{[^}]*\}\{[^}]*\}\{[^}]*\}\n?", "", t)
    t = re.sub(r"\\begin\{longtblr\}\[.*?\]\{.*?\n\s*\}\s*\n", "\\\\begin{longtable}{lll}\n", t, flags=re.S)
    t = re.sub(r"\n\s*& & \\\\[^\n]*\n\\end\{longtblr\}", "\n\\\\end{longtable}", t)
    t = t.replace("\\end{longtblr}", "\\end{longtable}")
    (STAGE / name).write_text(t)

# document body, from the preface to the end, without TOC, notation/glossary tables and bibliography commands
main = (BOOK / "main.tex").read_text()
body = main[main.index("\\input{preface}"):main.index("\\end{document}")]
keep = []
for line in body.splitlines():
    s = line.strip()
    if s.startswith("%") or not s:
        continue
    if any(s.startswith(x) for x in ("\\tableofcontents", "\\setcounter{tocdepth}", "\\bibliographystyle", "\\bibliography{",
                                     )):
        continue
    keep.append(line)
(STAGE / "book_web.tex").write_text(
    "\\input{../lx_preamble}\n\\begin{document}\n" + "\n".join(keep) + "\n\\end{document}\n")
print("staged", sum(1 for _ in STAGE.rglob("*.tex")), "tex files")

# preamble: base + every colour defined in the print preamble
cols = []
for f in ("main.tex", "command.tex"):
    for line in (BOOK / f).read_text().splitlines():
        t = line.strip()
        if t.startswith(("\\definecolor", "\\colorlet", "\\newcolumntype")) and not t.startswith("%"):
            cols.append(t.split("%")[0])
base = (Path(__file__).resolve().parent / "lx_preamble_base.tex").read_text()
(Path(__file__).resolve().parent / "lx_preamble.tex").write_text(base + "\n".join(dict.fromkeys(cols)) + "\n")
print("colours", len(cols))
