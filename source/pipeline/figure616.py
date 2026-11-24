"""Figure 6.16: layout parsing families and method chronology."""
import json
from html import escape
from pathlib import Path

INFO = {
 'perspective': {'t':'Perspective layout estimation','b':'Corners and edges are inferred from a perspective image, then decoded or fitted into a cuboid room layout.'},
 'panorama': {'t':'Panoramic layout estimation','b':'Boundary-height and corner signals encode the room across the full panorama. These predictions are decoded into a 3D layout.'},
 'footprint': {'t':'Beyond the cuboid assumption','b':'Projection or fusion recovers a footprint and height. Manhattan footprints allow orthogonal turns, while arbitrary-angle footprints support more general rooms.'},
 'planes': {'t':'Plane geometry','b':'Predicted plane depths determine the room surfaces. Intersections between the planes recover the layout edges and corners.'},
 'outdoor': {'t':'Outdoor cross-view estimation','b':'A street-view observation is transformed into a bird’s-eye view (BEV), representing road structure and vehicle locations.'},
}
METHODS = [
 ('mallya',929,68,375,102,'Mallya &amp; Lazebnik','FCN edges','2015',1117,179),
 ('roomnet',1342,68,258,102,'RoomNet','11 topologies','2017',1471,179),
 ('layout-perspective',1658,68,296,102,'LayoutNet','2D boundaries','2018',1806,179),
 ('layout-panorama',923,265,246,101,'LayoutNet','2D maps','2018',1046,376),
 ('horizon',1181,265,259,101,'HorizonNet','1D signals','2019',1311,376),
 ('hoho',1452,265,240,101,'HoHoNet','1D / multi-task','2021',1572,376),
 ('led',1711,265,249,101,'LED<tspan baseline-shift="super" font-size="21">2</tspan>-Net','Render loss','2021',1835,376),
 ('dula',1012,462,376,102,'DuLa-Net','Manhattan','2019',1200,572),
 ('atlanta',1554,462,391,102,'AtlantaNet','Arbitrary angles','2020',1749,572),
 ('geo',1012,659,413,102,'GeoLayout','Plane depth maps','2020',1219,769),
 ('pyva',1542,856,412,90,'Yang et al. (PYVA)','Cross-view','2021',1748,954),
]
for k,_,_,_,_,title,desc,year,_,_ in METHODS:
 INFO[k]={'t':title.replace('&amp;','&').replace('<tspan baseline-shift="super" font-size="21">2</tspan>','²'), 'b':f'{year} · {desc}. The horizontal placement follows the source figure; chronology spacing is not to scale.'}

def fig616():
 out=[]; add=out.append
 def text(x,y,s,size=29,bold=False,blue=False):
  add(f'<text class="f616-text{" f616-title" if bold else ""}{" f616-blue-text" if blue else ""}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{s}</text>')
 def path(d,cls='ink',arrow=False,flow=False):
  add(f'<path class="f616-{cls}{" f616-route" if flow else ""}" d="{d}"'+(' marker-end="url(#f616-'+('gray' if cls=='gray' else 'blue')+')"' if arrow else '')+'/>')
 def poly(points,fill,stroke='#4545ed',width=3): add(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 def dot(x,y): add(f'<circle class="f616-point" cx="{x}" cy="{y}" r="4.4"/>')
 def photo(name,x,y,w=133,h=68): add(f'<image href="/assets/img/figs/f616/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def zone(k,x,y,w,h,draw):
  add(f'<g class="f616-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">'); draw(); add(f'<rect class="f616-hit" x="{x}" y="{y}" width="{w}" height="{h}"/></g>')
 def room(x,y,w=124,h=83):
  # Shared axonometric cuboid, with a translucent floor and blue floor corners.
  pts=[(0,.82),(.38,.53),(.57,1),(1,.71),(.38,0),(0,.29),(.57,.47),(1,.17)]
  p=[(x+a*w,y+b*h) for a,b in pts]
  a,b,c,d,e,f,g,j=p
  def coord(v): return f'{v[0]:g} {v[1]:g}'
  poly(' '.join(f'{v[0]:g},{v[1]:g}' for v in [a,b,d,c]),'#ebebff','none')
  path(f'M{coord(a)}L{coord(f)}M{coord(b)}L{coord(e)}M{coord(c)}L{coord(g)}M{coord(d)}L{coord(j)}','gray-thin')
  path(f'M{coord(f)}L{coord(e)}L{coord(j)}L{coord(g)}Z','ink')
  path(f'M{coord(a)}L{coord(b)}L{coord(d)}L{coord(c)}Z','blue',flow=True)
  for px,py in [a,b,c,d]: dot(px,py)
 add('<div class="nf nf-616" data-nf="616" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1031" role="group" aria-label="Figure 6.16: layout parsing families, mechanisms and method chronology"><defs>')
 for name,color in [('blue','#4545ed'),('gray','#aab3b9')]:
  add(f'<marker id="f616-{name}" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="11" refY="7.5" orient="auto"><path d="M3 3L11 7.5L3 12" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 add('</defs><rect width="2000" height="1031" fill="white"/><g class="f616-scaffold">')
 text(154,45,'Family',32,True); text(603,45,'Core mechanism',32,True); text(1449,45,'Method chronology (spacing not to scale)',32,True)
 for y in [261,458,655,852]: path(f'M18 {y}H1979','divider')
 for y in [179,376,572,769,954]: path(f'M917 {y}H1964','gray',True,True)
 add('</g>')
 def perspective():
  text(159,156,'(i) Perspective',32,True); photo('perspective/room',338,103,h=67)
  path('M480 136H521','blue',True,True)
  poly('535,92 665,92 665,173 535,173','#fff','#aab3b9',2)
  path('M535 92L561 108H639L665 92M535 173L561 156H639L665 173M561 108V156M639 108V156','blue')
  for x,y in [(561,108),(639,108),(561,156),(639,156)]: dot(x,y)
  path('M674 136H719','blue',True,True); room(735,91)
  text(603,231,'Corners / edges → decode or fit',29)
 zone('perspective',25,66,865,187,perspective)
 def panorama():
  text(159,353,'(ii) Panorama',32,True); photo('panorama/room',338,299)
  path('M480 333H521','blue',True,True)
  poly('535,289 668,289 668,372 535,372','#fff','#aab3b9',2)
  for x in [562,617,648]: path(f'M{x} 290V371','gray-thin')
  path('M535 314C559 299 568 306 590 317S620 321 638 313S658 305 668 306M535 351C556 341 569 351 587 360S617 363 639 353S657 347 668 349','blue',flow=True)
  path('M677 333H719','blue',True,True); room(735,287)
  text(603,428,'Boundary heights + corner signals',29)
 zone('panorama',25,270,865,180,panorama)
 def footprint():
  text(159,531,'(iii) Beyond',32,True); text(159,569,'cuboid',32,True); photo('beyond-cuboid/room',338,496,h=69)
  path('M480 530H527','blue',True,True)
  poly('550,489 653,489 653,539 617,539 617,566 550,566','#ebebff')
  for x,y in [(550,489),(653,489),(653,539),(617,539),(617,566),(550,566)]: dot(x,y)
  text(692,534,'/',32)
  poly('742,504 790,489 837,514 821,551 769,566 732,557','#ebebff')
  for x,y in [(742,504),(790,489),(837,514),(821,551),(769,566),(732,557)]: dot(x,y)
  text(603,625,'Project / fuse → footprint + height',29)
 zone('footprint',25,467,865,180,footprint)
 def planes():
  text(159,727,'(iv-a) Plane',32,True); text(159,765,'geometry',32,True)
  poly('375,683 412,683 394,763 357,763','#dfe3ff','#aab3b9',2.5)
  poly('412,683 449,683 431,763 394,763','#f0e7d6','#aab3b9',2.5)
  poly('449,683 510,683 492,763 431,763','#e9ebee','#aab3b9',2.5)
  path('M536 726H591','blue',True,True); room(624,675,170,89)
  text(603,822,'Plane depths → intersections',29)
 zone('planes',25,664,865,180,planes)
 def outdoor():
  text(159,912,'(iv-b) Outdoor',32,True); text(159,950,'cross-view',32,True); photo('outdoor/street',338,878)
  path('M484 911H567','blue',True,True)
  poly('600,863 800,863 800,956 600,956','#f3f4f6','#aab3b9',2)
  poly('637,863 757,863 757,956 637,956','#ebebff','#4545ed',2)
  path('M697 866V953','lane')
  add('<rect class="f616-vehicle" x="655" y="912" width="21" height="30"/><rect class="f616-vehicle" x="719" y="869" width="22" height="30"/>')
  text(603,1007,'Cross-view → road + vehicles (BEV)',29)
 zone('outdoor',25,862,865,163,outdoor)
 for k,x,y,w,h,title,desc,year,tick,axis in METHODS:
  def method(x=x,y=y,w=w,h=h,title=title,desc=desc,year=year,tick=tick,axis=axis):
   add(f'<rect class="f616-box" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
   text(x+w/2,y+38 if h==102 or h==101 else y+35,title,31)
   text(x+w/2,y+h-19,desc,29)
   path(f'M{tick} {y+h}V{axis+11}','gray-thin')
   text(tick,axis+59,year,29,blue=True)
  zone(k,x-4,y-3,w+8,axis+65-y,method)
 add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)

if __name__=='__main__':
 site=Path(__file__).resolve().parents[2]
 (site/'example/figure616.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure616-1"><title>Figure 6.16 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.16 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/layout_parsing_method.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig616()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure616-1';mountNative();</script></html>''')
