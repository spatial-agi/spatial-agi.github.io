"""Explore datasets derived from the book itself: milestones (Fig. 1.3 source), dataset/benchmark atlas (the book's
comparison tables), figure gallery, glossary and notation."""
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parents[2] / "Spt-Intell-share-paper"


def _t(el):
    return " ".join((el.text_content() if el is not None else "").split())


# ------------------------------------------------------------------ milestones (Figure 1.3)
FIELD_NAMES = {"mscog": "Cognition & symbolic AI", "msmap": "Robotics & mapping", "msgeo": "Geometry & 3D vision",
               "msvis": "Learned perception", "msfm": "Foundation & multimodal", "msag": "Agents & world models"}
FIELD_COLORS = {"mscog": "#8C6D46", "msmap": "#2E7D6B", "msgeo": "#46628C", "msvis": "#7A4E8C", "msfm": "#B9852F", "msag": "#1F4E9A"}


def milestones(refs):
    src = (BOOK / "figures/part1/si_milestones_tikz.tex").read_text()
    ticks = sorted((float(y), int(yr)) for y, yr in re.findall(r"at \(0\.910,([\d.]+)\) \{(\d{4})\}", src))

    def year_of(y):
        for (y0, a), (y1, b) in zip(ticks, ticks[1:]):
            if y0 <= y <= y1:
                return round(a + (b - a) * (y - y0) / (y1 - y0))
        (y0, a), (y1, b) = (ticks[0], ticks[1]) if y < ticks[0][0] else (ticks[-2], ticks[-1])
        return round(a + (b - a) * (y - y0) / (y1 - y0))

    out, lines = [], src.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"\\fill\[(ms[a-z]+)\] \(([\d.]+),([\d.]+)\) circle", line)
        if not m or m.group(1) not in FIELD_NAMES:
            continue
        for nxt in lines[i + 1:i + 3]:
            n = re.search(r"\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)~\\cite\{([^}]*)\}\}\s*;", nxt)
            if n:
                label = n.group(1).replace("\\&", "&").replace("$\\cdot$", "·").replace("--", "–")
                label = re.sub(r"\\[a-zA-Z]+\s*", "", label).replace("{", "").replace("}", "")
                keys = [k.strip() for k in n.group(2).split(",")]
                r = refs.get(keys[0], {})
                out.append(dict(label=label, year=year_of(float(m.group(3))), field=FIELD_NAMES[m.group(1)],
                                color=FIELD_COLORS[m.group(1)], keys=keys, num=r.get("num"), title=r.get("title"),
                                authors=(r.get("authors") or [])[:4], venue=r.get("venue")))
                break
    return out


# ------------------------------------------------------------------ dataset & benchmark atlas
DATA_WORDS = re.compile(r"dataset|benchmark|corpor|data sources|evaluation resources", re.I)
NOT_DATA = re.compile(r"reported performance|^Reported|results on|results|error \(|AUC|accuracy|mIoU|Acc@|R@1|cIoU|trajectory error|top-1|test error|recall at|"
                      r"automatic checking|comparison of satellite|five control axes|five subfields|seven spatial-generation", re.I)
NAME_HEAD = re.compile(r"^(dataset|benchmark|corpus|name|data source|resource)s?\b", re.I)


def datasets(pages, xref, chapter_of_page):
    rows_out, tables_out = [], []
    for slug, p in pages.items():
        for fig in p["el"].xpath('.//figure[contains(@class,"ltx_table")]'):
            fid = fig.get("id")
            x = xref.get(fid)
            if not x or not DATA_WORDS.search(x.get("full", "")) or NOT_DATA.search(x.get("full", "")):
                continue
            trs = fig.xpath('.//table[contains(@class,"ltx_tabular")]//tr')
            if len(trs) < 3:
                continue
            ncols = max(sum(int(c.get("colspan", 1)) for c in tr.xpath('./td|./th')) for tr in trs)

            def is_head(tr):
                cs = [c for c in tr.xpath('./td|./th') if _t(c)]
                return cs and all(c.tag == "th" or c.xpath('.//*[contains(@class,"ltx_font_bold")]') or "ltx_font_bold" in (c.get("class") or "") for c in cs)

            head_rows = []
            for tr in trs:
                if is_head(tr):
                    head_rows.append(tr)
                else:
                    break
            if not head_rows:
                continue
            header = [""] * ncols
            occupied = {}
            for r, tr in enumerate(head_rows):
                col = 0
                for c in tr.xpath('./td|./th'):
                    while occupied.get((r, col)):
                        col += 1
                    cs, rs = int(c.get("colspan", 1)), int(c.get("rowspan", 1))
                    for dr in range(rs):
                        for dc in range(cs):
                            occupied[(r + dr, col + dc)] = True
                    if _t(c):
                        for j in range(col, min(col + cs, ncols)):
                            header[j] = (header[j] + " " + _t(c)).strip()
                    col += cs
            header = [h or f"Column {i + 1}" for i, h in enumerate(header)]
            group = None
            recs = []
            for tr in trs[len(head_rows):]:
                cells = tr.xpath('./td|./th')
                txts = [_t(c) for c in cells]
                if len(cells) == 1 or (len(cells) < ncols and int(cells[0].get("colspan", 1)) > 1):
                    group = txts[0].lstrip("•· ").strip()
                    continue
                if len(cells) != ncols or not txts[0]:
                    continue
                ni = next((i for i, h in enumerate(header) if NAME_HEAD.search(h)), 0)
                keys = [a.get("data-k") for a in cells[ni].xpath('.//a[@class="cite"]')]
                name = re.sub(r"\s*\[[\d,\s]+\]\s*$", "", txts[ni]).strip()
                if not name or len(name) > 90:
                    continue
                attrs = [(header[i], txts[i]) for i in range(ncols) if i != ni and txts[i] and txts[i] not in ("–", "-")]
                recs.append(dict(name=name, keys=keys, group=group, attrs=attrs, table=x["label"], url=x["url"],
                                 chapter=chapter_of_page(slug), section=p["num"] if p["kind"] == "section" else None))
            if recs:
                rows_out += recs
                tables_out.append(dict(label=x["label"], caption=x["full"], url=x["url"], n=len(recs),
                                       chapter=chapter_of_page(slug), header=header))
    return rows_out, tables_out


# ------------------------------------------------------------------ glossary & notation
def term_tables(pages):
    out = {}
    for slug in ("glossary", "notation"):
        p = pages.get(slug)
        if not p:
            continue
        items = []
        for tr in p["el"].xpath('.//table[contains(@class,"ltx_tabular")]//tr')[1:]:
            tds = tr.xpath('./td')
            if len(tds) != 3:
                continue
            import html as _h
            import lxml.html as LH
            inner = lambda el: (_h.escape(el.text or "") + "".join(LH.tostring(c, encoding="unicode", method="html") for c in el)).strip()
            refa = tds[2].xpath('.//a')
            items.append(dict(term_html=inner(tds[0]), term=_t(tds[0]),
                              desc_html=inner(tds[1]), desc=_t(tds[1]),
                              ref=_t(tds[2]), url=refa[0].get("href") if refa else None))
        out[slug] = items
    return out
