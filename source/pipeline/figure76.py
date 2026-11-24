"""Figure 7.6, reconstructed in the source image's 2000 × 930 coordinates."""
from html import escape
from pathlib import Path
import json
from math import hypot, radians, cos, sin

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/716_causal.webp'
ASSETS = 'assets/img/figs/f76'
INFO = {
    'events': ('Event streams and spatial variables', 'Align actions, object states and spatial relations on the same timeline to track how events unfold.'),
    'measurements': ('Candidate variables and measurements', 'Convert raw observations into variables such as clearance, visibility and priority violations.'),
    'priors': ('Prior knowledge', 'Physics, commonsense and spatial locality help constrain which causal links are plausible.'),
    'data': ('Interventional data', 'Deliberately change a controllable variable, such as clearance, and observe the resulting outcomes.'),
    'scm': ('Structural causal models and counterfactuals', 'Infer background conditions from the observed trace, change a mechanism or action, and predict what follows for that same case.'),
    'constraints': ('Constraint-based discovery', 'Conditional independence tests can rule out edges. The remaining structure may include links whose direction the data cannot determine.'),
    'score': ('Score and order discovery', 'Score-based methods compare candidate graphs. Order-based methods seek a variable ordering under the assumptions of their model.'),
    'plan': ('Causal action and plan reasoning', 'A causal link records the condition one action establishes for another. Threats can remove that condition, while temporal edges bound differences between event times.'),
    'verify': ('Solver-based verification', 'A solver can return a satisfying witness or, when supported, a proof or core explaining why the encoded constraints cannot all hold.'),
    'model': ('Causal model', 'Directed edges show dependencies. Structural equations describe how each variable depends on its parents and background factors.'),
    'explanation': ('Causal explanation', 'Trace an observed failure back through intermediate events to contributing causes.'),
    'counterfactual': ('Counterfactual answer', 'Keep the actors and obstacles fixed while changing the blue vehicle’s path to compare the predicted outcomes.'),
    'strategy': ('Intervention and prevention', 'Change a controllable action or constraint to help produce a safer outcome.'),
}


def fig76():
    output = []
    add = output.append
    manifest = json.loads((SITE/'assets/figures/elements/figure76/manifest.json').read_text())
    assets = {entry['file'].removesuffix('.png'): entry for entry in manifest['assets']}

    def label(x, y, value, size=18, cls='', anchor='middle', raw=False):
        classes = ' '.join('f76-'+name for name in cls.split())
        add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" class="{classes}">{value if raw else escape(value)}</text>')

    def sub(base, index):
        return f'{base}<tspan baseline-shift="sub" font-size="72%">{index}</tspan>'

    def rect(x, y, width, height, cls='panel', radius=6):
        add(f'<rect class="f76-{cls}" x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}"/>')

    def path(d, cls='ink', marker=''):
        classes = ' '.join('f76-'+name for name in cls.split())
        end = f' marker-end="url(#f76-{marker}-arrow)"' if marker else ''
        add(f'<path class="{classes}" d="{d}"{end}/>')

    def arrow(d, color='ink', dashed=False):
        path(d, color + ' route' + (' dashed' if dashed else ''), color)

    def circle(x, y, radius, cls='node'):
        add(f'<circle cx="{x}" cy="{y}" r="{radius}" class="f76-{cls}"/>')

    def asset(name, placement=0):
        entry = assets[name]
        boxes = entry.get('placement_boxes', [entry['source_box']])
        x, y, right, bottom = boxes[placement]
        add(f'<image href="/{ASSETS}/{name}.png" x="{x}" y="{y}" width="{right-x}" height="{bottom-y}"/>')

    def cube(x, y, side=22, depth=8):
        path(f'M{x} {y}l{depth} {-depth}h{side}l{-depth} {depth}Z','cube-top')
        path(f'M{x} {y}h{side}v{side}h{-side}Z','cube-front')
        path(f'M{x+side+depth} {y-depth}v{side}','thin')

    def check(x, y, scale=1):
        path(f'M{x-9*scale} {y}l{6*scale} {8*scale}l{13*scale} {-17*scale}','green mark')

    def cross(x, y, r=5):
        path(f'M{x-r} {y-r}l{2*r} {2*r}m0 {-2*r}l{-2*r} {2*r}','red mark')

    def tag(x, y, width, height, value, size=16):
        rect(x,y,width,height)
        label(x+width/2,y+height/2+size*.34,value,size)

    def zone(key, frame, draw):
        add(f'<g class="f76-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        rect(*frame)
        draw()
        rect(*frame, 'hit')
        add('</g>')

    def link(a, b, radius=19, directed=True, dashed=False):
        x, y = a
        end_x, end_y = b
        length = hypot(end_x-x, end_y-y)
        dx, dy = (end_x-x)/length, (end_y-y)/length
        d = f'M{x+dx*(radius+3):.2f} {y+dy*(radius+3):.2f}L{end_x-dx*(radius+5):.2f} {end_y-dy*(radius+5):.2f}'
        if directed:
            arrow(d)
        else:
            path(d, 'removed' if dashed else 'ink')

    def graph(points, edges, radius=18.5):
        for a,b,kind in edges:
            link(points[a],points[b],radius,kind == 'directed',kind == 'removed')
        for index,(x,y) in enumerate(points,1):
            circle(x,y,radius)
            label(x,y+6,f'X{index}',17)

    add('<div class="nf nf-76" data-nf="76" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 930" role="group" aria-label="Figure 7.6: causal reasoning"><defs>')
    for color in ('ink','blue','red','green'):
        add(f'<marker id="f76-{color}-arrow" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" refX="10" refY="5.5" orient="auto"><path class="f76-head f76-{color}" d="M1 1L10 5.5L1 10Z"/></marker>')
    add('</defs><rect width="2000" height="930" fill="white"/><g class="f76-scaffold">')
    arrow('M502 442H532');arrow('M1457 442H1499')
    for x,value in [(251,'(i) Inputs'),(995,'(ii) Reasoning core'),(1749,'(iii) Outputs')]:
        label(x,913,value,26,'blue-text')
    add('</g>')

    def events():
        label(251,62,'1. Event streams + spatial variables',23)
        arrow('M101 97H453')
        for index,x in enumerate((138,210,282,354,427)):
            label(x,82,f't{index}',16)
        for value,y in [('actions',146),('states',196),('relations',250)]:
            label(55,y,value,19)
        for x,value in [(100,'blocked'),(226,'contact'),(345,'delay')]:
            tag(x,251,101,31,value)
        for x in (135,242,345):cube(x,182)
        arrow('M166 141H224','blue',True);arrow('M273 141H331','red',True)
        arrow('M166 245H224',dashed=True);arrow('M273 245H331',dashed=True)
        for index in range(3):asset('i-inputs/event-blue-agent',index)
        for index in range(3):asset('i-inputs/event-red-agent',index)
    zone('events',(8,22,487,266),events)

    def measurements():
        label(251,345,'2. Candidate variables / measurements',23)
        label(125,388,'Raw observations',20);label(360,388,'Causal variables',20)
        rect(22,443,50,34);circle(47,460,6)
        rect(126,423,25,21,'grid-accent',0)
        rect(100,402,76,63,'grid',0)
        path('M125 402V465M151 402V465M100 423H176M100 444H176','grid')
        arrow('M204 439H249')
        for y,value in [(400,'clearance'),(435,'priority violated'),(470,'visible')]:
            tag(282,y,161,28,value,17)
    zone('measurements',(8,304,487,211),measurements)

    def priors():
        label(251,571,'3. Prior knowledge',23)
        for x,value in [(94,'physics'),(251,'commonsense'),(414,'locality')]:label(x,603,value,18)
        path('M44 663H132');cube(63,637);arrow('M110 618V657')
        circle(251,634,14);path('M244 653H258M244 662H258')
        path('M384 644H446M399 616L430 671M430 616L399 671','grid')
        for x,y in [(384,644),(446,644),(399,616),(430,616),(399,671),(430,671)]:
            circle(x,y,4.6)
    zone('priors',(8,531,487,150),priors)

    def data():
        label(251,737,'4. Interventional data',23)
        for name in ('arm','blue-agent','red-agent','blue-car'):asset('i-inputs/intervention-'+name)
        label(75,868,'do(X = x)',22,'math blue-text')
        rect(138,779,141,59)
        label(209,802,'Clearance',17);label(209,822,'low ↔ high',17)
        cross(342,845);check(426,845,.83)
    zone('data',(8,696,487,180),data)

    def scm():
        label(692,81,'SCM / counterfactual',23)
        graph([(587,165),(683,165),(779,165),(625,248),(740,248)],
              [(0,1,'directed'),(1,2,'directed'),(0,3,'directed'),(1,4,'directed'),(2,4,'directed'),(3,4,'directed')])
        rect(574,302,233,56)
        arrow('M587 273V190');circle(587,289,14)
        label(587,295,sub('U',1),18,raw=True)
        label(690,334,f'{sub("X","i")} := {sub("f","i")}(Pa<tspan baseline-shift="sub" font-size="72%">i</tspan>, {sub("U","i")})',22,'math',raw=True)
        arrow('M609 402L651 365','blue');arrow('M773 402L733 365')
        label(622,422,f'do({sub("X","i")} = x)',22,'math blue-text',raw=True)
        label(768,422,'What if?',18);label(692,459,'Abduce → act → predict',18)
    zone('scm',(540,35,305,439),scm)

    def constraints():
        label(998,67,'Constraint-based',23);label(998,95,'discovery',23);label(998,118,'PC / FCI',20)
        graph([(898,163),(993,163),(1089,163),(936,242),(1051,242)],
              [(0,1,'plain'),(1,2,'plain'),(0,3,'directed'),(1,4,'directed'),(2,4,'directed'),(3,4,'removed')])
        label(996,314,'CI tests remove edges')
        path('M895 351H949','removed');label(1039,355,'removed')
        path('M895 395H949');label(1039,399,'unoriented')
        tag(901,415,195,43,'Locality-restricted tests',17)
    zone('constraints',(854,35,286,439),constraints)

    def score():
        label(1297,81,'Score / order discovery',23);label(1297,121,'GES / FGES / LiNGAM',19)
        label(1297,170,'Candidate structures')
        for x in (1206,1297,1388):
            arrow(f'M{x-20} 218L{x-5} 246');arrow(f'M{x+20} 218L{x+5} 246')
            for dx,y in [(-22,213),(22,213),(0,250)]:circle(x+dx,y,5.2)
        label(1297,296,'Model score (e.g., BIC)')
        cx,cy=1297,374
        def point(radius,angle):
            return f'{cx+radius*cos(radians(angle)):.2f} {cy-radius*sin(radians(angle)):.2f}'
        for start,end,color in [(180,135,'safe'),(135,90,'neutral'),(90,45,'warn'),(45,0,'danger')]:
            path(f'M{point(75,start)}A75 75 0 0 1 {point(75,end)}L{point(61,end)}A61 61 0 0 0 {point(61,start)}Z','gauge-'+color)
        path('M1297 373L1347 328')
        label(1297,415,'LiNGAM ordering')
        for x in (1193,1262,1331):arrow(f'M{x+19} 452H{x+48}')
        for index,x in enumerate((1193,1262,1331,1400),1):
            circle(x,452,14.5);label(x,458,f'X{index}',17)
    zone('score',(1149,35,296,439),score)

    def plan():
        label(756,536,'Causal action / plan reasoning',23)
        for x,value in [(571,'A'),(728,'B'),(889,'C')]:tag(x,571,50,51,value,20)
        arrow('M625 597H719');label(675,572,'p',18,'blue-text')
        arrow('M914 623V656L686 619','red',True);label(821,660,'threat: deletes p',17,'red-text')
        label(754,707,'Temporal difference constraints')
        for x,value in [(603,'A'),(754,'B'),(907,'C')]:
            circle(x,763,17.5);label(x,768,sub('T',value),22,'math',raw=True)
        arrow('M628 763H725');arrow('M780 763H879')
        label(676,732,'≤ 5',17);label(832,732,'≤ 3',17)
        label(753,842,'Edges bound time differences')
    zone('plan',(540,493,430,383),plan)

    def verify():
        label(1213,536,'Solver-based verification',23);label(1212,576,'SAT / SMT',19)
        rect(1011,606,88,91);label(1055,636,'Rules');label(1055,655,'…');label(1055,674,'…')
        tag(1143,625,122,56,'Solver',20);arrow('M1102 653H1137')
        arrow('M1268 644L1346 604','green');arrow('M1268 669L1346 712','red')
        label(1376,588,'SAT',18,'green-text');label(1376,625,'witness',18)
        label(1376,704,'UNSAT',18,'red-text');label(1372,746,'proof / core',18)
        for name in ('safety-shield','multi-agent-left','multi-agent-right','diagnosis-lens'):asset('ii-core/'+name)
        check(1064,796,.51)
        for x,value in [(1064,'safety'),(1218,'multi-agent'),(1368,'diagnosis')]:label(x,852,value)
    zone('verify',(980,493,465,383),verify)

    def model():
        label(1750,68,'1. Causal model',23)
        graph([(1560,136),(1650,136),(1740,136),(1597,204),(1704,204)],
              [(0,1,'directed'),(1,2,'directed'),(0,3,'directed'),(1,4,'directed'),(2,4,'directed'),(3,4,'directed')])
        rect(1771,97,188,129);label(1865,130,'mechanisms',20)
        label(1865,167,f'{sub("X",1)} = {sub("f",1)}({sub("U",1)})',20,'math',raw=True)
        label(1865,202,f'{sub("X",2)} = {sub("f",2)}({sub("X",1)}, {sub("U",2)})',20,'math',raw=True)
    zone('model',(1510,22,481,235),model)

    def car(color,index):
        asset(f'iii-outputs/explanation-{color}-car',index)

    def explanation():
        label(1750,317,'2. Explanation',23)
        label(1617,358,'Observed failure');label(1855,358,'Causal explanation')
        car('blue',0);car('red',0);cross(1617,402,3.6)
        for x,value in [(1765,sub('P',1)),(1846,sub('P',2)),(1937,'F')]:
            circle(x,405,16,'red-node' if value=='F' else 'node')
            label(x,411,value,19,'red-text' if value=='F' else '',raw=True)
        arrow('M1786 405H1822');arrow('M1867 405H1913')
        label(1771,459,'primary',16);label(1878,459,'intermediate',16)
    zone('explanation',(1510,273,481,204),explanation)

    def scene(index, start, end, obstacle_x, y, detour):
        car('blue',index);car('red',index)
        cube(obstacle_x,y+10,20,8)
        route_y=y-24 if detour else y-9
        path(f'M{start} {y+6}L{start+28} {route_y}H{end-30}L{end} {y+7}','blue flow dashed')
        arrow(f'M{end-23} {y+4}H{obstacle_x+18}','red',True)
        if detour:check(obstacle_x+5,y+47,.86)
        else:cross(obstacle_x+6,y+47,4.6)

    def counterfactual():
        label(1750,536,'3. Counterfactual answer',23)
        label(1623,578,'Actual trace');label(1864,578,'Different action')
        scene(1,1567,1695,1623,611,False)
        scene(2,1808,1937,1865,611,True)
    zone('counterfactual',(1510,493,481,191),counterfactual)

    def strategy():
        label(1750,743,'4. Intervention / prevention strategy',23)
        asset('iii-outputs/strategy-shield');check(1563,791,.51)
        asset('iii-outputs/strategy-arm')
        arrow('M1677 813H1737');label(1868,767,'Safe outcome')
        scene(3,1792,1937,1856,799,True)
    zone('strategy',(1510,700,481,176),strategy)

    info = json.dumps({key:{'t':title,'b':body} for key,(title,body) in INFO.items()})
    add(f'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">{info}</script></div>')
    return ''.join(output)


if __name__ == '__main__':
    (SITE/'example/figure76.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.6 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure76-1">
<style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style>
<main><h1>Figure 7.6 · Original and interactive reconstruction</h1>
<h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="930" alt="Original Figure 7.6">
<h2>Interactive reconstruction</h2>{fig76()}</main>
<script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure76-1';mountNative();</script>
</html>''')
