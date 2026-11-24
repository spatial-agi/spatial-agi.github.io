"""Figure 6.1: native detection illustration in the original 2000 × 1024 coordinates."""
import html
import json
from pathlib import Path

INFO = {
    'person-left': dict(t='Person · 0.95', b='A detected instance is represented by its class, bounding box and confidence score. This person has an illustrative score of 0.95.'),
    'person-right': dict(t='Person · 0.91', b='Two instances can share the same class while having different boxes and confidence scores.'),
    'car': dict(t='Car · 0.88', b='The bounding box localizes the car in image coordinates; the class identifies its category.'),
    'cyclist': dict(t='Bicycle · 0.72', b='The printed example labels this region as bicycle. Its tuple contains the class, the blue bounding box and the confidence score 0.72.'),
    'speed-sign': dict(t='Sign · 0.81', b='The detector localizes the traffic sign as another instance in the same image.'),
    'tuple': dict(t='Detection tuple · (cᵢ, bᵢ, sᵢ)', b='cᵢ denotes the class, bᵢ the bounding box and sᵢ the confidence score. The dashed leaders connect these attributes to the bicycle detection.'),
    'pre': dict(t='Pre-DL detectors', b='Handcrafted features feed a classifier. Representative families in the figure include Viola–Jones, HOG-SVM and DPM.'),
    'two': dict(t='Two-stage detectors', b='Candidate regions are processed by a CNN backbone before classification and box regression. The figure lists R-CNN, Fast R-CNN and Faster R-CNN.'),
    'one': dict(t='One-stage CNN detectors', b='Dense predictions jointly estimate categories and boxes. The figure lists YOLO, SSD and RetinaNet.'),
    'transformer': dict(t='Transformer set prediction', b='Object queries produce a set of predictions. Bipartite matching associates predictions with ground-truth boxes during training. The moving dots illustrate information flow.'),
    'open': dict(t='Open-vocabulary detection', b='Vision and text representations are aligned so detections can be conditioned on category names. The figure lists ViLD, OVR-CNN, GLIP and Detic.'),
}


def fig61():
    blue, ink = '#295b99', '#101313'

    def text(x,y,s,size=30,color=ink,anchor='start',cls=''):
        spans=''.join(f'<tspan x="{x}" dy="{0 if i==0 else size*1.22}">{html.escape(line)}</tspan>' for i,line in enumerate(s.split('\n')))
        return f'<text class="f61-text {cls}" x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{spans}</text>'

    def math(x,y,letter,size=36):
        return f'<text class="f61-math" x="{x}" y="{y}" font-size="{size}">{letter}<tspan baseline-shift="sub" font-size="{size*.65}">i</tspan></text>'

    def rect(x,y,w,h,r=0,color=ink,width=1.7,fill='white',cls='',dash=None):
        da=f' stroke-dasharray="{dash}"' if dash else ''
        return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{color}" stroke-width="{width}"{da}/>'

    def path(d,color=ink,width=1.8,arrow=False,dash=None,cls='',delay=0):
        extra=f' marker-end="url(#f61-{"blue" if color==blue else "black"})"' if arrow else ''
        if dash: extra+=f' stroke-dasharray="{dash}"'
        return f'<path class="{cls}" data-delay="{delay}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'

    def route(d,delay=0): return path(d,arrow=True,cls='f61-route',delay=delay)
    def image(name,x,y,w,h,cls=''):return f'<image class="{cls}" href="/assets/img/figs/f61/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def zone(k,box,body):
        x,y,w,h=box
        return f'<g class="f61-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(INFO[k]["t"])}">'+rect(x,y,w,h,cls='f61-hit',color='none',fill='transparent')+body+'</g>'

    out=['<div class="nf nf-61" data-nf="61" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1024" role="group" aria-label="Figure 6.1: 2D object detection and detector families">',
         '<defs><marker id="f61-black" markerWidth="13" markerHeight="12" refX="11" refY="6" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L13 6L0 12L3 6Z" fill="#101313"/></marker><marker id="f61-blue" markerWidth="44" markerHeight="42" refX="39" refY="21" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L44 21L0 42Z" fill="#295b99"/></marker></defs>',
         rect(14,13,1953,512,8,width=2.3),image('scene/street',20,21,1548,496)]
    detections=[('person-left','person : 0.95',(188,130,153,311),(199,142,141,293),200,121),
                ('person-right','person : 0.91',(485,156,129,233),(496,169,113,219),487,147),
                ('car','car : 0.88',(703,217,411,186),(705,224,405,175),715,209),
                ('cyclist','bicycle : 0.72',(1180,280,217,194),(1195,283,198,188),1187,271),
                ('speed-sign','sign : 0.81',(1434,103,82,112),(1438,114,75,283),1422,94)]
    for k,label,box,pic,tx,ty in detections:
        x,y,w,h=box
        body=image('objects/'+k,*pic,cls='f61-object')+rect(x,y,w,h,color=blue,width=2.6,fill='none',cls='f61-detection')
        if k=='car': body+=rect(704,189,409,27,color=blue,width=1.7,fill='white')
        body+=text(tx,ty,label,22,blue,cls='f61-score')
        out.append(zone(k,(x-5,min(y,ty-23),w+10,h+y-min(y,ty-23)+5),body))
    tuple_=rect(1583,93,365,373,12,width=2.1,cls='f61-frame')
    tuple_+='<text class="f61-math" x="1766" y="130" font-weight="700" font-size="37" text-anchor="middle">(c<tspan baseline-shift="sub" font-size="24">i</tspan>, b<tspan baseline-shift="sub" font-size="24">i</tspan>, s<tspan baseline-shift="sub" font-size="24">i</tspan>)</text>'
    for y,l in [(210,'c'),(324,'b'),(395,'s')]:tuple_+=math(1604,y,l)
    tuple_+=text(1647,210,'→ class (e.g.,',33)+text(1604,254,'"bicycle"',33,blue)
    tuple_+=text(1647,324,'→ bounding box',33)+rect(1911,295,31,45,color=blue,width=1.8,fill='none')
    tuple_+=text(1647,395,'→ confidence',33)+text(1604,438,'score (e.g.,',33)+text(1770,438,'0.72',33,blue)+text(1850,438,')',33)
    out.append(zone('tuple',(1580,90,371,379),tuple_))
    out += [path('M1600 203Q1562 200 1542 212L1396 278',width=2.2,arrow=True,dash='7 6',cls='f61-leader'),
            path('M1600 300L1397 334',width=2.2,dash='7 6',cls='f61-leader'),
            path('M1600 394L1480 416',width=2.2,arrow=True,dash='7 6',cls='f61-leader'),
            text(1010,568,'Output: bounding box + class + confidence per detection',36,anchor='middle'),
            path('M19 598H1947',blue,8.3,True,cls='f61-timeline')]
    for x in [187,576,947,1330,1734]:
        out += [path(f'M{x} 612V655',blue,2,dash='5 5'),f'<circle cx="{x}" cy="598" r="12" fill="white" stroke="{blue}" stroke-width="4"/>']

    def panel(k,x,w,title,body):
        return zone(k,(x,655,w,352),rect(x,655,w,352,18,blue,2.6,cls='f61-frame')+text(x+w/2,695,title,32,anchor='middle')+body)

    pre=image('methods/handcrafted-features',42,729,151,166)
    pre+=path('M202 811H226V804L239 817L226 830V823H202Z','#777',2)
    pre+=rect(247,758,90,112,9,width=1.8)+text(292,798,'Features\n↓\nclassifier',21,anchor='middle')
    pre+=text(190,958,'Viola-Jones /\nHOG-SVM / DPM',30,anchor='middle')
    out.append(panel('pre',21,337,'Pre-DL Detectors',pre))

    two=''
    for i,y in enumerate([709,784,861]):
        two+=rect(416,y,61,58,1,color='#555',dash='7 4',fill='#fafafa')
        two+=rect(426,y+16,39,34,color='#777',width=1.4,fill='#fff')
        if i==1:two+=rect(437,y+33,28,20,color='#777',width=1.3,fill='#eee')
    two+=path('M528 740L628 766V862L528 888Z',width=2)
    two+=text(578,807,'CNN\nBackbone',21,anchor='middle')
    for i,d in enumerate(['M487 743L519 762','M487 813H518','M487 881L519 864','M638 803L666 773','M638 821L666 848']):two+=route(d,i*220)
    two+=rect(674,752,59,42,7)+text(703,779,'class',21,anchor='middle')+rect(674,826,59,43,7)+text(703,854,'box',21,anchor='middle')
    two+=text(572,958,'R-CNN / Fast R-CNN /\nFaster R-CNN',30,anchor='middle')
    out.append(panel('two',391,362,'Two-stage',two))

    one=rect(824,718,232,206,width=1.7,fill='#fcfcfb')
    for x in [882,940,998]:one+=path(f'M{x} 719V923','#777',1.5)
    for y in [764,817,870]:one+=path(f'M825 {y}H1055','#777',1.5)
    one+=path('M824 843L868 795Q875 790 883 801L921 848L969 814Q980 803 994 816L1024 805Q1030 801 1040 809L1054 821','#555',1.6)
    one+='<circle cx="852" cy="752" r="11" fill="none" stroke="#777" stroke-width="1.6"/>'
    one+=rect(938,763,63,90,color=blue,width=2.6,cls='f61-gridbox')+text(970,788,'bicycle\n0.72',17,blue,anchor='middle')+image('methods/bicycle-icon',945,816,49,32)
    one+=text(940,958,'YOLO / SSD /\nRetinaNet',30,anchor='middle')
    out.append(panel('one',783,315,'One-stage CNN',one))

    transformer=''
    for x in [1143,1177,1211]:transformer+=rect(x,814,22,22,color='#16313b',width=1.8,cls='f61-query')
    transformer+=text(1134,875,'Object queries',20)+route('M1234 825H1251')
    transformer+=rect(1256,788,108,66,10)+text(1310,816,'Transformer\ndecoder',18,anchor='middle')
    for i,y in enumerate([758,794,836,870]):
        transformer+=rect(1389,y,24,24,fill='#fcfcfc',color='#555',cls='f61-prediction')
        transformer+=route(f'M1366 {812+i*9}L1384 {y+14}',i*200)
    for i,y in enumerate([757,794,832,869]):
        transformer+=rect(1500,y,31,31,fill='#fff',color='#555',dash='5 4' if i else None,cls='f61-ground')
    for i,(sy,ey) in enumerate([(770,883),(806,772),(848,848),(882,810),(770,810),(806,848),(848,883),(882,772)]):
        transformer+=path(f'M1415 {sy}L1496 {ey}', '#555',1.25,True,'5 4','f61-matching',i*240)
    transformer+=text(1491,725,'Ground-truth\nboxes',17,anchor='middle')+text(1453,915,'Bipartite matching',17,anchor='middle')
    transformer+=text(1338,958,'DETR / Deformable DETR /\nDINO / RT-DETR',30,anchor='middle')
    out.append(panel('transformer',1128,421,'Transformer Set Prediction',transformer))

    open_=rect(1600,731,103,199,16)+rect(1790,731,105,199,16)
    open_+=text(1652,759,'Vision\nTower',20,anchor='middle')+text(1842,759,'Text\nTower',20,anchor='middle')
    for y in [801,825,848,872,895]:open_+=rect(1619,y,63,22,3,color='#555',fill='#fcfcfb',cls='f61-feature')
    open_+=text(1842,827,'Dog\nSkateboard\nBicycle\nCar\nPerson',18,anchor='middle')
    open_+=route('M1717 836H1774')+route('M1774 836H1717',800)
    open_+=text(1748,958,'ViLD / OVR-CNN /\nGLIP / Detic',30,anchor='middle')
    out.append(panel('open',1579,341,'Open-vocabulary',open_))
    out+=['<g class="f61-pulses" aria-hidden="true" pointer-events="none"></g></svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>']
    return ''.join(out)


def preview():
    site=Path(__file__).resolve().parents[2]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css"><title>Figure 6.1 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1200px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:white}.nf{padding:0;border:0;border-radius:0}</style><main><h1>Figure 6.1 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/object_detection.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig61()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js';mountNative();</script></html>'''
    page=page.replace('/assets/css/site.css','/assets/css/site.css?v=figure61-1').replace('/assets/js/nfig.js','/assets/js/nfig.js?v=figure61-1')
    (site/'example/figure61.html').write_text(page)


if __name__=='__main__':
    preview()
