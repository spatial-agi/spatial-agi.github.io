"""Source-aligned reconstruction of Figure 6.24: temporal localization methods."""
import json
from html import escape
from pathlib import Path
SITE = Path(__file__).resolve().parents[2]
INFO = {
    'window': {'t':'Window-based localization','b':'A classifier scores sliding video windows. High-scoring windows are merged or filtered with non-maximum suppression to obtain action intervals.'},
    'proposal': {'t':'Two-stage proposal-based localization','b':'A proposal generator such as BSN or BMN suggests candidate temporal intervals. A second stage classifies each proposal and refines its start and end boundaries.'},
    'anchor': {'t':'One-stage anchor-free localization','b':'Multi-scale temporal features support predictions at each time position. The model estimates left and right boundary offsets together with an action class, as in ActionFormer and TriDet.'},
    'tal-transformer': {'t':'TAL with set prediction','b':'A Transformer encoder–decoder jointly predicts a set of action segments, classes and confidence scores. The query circles represent prediction slots rather than predefined temporal anchors.'},
    'matching': {'t':'Cross-modal matching','b':'A text encoder embeds the query. Cross-modal ranking compares it with video clip proposals and ranks the candidate moments. The displayed scores are illustrative.'},
    'map': {'t':'Temporal-map reasoning','b':'A temporal map represents candidate moments by start and end positions. Only start-before-end pairs are valid; the hatched cells are invalid. Context between valid candidates supports query-conditioned localization.'},
    'graph': {'t':'Proposal-graph alternative','b':'Graph nodes represent candidate moments. Edges relate the proposals so that information can be exchanged between neighboring or related moments. This is an alternative to the temporal-map representation.'},
    'tsg-transformer': {'t':'TSG with set prediction','b':'The text query and video features enter a Transformer encoder–decoder. The model directly predicts moments and their matching scores.'},
    'corpus': {'t':'Corpus-level retrieval extension','b':'For a collection of videos, first rank videos against the query and then localize the matching moment. This extension is separate from the single-video set-prediction pipeline.'},
}

def fig624():
    out=[]; add=out.append
    def rect(x,y,w,h,cls='module',rx=0):
        add(f'<rect class="f624-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
    def text(x,y,t,size=31,cls='text',anchor='middle',raw=False):
        add(f'<text class="f624-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{t if raw else escape(t)}</text>')
    def path(d,cls='blue',arrow=False,flow=False):
        add(f'<path class="f624-{cls}{" f624-route" if flow else ""}" d="{d}"'+(f' marker-end="url(#f624-{"ink" if cls=="ink" else "blue"})"' if arrow else '')+'/>')
    def circle(x,y,r=15,cls='query'):
        add(f'<circle class="f624-{cls}" cx="{x}" cy="{y}" r="{r}"/>')
    def frames(x,y,size=120,gap=12):
        for i in range(3):
            add(f'<image href="/assets/img/figs/f624/shared-video/frame-{i:02}.png" x="{x+i*(size+gap)}" y="{y}" width="{size}" height="{size}"/>')
            rect(x+i*(size+gap)-1,y-1,size+2,size+2,'image-border')
    def zone(k,x,y,w,h,draw):
        add(f'<g class="f624-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">')
        draw();rect(x,y,w,h,'hit',5);add('</g>')
    def timeline(x,y,w=370):path(f'M{x} {y}h{w}','ink',True,True)
    def segment(x,y,w,left,length):
        path(f'M{x} {y}h{w}','rule');rect(x+left,y-17,length,34,'segment')
    def block(x,y,w,h,lines,size=34):
        rect(x,y,w,h,'module',7)
        for i,t in enumerate(lines):text(x+w/2,y+h/2+(i-(len(lines)-1)/2)*42+size*.32,t,size)
    def math(x,y,t,size=34,blue=False):text(x,y,t,size,'math-blue' if blue else 'math',raw=True)
    def transformer(x,y,w,h,radius=15):
        block(x,y,w,h,[],34)
        text(x+w/2,y+80,'Transformer',34);text(x+w/2,y+122,'encoder–decoder',34)
        for cx in [x+w*.2,x+w*.5,x+w*.8]:circle(cx,y+h-28,radius)
    add('<div class="nf nf-624" data-nf="624" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1570" role="group" aria-label="Figure 6.24: temporal localization method families"><defs>')
    for name,color in [('blue','#4146eb'),('ink','#2c373d')]:
        add(f'<marker id="f624-{name}" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto"><path d="M3 3L12 8L3 13" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('<pattern id="f624-hatch" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" fill="#e9ecef"/><path d="M-8 8L8 -8M0 32L32 0M24 40L40 24" stroke="#aab2b9" stroke-width="4"/></pattern></defs><rect width="2000" height="1570" fill="white"/>')
    add('<g class="f624-scaffold">')
    text(1000,49,'TAL · detect instances of predefined action classes',36,'heading')
    for x in [500,1000,1500]:path(f'M{x} 94V743','divider')
    path('M17 846H1983','rule')
    text(1000,898,'TSG · query: “the person opens the microwave”',36,'heading')
    for x in [667,1333]:path(f'M{x} 928V1553','divider')
    for x,lines in [(250,['(i) Window-based']),(750,['(ii) Two-stage','proposal-based']),(1250,['(iii) One-stage','anchor-free']),(1750,['(iv) Transformer','set prediction'])]:
        for i,t in enumerate(lines):text(x,(163 if len(lines)==1 else 142)+i*42,t,36,'title')
    for x,t in [(333,'(a) Cross-modal matching'),(1000,'(b) Map / graph reasoning'),(1667,'(c) Transformer set prediction')]:text(x,975,t,36,'title')
    add('</g>')
    def window():
        frames(52,237);rect(46,231,265,133,'window')
        timeline(60,381,365);path('M250 373V406',arrow=True,flow=True)
        block(61,412,376,96,['Window classifier'])
        for x,y,h,w in [(92,584,26,30),(144,560,50,32),(197,532,78,31),(249,550,60,31),(301,584,26,32),(354,597,13,31)]:rect(x,y,w,h,'segment')
        text(250,654,'Scores → merge / NMS',31)
        segment(60,700,388,78,162);text(250,780,'IDT + classification',31)
    zone('window',39,226,415,572,window)
    def proposal():
        frames(552,237);timeline(560,381,365);path('M750 373V406',arrow=True,flow=True)
        block(547,412,407,96,['BSN / BMN proposals'])
        for y,left,length in [(543,22,132),(583,88,170),(623,168,160)]:segment(565,y,366,left,length)
        path('M751 650V676',arrow=True,flow=True)
        block(560,686,382,83,['Classify + refine'],32)
        math(750,813,'(<tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">s</tspan>, <tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">e</tspan>, <tspan font-style="italic">c</tspan>, score)')
    zone('proposal',541,226,419,600,proposal)
    def anchor():
        frames(1052,237);timeline(1060,381,365);path('M1250 373V406',arrow=True,flow=True)
        block(1049,412,400,96,['Multi-scale features'])
        for row,n in enumerate([7,5,3]):
            for i in range(n):rect(1108+i*40,540+row*28,32,17,'feature')
        path('M1085 652H1408','rule');path('M1249 646H1118',arrow=True,flow=True);path('M1249 646H1381',arrow=True,flow=True);circle(1249,652,9,'point')
        for x,t in [(1112,'t<tspan baseline-shift="sub" font-size="23">s</tspan>'),(1249,'t'),(1383,'t<tspan baseline-shift="sub" font-size="23">e</tspan>')]:math(x,705,t)
        text(1250,765,'Boundary offsets + class',31);text(1250,814,'ActionFormer / TriDet',31)
    zone('anchor',1043,226,413,600,anchor)
    def tal_transformer():
        frames(1552,237);timeline(1560,381,365);path('M1750 373V406',arrow=True,flow=True)
        transformer(1551,412,397,185);path('M1751 610V646',arrow=True,flow=True)
        segment(1571,681,346,56,108);segment(1571,731,346,132,131)
        text(1750,813,'Segments + classes + scores',30)
    zone('tal-transformer',1545,226,410,600,tal_transformer)
    def matching():
        math(148,1011,'q',34,True);block(28,1018,240,90,['Text encoder'],31)
        frames(31,1204,69,13);timeline(40,1298,212)
        path('M278 1062L329 1094',arrow=True,flow=True);path('M278 1221L329 1169',arrow=True,flow=True)
        block(341,1055,281,149,['Cross-modal','ranking'])
        path('M483 1215V1328',arrow=True,flow=True);text(148,1349,'Clip proposals',31)
        for y,left,length,score in [(1373,116,132,'0.93'),(1427,75,103,'0.61'),(1479,204,104,'0.28')]:
            segment(60,y,373,left,length);text(542,y+10,score,31,'blue-text' if score=='0.93' else 'text')
        text(331,1548,'Ranked moments · illustrative scores',28)
    zone('matching',20,988,620,568,matching)
    def temporal_map():
        math(814,1011,'q',34,True);block(694,1018,240,90,['Text encoder'],31)
        frames(698,1204,69,13);timeline(707,1298,211)
        path('M942 1062L1000 1123',arrow=True,flow=True);path('M942 1226L1000 1205',arrow=True,flow=True)
        # End increases upwards; diagonal and start >= end cells are invalid.
        for row in range(3):
            for col in range(3):
                cls='valid' if col < 2-row else 'invalid'
                rect(1018+col*64.5,1077+row*64.5,64.5,64.5,cls)
        rect(1082.5,1077,64.5,64.5,'selected')
        path('M1012 1270V1065','ink',True,True);path('M1018 1277H1233','ink',True,True)
        for i in range(3):text(1050+i*65,1311,str(i),28);text(944,1245-i*65,str(i),28)
        text(969,1048,'end',30);text(1123,1355,'start',31)
        math(1000,1401,'(<tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">1</tspan>, <tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">2</tspan>) :　<tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">1</tspan> &lt; <tspan font-style="italic">t</tspan><tspan baseline-shift="sub" font-size="23">2</tspan>',34,True)
    zone('map',686,988,625,420,temporal_map)
    def graph():
        text(871,1456,'Graph alternative',30);text(871,1521,'Proposal relations',30)
        path('M1058 1465L1175 1428L1258 1504Z','ink')
        for i,(x,y) in enumerate([(1058,1465),(1175,1428),(1258,1504)],1):
            circle(x,y,31,'graph-node');math(x,y+10,f'p<tspan baseline-shift="sub" font-size="23">{i}</tspan>')
    zone('graph',685,1409,622,141,graph)
    def tsg_transformer():
        math(1482,1011,'q',34,True);block(1361,1018,240,90,['Text encoder'],31)
        frames(1364,1204,69,13);timeline(1374,1298,211)
        path('M1613 1062L1646 1093',arrow=True,flow=True);path('M1613 1221L1646 1182',arrow=True,flow=True)
        transformer(1658,1043,320,185,11);path('M1818 1240V1282',arrow=True,flow=True)
        segment(1623,1321,326,92,117);segment(1623,1371,326,135,119)
        text(1492,1348,'Moments',31);text(1492,1402,'+ scores',31)
    zone('tsg-transformer',1354,988,631,427,tsg_transformer)
    def corpus():
        path('M1371 1428H1973','divider');text(1667,1469,'Corpus extension · query + videos',30)
        for x in [1366,1393,1420]:
            rect(x,1502,24,40,'cylinder');add(f'<ellipse class="f624-cylinder" cx="{x+12}" cy="1502" rx="12" ry="6"/>')
        path('M1452 1523H1483',arrow=True,flow=True);block(1495,1483,139,82,['Rank','videos'],30)
        path('M1644 1523H1673',arrow=True,flow=True);block(1686,1483,169,82,['Localize'],30)
        path('M1865 1523H1900',arrow=True,flow=True);segment(1909,1522,65,11,37)
    zone('corpus',1354,1422,631,146,corpus)
    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)

if __name__=='__main__':
    (SITE/'example/figure624.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure624-1"><title>Figure 6.24 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.24 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/temporal_localization.webp" alt="Original temporal localization method families"><h2>Interactive reconstruction</h2>'''+fig624()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure624-1';mountNative();</script></html>''')
