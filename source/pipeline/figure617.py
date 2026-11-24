"""Figure 6.17: action detection along an untrimmed video timeline."""
import json
from html import escape
from pathlib import Path

INFO = {
    'overview': {'t': 'Action detection in an untrimmed video', 'b': 'Action detection returns a start time, an end time, and an action class for each instance. Several actions can occur in one continuous stream.'},
    'classification': {'t': 'Action classification (AC)', 'b': 'The input clip is already trimmed to one action. The model predicts its class, with no temporal localization.'},
    'localization': {'t': 'Temporal action localization (TAL)', 'b': 'The input is an untrimmed video, and the model localizes one action interval by predicting its start and end.'},
    'detection': {'t': 'Temporal action detection (TAD)', 'b': 'The model localizes and classifies multiple action instances, including intervals that can overlap.'},
}


def fig617():
    out = []
    add = out.append

    def text(x, y, value, size=29, cls='text', anchor='middle'):
        add(f'<text class="f617-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{value}</text>')

    def path(d, cls='ink', arrow=None, flow=False):
        add(f'<path class="f617-{cls}{" f617-route" if flow else ""}" d="{d}"' + (f' marker-end="url(#f617-{arrow})"' if arrow else '') + '/>')

    def zone(key, x, y, w, h, draw):
        add(f'<g class="f617-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw()
        add(f'<rect class="f617-hit" x="{x}" y="{y}" width="{w}" height="{h}"/>')
        add('</g>')

    def image(pathname, x, y, w, h):
        add(f'<image href="/assets/img/figs/f617/{pathname}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>')

    def strip(panel, x, y, w, h, count, gap=2):
        add(f'<rect class="f617-film" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>')
        records = json.loads((Path(__file__).resolve().parents[2] / 'assets/figures/elements/figure617/manifest.json').read_text())['assets']
        selected = [r for r in records if r['file'].startswith(panel + '/')]
        top, bottom = (201, 346) if panel == 'overview' else (689, 782)
        edges = {'overview': [40,210,383,564,739,915,1090,1258,1424,1577], 'localization': [541,648,756,863,966,1068,1165], 'detection': [1244,1355,1466,1576,1685,1796,1904]}[panel]
        add(f'<rect x="{x+5}" y="{top}" width="{w-10}" height="{bottom-top}" fill="white"/>')
        for r in selected:
            left, top_image, right, bottom_image = r['source_box']
            image(r['file'][:-4], left, top_image, right-left, bottom_image-top_image)
        for edge in edges[1:-1]:
            path(f'M{edge} {top}V{bottom}', 'film-line')
        # Sprocket holes are independent geometry, not part of the image assets.
        hole_w = max(7, min(13, w / 90))
        hole_gap = 11 if w > 700 else 8
        cur = x + 10
        while cur + hole_w < x + w - 6:
            add(f'<rect class="f617-sprocket" x="{cur:.2f}" y="{y+5}" width="{hole_w:.2f}" height="7" rx="1"/>')
            add(f'<rect class="f617-sprocket" x="{cur:.2f}" y="{y+h-12}" width="{hole_w:.2f}" height="7" rx="1"/>')
            cur += hole_w + hole_gap

    add('<div class="nf nf-617" data-nf="617" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1094" role="group" aria-label="Figure 6.17: action detection"><defs>')
    add('<marker id="f617-blue" markerWidth="17" markerHeight="17" markerUnits="userSpaceOnUse" refX="13" refY="8.5" orient="auto"><path d="M3 3L13 8.5L3 14Z" fill="#355fbd"/></marker><marker id="f617-ink" markerWidth="14" markerHeight="14" markerUnits="userSpaceOnUse" refX="11" refY="7" orient="auto"><path d="M2 2L11 7L2 12Z" fill="#172c36"/></marker>')
    add('</defs><rect width="2000" height="1094" fill="white"/>')

    def top():
        # Main video strip and three temporal intervals.
        bars = [(80,557,'walking','0:12, 0:38'), (554,902,'sitting down','0:38, 0:45'), (914,1261,'drinking','0:50, 1:08')]
        for x1, x2, label, stamp in bars:
            mid = (x1+x2)/2
            text(mid, 45 if label == 'sitting down' else (82 if label == 'walking' else 85), f'({stamp}, {label})', 31, 'blue-text')
            y = 72 if label == 'sitting down' else (114 if label == 'walking' else 108)
            add(f'<rect class="f617-interval{" f617-muted" if label == "sitting down" else ""}" x="{x1}" y="{y}" width="{x2-x1}" height="31"/>')
            path(f'M{x1} {y+15}H{x2}', 'interval-flow', flow=True)
            path(f'M{x1} {y+31}V176M{x2} {y+31}V176', 'guide')
        strip('overview', 37, 177, 1542, 191, 9, 3)
        # Temporal baseline, ticks and endpoints.
        path('M44 397H1567', 'blue-axis', 'blue', True)
        for i in range(1,9):
            x = 44 + i * (1523/9)
            path(f'M{x:.1f} 370V397', 'tick')
        text(44, 431, '0', 28, 'text', 'middle')
        text(747, 431, 't', 28)
        text(1566, 431, 'T', 28, 'text', 'end')
        # Tuple semantics inset.
        add('<rect class="f617-tuple-box" x="1608" y="47" width="361" height="347" rx="38"/>')
        text(1788, 121, '<tspan class="f617-math">(t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="22">s</tspan><tspan class="f617-math">, t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="22">e</tspan><tspan class="f617-math">, c)</tspan>', 36)
        path('M1707 145L1679 204', 'blue-arrow', 'blue', True)
        path('M1767 141L1776 276', 'blue-arrow', 'blue', True)
        path('M1852 137L1894 204', 'blue-arrow', 'blue', True)
        text(1676, 242, 'Start', 32, 'blue-text'); text(1676, 285, 'time', 32, 'blue-text')
        text(1776, 314, 'End', 32, 'blue-text'); text(1776, 357, 'time', 32, 'blue-text')
        text(1896, 242, 'Action', 32, 'blue-text'); text(1896, 285, 'class', 32, 'blue-text')
        text(1000, 463, '<tspan font-weight="700">Task:</tspan> localize <tspan class="f617-math">(t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="19">s</tspan><tspan class="f617-math">, t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="19">e</tspan><tspan class="f617-math">)</tspan> and classify <tspan class="f617-math">c</tspan> for every action instance in an untrimmed video', 27)
        add('<rect class="f617-panel-border" x="2" y="2" width="1996" height="490" rx="22"/>')
    zone('overview', 6, 4, 1988, 481, top)

    def classification():
        add('<rect class="f617-heading-box" x="34" y="520" width="476" height="54" rx="10"/>')
        text(272, 558, '(i) Action Classification (AC)', 30, 'blue-text')
        add('<rect class="f617-photo-frame" x="108" y="605" width="304" height="190"/>')
        image('classification/tennis-serve', 112, 609, 296, 182)
        text(260, 828, 'trimmed', 30)
        path('M260 842V878', 'ink', 'ink', True)
        text(260, 908, '<tspan class="f617-math">c</tspan> = tennis serve', 29)

    def localization():
        add('<rect class="f617-heading-box" x="558" y="520" width="594" height="54" rx="10"/>')
        text(855, 558, '(ii) Temporal Action Localization (TAL)', 29, 'blue-text')
        strip('localization', 540, 677, 628, 120, 6, 2)
        add('<rect class="f617-interval" x="636" y="623" width="348" height="28"/>')
        path('M636 651V677M984 651V677', 'guide')
        path('M636 637H984', 'interval-flow', flow=True)
        text(854, 830, 'untrimmed', 30)
        path('M854 842V878', 'ink', 'ink', True)
        text(854, 908, '<tspan class="f617-math">(t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="19">s</tspan><tspan class="f617-math">, t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="19">e</tspan><tspan class="f617-math">, c)</tspan> = (0:08, 0:23, tennis serve)', 27)

    def detection():
        add('<rect class="f617-heading-box" x="1286" y="520" width="570" height="54" rx="10"/>')
        text(1571, 558, '(iii) Temporal Action Detection (TAD)', 29, 'blue-text')
        strip('detection', 1242, 677, 662, 120, 6, 2)
        for x, y, w in [(1246,603,183),(1398,640,281),(1793,603,107)]:
            add(f'<rect class="f617-interval{" f617-muted" if y == 640 else ""}" x="{x}" y="{y}" width="{w}" height="28"/>')
            path(f'M{x} {y+28}V677M{x+w} {y+28}V677', 'guide')
            path(f'M{x} {y+14}H{x+w}', 'interval-flow', flow=True)
        text(1573, 830, 'untrimmed', 30)
        path('M1573 842V878', 'ink', 'ink', True)
        text(1573, 908, '<tspan class="f617-math">(t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">s</tspan><tspan class="f617-math">¹, t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">e</tspan><tspan class="f617-math">¹, c¹), (t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">s</tspan><tspan class="f617-math">², t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">e</tspan><tspan class="f617-math">², c²), (t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">s</tspan><tspan class="f617-math">³, t</tspan><tspan class="f617-math" baseline-shift="sub" font-size="18">e</tspan><tspan class="f617-math">³, c³)</tspan>', 31)

    zone('classification', 14, 510, 510, 443, classification)
    zone('localization', 527, 510, 660, 443, localization)
    zone('detection', 1192, 510, 790, 443, detection)
    # Continuous complexity arrow and explanatory footer are unframed shared elements.
    add('<g class="f617-scaffold">')
    path('M65 969H1891', 'blue-axis', 'blue', True)
    add('<rect class="f617-complexity-label" x="711" y="944" width="380" height="48" rx="8"/>')
    text(901, 980, 'Increasing complexity', 29, 'blue-italic')
    text(1000, 1038, 'Three paradigms differ in (a) whether the input is trimmed and (b) whether multiple instances are localized', 27)
    add('<rect class="f617-panel-border" x="2" y="504" width="1996" height="588" rx="22"/>')
    add('</g></svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">' + json.dumps(INFO) + '</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[2]
    source = site / 'assets/figures/figures/part3/section6/action_detection.webp'
    (site / 'example/figure617.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure617-2"><title>Figure 6.17 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.17 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/action_detection.webp"><h2 id="redraw">Interactive reconstruction</h2>''' + fig617() + '''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure617-2';mountNative();</script></html>''')
