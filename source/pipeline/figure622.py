"""Figure 6.22: independently drawn tracking states over original scene PNGs."""
import json
import math
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
MASKS = json.loads((SITE/'assets/figures/elements/figure622/geometry/instance-masks.json').read_text())
COLORS = {'blue':'#4146eb','purple':'#9958a0','orange':'#bf7c24','ink':'#2c373d'}
INFO = {
    'sot': {'t':'Single object tracking','b':'An initial bounding box selects one target. The tracker follows that same object through subsequent frames; the dashed initial box marks the given state.'},
    'mot': {'t':'Multiple object tracking','b':'Each detected object has a bounding box and a persistent identity. Repeated IDs link the same person or vehicle across time.'},
    'mots': {'t':'Tracking and segmentation','b':'Instance masks describe each tracked object at pixel level, while persistent IDs associate those instances across frames.'},
    '3d': {'t':'3D multi-object tracking','b':'Camera or LiDAR observations support oriented 3D boxes. Trajectories connect earlier and later states while preserving object identity and orientation.'},
    'pose': {'t':'Pose and landmark tracking','b':'Tracked identities are paired with corresponding body joints. Joint locations and skeletal connections describe articulated motion over time.'},
    'panoptic': {'t':'Panoptic tracking','b':'Things such as people and vehicles retain instance IDs across time. Stuff such as sky and walkway receives semantic class labels.'},
}
# Coordinates relative to each 192 x 290 original street image.
POSES = [
    [[(61,87),(61,102),(47,111),(75,111),(40,137),(81,140),(34,158),(83,160),(53,161),(66,161),(51,191),(65,192),(50,227),(65,222)],
     [(131,95),(131,109),(120,116),(140,116),(113,139),(146,141),(108,164),(148,163),(124,164),(136,164),(127,198),(135,199),(126,232),(133,225)]],
    [[(65,87),(65,102),(51,111),(78,111),(46,137),(84,140),(48,155),(87,160),(59,162),(70,162),(59,192),(67,193),(69,232),(60,222)],
     [(132,96),(132,110),(121,117),(142,116),(115,140),(147,141),(109,165),(148,164),(125,164),(137,164),(126,199),(131,200),(124,232),(132,227)]],
    [[(69,87),(69,103),(56,111),(82,111),(51,138),(88,140),(56,155),(90,160),(63,162),(74,162),(65,193),(70,193),(72,232),(62,224)],
     [(134,96),(134,111),(124,117),(145,117),(118,141),(149,142),(110,166),(150,165),(127,165),(139,165),(127,199),(132,201),(126,232),(135,226)]]
]


def fig622():
    out=[];add=out.append
    def text(x,y,value,size=31,cls='text',anchor='middle'):
        add(f'<text class="f622-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{value}</text>')
    def path(d,cls='line',color='ink',arrow=False,flow=False):
        add(f'<path class="f622-{cls}{" f622-route" if flow else ""}" d="{d}" stroke="{COLORS[color]}"'+(f' marker-end="url(#f622-{color})"' if arrow else '')+'/>')
    def rect(x,y,w,h,cls='frame',color=None):
        add(f'<rect class="f622-{cls}" x="{x}" y="{y}" width="{w}" height="{h}"'+(f' stroke="{COLORS[color]}"' if color else '')+'/>')
    def label(x,y,value,color='blue',size=28):
        width=19 if len(value)==1 else len(value)*size*.53
        rect(x-width/2-2,y-size+4,width+4,size+1,'label-bg')
        text(x,y,escape(value),size,color+'-text')
    def zone(key,x,y,w,h,draw):
        add(f'<g class="f622-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw();rect(x,y,w,h,'hit');add('</g>')
    def scene(i,x,y,w=194,h=292):
        add(f'<image href="/assets/img/figs/f622/shared-street/frame-{i:02d}.png" x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" preserveAspectRatio="none"/>')
        rect(x,y,w,h)
    def time_labels(xs,y):
        for i,x in enumerate(xs):text(x,y,f't<tspan baseline-shift="sub" font-size="24">{i}</tspan>',36,'math')
    def time_arrow(x,y):path(f'M{x} {y}H{x+540}','time','ink',True,True)
    def instance(i,x,y,panoptic=False):
        add(f'<g transform="translate({x} {y})">')
        if panoptic:
            # Semantic regions follow the source sky/tree/building/walkway boundaries.
            add(f'<defs><mask id="f622-background-{i}" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="290"><rect width="192" height="290" fill="white"/>')
            for d in MASKS[i]:add(f'<path d="{d}" fill="black"/>')
            add(f'</mask></defs><g mask="url(#f622-background-{i})">')
            add('<path class="f622-semantic" fill="#f0c9b8" d="M0 152L86 154L192 230V290H0Z"/><path class="f622-semantic" fill="#c3cfa6" d="M67 0H192V128L149 141L91 141L62 153Z"/><path class="f622-semantic" fill="#b2e5f5" d="M125 0H192V29L178 28L166 50L147 59L123 53Z"/><path class="f622-semantic" fill="#ddd2b5" d="M0 0H67L62 153L0 177Z"/>')
            add('</g>')
        for k,d in enumerate(MASKS[i]):
            add(f'<path class="f622-mask f622-mask-{k}" d="{d}"/>')
        add('</g>')
    def skeleton(i,x,y):
        for person,points in enumerate(POSES[i]):
            color='blue' if person==0 else 'purple'
            edges=[(0,1),(1,2),(1,3),(2,4),(4,6),(3,5),(5,7),(1,8),(1,9),(8,9),(8,10),(10,12),(9,11),(11,13)]
            d=''.join(f'M{x+points[a][0]} {y+points[a][1]}L{x+points[b][0]} {y+points[b][1]}' for a,b in edges)
            path(d,'skeleton',color)
            for px,py in points:add(f'<circle class="f622-joint" fill="{COLORS[color]}" cx="{x+px}" cy="{y+py}" r="4.8"/>')
    def cube(x,y,color):
        # Front face, translated back face and four corresponding corner edges.
        d=f'M{x} {y}l44 8v30l-44 -8ZM{x+18} {y-29}l44 8v30l-44 -8ZM{x} {y}l18 -29M{x+44} {y+8}l18 -29M{x+44} {y+38}l18 -29M{x} {y+30}l18 -29'
        path(d,'cube',color)

    add('<div class="nf nf-622" data-nf="622" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1219" role="group" aria-label="Figure 6.22: six object-tracking subtasks"><defs>')
    for color,hexcolor in COLORS.items():
        add(f'<marker id="f622-{color}" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto"><path d="M2 3L12 8L2 13" fill="none" stroke="{hexcolor}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="1219" fill="white"/><g class="f622-scaffold"><path class="f622-divider" d="M667 30V1198M1333 30V1198M14 609H1986"/></g>')
    def a():
        xs=[23,239,454];time_labels([120,335,550],83)
        for i,x in enumerate(xs):
            scene(i,x,112)
            bx=[51,270,490][i];rect(bx,186,63,165,'initial' if i==0 else 'box','blue');label(bx+32,178,'1')
        time_arrow(61,443);text(332,503,'Initial box → same target',32,'blue-text');text(332,572,'(a) Single object tracking',36,'title')
    zone('sot',14,42,637,549,a)
    def b():
        xs=[690,906,1122];time_labels([787,1003,1218],83)
        for i,x in enumerate(xs):
            scene(i,x,112)
            bx=x+[28,31,33][i]
            for xx,yy,w,h,k,color in [(bx,186,63,165,'1','blue'),(x+103,197,52,154,'2','purple'),(x+157,219,35,25,'3','orange')]:
                rect(xx,yy,w,h,'box',color);label(xx+w/2,yy-8,k,color)
        time_arrow(728,443);text(1000,503,'Boxes + persistent IDs',32);text(1000,572,'(b) Multiple object tracking',36,'title')
    zone('mot',683,42,635,549,b)
    def c():
        xs=[1357,1573,1789];time_labels([1454,1670,1886],83)
        for i,x in enumerate(xs):
            scene(i,x,112);instance(i,x+1,113)
            label(x+62+[0,3,7][i],253,'1');label(x+130,258,'2','purple');label(x+174,235,'3','orange')
        time_arrow(1395,443);text(1667,503,'Instance masks + persistent IDs',32);text(1667,572,'(c) Tracking + segmentation',36,'title')
    zone('mots',1349,42,637,549,c)
    def d():
        add('<path class="f622-road" d="M221 670H400V763H630V896H400V1006H221V896H147V763H221Z"/>')
        path('M310 672V1004M149 831H628','road-dash')
        rect(30,735,75,47,'camera');add('<circle class="f622-camera" cx="67" cy="759" r="14"/>');text(68,819,'Camera',28)
        for angle in range(0,360,45):
            dx,dy=math.cos(math.radians(angle)),math.sin(math.radians(angle))
            path(f'M{68+15*dx:.2f} {886+15*dy:.2f}L{68+38*dx:.2f} {886+38*dy:.2f}','lidar-ray')
        add('<circle class="f622-camera" cx="68" cy="886" r="10"/>');text(68,960,'LiDAR',28)
        for x,y in [(236,716),(236,837),(236,945)]:cube(x,y,'blue')
        for x,y in [(313,686),(424,763),(554,763)]:cube(x,y,'orange')
        for x,y in [(378,846),(517,846),(326,944)]:cube(x,y,'purple')
        for a,b in [(('M268 811V777'),'blue'),(('M268 918V897'),'blue'),(('M422 755L382 727'),'orange'),(('M544 778H500'),'orange'),(('M450 861H504'),'purple'),(('M379 923L388 901'),'purple')]:path(a,'trajectory',b,True,True)
        text(268,680,'1',28,'blue-text');text(344,650,'3',28,'orange-text');text(548,920,'2',28,'purple-text')
        path('M566 994V955','axis','blue',True);path('M566 994H605','axis','blue',True);path('M566 994L542 1011','axis','blue',True)
        text(566,944,'z',27,'blue-text');text(622,1000,'x',27,'blue-text');text(530,1028,'y',27,'blue-text')
        text(332,1055,'Earlier → later states',30);text(332,1107,'Oriented boxes + trajectories',32);text(332,1178,'(d) 3D multi-object tracking',36,'title')
    zone('3d',14,618,637,578,d)
    def e():
        xs=[690,906,1122];time_labels([787,1003,1218],690)
        for i,x in enumerate(xs):
            scene(i,x,718);skeleton(i,x+1,719);label(x+62,784,'1');label(x+132,790,'2','purple')
        time_arrow(728,1049);text(1000,1104,'Person IDs + joint correspondence',32);text(1000,1178,'(e) Pose / landmark tracking',36,'title')
    zone('pose',683,650,635,546,e)
    def f():
        xs=[1357,1573,1789];time_labels([1454,1670,1886],690)
        for i,x in enumerate(xs):
            scene(i,x,718);instance(i,x+1,719,True)
            label(x+62+[0,3,7][i],860,'1');label(x+130,864,'2','purple');label(x+174,841,'3','orange');label(x+152,743,'sky','ink',28);label(x+96,993,'walkway','ink',28)
        time_arrow(1395,1049);text(1667,1104,'Things: IDs • Stuff: classes',32);text(1667,1178,'(f) Panoptic tracking',36,'title')
    zone('panoptic',1349,650,637,546,f)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__=='__main__':
    (SITE/'example/figure622.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure622-1"><title>Figure 6.22 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.22 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/object_tracking.webp"><h2>Interactive reconstruction</h2>'''+fig622()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure622-1';mountNative();</script></html>''')
