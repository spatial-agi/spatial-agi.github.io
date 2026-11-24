"""Figure 7.2: physics-aware spatial reasoning, independently annotated SVG."""
import json
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
INFO = {
    "grasp": ("Grasp stability", "Opposing contact forces act along the surface normals. The friction cones bound admissible contact forces; the origin inside the wrench-space convex hull indicates a force-closure grasp."),
    "pushing": ("Planar pushing", "The pusher applies a force inside the contact friction cone. The object translates and rotates under quasi-static friction, while the limit surface maps contact forces to motion."),
    "stacking": ("Stacking stability", "A stack is statically stable when the gravity projection stays inside the support interval. The marked minimum margin d_min measures distance to the support boundary."),
}


def fig72():
    out = []
    add = out.append

    def path(d, cls="ink", extra=""):
        classes = " ".join(f"f72-{part}" for part in cls.split())
        add(f'<path class="{classes}" d="{d}" {extra}/>')

    def rect(x, y, w, h, cls="ink", rx=0, extra=""):
        add(f'<rect class="f72-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {extra}/>')

    def text(x, y, value, size=28, cls="label", anchor="middle"):
        add(f'<text class="f72-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{value}</text>')

    def image(file, x, y, w, h):
        add(f'<image href="/assets/img/figs/f72/{file}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')

    def arrow(d, color="ink", cls="arrow"):
        path(d, f'{cls} {color}-stroke', f'marker-end="url(#f72-{color}-arrow)"')

    def zone(key, box, draw):
        add(f'<g class="f72-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        x, y, w, h = box
        rect(x, y, w, h, "hit")
        add('</g>')

    add('<div class="nf nf-72" data-nf="72" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 677" role="group" aria-label="Figure 7.2: physics-aware spatial reasoning"><defs>')
    for key, color in [("ink", "#111"), ("blue", "#2052c7"), ("gray", "#888")]:
        add(f'<marker id="f72-{key}-arrow" markerUnits="userSpaceOnUse" markerWidth="17" markerHeight="15" refX="15" refY="7.5" orient="auto"><path d="M0 0L16 7.5L0 15Z" fill="{color}"/></marker>')
    add('<pattern id="f72-ground" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><path d="M0 0V26" stroke="#111" stroke-width="2.3"/></pattern></defs><rect width="2000" height="677" fill="#fff"/><g class="f72-scaffold">')
    rect(15, 12, 617, 582, "panel", 21)
    rect(657, 12, 703, 582, "panel", 21)
    rect(1382, 12, 602, 582, "panel", 21)
    add('</g>')

    def grasp():
        rect(145, 118, 319, 180, "block")
        image("a-grasp/left-finger", 51, 182, 89, 84)
        image("a-grasp/right-finger", 470, 183, 89, 84)
        add('<circle class="f72-contact" cx="145" cy="206" r="8"/><circle class="f72-contact" cx="464" cy="206" r="8"/>')
        path("M145 206L210 131M145 206L211 281M464 206L393 131M464 206L392 281", "cone")
        arrow("M145 206H226", "blue"); arrow("M464 206H383", "blue")
        text(196, 78, "μ₁", 34, "math blue"); text(412, 78, "μ₂", 34, "math blue")
        arrow("M181 90L175 111", "blue", "thin-arrow"); arrow("M428 91L435 111", "blue", "thin-arrow")
        text(226, 181, "n₁", 30, "math blue"); text(382, 181, "n₂", 30, "math blue")
        rect(415, 359, 198, 214, "inset", 17, 'stroke="#2052c7"')
        text(514, 390, "0 ∈ int conv(W)", 25, "math blue")
        path("M471 412L548 412L591 475L548 538L471 538L436 475Z", "ink")
        path("M436 475H591M471 412L548 538M548 412L471 538", "cone")
        add('<circle class="f72-contact" cx="510" cy="475" r="7"/>')
        text(579, 557, "W", 27, "math blue")
        text(316, 644, "(a) Grasp Stability", 36, "caption")

    def pushing():
        image("b-pushing/pusher", 701, 148, 101, 99)
        path("M796 196L944 122M796 196L963 267M944 122Q978 195 963 267", "cone")
        arrow("M796 196H953", "blue")
        text(807, 267, "applied", 25, "blue"); text(807, 301, "force", 25, "blue")
        text(878, 306, "arctan(μ", 24, "math blue", "start"); text(971, 313, "c", 17, "math blue"); text(982, 306, ")", 24, "math blue")
        text(812, 78, "friction cone", 25, "label")
        arrow("M838 95L866 148", "ink", "thin-arrow")
        path("M979 97L1141 46L1268 183L1217 334L995 336L951 250Z", "block")
        add('<circle class="f72-center" cx="1083" cy="207" r="18"/><path class="f72-center-mark" d="M1072 196L1094 218M1094 196L1072 218"/>')
        arrow("M1064 263H1148", "gray")
        arrow("M1150 235Q1185 186 1126 153", "gray")
        rect(697, 359, 254, 214, "inset", 17, 'stroke="#2052c7"')
        text(823, 390, "motion cone", 27, "blue")
        path("M821 514L752 400M821 514L899 400", "ink")
        path("M821 514V402", "cone")
        text(718, 535, "Friction cone mapped", 20, "blue", "start")
        text(718, 562, "through limit surface", 20, "blue", "start")
        rect(988, 359, 301, 214, "inset", 17, 'stroke="#2052c7"')
        add('<g transform="rotate(3 1128 502)"><ellipse class="f72-ellipsoid" cx="1128" cy="502" rx="66" ry="40"/>')
        for rx in (15, 37, 58):
            add(f'<ellipse class="f72-mesh" cx="1128" cy="502" rx="{rx}" ry="40"/>')
        for ry in (13, 29):
            add(f'<ellipse class="f72-mesh" cx="1128" cy="502" rx="66" ry="{ry}"/>')
        add('</g>')
        arrow("M1125 460V422", "ink", "thin-arrow"); arrow("M1194 502H1238", "ink", "thin-arrow"); arrow("M1082 530L1052 554", "ink", "thin-arrow")
        text(1142, 427, "τ", 23, "math"); text(1250, 507, "fₓ", 24, "math"); text(1043, 567, "fᵧ", 24, "math")
        text(1007, 644, "(b) Planar Pushing", 36, "caption")

    def stacking():
        path("M1614 48L1804 77L1775 248L1587 224Z", "block")
        add('<circle class="f72-contact" cx="1696" cy="151" r="7"/>')
        arrow("M1696 160V232", "blue")
        text(1721, 199, "g", 29, "math blue", "start")
        rect(1538, 247, 320, 110, "block")
        rect(1454, 357, 480, 172, "block")
        path("M1696 233V357", "dashed")
        path("M1627 357H1772", "support")
        path("M1627 347V367M1772 347V367", "support")
        arrow("M1700 334H1766", "blue", "thin-arrow"); arrow("M1766 334H1700", "blue", "thin-arrow")
        text(1734, 319, "dₘᵢₙ", 28, "math blue")
        path("M1804 291L1815 303L1838 276", "check")
        path("M1401 529H1965", "ground")
        rect(1400, 529, 565, 30, "hatch", 0)
        text(1683, 644, "(c) Stacking Stability", 36, "caption")

    zone("grasp", (20, 18, 607, 565), grasp)
    zone("pushing", (662, 18, 693, 565), pushing)
    zone("stacking", (1387, 18, 592, 565), stacking)
    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">' + json.dumps({k: {"t": v[0], "b": v[1]} for k, v in INFO.items()}) + '</script></div>')
    return ''.join(out)


if __name__ == "__main__":
    preview = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure72-1"><title>Figure 7.2 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.2 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/physical_reasoning.webp" alt="Original Figure 7.2"><h2>Interactive reconstruction</h2>''' + fig72() + '''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure72-1';mountNative();</script></html>'''
    (SITE / "example/figure72.html").write_text(preview)
