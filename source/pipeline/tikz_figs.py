"""Compile the book's inline TikZ figures standalone (print preamble) and crop them, for the web fallback images."""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1] / "Spt-Intell-share-paper"
OUT = HERE / "build"
pre = (BOOK / "main.tex").read_text()
pre = pre[:pre.index("\\begin{document}")]


def extract_world_modeling():
    s = (BOOK / "part_3/section_8/p3_sec8_6.tex").read_text()
    i = s.index("\\resizebox{\\linewidth}{!}{%", s.index("\\begin{figure*}[!t]"))
    j = s.index("\\end{tikzpicture}", i) + len("\\end{tikzpicture}")
    k = s.index("}", j) + 1
    return s[i:k]


JOBS = {
    "si_milestones_tikz": "\\input{figures/part1/si_milestones_tikz}",
    "world_modeling_tikz": extract_world_modeling(),
}
for name, body in JOBS.items():
    tex = BOOK / f"_web_{name}.tex"
    # seed the job's .aux with the print build's labels and citation numbers so \\cite and \\eqref print as in the book
    (OUT / f"_web_{name}.aux").write_text((BOOK / "main.aux").read_text(errors="replace"))
    tex.write_text(pre + "\\begin{document}\\pagestyle{empty}\\thispagestyle{empty}\\noindent\n" + body + "\n\\end{document}\n")
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", str(OUT), tex.name], cwd=BOOK,
                       capture_output=True, text=True)
    tex.unlink()
    pdf = OUT / f"_web_{name}.pdf"
    subprocess.run(["pdfcrop", "--margins", "4", str(pdf), str(OUT / f"{name}.pdf")], capture_output=True)
    for ext in (".aux", ".log", ".out", ".pdf"):
        (OUT / f"_web_{name}{ext}").unlink(missing_ok=True)
    print(name, "ok" if (OUT / f"{name}.pdf").exists() else "FAILED")
