"""Faithful native reconstruction of Figure 7.8, in 2000 × 933 source coordinates."""
from html import escape
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/implicit_neural_spatial_reasoning_method.webp'
INFO = {
 'relation': ('Relation Network', 'A shared relation function combines pairs of object features with a query. Summing these pairwise embeddings produces a representation for the output head.'),
 'graph': ('GNN / latent graph', 'Each node receives messages from its neighbors. The blue edges illustrate messages aggregated at the selected node; the graph can be learned rather than supplied as a symbolic program.'),
 'attention': ('Spatial attention', 'Spatial weights select locations in a feature grid. Multiplication emphasizes the selected regions while retaining their spatial arrangement.'),
 'pyramid': ('Feature Pyramid Network', 'Lateral connections combine local features with a top-down pathway. Coarse semantic information is fused with finer spatial detail across scales.'),
 'film': ('Conditional feature modulation', 'The query or context predicts a scale and offset for each feature channel. FiLM applies the same channel-wise affine transform at every spatial location.'),
 'capsules': ('Capsule routing', 'Part capsules vote for a whole-object pose. Routing by agreement strengthens contributions whose predicted poses agree with the whole capsule.'),
 'equivariance': ('Equivariant features', 'Transforming the input and then computing features matches computing the features first and applying their corresponding transformation. The feature response follows the chosen symmetry.'),
}

def fig78():
    out=[];add=out.append
    entries=json.loads((SITE/'assets/figures/elements/figure78/manifest.json').read_text())['assets']
    assets={a['file'].removesuffix('.png'):a for a in entries}

    def text(x,y,value,size=31,cls='',raw=False):
        add(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" class="{" ".join("f78-"+s for s in cls.split())}">{value if raw else escape(value)}</text>')

    def sub(value,index):
        return f'{value}<tspan baseline-shift="sub" font-size="70%">{index}</tspan>'

    def path(d,cls='ink',arrow=False):
        classes=' '.join('f78-'+s for s in cls.split())
        marker=f' marker-end="url(#f78-{"blue" if "blue" in cls else "gray"}-arrow)"' if arrow else ''
        add(f'<path d="{d}" class="{classes}"{marker}/>')

    def arrow(d,color='blue'):
        path(d,color+' route',True)

    def box(x,y,w,h,cls='box',rx=7):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="f78-{cls}"/>')

    def asset(name,index=0):
        a=assets[name];x,y,r,b=a.get('placement_boxes',[a['source_box']])[index]
        add(f'<image href="/assets/img/figs/f78/{name}.png" x="{x}" y="{y}" width="{r-x}" height="{b-y}"/>')

    def node(x,y,selected=False):
        add(f'<circle cx="{x}" cy="{y}" r="19" class="f78-{"selected" if selected else "node"}"/>')

    def zone(key,bounds,draw):
        add(f'<g class="f78-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        x,y,w,h=bounds
        add(f'<rect class="f78-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/></g>')

    add('<div class="nf nf-78" data-nf="78" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 933" role="group" aria-label="Figure 7.8: mechanisms for implicit neural spatial reasoning"><defs>')
    for color,fill in [('blue','#3c44eb'),('gray','#a8b1b8')]:
        add(f'<marker id="f78-{color}-arrow" markerUnits="userSpaceOnUse" markerWidth="15" markerHeight="15" refX="12" refY="7.5" orient="auto"><path d="M2 3L12 7.5L2 12Z" fill="{fill}" stroke="{fill}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="933" fill="white"/><g class="f78-scaffold">')
    for x in (497,998,1498):path(f'M{x} 18V921','divider')
    for x,lines in [(249,['(a) Relational','aggregation']),(749,['(b) Attention +','multi-scale fusion']),(1249,['(c) Conditional','modulation']),(1749,['(d) Geometry-aware','inductive biases'])]:
        for y,line in zip((50,85),lines):text(x,y,line,36,'heading')
    add('</g>')

    def relation():
        text(249,174,'Relation Network',36,'heading')
        for x,value in [(34,sub('o','1')),(146,sub('o','2')),(258,sub('o','n'))]:
            box(x,202,81,78)
            text(x+40.5,246,value,31,raw=True)
        text(404,250,'q',31,'blue-text')
        for d in ('M83 285L236 324','M195 288L239 320','M291 289L260 320','M395 286L261 324'):arrow(d,'gray')
        box(106,329,286,94,'accent')
        text(249,382,f'{sub("g","θ")}({sub("o","i")}, {sub("o","j")}, q)',36,'math',True)
        arrow('M249 431V456')
        text(249,511,'Sum → fφ → output',33,'blue-text')
    zone('relation',(20,133,460,397),relation)

    def graph():
        text(249,593,'GNN / latent graph',36,'heading')
        for d in ('M93 749L176 659','M93 749L249 811','M249 811L398 768'):path(d,'gray')
        for x,y in [(93,749),(176,659),(249,811),(398,768)]:node(x,y)
        node(289,688,True)
        for d in ('M186 662L278 684','M252 802L284 701','M390 762L301 696'):arrow(d)
        text(249,890,'Aggregate neighbor messages',30)
    zone('graph',(22,555,456,351),graph)

    def attention():
        text(749,174,'Spatial attention',36,'heading')
        asset('b-attention/features');asset('b-attention/weights');asset('b-attention/weights',1)
        text(674,280,'×',29,'blue-text');text(823,280,'=',31)
        for x,label,cls in [(599,'features',''),(749,'weights','blue-text'),(901,'weighted','')]:text(x,381,label,30,cls)
    zone('attention',(520,133,458,264),attention)

    def pyramid():
        text(749,472,'Feature Pyramid Network',36,'heading')
        for name in ('coarse','middle','fine'):asset('b-pyramid/'+name)
        for d in ('M578 623V614','M578 720V706','M627 569H738','M646 662H719','M664 762H701'):arrow(d,'gray')
        for x,y,w in [(758,541,69),(739,634,106),(721,734,143)]:box(x,y,w,56,'accent')
        arrow('M792 605V614');arrow('M792 703V714')
        text(929,576,'coarse',30);text(929,769,'fine',30)
        text(749,891,'Top-down + lateral fusion',30)
    zone('pyramid',(505,435,487,475),pyramid)

    def film():
        text(1249,174,'FiLM',36,'heading')
        box(1066,211,367,88,'accent');text(1249,263,'Query / context c',33)
        arrow('M1249 307V335')
        box(1094,354,311,94);text(1249,410,'Predict γ, β',36)
        arrow('M1196 459V512');arrow('M1305 459V512')
        asset('c-modulation/features');asset('c-modulation/modulated')
        arrow('M1218 603H1270')
        text(1132,720,'F',31);text(1374,720,"F'",31,'blue-text')
        text(1249,792,f'{sub("F′","k")} = {sub("γ","k")}{sub("F","k")} + {sub("β","k")}',36,'math blue-text',True)
        text(1249,873,'Per-channel affine transform',30)
        text(1249,900,'Shared across spatial locations',30)
    zone('film',(1014,132,470,780),film)

    def capsules():
        text(1749,174,'Capsule routing',36,'heading')
        box(1681,202,137,72,'accent');arrow('M1732 255L1761 227')
        for d,color in [('M1624 341L1737 280','blue'),('M1747 336L1749 287','blue'),('M1869 341L1762 280','gray')]:arrow(d,color)
        for i in range(3):asset('d-geometry/part-capsule',i)
        text(1749,464,'Parts → whole: pose agreement',30)
    zone('capsules',(1514,132,470,351),capsules)

    def equivariance():
        text(1749,556,'Equivariant features',36,'heading')
        text(1749,604,'transform',30,'blue-text')
        text(1604,636,'x',31);text(1896,636,'T x',31)
        arrow('M1653 628H1833')
        arrow('M1604 670V714','gray');arrow('M1896 670V714','gray')
        text(1604,776,'Φ(x)',31);text(1896,776,'ρ(T) Φ(x)',31)
        arrow('M1684 768H1799')
        text(1749,825,'matching feature transform',29,'blue-text')
        text(1749,890,'Predictable response to symmetry',30)
    zone('equivariance',(1514,514,477,392),equivariance)
    info=json.dumps({key:{'t':title,'b':body} for key,(title,body) in INFO.items()})
    add(f'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">{info}</script></div>')
    return ''.join(out)


if __name__=='__main__':
    (SITE/'example/figure78.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.8 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure78-1">
<style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style>
<main><h1>Figure 7.8 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="933" alt="Original Figure 7.8"><h2>Interactive reconstruction</h2>{fig78()}</main>
<script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure78-1';mountNative();</script></html>''')
