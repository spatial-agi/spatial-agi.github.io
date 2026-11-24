"""Figure 7.3: topological and graph-based reasoning, source geometry 2000×868."""
import json
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
INFO = {
    'space': ('Free space and obstacles', 'Obstacle geometry separates free configurations from occupied space. Graph construction retains feasible connections through the free region.'),
    'sensing': ('Sensing and odometry', 'Range observations and odometry reveal local connectivity as a robot explores. The dashed rays represent sensing; the dark trace represents motion.'),
    'states': ('Start and goal states', 'A planning query specifies a start and a goal. A valid route connects them while avoiding obstacles.'),
    'constraints': ('Robot and task constraints', 'Robot shape, turning limits and task requirements restrict which graph transitions can be executed.'),
    'priors': ('Optional spatial priors', 'Floor plans or road networks can supply initial connectivity, which sensing can verify and update.'),
    'visibility': ('Visibility graph', 'Connect mutually visible obstacle vertices, start and goal. Graph search then selects a collision-free route around the obstacle.'),
    'voronoi': ('Voronoi and skeleton', 'A skeleton represents free-space connectivity along routes that maintain clearance from obstacles. Junctions connect alternative passages.'),
    'cells': ('Cell decomposition', 'Partition free space into cells and search their adjacency graph. The highlighted sequence passes through unoccupied cells.'),
    'roadmap': ('Roadmaps and trees', 'Sample configurations and connect feasible neighbors. Roadmaps and trees discover routes through the configuration space.'),
    'search': ('Graph search', 'A* or Dijkstra searches edges with assigned costs. Here the highlighted lower route has total cost 2, compared with cost 6 on the upper route.'),
    'hierarchy': ('Multi-agent and hierarchical reasoning', 'Abstract connectivity supports coarse planning; refinement resolves local paths and coordinates transitions among agents.'),
    'path': ('Collision-free path', 'The final route connects the start and goal without intersecting the obstacle.'),
    'map': ('Topological map', 'Vertices represent places or states and edges represent traversable connections. Connectivity is retained without requiring a full metric reconstruction.'),
    'agents': ('Multi-agent trajectories', 'Rows represent vertices A–D and columns represent successive time steps. A horizontal segment means waiting; the two trajectories avoid a shared vertex at the same time.'),
    'coverage': ('Coverage and sweep planning', 'A sweep route visits the accessible region around the obstacle, providing a plan for coverage tasks.'),
}


def fig73():
    out = []
    add = out.append

    def text(x, y, value, size=32, cls='text', raw=False):
        widths = {'Visibility graph':264, 'Voronoi / skeleton':328, 'Cell decomposition':352,
                  'Roadmap / tree':278, 'Graph search':241, 'Multi-agent / hierarchy':382}
        measure = f' textLength="{widths[value]}" lengthAdjust="spacingAndGlyphs"' if cls == 'heading' else ''
        add(f'<text class="f73-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{measure}>{value if raw else escape(value)}</text>')

    def lines(x, y, values, size=32, dy=39):
        for i, value in enumerate(values):
            text(x, y+i*dy, value, size)

    def path(d, cls='ink', extra=''):
        classes = ' '.join('f73-'+v for v in cls.split())
        add(f'<path class="{classes}" d="{d}" {extra}/>')

    def rect(x, y, w, h, cls='frame', rx=0):
        add(f'<rect class="f73-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def node(x, y, cls='node', r=6.5):
        add(f'<circle class="f73-{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def arrow(d, blue=False):
        path(d, 'route '+('blue' if blue else 'ink'), f'marker-end="url(#f73-{"blue" if blue else "ink"}-arrow)"')

    def zone(key, box, draw):
        add(f'<g class="f73-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        rect(*box, 'hit', 5)
        add('</g>')

    def small_path(x, y, w, h):
        rect(x, y, w, h)
        scale = w / 211
        rect(x+round(74*scale), y+25, round(40*scale), 53 if h == 104 else 50, 'obstacle')
        arrow(f'M{x+15} {y+h-17}L{x+round(51*scale)} {y+19}H{x+round(141*scale)}L{x+w-19} {y+47}', True)
        node(x+15, y+h-17, 'blue-node', 5.5)
        node(x+w-19, y+47, 'goal', 7)

    def local_graph(x, y):
        points = [(x, y+24), (x+19, y), (x+41, y+8), (x+71, y), (x+83, y+27), (x+38, y+34)]
        path('M'+'L'.join(f'{a} {b}' for a,b in points)+'Z', 'edge')
        path(f'M{x+19} {y}L{x+38} {y+34}L{x+41} {y+8}', 'edge')
        for a,b in points:
            node(a,b)

    add('<div class="nf nf-73" data-nf="73" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 868" role="group" aria-label="Figure 7.3: topological and graph-based reasoning"><defs>')
    for key, color in [('ink','#2c373d'),('blue','#4146eb')]:
        add(f'<marker id="f73-{key}-arrow" markerUnits="userSpaceOnUse" markerWidth="15" markerHeight="15" refX="12" refY="7.5" orient="auto"><path d="M2 2L12 7.5L2 13" fill="none" stroke="{color}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="868" fill="white"/><g class="f73-scaffold">')
    path('M480 27V777M1500 27V777', 'divider')
    arrow('M490 428H546'); arrow('M1432 428H1487')
    for x, label in [(238,'(i) Inputs'),(993,'(ii) Reasoning core'),(1754,'(iii) Outputs')]:
        text(x,838,label,36,'blue-text')
    text(990,531,'<tspan font-style="italic">G</tspan> = (<tspan font-style="italic">V</tspan>, <tspan font-style="italic">E</tspan>, <tspan font-weight="bold">w</tspan>)',38,'math',True)
    add('</g>')

    def space():
        rect(22,79,170,101); rect(81,104,32,51,'obstacle'); lines(340,118,['Free space /','obstacles'])
    zone('space',(14,65,459,127),space)

    def sensing():
        add('<image href="/assets/img/figs/f73/i-inputs/sensing-device.png" x="31" y="243" width="63" height="53"/>')
        path('M63 267L118 191M63 267L152 211M63 267L163 249','blue dashed flow')
        node(63,267,'blue-node',8)
        path('M88 306L132 286L185 308','ink dashed flow')
        lines(340,267,['Sensing +','odometry'])
    zone('sensing',(22,188,451,131),sensing)

    def states():
        small_path(22,358,170,98); lines(340,394,['Start / goal','states'])
    zone('states',(14,349,459,116),states)

    def constraints():
        add('<image href="/assets/img/figs/f73/i-inputs/robot-body.png" x="24" y="499" width="61" height="102"/>')
        path('M87 588C139 586 173 549 173 502','blue flow')
        lines(340,533,['Robot / task','constraints'])
    zone('constraints',(15,490,458,119),constraints)

    def priors():
        rect(24,650,155,82,'ink'); path('M91 651V676M91 697V732M90 688H155')
        lines(338,677,['Optional priors','Floor plans / roads'],29,38)
    zone('priors',(15,641,458,104),priors)

    def visibility():
        rect(562,41,418,211,'panel',6); text(771,94,'Visibility graph',36,'heading')
        rect(719,133,72,65,'soft-obstacle')
        path('M606 208L719 133H791L932 180M719 133V198M791 133V198','edge')
        path('M606 208L719 198H791L932 180','blue flow')
        for a,b in [(606,208),(719,133),(791,133),(719,198),(791,198),(932,180)]:node(a,b)
        text(609,155,'s',30,'blue-text');text(936,140,'g',30,'blue-text')
    zone('visibility',(562,41,418,211),visibility)

    def voronoi():
        rect(999,41,417,211,'panel',6);text(1207,94,'Voronoi / skeleton',36,'heading')
        rect(1058,120,85,32,'obstacle');rect(1246,195,86,32,'obstacle')
        for d in ['M1034 208L1152 173H1268L1372 134','M1152 173L1177 114','M1268 173L1372 198']:path(d,'blue dashed flow')
        node(1152,173,'blue-node');node(1268,173,'blue-node')
    zone('voronoi',(999,41,417,211),voronoi)

    def cells():
        rect(562,283,418,201,'panel',6);text(771,333,'Cell decomposition',36,'heading')
        rect(609,380,320,82,'frame');rect(716,421,53,41,'soft-obstacle')
        for x in [662,716,769,823,876]:path(f'M{x} 380V462','grid')
        path('M609 421H929','grid');path('M636 442V401H849L903 442','blue flow')
        for a,b in [(636,442),(636,401),(742,401),(849,401),(903,442)]:node(a,b,'blue-node',4.6)
    zone('cells',(562,283,418,201),cells)

    def roadmap():
        rect(999,283,417,201,'panel',6);text(1207,333,'Roadmap / tree',36,'heading')
        rect(1187,409,57,57,'obstacle')
        for d in ['M1036 459L1092 419L1155 377L1250 374L1317 419L1381 390','M1092 419L1083 371','M1092 419L1146 440','M1317 419L1344 465']:path(d,'ink flow')
        for a,b in [(1036,459),(1092,419),(1083,371),(1155,377),(1146,440),(1250,374),(1317,419),(1344,465),(1381,390)]:node(a,b,r=5.4)
    zone('roadmap',(999,283,417,201),roadmap)

    def search():
        rect(562,544,418,217,'panel',6);text(771,601,'Graph search',36,'heading')
        path('M609 692L710 642H810L926 692','edge');path('M609 692L766 729L926 692','blue flow')
        for a,b in [(609,692),(710,642),(810,642),(926,692),(766,729)]:node(a,b,'blue-node',7)
        for x,y,value in [(647,648,'2'),(763,635,'2'),(882,648,'2'),(664,740,'1'),(866,740,'1')]:text(x,y,value,29)
        text(770,790,'A* / Dijkstra',30)
    zone('search',(562,544,418,255),search)

    def hierarchy():
        rect(999,544,417,217,'panel',6);text(1207,601,'Multi-agent / hierarchy',35,'heading')
        path('M1083 642H1309','ink flow');path('M1092 652V688M1287 652V688','edge dashed')
        for x in [1083,1193,1309]:node(x,642,r=8)
        local_graph(1052,707);local_graph(1247,707)
        text(1207,789,'Abstract → refine / coordinate',28)
    zone('hierarchy',(999,544,417,255),hierarchy)

    def output_path():
        small_path(1541,73,211,104);lines(1883,115,['Collision-free','path'])
    zone('path',(1532,65,461,120),output_path)

    def topo_map():
        path('M1549 311L1591 252L1640 274L1703 252L1729 317L1631 332Z M1640 274L1631 332','edge')
        for a,b in [(1549,311),(1591,252),(1640,274),(1703,252),(1729,317),(1631,332)]:node(a,b)
        lines(1883,275,['Topological','map'])
    zone('map',(1532,238,461,108),topo_map)

    def agents():
        path('M1554 522L1633 475H1711','blue flow');path('M1554 381H1633L1711 428','green dashed flow')
        for y,label in [(381,'D'),(428,'C'),(475,'B'),(522,'A')]:
            text(1523,y+7,label,29)
            for x in [1554,1633,1711]:node(x,y,'small-node',4.3)
        text(1746,435,'2',29,'green-text');text(1746,482,'1',29,'blue-text')
        arrow('M1550 560H1720');text(1638,601,'Time',29)
        lines(1883,458,['Multi-agent','trajectories'])
    zone('agents',(1505,358,488,252),agents)

    def coverage():
        rect(1541,644,211,111);rect(1615,671,40,56,'obstacle')
        path('M1557 746V660H1589V746H1607V660H1717V746H1693V678','blue flow')
        lines(1883,687,['Coverage /','sweep plan'])
    zone('coverage',(1532,634,461,130),coverage)

    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    (SITE/'example/figure73.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure73-1"><title>Figure 7.3 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.3 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/713_topo.webp" alt="Original Figure 7.3"><h2>Interactive reconstruction</h2>'''+fig73()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure73-1';mountNative();</script></html>''')
