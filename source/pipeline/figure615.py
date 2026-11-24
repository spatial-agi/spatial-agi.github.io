"""Figure 6.15: structural layout estimation inputs and outputs."""
import json
from html import escape
from pathlib import Path

INFO = {
 'perspective': dict(t='Perspective room input', b='A perspective indoor image provides a single-view room observation. The estimator infers walls, floor, ceiling and corners from perspective cues.'),
 'panorama': dict(t='Panoramic room input', b='A 360-degree equirectangular panorama exposes a wider field of view and supports room-layout estimation beyond the visible perspective crop.'),
 'urban': dict(t='Outdoor street input', b='A dashcam image or video supplies an outdoor scene. Layout systems can predict road and surrounding surface structure from this view.'),
 'polygon': dict(t='Polygonal layout output', b='Polygonal layout represents rooms with 3D corners, edges and planes. Cuboid and non-rectangular footprints are alternative geometric outputs.'),
 'surface': dict(t='Per-pixel surface labels', b='Surface-label maps assign each pixel to floor, ceiling, wall, road, or another class. Indoor and outdoor maps use different scene-specific labels.'),
}

def fig615():
 out=[]; add=out.append
 def text(x,y,s,size=29,cls='text'):
  add(f'<text class="f615-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{s}</text>')
 def path(d,cls='ink',end=None,flow=True):
  m=f' marker-end="url(#f615-{end})"' if end else ''; r=' f615-route' if flow else ''
  add(f'<path class="f615-{cls}{r}" d="{d}"{m}/>')
 def line(x1,y1,x2,y2,cls='ink',dash=None):
  da=f' stroke-dasharray="{dash}"' if dash else ''; add(f'<path class="f615-{cls}" d="M{x1} {y1}L{x2} {y2}"{da}/>')
 def poly(points,cls='wall'): add(f'<polygon class="f615-{cls}" points="{points}"/>')
 def image(name,x,y,w,h): add(f'<image href="/assets/img/figs/f615/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def zone(k,x,y,w,h,draw):
  add(f'<g class="f615-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">'); draw(); add(f'<rect class="f615-hit" x="{x}" y="{y}" width="{w}" height="{h}"/>'); add('</g>')
 add('<div class="nf nf-615" data-nf="615" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1003" role="group" aria-label="Figure 6.15: structural layout estimation"><defs>')
 for n,c in [('blue','#4545ed'),('ink','#29343a')]: add(f'<marker id="f615-{n}" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="12" refY="7.5" orient="auto"><path d="M3 3L12 7.5L3 12Z" fill="{c}"/></marker>')
 add('<pattern id="f615-wall" patternUnits="userSpaceOnUse" width="26" height="26"><rect width="26" height="26" fill="#f0e7d6"/><path d="M0 0V26" stroke="#29343a" stroke-width="1.2"/></pattern>')
 add('<pattern id="f615-ceiling" patternUnits="userSpaceOnUse" width="34" height="34"><rect width="34" height="34" fill="#e9ebee"/><path d="M-17 17L17 -17M0 34L34 0M17 51L51 17" stroke="#29343a" stroke-width="1.8"/></pattern>')
 add('<pattern id="f615-floor" patternUnits="userSpaceOnUse" width="26" height="26"><rect width="26" height="26" fill="#dfe3ff"/><circle cx="13" cy="13" r="2.3" stroke="#29343a" stroke-width="1.4" fill="none"/></pattern>')
 add('<pattern id="f615-road" patternUnits="userSpaceOnUse" width="54" height="54"><rect width="54" height="54" fill="#c3cdd8"/><path d="M0 0L54 54M54 0L0 54" stroke="#29343a" stroke-width="1.4"/></pattern>')
 add('</defs><rect width="2000" height="1003" fill="#fff"/>')
 for x in [665,1330]: path(f'M{x} 90V451','divider',None,False)
 path('M22 474H1980','divider',None,False); path('M1000 620V980','divider',None,False)
 def top1(): text(333,47,'(i) Perspective room',36,'title'); image('perspective/room',24,82,617,309); text(333,438,'Perspective image',31)
 def top2(): text(998,47,'(ii) Panoramic room',36,'title'); image('panorama/room',689,82,616,309); text(997,438,'360° equirectangular panorama',31)
 def top3(): text(1662,47,'(iii) Urban street',36,'title'); image('urban/street',1353,82,617,309); text(1662,438,'Dashcam image / video',31)
 zone('perspective',4,8,650,450,top1); zone('panorama',670,8,650,450,top2); zone('urban',1335,8,660,450,top3)
 def polygon_panel():
  text(500,585,'(a) Polygonal layout',36,'title')
  path('M997 474V501H499V540','blue','blue')
  poly('197,641 443,680 443,790 197,751','wall')
  poly('52,811 197,751 443,790 279,845','floor')
  path('M52 811L197 751L443 790L279 845Z','blue')
  path('M197 751V641L443 680V790','ink',flow=False)
  path('M197 641L52 701L279 736L443 680M52 701V811M279 736V845','dash',flow=False)
  poly('742,629 942,666 942,776 742,739','wall')
  poly('760,688 863,715 863,825 760,798','wall')
  poly('548,811 742,739 942,776 863,825 760,798 658,845','floor')
  path('M548 811L742 739L942 776L863 825L760 798L658 845Z','blue')
  path('M742 739V629L942 666V776M942 666L863 715L760 688V798M863 715V825','ink',flow=False)
  path('M742 629L548 701L658 736L760 688M548 701V811M658 736V845','dash',flow=False)
  for x,y in [(197,641),(443,680),(742,629),(942,666),(760,688),(863,715)]: add(f'<circle class="f615-point" cx="{x}" cy="{y}" r="6"/>')
  for x,y in [(52,811),(197,751),(443,790),(279,845),(548,811),(742,739),(942,776),(863,825),(760,798),(658,845)]: add(f'<circle class="f615-point f615-blue-point" cx="{x}" cy="{y}" r="6"/>')
  text(250,899,'Cuboid room',29); text(755,899,'Non-rectangular room',29); text(500,957,'3D corners, edges and planes',31,'blue-text')
 zone('polygon',20,490,965,495,polygon_panel)
 def surface_panel():
  text(1495,585,'(b) Per-pixel surface labels',36,'title')
  path('M997 501H1499V540','blue','blue')
  poly('1055,624 1480,624 1382,654 1149,654','ceiling')
  poly('1055,624 1149,654 1149,769 1055,834','wall-map')
  poly('1149,654 1382,654 1382,769 1149,769','wall-map')
  poly('1480,624 1382,654 1382,769 1480,834','wall-map')
  poly('1149,769 1382,769 1480,834 1055,834','floor-map')
  text(1267,881,'Indoor',31)
  poly('1545,624 1966,624 1966,834 1545,834','other')
  poly('1545,624 1734,723 1734,741 1545,806','wall-map')
  poly('1966,624 1776,723 1776,741 1966,806','wall-map')
  poly('1545,834 1750,743 1768,743 1966,834','road')
  text(1755,881,'Outdoor',31)
  for x,y,l,c in [(1077,938,'Floor','floor-map'),(1369,938,'Ceiling','ceiling'),(1711,938,'Wall','wall-map'),(1077,985,'Road','road'),(1369,985,'Other / not modeled','other')]:
   add(f'<rect class="f615-swatch f615-{c}" x="{x}" y="{y-20}" width="37" height="28"/>')
   add(f'<text class="f615-text" x="{x+55}" y="{y}" font-size="28">{l}</text>')
 zone('surface',1015,490,980,495,surface_panel)
 add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)

if __name__=='__main__':
 site=Path(__file__).resolve().parents[2]
 (site/'example/figure615.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure615-1"><title>Figure 6.15 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.15 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/layout_parsing.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig615()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure615-1';mountNative();</script></html>''')
