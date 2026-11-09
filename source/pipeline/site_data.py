"""Structured data from the book source for the non-reader pages: authors, institutions, eras (Table 1.1),
definition, operators, BibTeX."""
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parents[2] / "Spt-Intell-share-paper"


def authors():
    m = (BOOK / "main.tex").read_text()
    block = m[m.index("\\author{"):m.index("% Uncomment to override", m.index("\\author{"))]
    names = re.findall(r"\\textbf\{([^}]*)\}\$\^\{([^}]*)\}\$", block)
    affs = dict((int(n), a.strip().rstrip(",")) for n, a in re.findall(r"\$\^\{(\d+)\}\$([^$\\\n]+)", block))
    out = []
    for name, sup in names:
        nums = [int(x) for x in re.findall(r"\d+", sup)]
        out.append(dict(name=name, affs=[affs[n] for n in nums if n in affs], lead="*" in sup, first="\\dagger" in sup))
    return out, [affs[k] for k in sorted(affs)]


def eras():
    t = (BOOK / "part_1/section_1/p1_sec1.tex").read_text()
    i = t.index("\\label{tab:p1_s1_2_eras}") if "\\label{tab:p1_s1_2_eras}" in t else t.index("tab:p1_s1_2_eras")
    tab = t[t.rindex("\\begin{table", 0, i):t.index("\\end{table", i)]
    head = re.search(r"&\s*\\textbf\{I\.\\ (.*?)\\\\\s*\n", tab, re.S).group(0)
    cols = re.findall(r"\\textbf\{([IV]+)\.\\ ([^}]*)\}\s*\\newline\s*\{\\scriptsize\s*([^}]*)\}", head)
    rows = re.findall(r"^\\textbf\{([^}]*)\}\s*&(.*?)\\\\\s*$", tab, re.M)
    clean = lambda s: re.sub(r"\s+", " ", re.sub(r"\\[a-z]+\{([^}]*)\}", r"\1", s.replace("--", "–"))).strip()
    out = []
    for k, (roman, name, years) in enumerate(cols):
        out.append(dict(roman=roman, name=clean(name).capitalize(), years=clean(years),
                        rows=[(clean(r[0]), clean(r[1].split("&")[k])) for r in rows]))
    return out


def definition():
    t = (BOOK / "part_1/section_2/p1_sec2.tex").read_text()
    return re.sub(r"\s+", " ", re.search(r"\\textbf\{Definition \(Spatial Intelligence\)\.\}\s*\\emph\{(.*?)\}\s*\n", t, re.S).group(1))


OPERATORS = [
    dict(id="perc", name="Perception", sigsvg="f<tspan font-size='9' dy='4'>perc</tspan><tspan dy='-4'> : 𝒪 → ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan>",
         sightml="<i>f</i><sub>perc</sub> : 𝒪 → ℛ<sub>𝒮</sub>",
         desc="Extracts spatial structure from multimodal sensory inputs: recognizing objects and scene elements, estimating distances, identifying spatial layouts, and localizing entities within an environment."),
    dict(id="reason", name="Reasoning & planning", sigsvg="f<tspan font-size='9' dy='4'>reason</tspan><tspan dy='-4'> : ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan><tspan dy='-4'> → ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan>",
         sightml="<i>f</i><sub>reason</sub> : ℛ<sub>𝒮</sub> → ℛ<sub>𝒮</sub>",
         desc="Elaborates the current world state by inferring relations and constraints already implicit in it: trajectory and path planning, occlusion reasoning, spatial causality, relational and commonsense inference."),
    dict(id="pred", name="Prediction", sigsvg="f<tspan font-size='9' dy='4'>pred</tspan><tspan dy='-4'> : ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan><tspan dy='-4'> × 𝒜 → ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan>",
         sightml="<i>f</i><sub>pred</sub> : ℛ<sub>𝒮</sub> × 𝒜 → ℛ<sub>𝒮</sub>",
         desc="Advances the state in time: forecasts future spatial states consistent with physical laws and causal structure, and generates spatially aware images, videos, 3D or 4D scenes and motion."),
    dict(id="act", name="Embodied action", sigsvg="f<tspan font-size='9' dy='4'>act</tspan><tspan dy='-4'> : ℛ</tspan><tspan font-size='9' dy='4'>𝒮</tspan><tspan dy='-4'> → 𝒜</tspan>",
         sightml="<i>f</i><sub>act</sub> : ℛ<sub>𝒮</sub> → 𝒜",
         desc="Reads the representation to act on the environment while pursuing goals: pose adjustment, navigation, grasping and manipulation, aligned with task objectives, human intent and social context."),
]

BIBTEX = """@book{wu2026spatial,
  title     = {Spatial Intelligence: Foundations, Architectures, Methodologies,
               Applications and Challenges},
  author    = {AUTHORS},
  year      = {2026},
  url       = {https://spatial-agi.github.io}
}"""


def bibtex(auth):
    names = []
    for a in auth:
        parts = a["name"].replace("(Bryan) ", "").split()
        names.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
    lines, cur = [], ""
    for n in names:
        piece = (" and " if cur else "") + n
        if len(cur) + len(piece) > 62:
            lines.append(cur + " and")
            cur = n
        else:
            cur += piece
    lines.append(cur)
    return BIBTEX.replace("AUTHORS", ("\n" + " " * 15).join(lines))


if __name__ == "__main__":
    a, i = authors()
    print(len(a), "authors", len(i), "institutions"); print(a[:2], a[-1]); print(i)
    for e in eras(): print(e["roman"], e["name"], e["years"], len(e["rows"]), e["rows"][0])
    print(definition())


def contributions():
    """Parse part_6/author_contribution_list.tex -> [{names:[...], aff, items:[{tex, labels}], advisory}]"""
    t = (BOOK / "part_6/author_contribution_list.tex").read_text()
    body = t[t.index("\\begin{itemize}"):]
    out = []
    for block in re.split(r"\n    \\item ", body)[1:]:
        head, _, rest = block.partition("\n")
        m = re.match(r"\\textbf\{([^}]*)\},\s*([^:]*?):\s*(.*)$", head.strip())
        if not m:
            m = re.match(r"\\textbf\{([^}]*)\}:\s*()(.*)$", head.strip())
        if not m:
            continue
        names = [n.strip() for n in re.split(r"\s+and\s+", m.group(1))]
        items = []
        for line in re.findall(r"^\s{12}\\item (.*)$", rest, re.M):
            items.append(dict(tex=line.strip(), labels=re.findall(r"\\ref\{([^}]*)\}", line)))
        adv = "Reviewing" in m.group(3)
        out.append(dict(names=names, aff=m.group(2).strip(), items=items, advisory=adv, note=m.group(3).strip()))
    return out


def detex(s, num):
    """Render an item line: \\ref{x} -> number, ~ -> space, \\& -> &."""
    s = re.sub(r"\\ref\{([^}]*)\}", lambda m: num(m.group(1)), s)
    s = s.replace("~", " ").replace("\\&", "&").replace("--", "–")
    s = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", s)
    return s
