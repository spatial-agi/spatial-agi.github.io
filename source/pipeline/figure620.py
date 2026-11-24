"""Faithful interactive reconstruction of Figure 6.20: SLAM module data flow."""
import json
import math
import random
from html import escape
from pathlib import Path

INFO = {
    'sensors': {'t': 'Sensor observations', 'b': 'Camera, LiDAR, IMU and wheel or GPS measurements provide observations for motion estimation and place recognition. Raw observations also reach mapping.'},
    'odometry': {'t': 'Odometry: local motion', 'b': 'The visual or LiDAR front end matches consecutive observations and estimates local pose changes. These relative-motion constraints enter back-end optimization.'},
    'loop': {'t': 'Loop closing: retrieve and verify', 'b': 'The current observation is compared with historical views. A geometrically verified revisit supplies an additional constraint to the back end.'},
    'backend': {'t': 'Back-end optimization', 'b': 'Bundle adjustment or pose-graph optimization jointly refines poses and landmarks. The blue curved edge connects revisited poses; it is a constraint, not an execution-loop arrow.'},
    'mapping': {'t': 'Mapping: register and fuse', 'b': 'Mapping registers raw observations using optimized poses and landmarks. Sparse, dense and topological maps are alternative representations.'},
    'output': {'t': 'Map and trajectory', 'b': 'The result combines a consistent environment map with the estimated sensor trajectory. The blue polyline shows the trajectory through the mapped environment.'},
}


def fig620():
    out = []
    add = out.append

    def text(x, y, value, size=28, cls='text', anchor='middle'):
        add(f'<text class="f620-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{value}</text>')

    def path(d, cls='ink', arrow=False, flow=False):
        add(f'<path class="f620-{cls}{" f620-route" if flow else ""}" d="{d}"' + (f' marker-end="url(#f620-{"gray" if cls == "raw" else "blue"})"' if arrow else '') + '/>')

    def rect(x, y, w, h, cls='border', rx=7):
        add(f'<rect class="f620-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def circle(x, y, r, cls='dot'):
        add(f'<circle class="f620-{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def image(name, x, y, w, h):
        add(f'<image href="/assets/img/figs/f620/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')

    def zone(key, x, y, w, h, draw):
        add(f'<g class="f620-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw()
        rect(x, y, w, h, 'hit')
        add('</g>')

    add('<div class="nf nf-620" data-nf="620" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 847" role="group" aria-label="Figure 6.20: SLAM module data flow"><defs>')
    for name, color in [('blue', '#4146eb'), ('gray', '#aab2b9')]:
        add(f'<marker id="f620-{name}" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="11" refY="7.5" orient="auto"><path d="M2 2.5L11 7.5L2 12.5" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="847" fill="white"/>')

    # Shared data routes use the original bends and arrow sizes.
    add('<g class="f620-scaffold">')
    text(1095, 56, 'Raw observations for map integration')
    path('M296 90H1526V241', 'raw', True, True)
    path('M295.5 90V662', 'bus')
    path('M240 428H286', 'blue', True, True)
    path('M298 286H346', 'blue', True, True)
    path('M298 662H346', 'blue', True, True)
    circle(295.5, 428, 8)
    path('M738 341.5H809.5V406H869', 'blue', True, True)
    text(805, 470, 'Local pose'); text(805, 503, 'change')
    path('M738 683.5H809.5V593.5H869', 'blue', True, True)
    text(812, 744, 'Revisit'); text(812, 777, 'constraints')
    path('M1247 471H1386', 'blue', True, True)
    text(1317, 367, 'Optimized'); text(1317, 416, 'poses +'); text(1317, 533, 'landmarks')
    path('M1711 471H1786', 'blue', True, True)
    add('</g>')

    def sensors():
        text(132, 184, 'Sensor'); text(132, 217, 'observations')
        rect(12, 261.5, 222, 443)
        text(123, 320, 'Sensors', 36, 'title')
        rect(35, 374, 37, 28, 'icon', 0); circle(54, 388, 8.5, 'ring')
        text(89, 394, 'Camera', anchor='start')
        rect(40, 458, 28, 23, 'lidar', 0)
        path('M54 483V506M54 483L36 503M54 483L73 503', 'rays')
        text(101, 477, 'LiDAR', anchor='start')
        path('M54 556V535M54 556L70 557M54 556L45 566', 'blue', True)
        path('M54 556V535', 'blue', True); path('M54 556L70 557', 'blue', True)
        text(114, 562, 'IMU', anchor='start')
        circle(54, 637, 15, 'ring')
        for angle in range(0, 180, 60):
            dx, dy = 13 * math.cos(math.radians(angle)), 13 * math.sin(math.radians(angle))
            path(f'M{54-dx} {637-dy}L{54+dx} {637+dy}', 'wheel')
        text(142, 627, 'Wheel /'); text(142, 660, 'GPS')
    zone('sensors', 12, 156, 222, 549, sensors)

    def odometry():
        rect(357, 144.5, 376, 271)
        text(545, 199, '(1) Odometry', 36, 'title')
        text(545, 253, 'Visual / LiDAR front end')
        image('odometry/frame-01', 381, 280, 112, 111)
        image('odometry/frame-02', 596, 280, 112, 111)
        for x, y, xx, yy in [(480,298,609,295), (480,329,609,326), (480,366,609,364)]:
            path(f'M{x} {y}L{xx} {yy}', 'match', flow=True)
            circle(x,y,4.5,'blue-dot');circle(xx,yy,4.5,'blue-dot')
    zone('odometry', 357, 144.5, 376, 271, odometry)

    def loop():
        rect(357, 523, 376, 290)
        text(545, 581, '(3) Loop closing', 36, 'title')
        text(437, 634, 'Current'); text(634, 634, 'History')
        image('loop-closing/current', 381, 655, 87, 87)
        image('loop-closing/history-01', 550, 670, 72, 72)
        # Selection border and its white inset are independent frontend elements.
        rect(633.5, 667.5, 77, 77, 'selection', 0)
        image('loop-closing/history-02', 637, 671, 70, 70)
        path('M480 704.5H531', 'blue', True, True)
        text(545, 788, 'Retrieve + verify revisit', 28, 'blue-text')
    zone('loop', 357, 523, 376, 290, loop)

    def backend():
        rect(880, 236.5, 360, 450)
        text(1060, 295, '(2) Back end', 36, 'title')
        text(1060, 350, 'Bundle adjustment /'); text(1060, 383, 'pose-graph optimization')
        path('M936 539L997 446L1060 539L1123 446L1185 539M936 539H1185', 'graph')
        for x, label in [(997, '1'), (1123, '2')]:
            rect(x-12, 434, 24, 24, 'landmark', 0)
            text(x, 455, f'<tspan font-style="italic">l</tspan><tspan baseline-shift="sub" font-size="18">{label}</tspan>', 29, 'math')
        for x, label in [(936, '1'), (1060, '2'), (1185, '3')]:
            circle(x, 539, 20, 'node')
            text(x, 548, f'<tspan font-style="italic">x</tspan><tspan baseline-shift="sub" font-size="21">{label}</tspan>', 32, 'math')
        path('M944 574Q1060 645 1177 574', 'revisit')
        text(1060, 650, 'Revisit edge', 28, 'blue-text')
    zone('backend', 880, 236.5, 360, 450, backend)

    def mapping():
        rect(1397, 252.5, 308, 434)
        text(1551, 307, '(4) Mapping', 36, 'title')
        for x,y in [(1430,379),(1443,380),(1456,380),(1469,380),(1484,385),(1485,395),(1476,401),(1468,386),(1437,393),(1428,411),(1437,406),(1453,418),(1454,428),(1447,436),(1435,432),(1440,440),(1454,434),(1469,444),(1476,437)]:
            circle(x,y,4)
        # Dense mesh: three slanted columns with the source triangulation.
        path('M1528 389L1526 450L1546 446L1565 448L1584 426M1526 409L1547 387L1545 446M1546 407L1566 386L1563 447M1564 407L1585 386M1527 409L1584 406M1527 430L1584 426M1526 450L1546 428L1565 407M1527 430L1547 407L1566 386M1546 446L1565 427L1584 406', 'mesh')
        path('M1624 382L1646 416L1671 382M1646 416L1621 453M1646 416L1677 453', 'graph')
        for x,y in [(1624,382),(1646,416),(1671,382),(1621,453),(1677,453)]: circle(x,y,5.5,'small-node')
        text(1551, 511, 'Sparse / dense /'); text(1551, 560, 'topological')
        text(1551, 634, 'Register / fuse', 28, 'blue-text')
    zone('mapping', 1397, 252.5, 308, 434, mapping)

    def output():
        rect(1797, 252.5, 191, 434)
        text(1892, 316, 'Map +', 36, 'title');text(1892, 377, 'trajectory', 36, 'title')
        rng = random.Random(620)
        for x1,y1,x2,y2 in [(1827,427,1957,427),(1957,427,1957,622),(1957,622,1827,622),(1827,622,1827,427),(1860,498,1930,498)]:
            count = round(math.hypot(x2-x1,y2-y1)/5)
            for i in range(count+1):
                t = i/count
                circle(round(x1+(x2-x1)*t+rng.uniform(-2.6,2.6),2), round(y1+(y2-y1)*t+rng.uniform(-2.6,2.6),2), rng.uniform(3.1,4.3), 'map-point')
        path('M1877 458L1929 449L1938.5 514L1935 585L1879 566L1840 600', 'trajectory', flow=True)
        for x,y in [(1877,458),(1929,449),(1938.5,514),(1935,585),(1879,566),(1840,600)]: circle(x,y,5,'blue-dot')
    zone('output', 1797, 252.5, 191, 434, output)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">' + json.dumps(INFO) + '</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[2]
    (site / 'example/figure620.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure620-1"><title>Figure 6.20 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.20 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/slam_method.webp"><h2 id="redraw">Interactive reconstruction</h2>''' + fig620() + '''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure620-1';mountNative();</script></html>''')
