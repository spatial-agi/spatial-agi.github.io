"""Natively drawn web figures: Fig. 1.1 and Fig. 2.1 as SVG in the print figure's own point coordinates
(ports of figgen/fig1_1.py and figgen/fig2_1.py), and the part openers as artwork + live text.

Text is real SVG text (selectable, searchable by the browser); photos and point clouds are the raster pieces
exported by figassets.py. Interactivity lives in src/js/nfig.js; each module carries data-k for it.
"""
import html
import json
import math
from figure46 import fig46
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


# ---------------------------------------------------------------- Fig. 4.4
def fig45():
    """Language representation diagram in the original 2000 × 788 coordinates."""
    blue, ink = '#164F9B', '#111111'
    notes={
      'chair':dict(t='Language · Adjacency',b='“The chair is next to the table” describes a spatial relation between two named objects.'),
      'window':dict(t='Language · Across from',b='The window and the door occupy opposite sides of the room. Language describes this relation symbolically.'),
      'lamp':dict(t='Language · Above',b='The description places the lamp above the table. The drawing uses a top view to locate the objects.'),
      'tokens':dict(t='Move sequence',b='The model receives a sequence of Othello moves as tokens. The diagram illustrates sequence-only training.'),
      'model':dict(t='Transformer hidden activations',b='Hidden activations can carry information about the spatial state implied by the move history.'),
      'probe':dict(t='Probe',b='A probe reads the hidden activations to predict board occupancy. The arrows illustrate information flow, not additional moves being played.'),
      'board':dict(t='Recovered board state',b='The 8 × 8 board visualizes empty squares and black or white discs decoded from the model’s activations.')}
    out=['<div class="nf nf-45" data-nf="45" data-pagefind-ignore="all"><div class="f45-viewport"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 788" role="group" aria-label="Figure 4.5: spatial information in language representations">',
      '<defs><marker id="f45-blue" markerWidth="19" markerHeight="18" refX="16" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L19 9L0 18L4 9Z" fill="#164F9B"/></marker><marker id="f45-black" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L16 8L0 16Z" fill="#111"/></marker><radialGradient id="f45-disc-white" cx="35%" cy="30%"><stop stop-color="#fff"/><stop offset="1" stop-color="#edf2ec"/></radialGradient><linearGradient id="f45-board" x2="1" y2="1"><stop stop-color="#ccd8b4"/><stop offset=".5" stop-color="#bfcea5"/><stop offset="1" stop-color="#c8d6af"/></linearGradient></defs>']
    def text(x,y,s,size=30,color=ink,anchor='start',weight=400):
        lines=s.split('\n'); spans=''.join(f'<tspan x="{x}" dy="{0 if i==0 else size*1.28}">{esc(v)}</tspan>' for i,v in enumerate(lines))
        return f'<text class="f45-text" x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{spans}</text>'
    def route(d,color=blue,delay=0,duration=1300):
        marker='f45-black' if color==ink else 'f45-blue'
        return f'<path class="f45-route" d="{d}" stroke="{color}" stroke-width="3" fill="none" marker-end="url(#{marker})" data-delay="{delay}" data-duration="{duration}"/>'
    def zone(k,x,y,w,h,content):
        return f'<g class="f45-zone" data-k="{k}" role="button" tabindex="0" aria-label="{esc(notes[k]["t"])}" aria-pressed="false"><rect class="f45-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="transparent"/>{content}</g>'
    def image(name,x,y,w,h): return f'<image href="/assets/img/figs/f45/left/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    out += [R(17,1,937,673,fill='white',stroke='#16343D',lw=2.5,r=26),R(975,1,1024,673,fill='white',stroke='#16343D',lw=2.5,r=26)]
    # Floor plan: double wall, top window and open door, independently drawn.
    out += ['<path d="M395 62H268V621H419M577 62H705V621H511" stroke="#222" stroke-width="15" fill="none" stroke-linejoin="miter"/>',
            '<path d="M395 62H268V621H419M577 62H705V621H511" stroke="#b5b5b5" stroke-width="8" fill="none"/>',
            R(395,51,183,22,fill='white',stroke='#222',lw=3),'<path d="M401 52V72M573 52V72M396 62H577" fill="none" stroke="#333" stroke-width="2"/>',
            '<path d="M420 564V654H511M420 564A90 90 0 0 1 510 654M415 619V655H423M507 618V655H515" stroke="#222" stroke-width="3" fill="white"/>',
            image('table',416,212,186,207)]
    out += [zone('chair',24,218,384,155,text(140,251,'The chair is next\nto the table',30,blue,'middle')+image('chair',316,255,92,115)+route('M179 318Q225 330 305 316',delay=0)),
            zone('window',588,80,357,170,text(833,168,'The window is\nacross from the\ndoor',30,blue,'middle')+route('M725 178L592 88',delay=500)),
            zone('lamp',383,278,267,268,image('lamp',474,280,71,72)+text(516,499,'The lamp is above\nthe table',30,blue,'middle')+route('M509 460V365',delay=1000))]
    out.append(text(1063,81,'Othello-GPT:',42,weight=700)+text(1338,81,'probing recovers board state',42))
    out.append(zone('tokens',984,554,329,101,text(985,597,'E4 c5 d4 ...',30)+text(1142,648,'Token sequence',36,anchor='middle')+route('M1142 596H1221V554',ink,delay=0,duration=750)))
    model=''
    for y in [183,287,481]:
        model+=R(1122,y,197,68,fill='white',stroke='#333',lw=3,r=12)+text(1220,y+44,'Transformer',30,anchor='middle')
    model+=text(1220,421,'...',38,anchor='middle')
    model+=route('M1220 480V448',ink,750,500)+route('M1220 389V359',ink,1250,500)+route('M1220 285V257',ink,1750,500)
    model+=text(1413,260,'Hidden\nactivations',30,blue,'middle')+route('M1327 327H1466V376',delay=2300,duration=1100)
    out.append(zone('model',1114,174,389,381,model))
    out.append(zone('probe',1400,377,180,119,R(1410,384,111,104,fill='white',stroke=blue,lw=3,r=12)+text(1465,427,'probe',30,blue,'middle')+route('M1523 436H1567',delay=3400,duration=650)))
    # The board is redrawn as 64 independent cells and 13 discs; match source coordinates.
    board=['<rect x="1611" y="205" width="372" height="380" fill="url(#f45-board)" stroke="#222" stroke-width="3"/>']
    for i in range(1,8):
        board.append(f'<path d="M{1611+i*46.5} 205V585M1611 {205+i*47.5}H1983" fill="none" stroke="#344031" stroke-width="2"/>')
    for i,c in enumerate('abcdefgh'):
        board.append(text(1634.25+i*46.5,193,c,26,anchor='middle'))
        board.append(text(1598,237+i*47.5,str(8-i),26,anchor='end'))
    pieces=[('c',7,'w'),('d',6,'b'),('e',6,'w'),('c',5,'b'),('d',5,'w'),('e',5,'b'),('d',4,'b'),('e',4,'w'),('f',4,'w'),('c',3,'w'),('f',3,'b'),('c',2,'b'),('g',1,'w')]
    for col,row,c in pieces:
        cx=1611+('abcdefgh'.index(col)+.5)*46.5; cy=205+(8-row+.5)*47.5
        board.append(f'<circle class="f45-disc" cx="{cx}" cy="{cy}" r="17.5" fill="{"url(#f45-disc-white)" if c=="w" else "#060907"}" stroke="#30382d" stroke-width="2"/>')
    board.append(text(1797,636,'Othello board state',37,anchor='middle'))
    out.append(zone('board',1577,164,414,480,''.join(board)))
    out += [text(486,746,'Surface: language describes space',42,anchor='middle'),text(1487,746,'Latent: probes recover world state',42,anchor='middle'),'<g class="f45-pulses" aria-hidden="true"></g></svg></div><div class="nf-card" hidden></div><script type="application/json" class="nf-info">'+json.dumps(notes,ensure_ascii=False)+'</script></div>']
    return ''.join(out)


def fig44():
    """Native reconstruction in the original 2000 × 810 coordinate system."""
    blue, ink = '#3D43ED', '#2C383F'
    notes = {
        'a':dict(t='RGBD video · Moving camera', b='Each time step pairs an RGB frame with aligned depth. Camera poses change together with the observed scene.'),
        'b':dict(t='4D point cloud · Temporal correspondence', b='Independent per-frame samples do not guarantee point identities. The lower cloud maintains correspondences through persistent point trajectories.'),
        'c':dict(t='Deformable mesh · Vertex displacement', b='A deformation field moves each vertex from its reference position. Colour encodes displacement. Re-extracting a surface at each time is an alternative.'),
        'd':dict(t='Dynamic NeRF · Time and view', b='Columns represent time and rows represent viewpoints. The neural field maps position, viewing direction and time to colour and density, directly or through deformation and latent codes.'),
        'e':dict(t='Deformable 3DGS · Gaussian motion', b='Gaussian centres translate by Δμᵢ(t), while rotations Rᵢ(t) and scales Sᵢ(t) determine the covariance. Opacity and colour remain constant in this illustrated parameterization.')
    }
    out = ['<div class="nf nf-44" data-nf="44" data-pagefind-ignore="all"><div class="f44-viewport"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 810" role="group" aria-label="Figure 4.4: five 4D representations">',
           f'<defs><marker id="f44-arrow" markerWidth="13" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 1L10 6L2 11" fill="none" stroke="{blue}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker><linearGradient id="f44-displacement"><stop stop-color="#DCEAF3"/><stop offset="1" stop-color="#1F72AD"/></linearGradient></defs>']
    def t(x,y,s,size=30,anchor='start',weight=400,color=ink,math=False,fit=None):
        measure=f' textLength="{fit}" lengthAdjust="spacingAndGlyphs"' if fit else ''
        return f'<text class="f44-{"math" if math else "text"}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{measure}>{s}</text>'
    def m(x,y,s,size=32,color=blue): return t(x,y,s,size,'middle',color=color,math=True)
    def sub(s,i): return s+f'<tspan baseline-shift="sub" font-size="70%">{i}</tspan>'
    def frame(x,y,w,h,color='#A8B0B8',width=3,r=0,cls='',dash=None): return R(x,y,w,h,fill='none',stroke=color,lw=width,r=r,cls=cls,dash=dash)
    def path(d,color=blue,width=3,dash=None,arrow=False,delay=0):
        da=f' stroke-dasharray="{dash}"' if dash else ''
        marker=' marker-end="url(#f44-arrow)"' if arrow else ''
        cls='f44-route' if arrow else 'f44-line'
        return f'<path class="{cls}" data-delay="{delay}" d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"{da}{marker}/>'
    def img(key,x,y,w=None,h=None):
        from PIL import Image
        iw,ih=Image.open(Path(__file__).resolve().parents[1]/'src/img/figs/f44'/key).size
        w=iw if w is None else w; h=ih if h is None else h
        return f'<image class="f44-art" href="/assets/img/figs/f44/{key}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def begin(k,x,w,label):
        out.append(f'<g class="f44-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{esc(notes[k]["t"])}">')
        out.append(R(x,6,w,735,fill='white',stroke='#A8B0B8',lw=3,r=6,cls='f44-frame'))
        out.append(t(x+w/2,786,label,32,'middle',700))
    def end(): out.append('</g>')
    begin('a',4,394,'(a) RGBD video')
    out += [t(23,58,'Moving camera · top view',30,fit=354),m(201,96,sub('P','t₀')+' ≠ '+sub('P','t₁')+' ≠ '+sub('P','t₂'),34)]
    for i,(x,cx,camx,camy,cw,ch) in enumerate([(22,77,40,123,51,53),(147,202,189,124,32,57),(273,328,312,125,58,41)]):
        out += [img(f'a/camera_t{i}.png',camx,camy,cw,ch),m([75,203,327][i],184,sub('t',str(i)),31,ink),
                frame(x,224,110,121,width=2),frame(x,444,110,122,width=2),
                path(f'M{cx} 358V422',width=4,arrow=True,delay=i*260)]
    # Keep the extracted scenes at their original scale and locations.
    for i,(rx,ry,dx,dy) in enumerate([(36,230,36,450),(156,230,156,450),(278,230,278,450)]):
        out += [img(f'a/rgb_t{i}.png',rx,ry),img(f'a/depth_t{i}.png',dx,dy)]
    out += [path('M59 154L71 141',width=5,arrow=True),path('M205 160L202 144',width=5,arrow=True,delay=260),path('M348 151L331 141',width=5,arrow=True,delay=520),
            t(202,209,'RGB',31,'middle'),t(202,610,'Aligned depth',31,'middle'),path('M38 665H360',arrow=True),t(202,711,'Time',31,'middle')]
    end()
    begin('b',405,393,'(b) 4D point cloud')
    out += [t(601,64,'Per-frame sequence',32,'middle'),t(601,387,'No identity guarantee',30,'middle'),path('M415 421H783','#A8B0B8',2.5,'6 5'),t(601,466,'Unified cloud + tracks',32,'middle')]
    for i,(x,y,w,h,tx,ty,tw,th) in enumerate([(441,147,84,204,440,490,85,190),(574,149,52,200,574,490,56,191),(688,148,68,201,684,490,76,190)]):
        out += [m([479,600,720][i],127,sub('t',str(i)),31,ink),img(f'b/point_cloud_t{i}.png',x,y,w,h),img(f'b/tracked_cloud_t{i}.png',tx,ty,tw,th)]
    for j,(x1,y1,x2,y2,x3,y3) in enumerate([(490,508,605,508,725,508),(487,589,605,588,725,585),(480,625,588,624,698,622)]):
        out += [path(f'M{x1} {y1}L{x2} {y2}',arrow=True,delay=j*240),path(f'M{x2+5} {y2}L{x3} {y3}',arrow=True,delay=800+j*240)]
    out.append(t(601,717,'Persistent point identities',30,'middle',fit=361)); end()
    begin('c',805,393,'(c) Deformable mesh')
    for i,(x,y) in enumerate([(837,116),(969,116),(1080,116)]):
        out += [m([881,998,1114][i],84,sub('t',str(i)),31,ink),img(f'c/mesh_t{i}.png',x,y)]
    out += [path('M858 449H1145',width=4,arrow=True),t(1002,497,'Deformation field',32,'middle'),
            m(1002,550,sub('v','i')+'(t) = '+sub('v','i')+'(0) + Δ'+sub('v','i')+'(t)',32),
            t(883,591,'Low',28,'end'),'<rect x="898" y="577" width="176" height="13" fill="url(#f44-displacement)"/>',t(1097,591,'High',28),
            t(1002,631,'Vertex displacement',29,'middle'),t(1002,683,'Or re-extract each time',30,'middle'),t(1002,727,'Marching Cubes / Poisson',29,'middle',fit=345)]
    end()
    begin('d',1205,393,'(d) Dynamic NeRF')
    out += [m(1316,48,sub('t','0'),32,ink),m(1498,48,sub('t','1'),32,ink),t(1226,142,'1',28,'middle'),t(1226,299,'2',28,'middle')]
    for row,y in enumerate([74,231]):
        for i,x in enumerate([1268,1451]): out.append(img(f'd/view{row+1}_t{i}.png',x,y))
    out += [path('M1250 402H1562',width=4,arrow=True),t(1410,442,'Time × view',31,'middle'),frame(1234,461,345,158,r=8),t(1407,504,'Neural field (MLP)',32,'middle',700,fit=283),
            m(1407,559,'(x, d, t) ↦ ('+sub('c','t')+', '+sub('σ','t')+')',33),t(1407,683,'Direct t / deformation /',30,'middle'),t(1407,730,'latent code (alternatives)',30,'middle',fit=351)]
    end()
    begin('e',1606,393,'(e) Deformable 3DGS')
    for i,(x,y) in enumerate([(1628,116),(1763,116),(1868,116)]):
        out += [m([1675,1798,1921][i],84,sub('t',str(i)),31,ink),img(f'e/gaussians_t{i}.png',x,y)]
    out += [frame(1780,205,42,58,blue,2.7,dash='8 6'),path('M1780 263L1636 411',width=2.5,dash='8 5'),path('M1822 263L1967 411',width=2.5,dash='8 5'),frame(1636,411,332,277,blue,3,r=7),
            '<ellipse class="f44-gaussian" cx="1702" cy="499" rx="23" ry="49" transform="rotate(25 1702 499)" fill="#C5CFDD" stroke="#2C383F" stroke-width="3"/>',
            '<ellipse class="f44-gaussian" cx="1878" cy="499" rx="23" ry="49" transform="rotate(-35 1878 499)" fill="#C5CFDD" stroke="#2C383F" stroke-width="3"/>',
            path('M1743 499H1826',width=4,arrow=True),m(1797,453,'Δ'+sub('μ','i')+'(t)',34),m(1924,435,sub('R','i')+'(t)',32),path('M1910 449L1930 482',width=4,arrow=True,delay=450),
            m(1917,598,sub('S','i')+'(t)',32),path('M1898 534L1928 562',width=4,arrow=True,delay=850),
            m(1802,643,sub('Σ','i')+'(t) = RSS<tspan baseline-shift="super" font-size="70%">T</tspan>R<tspan baseline-shift="super" font-size="70%">T</tspan>',32),
            m(1802,728,sub('α','i')+', '+sub('c','i')+' constant',34,ink)]
    end()
    out.append('<g class="f44-pulses" aria-hidden="true"></g></svg></div><div class="nf-card" hidden></div><script type="application/json" class="nf-info">'+json.dumps(notes,ensure_ascii=False)+'</script></div>')
    return ''.join(out)

# ---------------------------------------------------------------- Fig. 4.3
def fig43():
    """Reconstruct the print figure in its original 2000 × 708 pixel coordinate system."""
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'src/img/figs/f43/placements.json').read_text())
    blue, ink = '#477CB8', '#151515'
    out = ['<div class="nf nf-43" data-nf="43" data-pagefind-ignore="all">',
           '<div class="f43-viewport"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 708" role="group" aria-label="Figure 4.3: NeRF, 3DGS, and Hybrid (DMTet + Tri-plane)">',
           '<defs><marker id="f43-arrow" markerWidth="11" markerHeight="9" refX="9" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L11 4.5L0 9L3 4.5Z" fill="#477CB8"/></marker><marker id="f43-ink" markerWidth="12" markerHeight="10" refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L12 5L0 10L3 5Z" fill="#202020"/></marker><radialGradient id="f43-ray"><stop stop-color="#53B1EA"/><stop offset="1" stop-color="#1760A0"/></radialGradient></defs>']
    def text(x, y, value, size=24, color=ink, anchor='start', weight=400, math=False, cls='', fit=None):
        measure = f' textLength="{fit}" lengthAdjust="spacingAndGlyphs"' if fit else ''
        return f'<text{measure} class="f43-text {"f43-math" if math else ""} {cls}" x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{value}</text>'
    def path(d, color='#777', width=1.8, dash=None, cls='', fill='none', arrow=False):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        marker = f' marker-end="url(#{"f43-arrow" if color == blue else "f43-ink"})"' if arrow else ''
        return f'<path class="{cls}" d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}"{da}{marker}/>'
    def rect(x, y, w, h, r=0, color='#666', width=1.7, fill='none', dash=None, cls=''):
        return R(x,y,w,h,fill=fill,stroke=color,lw=width,r=r,dash=dash,cls=cls)
    def route(d, k, color=blue, dash=None, width=2, duration=1100, delay=0):
        return path(d,color,width,dash,cls=f'f43-route f43-route-{k}',arrow=True).replace('class="',f'data-duration="{duration}" data-delay="{delay}" class="',1)
    def zone(k, bounds):
        x,y,w,h=bounds
        out.append(f'<g class="f43-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{esc(notes[k]["t"])}">')
        out.append(rect(x,y,w,h,fill='transparent',color='none',width=0,cls='f43-hit'))
    def end(): out.append('</g>')
    def image(key, cls=''):
        p = manifest[key]; x,y=p['position']; w,h=p['size']
        return f'<image class="f43-art {cls}" href="{IMG}f43/{key}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def plane(points, cols=5, rows=6, fill='white', stroke='#444', width=1.8):
        a,b,c,d=points
        poly=' '.join(f'{x},{y}' for x,y in points)
        result=f'<polygon points="{poly}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
        for i in range(1,cols):
            t=i/cols; p=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t); q=(d[0]+(c[0]-d[0])*t,d[1]+(c[1]-d[1])*t)
            result+=path(f'M{p[0]} {p[1]}L{q[0]} {q[1]}','#A7A7A7',.8)
        for i in range(1,rows):
            t=i/rows; p=(a[0]+(d[0]-a[0])*t,a[1]+(d[1]-a[1])*t); q=(b[0]+(c[0]-b[0])*t,b[1]+(c[1]-b[1])*t)
            result+=path(f'M{p[0]} {p[1]}L{q[0]} {q[1]}','#A7A7A7',.8)
        return result
    notes={
      'nerf':dict(t='NeRF · Ray sampling',b='A camera ray passes through a pixel into the volume, sampling the radiance field at 3D positions along its path. Blue dots mark the sample positions.'),
      'field':dict(t='NeRF · Neural field & volume rendering',b='Fθ maps a 3D position x and viewing direction d to colour c and volume density σ. Volume rendering integrates these samples along the ray to produce a pixel colour. Density σ depends only on x; colour c depends on both x and d.'),
      'gs':dict(t='3DGS · Anisotropic Gaussian ellipsoids',b='The teapot is represented by anisotropic 3D Gaussian ellipsoids. The dashed box selects a local region and connects it to the parameter illustration below.'),
      'detail':dict(t='Gaussian parameters · μ, Σ, α, SH',b='μ is the centre; Σ controls shape and orientation; α is opacity; and SH (spherical harmonic coefficients) describes view-dependent colour.'),
      'project':dict(t='① Project / splat',b='Project the 3D Gaussians onto the image plane to obtain 2D Gaussian splats.'),
      'sort':dict(t='② Depth sort',b='Sort the projected Gaussian splats by depth. The illustration orders them from far to near.'),
      'blend':dict(t='③ Alpha-blend',b='Composite the splats using their colours and opacities to form the final image.'),
      'dmtet':dict(t='DMTet · Differentiable marching tetrahedra',b='Extract a triangle mesh from an implicit field on a coarse tetrahedral grid. The loss between rendered and target images propagates back to the geometry through differentiable rendering and surface extraction.'),
      'triplane':dict(t='Tri-plane · Feature lookup & decoding',b='Project a 3D point onto the XY, YZ and XZ feature planes, sample and aggregate their features, then decode colour, density or SDF using an MLP.'),
    }
    # Frames and labels follow the source bitmap's measured coordinates.
    out += [rect(12,6,609,628,25,'#16343D',1.9,fill='white'),rect(642,6,717,628,25,'#16343D',1.9,fill='white'),rect(1374,2,622,632,24,'#16343D',1.9,fill='white')]
    # (a) camera, image plane and bounding volume.
    zone('nerf',(22,39,590,310))
    out += [text(24,149,'camera'),text(122,94,'Image plane'),text(301,59,'volume (bounding box)'),
            path('M264 106L321 83L591 91L529 123Z','#999',1.5,'5 4'),
            path('M264 106V305L529 342L590 293V91M529 123V342M321 83V281L590 293M264 305L321 281','#999',1.5,'5 4'),
            image('a/teapot'),image('a/camera'),
            plane([(166,136),(217,110),(217,233),(166,259)],4,6),
            path('M187 187L198 181V203L187 209',blue,0,fill='#669BD2'),
            route('M110 195H193L610 235','nerf',duration=1900),
            text(134,300,'Pixel <tspan class="f43-math">(μ, ν)</tspan>',24,blue),
            route('M199 264L193 215','nerf',width=1.7,delay=1900,duration=650)]
    for i,(x,y) in enumerate([(290,204),(334,209),(379,213),(435,219),(494,226),(559,231)]):
        out.append(f'<circle class="f43-sample" data-i="{i}" cx="{x}" cy="{y}" r="7.3" fill="url(#f43-ray)" stroke="#C1E4F8" stroke-width="1.2"/>')
    end()
    zone('field',(56,263,551,366))
    out += [route('M379 223V371','field',dash='5 4',width=1.6,duration=850),
            rect(180,376,427,251,17,blue,1.8,fill='white',dash='4 4'),
            route('M178 406C88 402 65 360 67 269','field',width=2.2,duration=1300,delay=3100),
            text(108,359,'∫',38,blue,math=True),text(70,420,'volume',20,blue,cls='f43-condensed'),text(62,445,'rendering',20,blue,cls='f43-condensed'),
            text(201,417,'inputs <tspan class="f43-math" fill="#477CB8">(x, d)</tspan>',22,cls='f43-condensed'),
            text(473,417,'outputs <tspan class="f43-math" fill="#477CB8">(c, σ)</tspan>',22,cls='f43-condensed'),
            rect(195,437,120,47,6,blue,1.5,'#F4F8FC'),rect(195,502,120,47,6,blue,1.5,'#F4F8FC'),
            rect(365,429,63,125,9,'#444',1.8,'#F4F4F3'),rect(474,437,115,47,5,blue,1.5,'#F4F8FC'),rect(474,502,115,47,5,blue,1.5,'#F4F8FC'),
            text(255,467,'3D position <tspan class="f43-math">x</tspan>',20,anchor='middle',cls='f43-condensed'),
            text(255,532,'view direction <tspan class="f43-math">d</tspan>',20,anchor='middle',cls='f43-condensed'),
            text(396,499,'F<tspan baseline-shift="sub" font-size="24">θ</tspan>',37,anchor='middle',math=True),
            text(532,467,'colour <tspan class="f43-math">c</tspan>',21,anchor='middle',cls='f43-condensed'),text(532,532,'density <tspan class="f43-math">σ</tspan>',21,anchor='middle',cls='f43-condensed'),
            route('M321 460H357','field',delay=950),route('M321 524H357','field',delay=950),route('M435 460H466','field',delay=2000),route('M435 524H466','field',delay=2000),
            text(210,602,'<tspan class="f43-math" fill="#477CB8">σ</tspan> depends on <tspan class="f43-math" fill="#477CB8">x</tspan> only; <tspan class="f43-math" fill="#477CB8">c</tspan> depends on <tspan class="f43-math" fill="#477CB8">(x, d)</tspan>',23,cls='f43-condensed',fit=358)]
    end()
    out.append(text(316,678,'(a) NeRF',30,anchor='middle'))
    # (b) Teapot and the detail callout. The dashed overlays are independent SVG paths.
    out.append(text(658,38,'Anisotropic Gaussian Ellipsoids on the teapot surface',25))
    zone('gs',(671,53,381,275))
    out += [image('b/gaussian-teapot'),rect(888,156,56,51,0,'#333',2,dash='6 4',cls='f43-callout'),path('M888 207L667 332M944 207L990 332','#fff',6),path('M888 207L667 332M944 207L990 332','#333',1.8,'6 4')]
    end()
    zone('detail',(668,332,373,260))
    out += [rect(667,331,374,262,11,'#333',1.8,'white','5 4'),image('b/gaussian-detail'),
            text(872,393,'μ:',28,blue,math=True),text(901,393,'centre'),text(872,444,'Σ:',30,blue,math=True),text(909,440,'shape and'),text(872,467,'orientation'),
            text(872,517,'α:',28,blue,math=True),text(903,517,'opacity'),text(872,562,'SH:',24,blue,math=True),text(927,562,'colour')]
    end()
    out += [rect(1118,64,225,528,12,blue,1.5,dash='4 4'),text(1128,103,'Rasterizers (3 steps)',25,fit=205)]
    zone('project',(1126,112,209,149))
    out += [text(1125,137,'①',28,blue),text(1154,134,'Project / splat',23),image('b/raster-gaussian-primitives'),
            path('M1259 149L1323 127V223L1259 250Z','#444',2,fill='white'),image('b/raster-projected-splats'),route('M1209 192H1245','project','#333',dash='4 3',width=1.8)]
    end()
    zone('sort',(1126,267,211,159))
    out += [text(1125,291,'②',28,blue),text(1154,289,'Depth sort',23),path('M1132 332L1195 315V402L1132 420Z','#444',2,fill='white'),image('b/raster-depth-splats'),
            image('b/raster-depth-stack'),route('M1201 357H1235','sort','#333',dash='4 3',width=1.8),text(1304,319,'far',20,cls='f43-condensed'),text(1300,407,'near',20,cls='f43-condensed'),route('M1314 329V384','sort','#333',width=1.8,delay=1300)]
    end()
    zone('blend',(1126,440,211,138))
    out += [text(1125,469,'③',28,blue),text(1154,466,'Alpha-blend',23),image('b/raster-blend-stack'),rect(1250,486,77,80,0,'#444',2,'white'),image('b/raster-render-teapot'),route('M1202 526H1240','blend','#333',dash='4 3',width=1.8)]
    end()
    out.append(text(1003,678,'(b) 3DGS',30,anchor='middle'))
    # (c) DMTet; the grid cage is intrinsic artwork, while all process arrows are native.
    out += [path('M1658 20V617','#666',1.5,'7 6'),text(1519,35,'DMTet',25,anchor='middle',weight=700),text(1403,77,'Coarse tetrahedral grid',23)]
    zone('dmtet',(1395,89,257,536))
    out += [image('c/tetrahedral-grid-teapot'),image('c/triangle-mesh-teapot'),route('M1499 284V355','dmtet','#111',width=2.7,duration=1400),
            text(1511,299,'Differentiable',23),text(1526,326,'marching',23),text(1528,353,'tetrahedra',23),
            rect(1474,527,79,96,10,'#666',1.7,'white'),text(1480,543,'2D render',18,fit=68),image('c/render-teapot'),
            rect(1586,544,51,60,8,'#666',1.7,'white'),text(1591,565,'loss',23),text(1611,595,'ℒ',36,anchor='middle',math=True),
            route('M1583 575H1560','dmtet','#222',width=2,delay=1600),
            route('M1445 548C1407 527 1405 489 1408 414L1409 227','dmtet',blue,dash='5 4',width=1.6,duration=1800,delay=2800),
            text(1420,363,'∇',36,blue,math=True),text(1400,578,'gradients',19,blue,cls='f43-condensed',fit=65),text(1398,602,'from 2D loss',19,blue,cls='f43-condensed',fit=69)]
    end()
    # Tri-plane is reconstructed as in print: two visible planes and the middle axis label.
    out += [text(1822,35,'Tri-plane',25,anchor='middle',weight=700),text(1666,77,'Three orthogonal feature planes',23,fit=315)]
    zone('triplane',(1667,88,318,537))
    out += [text(1730,113,'XY',20,anchor='middle',cls='f43-condensed'),text(1826,113,'YZ',20,anchor='middle',cls='f43-condensed'),text(1938,113,'XZ',20,anchor='middle',cls='f43-condensed'),
            plane([(1704,146),(1771,109),(1771,208),(1704,245)],5,6),plane([(1892,108),(1961,146),(1961,245),(1892,207)],5,6),
            path('M1732 160L1746 152V174L1732 182',blue,0,fill='#6B9FD1'),path('M1920 154L1934 162V183L1920 175',blue,0,fill='#6B9FD1'),
            path('M1740 168L1832 178L1927 168',blue,1.8,'5 4'),
            '<circle class="f43-query" cx="1832" cy="178" r="4.6" fill="#1465AD"/>',text(1832,156,'(x, y, z)',23,blue,anchor='middle',math=True),
            route('M1740 177V273','triplane',dash='5 4',width=1.8,duration=950),route('M1832 188V273','triplane',dash='5 4',width=1.8,duration=950),route('M1927 180V273','triplane',dash='5 4',width=1.8,duration=950),
            image('c/feature-xy'),image('c/feature-yz'),image('c/feature-xz')]
    for x,label_ in [(1740,'XY'),(1832,'YZ'),(1927,'XZ')]:
        out.append(text(x,366,f'f<tspan baseline-shift="sub" font-size="18">{label_}</tspan>',27,anchor='middle',math=True))
    out += [route('M1738 382V396L1814 418','triplane',width=1.8,duration=1000,delay=1100),route('M1832 381V400','triplane',width=1.8,duration=1000,delay=1100),route('M1927 382V396L1850 418','triplane',width=1.8,duration=1000,delay=1100),
            '<circle cx="1832" cy="422" r="15" fill="white" stroke="#333" stroke-width="1.9"/>',path('M1821 422H1843M1832 411V433','#111',1.8),route('M1832 444V473','triplane',width=1.8,duration=700,delay=2200),
            rect(1788,478,87,53,10,'#555',1.8,'#F3F3F2',cls='f43-decoder'),text(1832,513,'MLP',25,anchor='middle'),route('M1832 540V566','triplane',width=1.8,duration=700,delay=3000),text(1834,622,'Color / Density / SDF',25,anchor='middle')]
    end()
    out += [text(1684,678,'(c) Hybrid (DMTet + Tri-plane)',30,anchor='middle'),'<g class="f43-pulses" aria-hidden="true" pointer-events="none"></g></svg></div>',

            '<div class="nf-card" hidden role="status"></div>',f'<script type="application/json" class="nf-info">{json.dumps(notes,ensure_ascii=False)}</script></div>']
    return ''.join(out)


from figure3 import fig3opener


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


# ---------------------------------------------------------------- Fig. 7.13
FIG713_INFO = {
    "agent": dict(t="Agent · choose an action", b="The agent uses its policy πθ(a | o) to choose an action from the current observation. Feedback from interaction provides the signal for policy improvement."),
    "action": dict(t="Action · aₜ", b="The chosen action is applied to the environment. In a spatial task, this can be a movement, a navigation decision or a manipulation command."),
    "env": dict(t="Environment · ℰ", b="The environment responds to the action. Its next state determines the observation and reward returned to the agent."),
    "current": dict(t="Observation oₜ · Reward rₜ", b="The current observation is the input to the agent’s policy. The reward provides feedback on the preceding interaction. These are the original labels on the left side of the time boundary."),
    "next": dict(t="Observation oₜ₊₁ · Reward rₜ₊₁", b="After action aₜ, the environment returns the next observation and reward. The dashed separator in the original diagram distinguishes the two time indices."),
}


def fig713():
    """Native SVG styling with every printed node, label and connection retained."""
    def target(k, body):
        return g(k, body, f' role="button" tabindex="0" aria-pressed="false" aria-label="{esc(FIG713_INFO[k]["t"])}"')

    agent = R(16, 38, 215, 202, fill=BLUE_FILL, stroke=BLUE, lw=1.2, r=15, cls="frame")
    agent += T(123.5, 79, "Agent", 25, w=700, ha="center")
    agent += R(30, 112, 187, 62, stroke=BLUE_MID, r=9)
    agent += T(123.5, 144, "Policy πθ(a | o)", 22, ha="center")
    env = R(785, 38, 199, 202, fill="#F6F7FA", stroke=LINE, lw=1.2, r=15, cls="frame")
    env += T(884.5, 116, "Environment", 23, w=700, ha="center")
    env += T(884.5, 171, "ℰ", 36, BLUE, ha="center")
    action = A(231, 65, 785, 65, color=BLUE, lw=2, head=9)
    action += T(508, 28, "Action aₜ", 23, ha="center")
    action += R(232, 5, 552, 82, fill="transparent", stroke="none")
    current = A(545, 200, 231, 200, color=BLUE, lw=2, head=9)
    current += T(388, 172, "Observation oₜ", 20, ha="center")
    current += T(388, 233, "Reward rₜ", 20, ha="center")
    current += R(232, 150, 312, 102, fill="transparent", stroke="none")
    next_ = A(785, 200, 545, 200, color=BLUE, lw=2, head=9)
    next_ += T(665, 172, "Observation oₜ₊₁", 20, ha="center")
    next_ += T(665, 233, "Reward rₜ₊₁", 20, ha="center")
    next_ += R(550, 150, 234, 102, fill="transparent", stroke="none")
    svg = ('<svg class="nf-svg" viewBox="0 0 1000 270" role="group" aria-label="Figure 7.13: reinforcement learning framework, retaining both time-indexed observation and reward pairs">'
           + target("agent", agent) + target("env", env) + target("action", action)
           + target("current", current) + target("next", next_)
           + L([(545, 153), (545, 225)], color="#858B96", lw=1.6, dash="6 4")
           + '<circle class="token" r="4.5" aria-hidden="true"/></svg>')
    return ('<div class="nf nf-713" data-nf="713" data-pagefind-ignore="all">' + svg
            + '<div class="nf-card" role="status" hidden></div>'
            '<script type="application/json" class="nf-info">' + json.dumps(FIG713_INFO, ensure_ascii=False) + '</script></div>')


# ---------------------------------------------------------------- Fig. 1.2

def fig12():
    """Approved five-era drawing, without any preview controls or comparison UI."""
    assets = Path(__file__).resolve().parents[1] / "src/img/figs"
    svg = (assets / "f12-evolution.svg").read_text()
    info = (assets / "f12-info.json").read_text()
    return ('<div class="nf nf-12" data-nf="12" data-pagefind-ignore="all">'
            '<div class="nf12-scroll"><div class="evolution">' + svg
            + '<aside class="reading-card" role="status" hidden></aside></div></div>'
            '<script type="application/json" class="nf-info">' + info + '</script></div>')
