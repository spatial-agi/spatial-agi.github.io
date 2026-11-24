"""Figure 6.14: scene graph modalities and task variants."""
import json
from html import escape
from pathlib import Path

INFO = {
    'image': dict(t='Image scene graph', b='Objects detected in one image become graph entities. Directed, labeled edges describe relations: the person rides the horse, and the horse is in the field.'),
    'video': dict(t='Video scene graph', b='A video graph associates entities and relations across time. The riding relation spans the interval from t₁ to t₃ shown below the sampled frames.'),
    'text': dict(t='Text scene graph', b='A sentence can be parsed into entities and predicates. Here the person, horse, and field form the same relational structure as the visual example.'),
    '3d': dict(t='3D scene graph', b='A 3D scene graph represents objects and their spatial or functional relationships. The chair is next to the table, and the table supports the lamp.'),
    'universal': dict(t='Universal scene graph', b='Image, video, text, and 3D inputs can share a graph representation with aligned entities and relations.'),
    'hoi': dict(t='Human–object interaction', b='Human–object interaction detection focuses on a human subject, an interacting object, and their action. Bounding boxes locate the person and bicycle; the directed edge denotes riding.'),
    'psg': dict(t='Panoptic scene graph', b='Panoptic scene graphs include both countable things and background stuff, grounded in segmentation masks. This example connects the person, bicycle, road, and sky through rides, on, and below relations.'),
}


def fig614():
    out = []
    add = out.append

    def text(x, y, label, size=29, cls='text'):
        add(f'<text class="f614-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{label}</text>')

    def box(x, y, w, h, cls='box', fill=None, rx=7):
        color = f' style="fill:{fill}"' if fill else ''
        add(f'<rect class="f614-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"{color}/>')

    def path(d, cls='blue', end='blue', flow=True):
        marker = f' marker-end="url(#f614-{end})"' if end else ''
        route = ' f614-route' if flow else ''
        add(f'<path class="f614-{cls}{route}" d="{d}"{marker}/>')

    def image(name, x, y, w, h):
        add(f'<image href="/assets/img/figs/f614/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')

    def node(x, y, w, label, fill=None):
        box(x, y, w, 68, fill=fill)
        text(x+w/2, y+43, label)

    def zone(key, x, y, w, h, draw):
        add(f'<g class="f614-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw()
        box(x, y, w, h, 'hit')
        add('</g>')

    def horse_graph(offset, field=True):
        node(offset+6, 350, 142, 'person')
        node(offset+252, 350, 130, 'horse')
        path(f'M{offset+154} 384H{offset+242}')
        text(offset+200, 354, 'rides', 28, 'blue-text')
        if field:
            path(f'M{offset+317} 424V475')
            text(offset+267, 458, 'in', 28, 'blue-text')
            node(offset+252, 486, 130, 'field')

    add('<div class="nf nf-614" data-nf="614" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 975" role="group" aria-label="Figure 6.14: scene graph modalities and task variants"><defs>')
    for name, color in [('blue', '#4545ed'), ('gray', '#aab3b9'), ('ink', '#29343a')]:
        add(f'<marker id="f614-{name}" markerWidth="15" markerHeight="15" refX="12" refY="7.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M3 3L12 7.5L3 12Z" fill="{color}" stroke="{color}" stroke-width="2" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="975" fill="#fff"/>')
    for x in [400, 800, 1200, 1600]:
        path(f'M{x} 91V551', 'divider f614-scaffold', None, False)
    path('M20 572H1980', 'divider f614-scaffold', None, False)
    path('M1000 654V957', 'divider f614-scaffold', None, False)

    def image_panel():
        text(200, 46, '(i) Image SG', 36, 'title')
        image('image/horse-scene', 24, 69, 352, 236)
        box(49, 118, 259, 170, 'detection', rx=0)
        box(152, 72, 60, 139, 'detection', rx=0)
        horse_graph(0)
    zone('image', 3, 8, 390, 550, image_panel)

    def video_panel():
        text(600, 46, '(ii) Video SG', 36, 'title')
        for i, x in enumerate([424, 544, 664], 1):
            image(f'video/frame-{i}', x, 162, 112, 75)
            text(x+56, 135, f't<tspan baseline-shift="sub" font-size="70%">{i}</tspan>', 32, 'math time')
        path('M440 276H763', 'gray', 'gray')
        horse_graph(400, False)
        box(471, 458, 258, 80, 'interval')
        text(600, 505, 'rides [t<tspan baseline-shift="sub" font-size="70%">1</tspan>, t<tspan baseline-shift="sub" font-size="70%">3</tspan>]', 34, 'math blue-text')
    zone('video', 404, 8, 390, 550, video_panel)

    def text_panel():
        text(1000, 46, '(iii) Text SG', 36, 'title')
        box(828, 88, 344, 213)
        text(1000, 185, '“A person is riding', 32)
        text(1000, 223, 'a horse in a field.”', 32)
        horse_graph(800)
    zone('text', 804, 8, 390, 550, text_panel)

    def three_d():
        text(1400, 46, '(iv) 3D SG', 36, 'title')
        image('3d/room-without-axes', 1224, 69, 352, 236)
        for d in ['M1277 270H1323', 'M1277 270L1249 251', 'M1277 270V221']:
            path(d, 'ink', 'ink', False)
        text(1338, 277, 'x', 28); text(1238, 249, 'y', 28); text(1277, 211, 'z', 28)
        node(1218, 350, 130, 'chair'); node(1458, 350, 130, 'table')
        path('M1354 384H1448')
        text(1403, 354, 'next to', 28, 'blue-text')
        path('M1523 424V475')
        text(1400, 458, 'supports', 28, 'blue-text')
        node(1458, 486, 130, 'lamp')
    zone('3d', 1204, 8, 390, 550, three_d)

    def universal():
        text(1800, 46, '(v) Universal SG', 36, 'title')
        text(1692, 92, 'Image', 29); text(1868, 92, 'Video', 29)
        image('universal/image', 1636, 109, 112, 75)
        image('universal/video-frame-1', 1812, 149, 53, 35)
        image('universal/video-frame-2', 1867, 149, 54, 35)
        box(1634, 215, 117, 68); text(1692, 255, 'Text', 29)
        text(1870, 219, '3D', 29)
        image('universal/point-cloud', 1812, 237, 96, 43)
        path('M1870 288V310H1692', 'gray', None, True)
        path('M1692 288V338', 'gray', 'gray')
        horse_graph(1600)
        text(1775, 488, 'Shared', 28); text(1775, 522, 'entities', 28)
    zone('universal', 1604, 8, 390, 550, universal)

    def hoi():
        text(500, 627, '(i) HOI: human subject, boxes', 36, 'title')
        image('hoi/cyclist-without-boxes', 24, 670, 401, 268)
        box(153, 678, 129, 218, 'detection', rx=0)
        box(87, 778, 260, 135, 'detection', rx=0)
        node(467, 747, 155, 'person'); node(804, 747, 158, 'bicycle')
        path('M628 781H796')
        text(713, 747, 'rides', 28, 'blue-text')
        text(545, 877, 'Subject', 29); text(883, 877, 'Object', 29)
    zone('hoi', 16, 591, 973, 364, hoi)

    def psg():
        text(1500, 627, '(ii) PSG: things + stuff, masks', 36, 'title')
        image('psg/panoptic-cyclist', 1033, 670, 401, 268)
        node(1458, 679, 155, 'person', '#efb779')
        node(1807, 679, 158, 'bicycle', '#c2c0ff')
        node(1464, 867, 143, 'road', '#ccd1d5')
        node(1822, 867, 129, 'sky', '#dceefa')
        path('M1619 713H1799')
        text(1710, 683, 'rides', 28, 'blue-text')
        path('M1855 753L1582 859')
        text(1750, 840, 'on', 28, 'blue-text')
        path('M1613 901H1812')
        text(1714, 944, 'below', 28, 'blue-text')
    zone('psg', 1015, 591, 973, 364, psg)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[2]
    (site/'example/figure614.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure614-1"><title>Figure 6.14 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.14 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/scene_graph.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig614()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure614-1';mountNative();</script></html>''')
