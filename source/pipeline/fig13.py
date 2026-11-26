"""Figure 1.3 drawn natively: the print TikZ (figures/part1/si_milestones_tikz.tex, itself generated from the work list)
is parsed and redrawn as SVG in TeX points, so every band, tick, leader and label sits where it sits in the PDF.

Each work is a citation link (the reader's reference popover applies); interactivity lives in src/js/nfig.js (fig13).
"""
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1] / "Spt-Intell-share-paper"
TIKZ = BOOK / "figures/part1/si_milestones_tikz.tex"
CM = 72.27 / 2.54                       # TeX pt per cm: the SVG user unit is the TeX point
SIZES = {"tiny": 6.0, "scriptsize": 8.0, "footnotesize": 10.0}     # 12pt book class
LABEL = 6.8
NUM = r"(-?[\d.]+)"


def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(s, quote=True)


def p(v):
    return float(v) * CM


def rgb(r, g, b):
    return "#%02X%02X%02X" % (round(r), round(g), round(b))


def tex_text(s):
    """Label TeX -> SVG tspans (escaped). Handles en dashes, \\& and the one math label ($\\pi_0$)."""
    out = []
    for part in re.split(r"(\$[^$]*\$)", s):
        if part.startswith("$"):
            m = re.fullmatch(r"\$\\pi_(\w)\$", part)
            out.append(f'<tspan class="m">𝜋</tspan><tspan class="m" font-size="{n(LABEL * .72)}" dy="1.4">{m.group(1)}</tspan><tspan dy="-1.4"></tspan>'
                       if m else esc(part.strip("$")))
        else:
            out.append(esc(part.replace("--", "–").replace(r"\&", "&").replace("~", " ")))
    return "".join(out)


def parse(src):
    col = {k: rgb(*map(int, v.split(","))) for k, v in re.findall(r"\\definecolor\{(\w+)\}\{RGB\}\{([\d,]+)\}", src)}
    mix = lambda c, t: rgb(*[int(c[i:i + 2], 16) * t + 255 * (1 - t) for i in (1, 3, 5)])
    F = dict(col=col, bands=[], eras=[], ticks=[], breaks=[], fields=[], items=[], axis=None)
    cur, pend = None, {}
    for ln in src.splitlines():
        ln = ln.strip()
        if m := re.match(rf"\\fill\[msband\] \({NUM},{NUM}\) rectangle \({NUM},{NUM}\);", ln):
            F["bands"].append(tuple(map(p, m.groups())))
        elif m := re.match(rf"\\node\[font=\\footnotesize\\scshape, text=msaccent, anchor=north west\] at \({NUM},{NUM}\) \{{(\w+)\}};", ln):
            F["eras"].append(dict(x=p(m[1]), y=p(m[2]), roman=m[3]))
        elif m := re.match(rf"\\node\[font=\\tiny, text=msgrey, anchor=east\] at \({NUM},{NUM}\) \{{(\d+)\}};", ln):
            F["ticks"].append(dict(x=p(m[1]), y=p(m[2]), year=int(m[3])))
        elif m := re.match(rf"\\draw\[msgrey, line width=0\.3pt\] \({NUM},{NUM}\) -- \({NUM},{NUM}\);", ln):
            F.setdefault("tickmarks", []).append(tuple(map(p, m.groups())))
        elif m := re.match(rf"\\draw\[msink, line width=0\.5pt, -\{{Stealth\[length=([\d.]+)mm\]\}}\] \({NUM},{NUM}\) -- \({NUM},{NUM}\);", ln):
            F["axis"] = dict(head=float(m[1]) / 25.4 * 72.27, pts=tuple(map(p, m.groups()[1:])))
        elif m := re.match(rf"\\draw\[msgrey, line width=0\.35pt\] \({NUM},{NUM}\) -- \({NUM},{NUM}\) \({NUM},{NUM}\) -- \({NUM},{NUM}\);", ln):
            v = list(map(p, m.groups()))
            F["breaks"].append(v)
        elif m := re.match(rf"\\node\[font=\\scriptsize\\bfseries, text=(\w+), anchor=south west, align=left\] at \({NUM},{NUM}\) \{{(.*)\}};", ln):
            cur = dict(key=m[1], color=col[m[1]], x=p(m[2]), y=p(m[3]), lines=[l.replace(r"\&", "&").strip() for l in m[4].split(r"\\")])
            F["fields"].append(cur)
        elif m := re.match(rf"\\draw\[(\w+)!(\d+), line width=0\.4pt\] \({NUM},{NUM}\) -- \({NUM},{NUM}\);", ln):
            cur.update(line=mix(col[m[1]], int(m[2]) / 100), lx=p(m[3]), ly0=p(m[4]), ly1=p(m[6]))
        elif m := re.match(rf"\\fill\[(\w+)\] \({NUM},{NUM}\) circle \(([\d.]+)pt\);", ln):
            pend = dict(field=cur["key"], color=col[m[1]], cx=p(m[2]), cy=p(m[3]), r=float(m[4]), leader=None)
        elif m := re.match(rf"\\draw\[msgrey, line width=0\.25pt\] \({NUM},{NUM}\) -- \({NUM},{NUM}\);", ln):
            pend["leader"] = tuple(map(p, m.groups()))
        elif m := re.match(rf"\\node\[font=\\fontsize\{{[\d.]+\}}\{{[\d.]+\}}\\selectfont, text=msink, anchor=west, inner sep=([\d.]+)pt\] at \({NUM},{NUM}\) \{{(.*)\}};", ln):
            body = m[4]
            keys = re.findall(r"\\cite\{([^}]*)\}", body)
            text = re.sub(r"~?\\cite\{[^}]*\}", "", body).strip()
            pend.update(lx=p(m[2]) + float(m[1]), ly=p(m[3]), text=text, keys=[k.strip() for ks in keys for k in ks.split(",")])
            F["items"].append(pend)
            pend = {}
    return F


def year_of(y, ticks):
    """Invert the piecewise-linear time axis (compressed before 1980, expanded after 2012) at a marker's y."""
    t = sorted(ticks, key=lambda d: d["y"])
    for a, b in zip(t, t[1:]):
        if a["y"] - 1e-6 <= y <= b["y"] + 1e-6:
            return math.floor(a["year"] + (y - a["y"]) / (b["y"] - a["y"]) * (b["year"] - a["year"]) + 0.02)
    a, b = (t[-2], t[-1]) if y > t[-1]["y"] else (t[0], t[1])
    return math.floor(a["year"] + (y - a["y"]) / (b["y"] - a["y"]) * (b["year"] - a["year"]) + 0.02)


def fig13(refs, eras, table_url=""):
    F = parse(TIKZ.read_text())
    C = F["col"]
    ink, grey, band, accent = C["msink"], C["msgrey"], C["msband"], C["msaccent"]
    ax = F["axis"]
    x_axis, y_top, _, y_end = ax["pts"]
    y_plot_end = max(f["ly1"] for f in F["fields"])
    W = max(b[2] for b in F["bands"])
    top = min(f["y"] for f in F["fields"]) - 2.67 - 9.5 - 8.0 - 3
    H = y_end + 3 - top
    s = []
    # era bands (shaded I, III, V as printed) and a hover overlay for every era
    for x0, y0, x1, y1 in F["bands"]:
        s.append(f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{band}"/>')
    eras_d = {e["roman"]: e for e in eras}
    spans = []
    for i, e in enumerate(F["eras"]):
        y0 = e["y"] - 0.04 * CM
        y1 = F["eras"][i + 1]["y"] - 0.04 * CM if i + 1 < len(F["eras"]) else y_plot_end
        spans.append((e["roman"], y0, y1))
        s.append(f'<rect class="eraband" data-era="{e["roman"]}" x="0" y="{n(y0)}" width="{n(W)}" height="{n(y1 - y0)}" fill="{accent}"/>')
    # time axis: ticks, year labels, break marks, arrow
    for x0, y0, x1, y1 in F.get("tickmarks", []):
        s.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{grey}" stroke-width="0.3"/>')
    for t in F["ticks"]:
        s.append(f'<text class="yr" x="{n(t["x"] - 2)}" y="{n(t["y"] + 2.05)}" font-size="{n(SIZES["tiny"])}" fill="{grey}" text-anchor="end">{t["year"]}</text>')
    hl = ax["head"]
    s.append(f'<line x1="{n(x_axis)}" y1="{n(y_top)}" x2="{n(x_axis)}" y2="{n(y_end - hl * .6)}" stroke="{ink}" stroke-width="0.5"/>'
             f'<path d="M{n(x_axis)} {n(y_end)} L{n(x_axis - hl * .42)} {n(y_end - hl)} L{n(x_axis)} {n(y_end - hl * .62)} L{n(x_axis + hl * .42)} {n(y_end - hl)} Z" fill="{ink}"/>')
    for v in F["breaks"]:
        s.append(f'<path d="M{n(v[0])} {n(v[1])} L{n(v[2])} {n(v[3])} M{n(v[4])} {n(v[5])} L{n(v[6])} {n(v[7])}" stroke="{grey}" stroke-width="0.35" fill="none"/>')
    # field columns
    for f in F["fields"]:
        s.append(f'<line class="fl" data-f="{f["key"]}" style="--c:{f["color"]}" x1="{n(f["lx"])}" y1="{n(f["ly0"])}" x2="{n(f["lx"])}" y2="{n(f["ly1"])}" stroke="{f["line"]}" stroke-width="0.4"/>')
    # hover guide (year line + pill on the axis) and the label highlight, drawn under the works
    s.append(f'<g class="yguide" aria-hidden="true"><line x1="{n(x_axis)}" x2="{n(W)}" y1="0" y2="0" stroke-width="0.5" stroke-dasharray="2 2"/></g>'
             f'<rect class="hl" x="0" y="0" width="0" height="0" rx="2" aria-hidden="true"/>')
    # works: marker, leader, label with its citation number (one link per work)
    count, items = {}, []
    span_of = lambda y: next((r for r, a, b in spans if a - 1e-6 <= y < b), spans[-1][0])
    y_min, y_max = min(i["cy"] for i in F["items"]), max(i["cy"] for i in F["items"])
    for i in F["items"]:
        nums = [refs[k]["num"] for k in i["keys"] if k in refs]
        yr = year_of(i["cy"], F["ticks"])
        era = span_of(i["cy"])
        count[i["field"]] = count.get(i["field"], 0) + 1
        k0 = i["keys"][0] if i["keys"] else ""
        d = round(900 * (i["cy"] - y_min) / max(1, y_max - y_min))
        cite = "".join(f'{"," if j else ""}<tspan class="cn">{nm}</tspan>' for j, nm in enumerate(nums))
        lead = ""
        if i["leader"]:
            x0, y0, x1, y1 = i["leader"]
            lead = f'<line class="ld" x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{grey}" stroke-width="0.25"/>'
        label = (f'<a class="cite" href="/read/references/#ref-{nums[0] if nums else ""}" data-k="{esc(k0)}">'
                 f'<text class="lb" x="{n(i["lx"])}" y="{n(i["ly"] + LABEL * .24)}" font-size="{LABEL}" fill="{ink}">{tex_text(i["text"])} [{cite}]</text></a>')
        items.append(f'<g class="ms" data-f="{i["field"]}" data-era="{era}" data-y="{yr}" data-cy="{n(i["cy"])}" style="--c:{i["color"]};--d:{d}ms">'
                     f'{lead}<circle class="dot" cx="{n(i["cx"])}" cy="{n(i["cy"])}" r="{n(i["r"])}" fill="{i["color"]}"/>{label}</g>')
    s.append(f'<g class="works">{"".join(items)}</g>')
    # field headers (two lines, bold, field colour) act as toggles
    for f in F["fields"]:
        bx, by = f["x"] + 2.67, f["y"] - 2.67 - 1.8
        lines = f["lines"]
        sp = "".join(f'<tspan x="{n(bx)}" y="{n(by - (len(lines) - 1 - j) * 9.5)}">{esc(l)}</tspan>' for j, l in enumerate(lines))
        w = 66
        s.append(f'<g class="fh" data-f="{f["key"]}" role="button" tabindex="0" aria-pressed="false" aria-label="Highlight {esc(" ".join(lines))} ({count.get(f["key"], 0)} works)" style="--c:{f["color"]}">'
                 f'<rect class="hit" x="{n(f["x"])}" y="{n(by - 9.5 * len(lines) - 1)}" width="{w}" height="{n(9.5 * len(lines) + 6)}" fill="transparent"/>'
                 f'<text font-size="{SIZES["scriptsize"]}" font-weight="700" fill="{f["color"]}">{sp}<tspan class="fc" dx="3" font-weight="400" font-size="6.6">{count.get(f["key"], 0)}</tspan></text></g>')
    # era numerals with a hit strip along the axis gutter
    for (roman, y0, y1), e in zip(spans, F["eras"]):
        s.append(f'<g class="eh" data-era="{roman}" role="button" tabindex="0" aria-pressed="false" aria-label="Era {roman}: {esc(eras_d.get(roman, {}).get("name", ""))}">'
                 f'<rect class="hit" x="0" y="{n(y0)}" width="{n(x_axis - 0.5)}" height="{n(y1 - y0)}" fill="transparent"/>'
                 f'<text x="{n(e["x"] + 3.33)}" y="{n(e["y"] + 3.33 + 6.9)}" font-size="{SIZES["footnotesize"]}" fill="{accent}">{roman}</text></g>')
    # the hovered work's year on the axis, above everything else (it may cover an era numeral for a moment)
    s.append(f'<g class="yguide ypill" aria-hidden="true"><rect x="{n(x_axis - 27)}" y="-5" width="25" height="10" rx="5"/>'
             f'<text x="{n(x_axis - 14.5)}" y="2.3" font-size="6.4" text-anchor="middle" fill="#fff" font-weight="700"></text></g>')
    ecount = {}
    for i in F["items"]:
        r = span_of(i["cy"]); ecount[r] = ecount.get(r, 0) + 1
    info = {"eras": {r: dict(name=eras_d.get(r, {}).get("name", ""), years=eras_d.get(r, {}).get("years", ""), n=ecount.get(r, 0),
                             rows=[x for x in eras_d.get(r, {}).get("rows", []) if x[0] in ("Space treated as", "Left unsolved")])
                     for r, _, _ in spans},
            "table": table_url}
    svg = (f'<svg class="nf-svg" viewBox="0 {n(top)} {n(W)} {n(H)}" role="group" aria-label="Figure 1.3: representative works in spatial intelligence by field and year, set against the five eras">'
           f'{"".join(s)}</svg>')
    return (f'<div class="nf nf-13" data-nf="13" data-pagefind-ignore="all">{svg}<div class="nf-card" hidden></div>'
            f'<script type="application/json" class="nf-info">{json.dumps(info, ensure_ascii=False)}</script></div>')


if __name__ == "__main__":
    refs = json.loads((HERE / "data/refs.json").read_text())
    import site_data as SD
    out = fig13(refs, SD.eras(), "/read/1.2/")
    print(len(out))
