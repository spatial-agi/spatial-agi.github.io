"""Natively drawn web figures: Fig. 1.1 and Fig. 2.1 as SVG in the print figure's own point coordinates
(ports of figgen/fig1_1.py and figgen/fig2_1.py), and the part openers as artwork + live text.

Text is real SVG text (selectable, searchable by the browser); photos and point clouds are the raster pieces
exported by figassets.py. Interactivity lives in src/js/nfig.js; each module carries data-k for it.
"""
import html
import json
import math
from pathlib import Path

BLUE, BLUE_FILL, BLUE_MID = "#3646F0", "#E9EBFB", "#AEB6F7"
INK, GREY, LINE, FAINT, GREEN = "#2A3242", "#6B7480", "#A8B0B8", "#D5DAE0", "#2E9E5B"
IMG = "/assets/img/figs/"
META = json.loads((Path(__file__).resolve().parents[1] / "src/img/figs/meta.json").read_text())
FS = 0.9           # Inter sets wider than the print font (Aptos); scale so text keeps the print layout


def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- primitives (matplotlib -> SVG)
def T(x, y, s, size=8, color=INK, w=None, ha="left", va="c", italic=False, ls=1.0, cls=""):
    """Text; va='c' centres the block on y as matplotlib does, va='t' hangs it from y."""
    lines = s.split("\n")
    lh = size * 1.2 * ls
    y0 = y - (len(lines) - 1) * lh / 2 if va == "c" else y + size * 0.42
    anchor = {"left": "start", "center": "middle", "right": "end"}[ha]
    a = f'font-size="{n(size * FS)}" fill="{color}" text-anchor="{anchor}"'
    a += f' font-weight="{w}"' if w else ""
    a += ' font-style="italic"' if italic else ""
    base = lambda yy: n(yy + size * 0.34)
    if len(lines) == 1:
        return f'<text class="t {cls}" x="{n(x)}" y="{base(y0)}" {a}>{esc(s)}</text>'
    spans = "".join(f'<tspan x="{n(x)}" y="{base(y0 + i * lh)}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    return f'<text class="t {cls}" {a}>{spans}</text>'


def M(x, y, src, size=8, color=BLUE, ha="center"):
    """Math in Pagella Math: plain Unicode with _{...} and ^{...} for sub- and superscripts."""
    toks, buf, i = [], "", 0
    while i < len(src):
        if src[i] in "_^" and src[i + 1:i + 2] == "{":
            if buf:
                toks.append((buf, "")); buf = ""
            j = src.index("}", i)
            toks.append((src[i + 2:j], src[i])); i = j + 1
        else:
            buf += src[i]; i += 1
    if buf:
        toks.append((buf, ""))
    small, cur, prev, out = size * 0.7, 0.0, None, []
    for txt, kind in toks:
        target = {"": 0.0, "_": size * 0.3, "^": -size * 0.38}[kind]
        a = f' font-size="{n(small if kind else size)}"'
        if target != cur:
            a += f' dy="{n(target - cur)}"'
        if kind == "_" and prev and prev[1] == "^":
            a += f' dx="{n(-len(prev[0]) * small * 0.62)}"'
        out.append(f"<tspan{a}>{esc(txt)}</tspan>")
        cur, prev = target, (txt, kind)
    anchor = {"left": "start", "center": "middle", "right": "end"}[ha]
    return (f'<text class="m" x="{n(x)}" y="{n(y + size * 0.3)}" fill="{color}" text-anchor="{anchor}">{"".join(out)}</text>')


def R(x, y, w, h, fill="white", stroke=LINE, lw=0.6, r=0, dash=None, cls="", op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    c = f' class="{cls}"' if cls else ""
    rx = f' rx="{n(r)}"' if r else ""
    sw = f' stroke="{stroke}" stroke-width="{n(lw)}"' if stroke != "none" and lw else ' stroke="none"'
    return f'<rect{c} x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{rx} fill="{fill}"{o}{sw}{d}/>'


def C(x, y, r, fill="white", stroke=BLUE, lw=0.7, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<circle{c} cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{n(lw)}"/>'


def L(pts, color=LINE, lw=0.6, dash=None, cls="", fill="none"):
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="{fill}" stroke="{color}" stroke-width="{n(lw)}"{da}/>'


def P(pts, fill="white", stroke=BLUE, lw=0.6, op=None, cls=""):
    o = f' fill-opacity="{op}"' if op is not None else ""
    c = f' class="{cls}"' if cls else ""
    return f'<polygon{c} points="{" ".join(f"{n(a)},{n(b)}" for a, b in pts)}" fill="{fill}"{o} stroke="{stroke}" stroke-width="{n(lw)}" stroke-linejoin="round"/>'


def IM(name, x, y, w=None, h=None, border=None, lw=0.5, ext="webp", cls=""):
    ar = META.get(name, {}).get("ar", 1)
    w = w if w is not None else h * ar
    h = h if h is not None else w / ar
    c = f' class="{cls}"' if cls else ""
    s = f'<image{c} href="{IMG}{name}.{ext}" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" preserveAspectRatio="none"/>'
    if border:
        s += R(x, y, w, h, fill="none", stroke=border, lw=lw)
    return s, (x, y, w, h)


def _head(x0, y0, x1, y1, head, color):
    side = head * 0.9
    th = math.atan2(0.55, 0.9)
    ang = math.atan2(y1 - y0, x1 - x0)
    pts = [(x1, y1)]
    for sgn in (1, -1):
        a = ang + math.pi + sgn * th
        pts.append((x1 + side * math.cos(a), y1 + side * math.sin(a)))
    return P(pts, fill=color, stroke=color, lw=0.3), side * math.cos(th)


def A(x0, y0, x1, y1, color=BLUE, lw=1.0, head=4.2, both=False, dash=None, cls="arr"):
    """Straight arrow with a filled wedge head (matplotlib '-|>' with the same head_length/head_width)."""
    h1, d1 = _head(x0, y0, x1, y1, head, color)
    out = [h1]
    L_ = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L_, (y1 - y0) / L_
    sx, sy, ex, ey = x0, y0, x1 - ux * d1 * 0.8, y1 - uy * d1 * 0.8
    if both:
        h0, d0 = _head(x1, y1, x0, y0, head, color)
        out.append(h0)
        sx, sy = x0 + ux * d0 * 0.8, y0 + uy * d0 * 0.8
    shaft = L([(sx, sy), (ex, ey)], color=color, lw=lw, dash=dash, cls="shaft")
    return f'<g class="{cls}">{shaft}{"".join(out)}</g>'


def curved(p0, p1, rad, shrink, color=BLUE, lw=0.8, head=3.2, cls="arr"):
    """matplotlib arc3 connection (y-down data), trimmed by `shrink` at both ends, head at the end."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, -(y1 - y0)                       # display space has y up
    cx, cy = mx + rad * dy, -(-my - rad * dx)
    bez = lambda t: ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1)
    pts = [bez(k / 80) for k in range(81)]
    keep = [p for p in pts if math.hypot(p[0] - x0, p[1] - y0) >= shrink and math.hypot(p[0] - x1, p[1] - y1) >= shrink]
    h, d = _head(keep[-2][0], keep[-2][1], keep[-1][0], keep[-1][1], head, color)
    return f'<g class="{cls}">{L(keep[:-1], color=color, lw=lw, cls="shaft")}{h}</g>'


def dash(pattern, lw):
    return " ".join(n(v * lw) for v in pattern)


def wave(x, y, w=14, amp=4, color=INK, lw=0.6, k=7, npts=120):
    pts = []
    for i in range(npts):
        t = i / (npts - 1)
        env = math.sin(math.pi * t) ** 0.7
        pts.append((x + t * w, y + amp * env * math.sin(2 * math.pi * k * t)))
    return L(pts, color=color, lw=lw)


def doc(x, y, w=11, h=13, lines=3):
    s = R(x, y, w, h, fill="white", stroke=INK, lw=0.6)
    for k in range(lines):
        s += L([(x + 2.2, y + 3.5 + k * 3), (x + w - 2.2 - (k == lines - 1) * 2.5, y + 3.5 + k * 3)], color=INK, lw=0.5)
    return s


def picture(x, y, w=14, h=11):
    s = R(x, y, w, h, fill="white", stroke=INK, lw=0.6)
    s += P([(x + 1.5, y + h - 1.5), (x + w * 0.4, y + h * 0.4), (x + w * 0.65, y + h * 0.7), (x + w * 0.8, y + h * 0.55),
            (x + w - 1.5, y + h - 1.5)], fill="none", stroke=INK, lw=0.5)
    return s + C(x + w * 0.72, y + h * 0.3, 1.2, fill="none", stroke=INK, lw=0.5)


def mix(t):
    """white -> cobalt at fraction t (the print figure's voxel shading)."""
    b = (0x36, 0x46, 0xF0)
    return "#" + "".join(f"{round(255 * (1 - t) + c * t):02x}" for c in b)


def g(k, body, extra=""):
    return f'<g data-k="{k}"{extra}>{body}</g>'


# ---------------------------------------------------------------- Fig. 2.1
FIG21_INFO = {
    "env": dict(t="Environment <i class='m'>ℰ</i>", b="The physical world the system operates in, from objects and scenes to rooms, buildings, cities and terrain, governed by geometric, physical and causal constraints. Neither party can be defined without the other.", u="/read/2.2/#Ch2.S2.SS1.SSS1", l="2.2.1 Parties"),
    "obs": dict(t="Observations <i class='m'>𝑜<sub>𝑡</sub></i>", b="What the system receives from the environment: images, depth, point clouds, text and sound. Perception turns them into structure.", u="/read/2.2/#Ch2.S2.SS2", l="2.2.2 Formal characterization"),
    "task": dict(t="Task", b="The goal the system is given, here to put the cup on the shelf. It conditions what the system reasons about and how it acts.", u="/read/2.2/#Ch2.S2.SS2", l="2.2.2 Formal characterization"),
    "perc": dict(op="perc"), "reason": dict(op="reason"), "pred": dict(op="pred"), "act": dict(op="act"),
    "rep": dict(t="World-centered spatial representation <i class='m'>ℛ<sub>𝒮</sub></i>", b="The structured world model at the centre of the loop: compositional, generalizable and reusable across tasks. It holds objects, scenes and relations in geometric, topological, symbolic and abstract form, and is updated through interaction, <i class='m'>ℛ<sub>𝑡+1</sub> = Ψ<sub>𝒮</sub>(ℛ<sub>𝑡</sub>, 𝑎<sub>𝑡</sub>, 𝑜<sub>𝑡+1</sub>)</i>.", u="/read/2.2/#Ch2.S2.SS1.SSS2", l="2.2.1 Spatial representation"),
    "actions": dict(t="Actions <i class='m'>𝑎<sub>𝑡</sub></i>", b="Embodied action reads the representation and acts on the environment, whose response is observed in turn. Spatial understanding is grounded in this interaction.", u="/read/2.2/#Ch2.S2.SS1.SSS3", l="2.2.1 Dynamic interaction"),
    "geometric": dict(t="Geometric", b="Metric structure (points, depth, surfaces), here the living room as a point cloud.", u="/read/chapter-4/", l="Chapter 4"),
    "topological": dict(t="Topological", b="Entities and how they connect: shelf, door, person and cup, all related through the table.", u="/read/chapter-4/", l="Chapter 4"),
    "symbolic": dict(t="Symbolic", b="Explicit relations that a planner can query, such as on(cup, table).", u="/read/chapter-4/", l="Chapter 4"),
    "abstract": dict(t="Abstract", b="Learned, latent encodings of the scene, drawn as a grid of feature activations.", u="/read/chapter-5/", l="Chapter 5"),
}
OP_LINK = dict(u="/read/2.2/#Ch2.S2.SS2", l="2.2.2 Formal characterization")


def fig21(operators):
    W, H = 468, 232
    o = []
    # ---- environment
    EX, EW = 2, 92
    e = [R(EX, 2, EW, H - 4, stroke=LINE, lw=0.7, r=4, cls="frame"),
         T(EX + 6, 13, "Environment", 9, w=700), M(EX + 64, 13.5, "ℰ", 9.5, ha="left"),
         T(EX + 6, 30, "geometric · physical ·\ncausal constraints", 7, GREY, ls=1.1)]
    for name, lab, y, h in [("f21-tablecup", "objects & scenes", 40, 38), ("f21-cutaway", "rooms & buildings", 98, 50),
                            ("f21-city", "cities & terrain", 166, 46)]:
        iw = h * META[name]["ar"]
        e.append(IM(name, EX + (EW - iw) / 2, y, h=h, cls="tier")[0])
        e.append(T(EX + EW / 2, y + h + 6.5, lab, 7, INK, ha="center"))
    for y0, y1 in [(87, 96), (156, 165)]:
        e.append(A(EX + EW / 2, y0, EX + EW / 2, y1, color=LINE, lw=0.6, head=3, cls="arr arr-s"))
    o.append(g("env", "".join(e)))

    # ---- AI system frame
    SX = 152
    o.append(g("sys", R(SX, 2, W - SX - 2, H - 4, stroke=BLUE, lw=0.8, r=4, cls="frame") +
               T(SX + 6, 13, "AI system", 9, w=700) + M(SX + 52, 13.5, "𝒮", 9.5, ha="left")))
    PX, PW, RX, RW, QX, QW = 157, 76, 255, 110, 387, 75
    ROW1, ROW2 = (24, 118), (126, 222)

    def func_box(x, w, row, title, formula, caption):
        y0, y1 = row
        return (R(x, y0, w, y1 - y0, stroke=LINE, lw=0.6, r=3, cls="frame") + T(x + 5, y0 + 8, title, 8, w=700) +
                M(x + w / 2, y0 + 19.5, formula, 7.2) + T(x + w / 2, y1 - 7, caption, 7, GREY, ha="center"))

    # perception
    p = [func_box(PX, PW, ROW1, "Perception", "𝑓_{perc}: 𝒪 → ℛ_{𝒮}", "extracts structure")]
    im, (_, iy, iw, ih) = IM("f21-perception", PX + 4, ROW1[0] + 27, w=PW - 8, border=LINE)
    p.append(im)
    sx, sy = iw / 1476, ih / 984
    for i, ((l, t, r, b), lab) in enumerate([((110, 200, 580, 775), "person"), ((660, 13, 947, 560), "shelf"),
                                            ((589, 553, 1104, 847), "table"), ((912, 528, 982, 592), None),
                                            ((1020, 377, 1400, 751), "robot")]):
        if lab == "robot":
            t = 600
        l, r = l - 60, r - 60
        X, Y, Wd, Hd = PX + 4 + l * sx, iy + t * sy, (r - l) * sx, (b - t) * sy
        bb = R(X, Y, Wd, Hd, fill="none", stroke=BLUE, lw=0.55)
        if lab:
            bb += R(X, Y, len(lab) * 3.25 + 3, 7.6, fill=BLUE, stroke="none", lw=0) + T(X + 1.5, Y + 3.9, lab, 6.5, "white")
        p.append(f'<g class="bb" style="--i:{i}">{bb}</g>')
    o.append(g("perc", "".join(p)))

    # action
    gw = 50 * META["f21-gripper"]["ar"]
    o.append(g("act", func_box(PX, PW, ROW2, "Action", "𝑓_{act}: ℛ_{𝒮} → 𝒜", "acts on the world") +
               IM("f21-gripper", PX + (PW - gw) / 2, ROW2[0] + 27, h=50, cls="grip")[0]))

    # representation
    r_ = [R(RX, ROW1[0], RW, ROW2[1] - ROW1[0], fill=BLUE_FILL, stroke=BLUE, lw=0.9, r=3, cls="frame"),
          T(RX + RW / 2, ROW1[0] + 9.5, "World-centered spatial\nrepresentation", 8, w=700, ha="center", ls=1.05),
          M(RX + RW / 2, ROW1[0] + 25, "ℛ_{𝒮}", 9)]
    CW, CH = (RW - 12) / 2, 58
    cells = {"geometric": (RX + 4, 56), "topological": (RX + 8 + CW, 56), "symbolic": (RX + 4, 118), "abstract": (RX + 8 + CW, 118)}
    cell = {}
    for lab, (x, y) in cells.items():
        cell[lab] = [R(x, y, CW, CH, stroke=BLUE_MID, lw=0.5, r=2, cls="cframe"), T(x + 3, y + 6, lab, 7, GREY)]
    x, y = cells["geometric"]
    cell["geometric"].append(IM("f21-geometric", x + 2, y + 12, w=CW - 4, h=CH - 15, ext="png", cls="cloud")[0])
    x, y = cells["topological"]
    nodes = {"shelf": (x + 22, y + 18), "door": (x + 40, y + 27), "table": (x + 25, y + 38), "person": (x + 9, y + 30), "cup": (x + 12, y + 50)}
    for a, b in [("shelf", "table"), ("door", "table"), ("person", "table"), ("cup", "table"), ("shelf", "door")]:
        cell["topological"].append(L([nodes[a], nodes[b]], color=BLUE, lw=0.6, cls="edge"))
    for k, (nx, ny) in nodes.items():
        cell["topological"].append(C(nx, ny, 2.2, fill=BLUE if k == "table" else "white", stroke=BLUE, lw=0.6, cls="node"))
    for k, (dx, dy, ha) in {"shelf": (0, -5.5, "center"), "door": (0, -5.5, "center"), "table": (4, 4.0, "left"),
                            "person": (0, -5.5, "center"), "cup": (4, 0.5, "left")}.items():
        cell["topological"].append(T(nodes[k][0] + dx, nodes[k][1] + dy, k, 6.5, ha=ha))
    x, y = cells["symbolic"]
    for k, s_ in enumerate(["on(cup, table)", "in(table, room)", "near(cup, sofa)"]):
        cell["symbolic"].append(f'<g class="fact" style="--i:{k}">' + R(x + 2.5, y + 13 + k * 14, CW - 5, 10.5, fill=BLUE_FILL, stroke=BLUE_MID, lw=0.4, r=1.5) +
                                T(x + CW / 2, y + 18.4 + k * 14, s_, 6.5, ha="center") + "</g>")
    x, y = cells["abstract"]
    cs, ox, oy = 7.2, x + 10, y + 47
    vox = sorted(enumerate(META["f21-voxels"]), key=lambda kv: (5 + kv[1]["k"] * 0.01 - kv[1]["j"] * 0.001, kv[0]))
    for idx, vx in vox:
        px_ = ox + vx["i"] * cs + vx["k"] * cs * 0.45
        py_ = oy - vx["j"] * cs - vx["k"] * cs * 0.38
        cell["abstract"].append(f'<polygon class="vox" style="--d:{(idx * 37) % 23 / 10:.1f}s" points="{n(px_)},{n(py_)} {n(px_ + cs)},{n(py_)} {n(px_ + cs)},{n(py_ - cs)} {n(px_)},{n(py_ - cs)}" fill="{mix(vx["t"])}" stroke="white" stroke-width="0.4"/>')
    for lab in cells:
        r_.append(g(lab, "".join(cell[lab]), ' class="cell"'))
    r_ += [T(RX + RW / 2, 186, "object · scene · relation", 7, GREY, ha="center"),
           f'<g class="psi">{M(RX + RW / 2, 204, "ℛ^{𝒮}_{𝑡+1} = Ψ_{𝒮}(ℛ^{𝒮}_{𝑡}, 𝑎_{𝑡}, 𝑜_{𝑡+1})", 7.5)}'
           f'{T(RX + RW / 2, 215.5, "updated through interaction", 7, BLUE, ha="center")}</g>']
    o.append(g("rep", "".join(r_)))

    # reasoning: top-down plan, reachability inferred
    fx, fy, fw, fh = QX + 6, ROW1[0] + 27, QW - 12, 52
    rx, ry = fx + 58, fy + 40
    q = [func_box(QX, QW, ROW1, "Reasoning", "𝑓_{reason}: ℛ_{𝒮} → ℛ_{𝒮}", "elaborates the state"),
         R(fx, fy, fw, fh, fill="#F7F8FA", stroke=INK, lw=0.7), R(fx + fw - 1, fy + 10, 2, 12, fill="white", stroke="none", lw=0),
         R(fx + 3, fy + 22, 13, 26, fill="#D9DDE3", stroke=LINE, lw=0.4), R(fx + 24, fy + 1.5, 22, 5, fill="#D9DDE3", stroke=LINE, lw=0.4),
         C(fx + 34, fy + 32, 7.5, fill="#E8DCC8", stroke=LINE, lw=0.4), C(fx + 37, fy + 30, 1.6, fill="white", stroke=INK, lw=0.5),
         C(rx, ry, 3.4, fill="white", stroke=INK, lw=0.7, cls="robot"),
         L([(rx - 3, ry - 2), (fx + 50, fy + 31), (fx + 41.5, fy + 30.5)], color=GREEN, lw=0.9, dash=dash((2, 1.4), 0.9), cls="reach"),
         T(fx + 2, fy + 13, "sofa", 6.5, GREY), T(fx + 35, fy + 12, "shelf", 6.5, GREY, ha="center"),
         T(fx + fw - 2, fy + fh - 4.5, "cup reachable", 6.5, GREEN, ha="right")]
    o.append(g("reason", "".join(q)))

    # prediction: action-conditioned rollout
    fr_w = (QW - 12) / 3
    pr = [func_box(QX, QW, ROW2, "Prediction", "𝑓_{pred}: ℛ_{𝒮} × 𝒜 → ℛ_{𝒮}", "advances the state")]
    for k in range(3):
        fx_ = QX + 4 + k * (fr_w + 2)
        im, (_, _, _, fh_) = IM(f"f21-pred{k}", fx_, ROW2[0] + 31, w=fr_w, border=LINE)
        pr.append(f'<g class="frame-t" style="--i:{k}">{im}{R(fx_, ROW2[0] + 31, fr_w, fh_, fill="none", stroke=BLUE, lw=0.9, cls="tick")}</g>')
        pr.append(M(fx_ + fr_w / 2, ROW2[0] + 31 + fh_ + 7, ["𝑡", "𝑡+1", "𝑡+2"][k], 7))
    pr.append(A(QX + 8, ROW2[0] + 28, QX + QW - 8, ROW2[0] + 28, lw=0.6, head=3, color=BLUE_MID, cls="arr arr-s"))
    o.append(g("pred", "".join(pr)))

    # operator arrows inside the system
    r1, r2 = (ROW1[0] + ROW1[1]) / 2, (ROW2[0] + ROW2[1]) / 2
    o.append(A(PX + PW + 1, r1, RX - 1, r1, cls="arr flow s-pr"))
    o.append(A(RX - 1, r2, PX + PW + 1, r2, cls="arr flow s-ra"))
    o.append(A(RX + RW + 1, r1, QX - 1, r1, both=True, cls="arr flow s-rq"))
    o.append(A(RX + RW + 1, r2, QX - 1, r2, both=True, cls="arr flow s-rp"))

    # environment <-> system
    GX0, GX1 = EX + EW, SX
    ob = [T((GX0 + GX1) / 2, 40, "observations", 7, BLUE, ha="center")]
    tx = GX0 + 2.5
    for name in ("f21-obs-rgb", "f21-obs-depth"):
        ob.append(IM(name, tx, 46, w=10, h=10, border=LINE)[0])
        tx += 11.2
    ob.append(R(tx, 46, 10, 10, stroke=LINE, lw=0.5) + IM("f21-obs-cloud", tx + 0.8, 46.8, w=8.4, h=8.4, ext="png")[0])
    tx += 11.2
    ob.append(R(tx, 46, 10, 10, stroke=LINE, lw=0.5) + "".join(
        L([(tx + 2, 48.8 + k * 2.2), (tx + 8 - (k == 2) * 2.2, 48.8 + k * 2.2)], color=INK, lw=0.45) for k in range(3)))
    tx += 11.2
    pts = [(tx + 1.5 + 7 * t, 51 + 3 * math.sin(math.pi * t) * math.sin(2 * math.pi * 5 * t)) for t in (i / 79 for i in range(80))]
    ob.append(R(tx, 46, 10, 10, stroke=LINE, lw=0.5) + L(pts, color=INK, lw=0.45))
    ob.append(A(GX0 + 1, 62, PX - 1, 62, cls="arr flow s-obs"))
    o.append(g("obs", "".join(ob)))
    o.append(g("task", R(GX0 + 6, 100, GX1 - GX0 - 12, 26, fill="#FBFBFC", stroke=LINE, lw=0.5, r=2, dash=dash((3.7, 1.6), 0.5)) +
               T((GX0 + GX1) / 2, 107, "task", 7, GREY, ha="center") +
               T((GX0 + GX1) / 2, 118, "put the cup\non the shelf", 7, ha="center", ls=1.0) +
               A(GX1 - 6, 113, SX - 1, 113, color=GREY, lw=0.7, head=3.2, dash=dash((2, 1.5), 0.7))))
    o.append(g("actions", T((GX0 + GX1) / 2, 166, "actions", 7, BLUE, ha="center") + A(PX - 1, 174, GX0 + 1, 174, cls="arr flow s-act")))
    o.append('<circle class="token" r="2.6" cx="-10" cy="-10"/>')

    info = {}
    ops = {op["id"]: op for op in operators}
    for k, v in FIG21_INFO.items():
        if "op" in v:
            op = ops[v["op"]]
            info[k] = dict(t=f"{op['name']} <i class='m'>{op['sightml']}</i>", b=op["desc"], **OP_LINK)
        else:
            info[k] = v
    svg = (f'<svg class="nf-svg" viewBox="0 0 {W} {H}" role="img" aria-label="Figure 2.1: spatial intelligence as a closed loop between an AI system and its environment">'
           + "".join(o) + "</svg>")
    return f'<div class="nf nf-21" data-nf="21" data-pagefind-ignore="all">{svg}<div class="nf-card" hidden></div><script type="application/json" class="nf-info">{json.dumps(info, ensure_ascii=False)}</script></div>'


# ---------------------------------------------------------------- Fig. 1.1
FIG11_INFO = {
    "0": dict(t="Paradigm: task-specific → world-centric", b="Traditional systems were each trained for one narrowly defined problem, such as image classification, text generation or speech recognition. Foundation models raise the expectation that AI generalizes across domains, modalities and tasks in open-world settings, which hinges on modelling the world itself.", u="/read/1.1/#Ch1.S1.SS1", l="1.1.1 AI paradigm shift"),
    "1": dict(t="Methodology: static data → experience", b="Progress has followed a data-centric trajectory: ever larger models trained on static corpora, then frozen. Silver and Sutton argue for an “era of experience”, in which agents learn predominantly from acting in the world and observing the consequences.", u="/read/1.1/#Ch1.S1.SS2", l="1.1.2 AI methodological shift"),
    "2": dict(t="Modality: separate 2D → integrated 4D", b="From systems confined to a single modality toward deep integration and any-to-any understanding and generation, and from static 2D images to video, 3D and 4D spatiotemporal structure.", u="/read/1.1/#Ch1.S1.SS3", l="1.1.3 Modality shift"),
    "3": dict(t="Disciplines: siloed → converging", b="Computer vision, NLP, audio processing, robotics, GIS and urban simulation converge toward a unified framework for modelling intelligent agents that are physically embedded in, and interact with, the real world.", u="/read/1.1/#Ch1.S1.SS4", l="1.1.4 Disciplinary convergence"),
    "hub": dict(t="Spatial intelligence", b="Where the four shifts meet: constructing, maintaining and manipulating spatial representations of the world to perceive, reason, predict and act. Chapter 2 makes the definition precise.", u="/read/2.2/", l="2.2 The framework"),
}


def fig11():
    W, H = 468, 250
    LX, FX, FW, TX, TW, HX = 4, 60, 110, 183, 136, 333
    HW = W - HX - 2
    ROWS, RH = [4, 65, 126, 187], 57
    rows = []

    def from_box(y, title, caption):
        return R(FX, y, FW, RH, stroke=LINE, lw=0.6, r=3, cls="frame") + T(FX + 5, y + 8, title, 7.5, w=700) + \
            T(FX + FW / 2, y + RH - 6.5, caption, 7, GREY, ha="center")

    def to_box(y, title, caption, cap_x=None):
        s = R(TX, y, TW, RH, fill=BLUE_FILL, stroke=BLUE, lw=0.7, r=3, cls="frame") + T(TX + 5, y + 8, title, 7.5, w=700)
        if caption:
            s += T(cap_x or TX + TW / 2, y + RH - 6.5, caption, 7, BLUE, ha="center")
        return s

    def arrows(y):
        return (A(FX + FW + 2, y + RH / 2, TX - 2, y + RH / 2, head=4.5, cls="arr flow f1") +
                A(TX + TW + 2, y + RH / 2, HX - 2, y + RH / 2, head=4.5, cls="arr flow f2"))

    def label(y, name, sub):
        return T(LX, y + 18, name, 8.5, w=700) + T(LX, y + 34, sub, 7, BLUE, ls=1.15)

    # 1. paradigm
    y = ROWS[0]
    s = [label(y, "Paradigm", "task-specific →\nworld-centric"), from_box(y, "Task-specific models", "one model per task")]
    for k, tag in enumerate(["cat", "summary", "transcript"]):
        cx = FX + 18 + k * 34
        if k == 2:
            s.append(R(cx - 7.5, y + 15, 15, 12, stroke=INK, lw=0.6) + wave(cx - 5.5, y + 21, w=11, amp=3.5))
        elif k == 1:
            s.append(doc(cx - 5.5, y + 14.5))
        else:
            s.append(picture(cx - 7, y + 15.5))
        s.append(A(cx, y + 28.5, cx, y + 35, lw=0.7, head=3, color=GREY, cls="arr arr-s map"))
        s.append(T(cx, y + 40.5, tag, 7, ha="center"))
    s.append(to_box(y, "World-centric intelligence", None))
    im, (_, _, iw, _) = IM("f11-world", TX + 5, y + 14, h=RH - 18, border=LINE)
    s += [im, T(TX + 5 + iw + 6, y + 30, "one agent\nmany tasks\nopen world", 7, BLUE, ls=1.25), arrows(y)]
    rows.append(s)

    # 2. methodology
    y = ROWS[1]
    s = [label(y, "Methodology", "static data →\nexperience"), from_box(y, "Era of human data", "trained once, then frozen")]
    for k in range(3):
        s.append(doc(FX + 30 + k * 4, y + 14 + k * 3, w=16, h=19, lines=4))
    lx, ly = FX + 72, y + 24
    s.append(f'<path d="M{n(lx + 2.4)},{n(ly)} L{n(lx + 2.4)},{n(ly - 2)} A2.6,2.6 0 0 1 {n(lx + 7.6)},{n(ly - 2)} L{n(lx + 7.6)},{n(ly)}" fill="none" stroke="{INK}" stroke-width="0.8"/>')
    s.append(R(lx, ly, 10, 8, stroke=INK, lw=0.7, r=1) + C(lx + 5, ly + 3.6, 0.9, fill=INK, stroke=INK, lw=0.3))
    s.append(to_box(y, "Era of experience", "learning by acting", cap_x=TX + 46))
    pts = {"act": (TX + 22, y + 21), "observe": (TX + 70, y + 21), "learn": (TX + 46, y + 37)}
    for a, b in [("act", "observe"), ("observe", "learn"), ("learn", "act")]:
        s.append(curved(pts[a], pts[b], -0.2, 13, lw=0.8, head=3.2, cls=f"arr cyc cyc-{a}"))
    for i, (k, (px_, py_)) in enumerate(pts.items()):
        s.append(f'<g class="pill" style="--i:{i}">' + R(px_ - 15.5, py_ - 5.5, 31, 11, stroke=BLUE, lw=0.6, r=5.5) +
                 T(px_, py_ + 0.3, k, 7, ha="center") + "</g>")
    s.append(IM("f11-experience", TX + 94, y + 13, w=TW - 98, border=LINE)[0])
    s.append(arrows(y))
    rows.append(s)

    # 3. modality
    y = ROWS[2]
    s = [label(y, "Modality", "separate 2D →\nintegrated 4D"), from_box(y, "Modality separation", "one modality at a time")]
    fd = dash((3.7, 1.6), 0.6)
    s += [R(FX + 10, y + 18, 22, 13, fill="none", stroke=FAINT, lw=0.6, dash=fd), picture(FX + 14, y + 19),
          R(FX + 38, y + 18, 26, 13, fill="none", stroke=FAINT, lw=0.6, dash=fd), doc(FX + 46, y + 18.5),
          R(FX + 72, y + 18, 22, 13, fill="none", stroke=FAINT, lw=0.6, dash=fd), wave(FX + 75, y + 24.5, w=16, amp=4)]
    s.append(to_box(y, "Modality integration", None))
    s.append(T(TX + 6, y + RH - 6.5, "any-to-any, 3D + time", 7, BLUE))
    ix = TX + 7
    ins = []
    im, (_, _, _, rh) = IM("f11-room", ix, y + 14, w=17, border=LINE)
    s.append(im); ins.append((ix + 17, y + 19.5))
    s.append(doc(ix + 3, y + 27, w=11, h=10)); ins.append((ix + 17, y + 32))
    s.append(wave(ix, y + 44, w=17, amp=3.5)); ins.append((ix + 17, y + 44))
    cx0, cy0, sz = TX + 74, y + 14, 25
    front = [(cx0, cy0 + 8), (cx0 + sz, cy0 + 8), (cx0 + sz, cy0 + 8 + sz), (cx0, cy0 + 8 + sz)]
    back = [(px_ + 9, py_ - 7) for px_, py_ in front]
    target = (cx0 - 1.5, cy0 + 8 + sz / 2)
    for i, p_ in enumerate(ins):
        s.append(f'<path class="feed" style="--i:{i}" d="M{n(p_[0])},{n(p_[1])} L{n(target[0])},{n(target[1])}" fill="none" stroke="none"/>')
        s.append(A(p_[0], p_[1], target[0], target[1], lw=0.6, head=3, cls="arr arr-s"))
    s += [P(front, fill="white", stroke=BLUE, lw=0.7, op=0.9), P([front[0], back[0], back[1], front[1]], stroke=BLUE, lw=0.7),
          P([front[1], back[1], back[2], front[2]], stroke=BLUE, lw=0.7),
          IM("f11-cloud", cx0 + 2, cy0 + 10, w=sz - 4, h=sz - 4, ext="png", cls="cube-cloud")[0]]
    tx = cx0 + sz + 9 + 7
    s += [A(tx, cy0 + 8 + sz, tx, cy0 - 1, lw=0.8, head=3.2, cls="arr arr-s time"), M(tx + 5, cy0 + 2, "𝑡", 8)]
    s.append(arrows(y))
    rows.append(s)

    # 4. disciplines
    y = ROWS[3]
    s = [label(y, "Disciplines", "siloed →\nconverging"), from_box(y, "Siloed fields", "separate problems")]
    FIELDS = ["CV", "NLP", "Audio", "Robotics", "GIS", "Urban sim."]
    for k, f in enumerate(FIELDS):
        r_, c_ = divmod(k, 3)
        bx, by = FX + 3 + c_ * 35, y + 15 + r_ * 15.5
        s.append(R(bx, by, 34, 12, fill="#F2F3F5", stroke=LINE, lw=0.6, r=1.5) + T(bx + 17, by + 6.3, f, 7, ha="center"))
    s.append(to_box(y, "Converging fields", None))
    hx, hy = TX + TW / 2, y + 33
    for k, f in enumerate(FIELDS):
        side, r_ = divmod(k, 3)
        bx = TX + 6 if side == 0 else TX + TW - 6 - 37
        by = y + 15 + r_ * 13.5
        ex = bx + 37 if side == 0 else bx
        s.append(f'<path class="conv" style="--i:{k}" d="M{n(ex)},{n(by + 5.5)} L{n(hx)},{n(hy)}" fill="none" stroke="{BLUE}" stroke-width="0.6"/>')
        s.append(R(bx, by, 37, 11, stroke=BLUE, lw=0.55, r=1.5) + T(bx + 18.5, by + 5.8, f, 7, ha="center"))
    s.append(f'<g class="shared">{R(hx - 18, hy - 9, 36, 18, fill=BLUE, stroke=BLUE, lw=0.6, r=3)}'
             f'{T(hx, hy + 0.3, "one shared" + chr(10) + "problem", 7, "white", w=700, ha="center", ls=1.0)}</g>')
    s.append(arrows(y))
    rows.append(s)

    # hub
    h = [R(HX, 4, HW, H - 8, fill=BLUE_FILL, stroke=BLUE, lw=0.9, r=4, cls="frame"),
         T(HX + HW / 2, 22, "Spatial intelligence", 10.5, w=700, ha="center"),
         T(HX + HW / 2, 36, "world modeling · embodied reasoning", 7.5, BLUE, ha="center")]
    im, (_, iy, iw, ih) = IM("f11-hub", HX + 7, 48, w=HW - 14, border=LINE)
    h.append(im)
    ox, oy = HX + 7 + 0.29 * iw, 48 + 0.63 * ih
    ax = []
    for dx, dy, lab in [(14, 0, "𝑥"), (-9, 6, "𝑦"), (0, -15, "𝑧")]:
        ax.append(A(ox, oy, ox + dx, oy + dy, lw=0.9, head=3.4, cls="arr axis"))
        ax.append(M(ox + dx * 1.3 + (2 if lab == "𝑥" else 0), oy + dy * 1.25 - (1 if lab == "𝑧" else 0), lab, 7.5))
    h.append(f'<g class="axes">{"".join(ax)}</g>')
    h.append(L([(HX + 10, 48 + ih + 10), (HX + HW - 10, 48 + ih + 10)], color=BLUE_MID, lw=0.5))
    h.append(T(HX + HW / 2, 48 + ih + 36, "constructing, maintaining and\nmanipulating spatial representations\nof the world to perceive, reason,\npredict and act",
               7.5, INK, ha="center", italic=True, ls=1.25))
    body = "".join(g(str(i), "".join(r), ' class="row"') for i, r in enumerate(rows)) + g("hub", "".join(h))
    svg = (f'<svg class="nf-svg" viewBox="0 0 {W} {H}" role="img" aria-label="Figure 1.1: four converging shifts in AI that lead to spatial intelligence">'
           f'{body}<g class="pulses"></g></svg>')
    return (f'<div class="nf nf-11" data-nf="11" data-pagefind-ignore="all">{svg}<div class="nf-card" hidden></div>'
            f'<script type="application/json" class="nf-info">{json.dumps(FIG11_INFO, ensure_ascii=False)}</script></div>')


# ---------------------------------------------------------------- part openers
OPENERS = {
    1: [("Why now", "From data-centric to world-centric AI"), ("How it evolved", "Five eras of representing space"),
        ("What it is", "Spatial intelligence as a closed loop")],
    2: [("Encode first", "Representation bounds capability"), ("One modality at a time", "From explicit geometry\nto implicit structure"),
        ("Into a shared space", "Align without losing geometry")],
    3: [("Perceive", "A scene that is given"), ("Reason", "A scene that is understood"), ("Generate", "A scene that is made")],
    4: [("Leave the lab", "Deployment is a stress test"), ("Domain by domain", "Each field stresses a different axis"),
        ("A horizontal foundation", "One layer beneath every field")],
    5: [("What it requires", "One world state, kept\nconsistent over time"), ("Where the gaps are", "Along the loop, in benchmarks,\nat deployment"),
        ("What comes next", "Open problems and\nfuture directions")],
}
OPENER_NOTES = {3: [(0.5, 0.948, "generation runs the loop in reverse")]}


def opener(k, targets, alt=""):
    """targets: [(href, label)] for the three zones."""
    m = META[f"opener-{k}"]
    zones = []
    for i, ((head, sub), (href, lab)) in enumerate(zip(OPENERS[k], targets)):
        sub_html = "<br>".join(esc(x) for x in sub.split("\n"))
        zones.append(f'<a class="op-z" href="{href}" style="--i:{i}"><span class="op-n">{i + 1}</span><span class="op-txt">'
                     f'<span class="op-h">{esc(head)}</span><span class="op-s">{sub_html}</span>'
                     f'<span class="op-go">{esc(lab)} →</span></span></a>')
    notes = "".join(f'<span class="op-note" style="left:{fx * 100:.1f}%;top:{fy * 100:.1f}%">{esc(s)}</span>' for fx, fy, s in OPENER_NOTES.get(k, []))
    shades = "".join(f'<span class="op-shade" data-z="{i}"></span>' for i in range(3))
    return (f'<div class="op" data-pagefind-ignore="all" style="--ar:{m["w"]}/{m["h"]}">'
            f'<img class="op-art" src="{IMG}opener-{k}-1600.webp" srcset="{IMG}opener-{k}-1600.webp 1600w, {IMG}opener-{k}.webp {m["w"]}w" '
            f'sizes="(max-width: 980px) 100vw, 900px" width="{m["w"]}" height="{m["h"]}" alt="{esc(alt)}" decoding="async">'
            f'<span class="op-shades">{shades}</span><nav class="op-zones" aria-label="In this part">{"".join(zones)}</nav>{notes}</div>')
