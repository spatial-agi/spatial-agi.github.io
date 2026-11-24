"""Figure 6.13: source-layout spatial relation extraction and method lanes."""
import json
from html import escape
from pathlib import Path

INFO = {
    'input': dict(t='Visual scene and target objects', b='The scene supplies two target objects: the cup O₁ and the book O₂. Images, video, point clouds, and RGB-D are alternative input modalities. The blue boxes identify the objects whose spatial relation is queried.'),
    'sre': dict(t='Spatial relation extraction', b='The extractor uses geometric rules, learned representations, or a multimodal large language model. These are alternative mechanisms for predicting a relation between the target objects.'),
    'vsc': dict(t='Closed-set relation classification', b='Visual spatial classification (VSC) selects a relation from a predefined vocabulary. Here the predicted triplet says that the cup O₁ is left of the book O₂.'),
    'vsd': dict(t='Free-form spatial description', b='Visual spatial description (VSD) expresses spatial relations in natural language. A description may include both support and relative position, such as the cup being on the table and left of the book.'),
    'metric': dict(t='Quantitative spatial estimate', b='A metric output estimates a distance or another physical quantity for the object pair. Recovering a physical distance requires metric depth or scale information; an RGB image alone does not fix absolute scale.'),
    'rules': dict(t='Rule-based mechanisms', b='Detect the objects and lift them into a geometric representation. Coordinate differences are mapped to a rule and then a relation triplet. The dated timeline lists representative methods; its spacing does not represent elapsed time.'),
    'learning': dict(t='Learning-based, decoupled mechanisms', b='An encoder feeds separate spatial and generic description branches. Representative methods use decoupled captioning or 3D scene modeling to learn the relation. Timeline order does not imply a computational dependency.'),
    'mllm': dict(t='MLLM-based mechanisms', b='Visual regions and depth or geometry cues condition a multimodal large language model. The examples use image and depth, a depth API, boxes or masks, or qualitative and metric supervision to predict spatial relations.'),
}


def fig613():
    out = []
    add = out.append
    scale = 2000 / 1823

    def text(x, y, label, size=28, cls='f613-text', width=None):
        length = f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{label}</text>')

    def sub(label, suffix):
        return label + f'<tspan baseline-shift="sub" font-size="65%">{suffix}</tspan>'

    def rect(x, y, w, h, cls='f613-box', rx=6):
        add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def path(d, cls='f613-blue', end=None, start=None):
        markers = (f' marker-end="url(#f613-{end})"' if end else '') + (f' marker-start="url(#f613-{start})"' if start else '')
        add(f'<path class="{cls}" d="{d}"{markers}/>')

    def dot(x, y, r=8):
        add(f'<circle class="f613-dot" cx="{x}" cy="{y}" r="{r}"/>')

    def zone(key, x, y, w, h, body):
        add(f'<g class="f613-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        body()
        rect(x, y, w, h, 'f613-hit', 7)
        add('</g>')

    def image(name, box):
        x0, y0, x1, y1 = box
        add(f'<image href="/assets/img/figs/f613/input/{name}.png" x="{x0/scale}" y="{y0/scale}" width="{(x1-x0)/scale}" height="{(y1-y0)/scale}"/>')

    def timeline(y, entries):
        path(f'M836 {y}H1785', 'f613-gray f613-timeline f613-route', 'gray')
        for x, w, labels, year, top, h in entries:
            rect(x, top, w, h)
            for i, label in enumerate(labels):
                text(x+w/2, top+h/2+9+(i-(len(labels)-1)/2)*39, label, 28 if i == 0 else 26)
            path(f'M{x+w/2} {top+h-2}V{y+18}', 'f613-gray f613-tick')
            text(x+w/2, y+51, str(year), 25, 'f613-text f613-blue-text')

    add('<div class="nf nf-613" data-nf="613" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1493" role="group" aria-label="Figure 6.13: spatial relation extraction"><defs>')
    for name, color in [('blue', '#4545ed'), ('ink', '#29343a'), ('gray', '#aab3b9')]:
        add(f'<marker id="f613-{name}" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 2L12 7L2 12Z" fill="{color}" stroke="{color}" stroke-width="1" stroke-linejoin="round"/></marker>')
    add('<marker id="f613-measure" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M3 3L11 7L3 11" fill="none" stroke="#4545ed" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add(f'</defs><rect width="2000" height="1493" fill="#fff"/><g transform="scale({scale})">')
    text(1480, 66, 'Alternative relation outputs', 32, 'f613-title f613-scaffold', 439)
    text(399, 784, 'Family + core mechanism', 29, 'f613-title f613-scaffold', 363)
    text(1336, 784, 'Method chronology (spacing not to scale)', 29, 'f613-title f613-scaffold', 583)
    for y in [735, 977, 1161, 1347]:
        path(f'M27 {y}H1797', 'f613-divider f613-scaffold')
    path('M1105 193V567', 'f613-blue f613-scaffold')

    def inputs():
        text(314, 66, 'Visual scene + target objects', 32, 'f613-title', 460)
        image('scene', (30, 104, 671, 533))
        rect(166, 229, 64, 60, 'f613-detection', 0)
        rect(396, 244, 107, 58, 'f613-detection', 0)
        text(198, 211, sub('O', '1'), 34, 'f613-math')
        text(450, 227, sub('O', '2'), 34, 'f613-math')
        image('video-frame-1', (40, 641, 117, 693))
        image('video-frame-2', (123, 641, 201, 693))
        image('point-cloud', (247, 620, 371, 683))
        image('rgbd-color', (442, 636, 527, 693))
        image('rgbd-depth', (538, 631, 622, 693))
        for x, label in [(109, 'Video'), (283, 'Point cloud'), (485, 'RGB-D')]:
            text(x, 669, label, 26)
        path('M618 317H666', 'f613-ink f613-route', 'ink')
    zone('input', 24, 25, 647, 660, inputs)

    def sre():
        rect(681, 193, 354, 320)
        text(858, 251, 'SRE', 32, 'f613-title')
        dot(732, 311, 7); dot(805, 311, 7)
        path('M743 311H794', 'f613-blue f613-route')
        for x, y, w, h in [(721, 363, 18, 37), (755, 370, 18, 24), (789, 363, 18, 37), (721, 440, 19, 23), (755, 440, 19, 23), (789, 440, 19, 23)]:
            rect(x, y, w, h, 'f613-token', 0)
        for y, label in [(318, 'Rules'), (389, 'Learned'), (459, 'MLLM')]:
            text(914, y, label, 28)
        path('M1047 350H1093', 'f613-blue f613-route', 'blue')
    zone('sre', 679, 185, 419, 336, sre)

    def vsc():
        path('M1105 193H1155', 'f613-blue f613-route', 'blue')
        rect(1169, 115, 623, 155)
        text(1480, 167, '(a) VSC: closed-set label', 29, 'f613-title', 346)
        text(1480, 230, '('+sub('O', '1')+'<tspan font-style="normal">, left of, </tspan>'+sub('O', '2')+')', 36, 'f613-math', 242)
    zone('vsc', 1167, 110, 630, 166, vsc)

    def vsd():
        path('M1105 381H1155', 'f613-blue f613-route', 'blue')
        rect(1169, 303, 623, 171)
        text(1480, 352, '(b) VSD: description', 29, 'f613-title', 281)
        text(1480, 405, '“The cup is on the table,', 29, 'f613-text f613-blue-text')
        text(1480, 439, 'to the left of the book.”', 29, 'f613-text f613-blue-text')
    zone('vsd', 1167, 298, 630, 182, vsd)

    def metric():
        path('M1105 567H1155', 'f613-blue f613-route', 'blue')
        rect(1169, 510, 623, 155, 'f613-box f613-blue-box')
        text(1480, 560, '(c) Metric estimate', 29, 'f613-title', 267)
        dot(1242, 609); dot(1425, 609)
        path('M1264 609H1404', 'f613-blue f613-route f613-measure', 'measure', 'measure')
        text(1620, 620, 'd̂('+sub('O', '1')+', '+sub('O', '2')+')', 36, 'f613-math')
        text(1480, 708, 'Requires metric depth / scale', 26)
    zone('metric', 1167, 505, 630, 211, metric)

    def rules():
        text(146, 897, '(i) Rule-based', 29, 'f613-title', 194)
        rect(311, 835, 180, 90)
        text(401, 887, 'Detect / lift', 26)
        path('M502 881H549', 'f613-blue f613-route', 'blue')
        dot(589, 881, 10); dot(710, 881, 10)
        path('M602 881H697', 'f613-blue f613-route')
        text(651, 831, 'Δx, Δy, Δz', 29, 'f613-math')
        text(547, 968, 'Geometry → rule → triplet', 25)
        timeline(892, [(847, 356, ['Roadscene2Vec'], 2022, 828, 60), (1335, 323, ['HKT-SG'], 2024, 828, 60)])
    zone('rules', 27, 801, 1770, 172, rules)

    def learning():
        text(147, 1065, '(ii) Learning-', 29, 'f613-title', 177)
        text(147, 1098, 'based', 29, 'f613-title')
        rect(311, 1018, 135, 88)
        text(378, 1068, 'Enc', 28)
        path('M457 1063H491V1018H531', 'f613-ink f613-route', 'ink')
        path('M491 1063V1105H531', 'f613-ink f613-route', 'ink')
        rect(547, 988, 207, 61, 'f613-box f613-blue-box')
        rect(547, 1074, 207, 62)
        text(650, 1026, 'Spatial', 28); text(650, 1113, 'Generic', 28)
        timeline(1077, [(847, 356, ['VSDNet', 'Decoupled captioning'], 2022, 980, 94), (1335, 361, ['3DVSD', '3D scene modeling'], 2023, 980, 94)])
    zone('learning', 27, 980, 1770, 176, learning)

    def mllm():
        text(145, 1249, '(iii) MLLM-', 29, 'f613-title', 145)
        text(145, 1283, 'based', 29, 'f613-title')
        for x in [317, 350, 384]:
            rect(x, 1231, 23, 29, 'f613-token', 0)
        text(382, 1305, 'Regions', 26)
        path('M424 1245H478', 'f613-blue f613-route', 'blue')
        rect(494, 1198, 179, 90, 'f613-box f613-model')
        text(583, 1185, 'Depth / geometry', 26)
        text(583, 1250, 'MLLM', 28)
        path('M685 1245H749', 'f613-blue f613-route', 'blue')
        text(719, 1307, 'Relation', 26)
        timeline(1262, [(841, 214, ['SpatialVLM', 'Image + depth'], 2024, 1166, 93), (1074, 214, ['SpatialBot', 'Depth API'], 2024, 1166, 93), (1307, 224, ['SpatialRGPT', 'Box / mask'], 2024, 1166, 93), (1553, 225, ['SpatialLLM', 'Qual. + metric'], 2025, 1166, 93)])
    zone('mllm', 27, 1165, 1770, 177, mllm)

    add('</g></svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[2]
    (site/'example/figure613.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure613-1"><title>Figure 6.13 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.13 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/spatial_relation_extraction.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig613()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure613-1';mountNative();</script></html>''')
