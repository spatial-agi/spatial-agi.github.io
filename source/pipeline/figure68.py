"""Figure 6.8: independent SVG typography, matrices, cards and connectors."""
import json
from html import escape
from pathlib import Path

INFO = {
 'world': {'t':'World coordinates','b':'A 3D point starts in the world reference frame. Homogeneous coordinates append a fourth component equal to one.'},
 'camera': {'t':'Camera coordinates','b':'Rotation and translation express the world point in the camera reference frame.'},
 'plane': {'t':'Image-plane coordinates','b':'Perspective projection maps a camera-space point to the image plane. Divide by homogeneous depth to obtain Euclidean coordinates.'},
 'pixel': {'t':'Pixel coordinates','b':'Pixel scales and the principal point convert image-plane coordinates into image pixels.'},
 'extrinsic': {'t':'Extrinsic matrix','b':'The extrinsic transform contains rotation R and translation T. It maps world coordinates to camera coordinates.'},
 'projection': {'t':'Projection matrix','b':'This stage applies focal length f. The last row retains depth for the perspective division.'},
 'affine': {'t':'Affine matrix','b':'This stage contains pixel scales sx and sy, plus principal-point offsets Px and Py.'},
 'intrinsic': {'t':'Intrinsic matrix','b':'Combining the affine and projection stages gives the intrinsic matrix shown here in 3 × 4 form. The focal lengths in pixels are fx = sx f and fy = sy f.'},
 'full': {'t':'Full camera projection','b':'M = Mintrinsic Mextrinsic combines calibration and pose in one 3 × 4 projection matrix. Divide its homogeneous output by the third component to obtain pixel coordinates.'},
}

def fig68():
    out=[]
    def add(s): out.append(s)
    def text(x,y,label,size=40,cls='f68-math'):
        add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{label}</text>')
    def sub(a,b): return f'{a}<tspan baseline-shift="sub" font-size="65%">{b}</tspan>'
    def zone(key,x,y,w,h,body):
        add(f'<g class="f68-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        body()
        add(f'<rect class="f68-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></g>')
    def vector(x,y,w,h,color,labels,ys):
        add(f'<rect class="f68-var f68-{color}" x="{x}" y="{y}" width="{w}" height="{h}" rx="28"/>')
        for label,baseline in zip(labels,ys): text(x+w/2,baseline,label,43)
    def matrix(xs,ys,rows,size=40):
        for y,row in zip(ys,rows):
            for x,item in zip(xs,row): text(x,y,item,size)
    def rule(a,b,y): add(f'<path class="f68-rule" d="M{a} {y}H{b}"/>')
    def extrinsic(y):
        text(335,y,sub('M','extrinsic'),46); rule(222,443,y+20)
        matrix([271,390],[y+83,y+143],[[sub('R','3×3'),sub('T','3×1')],[sub('0','1×3'),'1']])
    world=[sub('X','w'),sub('Y','w'),sub('Z','w')]
    camera=[sub('X','c'),sub('Y','c'),sub('Z','c')]
    pixel=[sub('x','px'),sub('y','px')]
    add('''<div class="nf nf-68" data-nf="68" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" role="group" aria-label="Figure 6.8: pinhole camera model"><defs><marker id="f68-arrow" markerWidth="34" markerHeight="50" refX="29" refY="25" markerUnits="userSpaceOnUse" orient="auto"><path d="M5 5L26 25L5 45" fill="none" stroke="#080808" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect class="f68-bg" width="1536" height="1024"/>''')
    cards=[('world',28,263,['World','Coordinates'],'world-axes',(104,130,136,108)),('camera',441,265,['Camera','Coordinates'],'camera-axes',(510,130,140,108)),('plane',848,273,['Image Plane','Coordinates'],'image-plane-axes',(890,135,175,103)),('pixel',1254,256,['Pixel','Coordinates'],'pixel-axes',(1300,135,170,103))]
    for key,x,w,labels,asset,box in cards:
        def body(key=key,x=x,w=w,labels=labels,asset=asset,box=box):
            add(f'<rect class="f68-card f68-{key}" x="{x}" y="27" width="{w}" height="220" rx="30"/>')
            for label,y in zip(labels,[85,126]): text(x+w/2,y,label,36,'f68-title')
            a,b,c,d=box
            add(f'<image href="/assets/img/figs/f68/icons/{asset}.png" x="{a}" y="{b}" width="{c}" height="{d}"/>')
        zone(key,x,27,w,220,body)
    for a,b in [(321,405),(734,815),(1148,1228)]: add(f'<path class="f68-flow" d="M{a} 138H{b}" marker-end="url(#f68-arrow)"/>')
    vector(50,313,118,181,'world',world,[363,418,471])
    vector(498,313,108,181,'camera',camera,[363,418,471])
    vector(944,313,110,181,'plane',[sub('x','p'),sub('y','p')],[382,444])
    vector(1380,313,112,181,'pixel',pixel,[382,444])
    zone('extrinsic',211,266,241,230,lambda:extrinsic(310))
    def projection():
        text(777,310,sub('M','projection'),46); rule(674,878,330)
        matrix([665,737,809,882],[378,428,478],[['f','0','0','0'],['0','f','0','0'],['0','0','1','0']])
    zone('projection',631,266,279,230,projection)
    def affine():
        text(1222,310,sub('M','affine'),46); rule(1105,1340,330)
        matrix([1128,1217,1307],[378,428,478],[[sub('s','x'),'0',sub('P','x')],['0',sub('s','y'),sub('P','y')],['0','0','1']])
    zone('affine',1090,266,266,230,affine)
    vector(50,568,118,184,'world',world,[617,673,727])
    vector(499,568,108,184,'camera',camera,[617,673,727])
    vector(1378,569,111,183,'pixel',pixel,[640,701])
    zone('extrinsic',211,531,241,221,lambda:extrinsic(577))
    def intrinsic():
        text(996,569,sub('M','intrinsic')+' = '+sub('M','affine')+sub('M','projection'),44); rule(785,1202,589)
        matrix([852,939,1026,1120],[641,691,741],[[sub('f','x'),'0',sub('P','x'),'0'],['0',sub('f','y'),sub('P','y'),'0'],['0','0','1','0']])
    zone('intrinsic',729,526,528,229,intrinsic)
    vector(50,805,118,179,'world',world,[852,906,961])
    vector(1378,810,111,174,'pixel',pixel,[877,942])
    def full():
        text(777,819,'M = '+sub('M','intrinsic')+' '+sub('M','extrinsic'),44); rule(592,959,838)
        matrix([628,719,811,904],[879,930,980],[[sub('m','11'),sub('m','12'),sub('m','13'),sub('m','14')],[sub('m','21'),sub('m','22'),sub('m','23'),sub('m','24')],[sub('m','31'),sub('m','32'),sub('m','33'),sub('m','34')]],36)
    zone('full',546,778,481,218,full)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)

if __name__=='__main__':
    site=Path(__file__).resolve().parents[2]
    (site/'example/figure68.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure68-2"><title>Figure 6.8 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1400px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.8 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/camera-1.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig68()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure68-2';mountNative();</script></html>''')
