"""Figure 6.23: source-aligned object tracking method families."""
import json
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
INFO = {
    'propagation': {'t': 'Propagation-based methods', 'b': 'The previous target state guides matching in the next frame. Matching and online updates propagate the same target through the sequence; the dashed arrows connect successive predicted states.'},
    'associate': {'t': 'Detect, then associate', 'b': 'A detector first produces independent candidates in every frame. A separate association stage uses motion prediction, appearance re-identification and matching to connect detections into identity-consistent tracks.'},
    'joint': {'t': 'Joint detection and association', 'b': 'Tracking queries participate in joint optimization across the sequence. Detection and identity association are learned together, and the output retains identities across frames.'},
    'universal': {'t': 'Universal tracking models', 'b': 'A shared foundation backbone processes the video. Task-specific heads support single object tracking (SOT), multiple object tracking (MOT), video object segmentation (VOS), and multiple object tracking and segmentation (MOTS).'},
}


def fig623():
    out = []
    add = out.append

    def rect(x, y, w, h, cls='box', rx=0):
        add(f'<rect class="f623-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def text(x, y, value, size=18, cls='text', anchor='middle'):
        add(f'<text class="f623-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>')

    def path(d, arrow=True, dashed=False):
        add(f'<path class="f623-line f623-route{" f623-dashed" if dashed else ""}" d="{d}"'+(' marker-end="url(#f623-arrow)"' if arrow else '')+'/>')

    def strip(x, mode='clean'):
        # The photographs have no baked-in film edges, boxes or identity labels.
        for i, y in enumerate([58, 165, 272]):
            add(f'<image href="/assets/img/figs/f623/shared-frames/frame-{i:02}.png" x="{x}" y="{y}" width="104" height="107" preserveAspectRatio="none"/>')
        for sx in [x-13, x+104]:
            rect(sx, 58, 13, 322, 'film')
            for y in range(63, 378, 14):
                rect(sx+1, y, 11, 7, 'hole')
        if mode != 'clean':
            for i, (dx, dy, w, h) in enumerate([(40, 29, 25, 52), (42, 11, 23, 52), (43, 21, 27, 41)]):
                y = [58, 165, 272][i]
                rect(x+dx, y+dy, w, h)
                if mode in ['detections', 'ids']:
                    rect(x+dx-13, y+dy+17, 17, 19)
                if mode == 'ids':
                    text(x+6, y+37, 'ID1', 16, 'id', 'start')
                    text(x+69, y+[41, 40, 19][i], 'ID2', 16, 'id', 'start')

    def zone(key, x, w, draw):
        add(f'<g class="f623-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw()
        rect(x, 47, w, 338, 'hit', 5)
        add('</g>')

    add('<div class="nf nf-623" data-nf="623" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 454" role="group" aria-label="Figure 6.23: four object tracking method families"><defs><marker id="f623-arrow" markerWidth="9" markerHeight="8" markerUnits="userSpaceOnUse" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#123cda"/></marker></defs><rect width="2000" height="454" fill="white"/>')

    def propagation():
        strip(17, 'target')
        rect(147, 138, 98, 54, rx=10)
        text(196, 160, 'Matching'); text(196, 182, 'Update')
        rect(147, 242, 98, 55, rx=10)
        text(196, 265, 'Matching'); text(196, 287, 'Update')
        path('M82 113C130 112 173 119 196 137')
        path('M83 202C129 201 169 199 195 193')
        path('M84 203C140 204 181 222 196 241')
        path('M87 314C135 311 174 308 195 298')
        path('M249 270C266 269 258 233 274 228')
        # Propagated boxes on the right-hand film strip are frontend geometry.
        for sx in [274, 392]:
            rect(sx, 58, 13, 322, 'film')
            for y in range(63, 378, 14):
                rect(sx+1, y, 11, 7, 'hole')
        for y, h in [(58, 108), (166, 108), (274, 106)]:
            rect(287, y, 105, h, 'module')
        rect(326, 87, 24, 52, 'module')
        rect(327, 176, 24, 52, 'module')
        rect(328, 293, 28, 42, 'module')
        path('M338 140V175', dashed=True)
        path('M339 229L342 292', dashed=True)
    zone('propagation', 3, 406, propagation)

    def associate():
        strip(450)
        for y in [82, 188, 294]:
            rect(583, y, 98, 55, 'module', 10)
            text(632, y+33, 'Detector')
            path(f'M568 {y+28}H582')
            path(f'M682 {y+28}H701')
        strip(714, 'detections')
        rect(852, 55, 109, 324, 'module', 11)
        text(906.5, 90, 'Association')
        for y, label in [(125, 'Kalman'), (144, 'Re-ID'), (163, 'matching')]:
            text(906.5, y, label, 15, 'muted')
        path('M831 217H850'); path('M962 217H983')
        for y1, y2 in [(194, 239), (239, 194), (284, 284)]:
            path(f'M873 {y1}L935 {y2}', dashed=True)
            for x, y in [(873, y1), (935, y2)]:
                add(f'<circle class="f623-node" cx="{x}" cy="{y}" r="4.5"/>')
        strip(996, 'ids')
    zone('associate', 437, 677, associate)

    def joint():
        strip(1156)
        rect(1294, 56, 112, 323, 'module', 11)
        for y in [76, 172, 260]:
            rect(1319, y, 63, 64, 'module', 5)
            text(1350.5, y+38, 'Q')
            path(f'M1301 {y+32}H1318'); path(f'M1383 {y+32}H1400')
        text(1350, 345, 'Joint'); text(1350, 368, 'Optimization')
        path('M1273 217H1293'); path('M1407 217H1425')
        strip(1438, 'ids')
    zone('joint', 1143, 413, joint)

    def universal():
        strip(1606)
        rect(1741, 56, 111, 323, 'module', 11)
        text(1796.5, 191, 'Foundation')
        text(1796.5, 214, 'Backbone')
        text(1796.5, 237, '(Shared)')
        path('M1723 217H1740')
        for y, task in [(56, 'SoT'), (143, 'MoT'), (234, 'VoS'), (316, 'MoTS')]:
            rect(1874, y, 94, 63, 'module', 5)
            text(1921, y+25, task); text(1921, y+48, 'Head')
            path(f'M1853 {y+35}H1873')
    zone('universal', 1592, 380, universal)

    add('<g class="f623-scaffold">')
    for x, top, bottom in [(421, 24, 452), (1128, 2, 430), (1574, 2, 430)]:
        add(f'<path class="f623-divider" d="M{x} {top}V{bottom}"/>')
    for x, label in [(210, '(i) Propagation-based Methods'), (804, '(ii) Detect-then-associate Methods'), (1350, '(iii) Joint detection-association Methods'), (1770, '(iv) Universal Models')]:
        text(x, 408, label, 23)
    add('</g></svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    (SITE/'example/figure623.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure623-1"><title>Figure 6.23 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1800px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.23 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/object_tracking_method.webp" alt="Original object tracking method families"><h2>Interactive reconstruction</h2>'''+fig623()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure623-1';mountNative();</script></html>''')
