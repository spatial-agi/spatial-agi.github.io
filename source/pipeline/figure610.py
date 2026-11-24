"""Figure 6.10: metric scale, reconstructed at the original 2000 × 1124 size."""
import json
from html import escape
from pathlib import Path

INFO = {
 'stereo': {'t':'Calibrated stereo geometry','b':'The same scene point P projects to x_L and x_R in a rectified stereo pair. A known focal length f and camera baseline B make metric depth observable.'},
 'depth': {'t':'Disparity determines depth','b':'Disparity is d = x_L − x_R. For rectified cameras, Z = fB/d. The focal length and disparity must use the same image units; depth uses the units of the baseline.'},
 'height': {'t':'Reference and unknown height','b':'The reference and target share a ground plane and vertical direction. Their image heights alone are insufficient: perspective must be accounted for using the horizon and reference geometry.'},
 'transfer': {'t':'Projective height transfer','b':'A known reference height fixes scale. Ground-plane and vertical-direction geometry transfer that scale to another upright object in the same image.'},
 'rectangle': {'t':'Known planar reference','b':'The outlined reference rectangle and target lie on a shared plane. The reference dimensions provide the metric scale after the plane is rectified.'},
 'rectify': {'t':'Rectify the plane and set scale','b':'Use the known rectangle to constrain a planar rectification. Transfer its known dimensions to the coplanar target; reliability depends on the reference geometry and image measurements.'},
}

def fig610():
 out=[]
 def add(s): out.append(s)
 def text(x,y,label,size=30,cls='f610-text',width=None):
  length=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
  add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{label}</text>')
 def sub(a,b): return a+f'<tspan baseline-shift="sub" font-size="68%">{b}</tspan>'
 def path(d,cls='f610-line',arrow=False,both=False):
  marker=(' marker-end="url(#f610-arrow)"' if arrow or both else '')+(' marker-start="url(#f610-arrow)"' if both else '')
  add(f'<path class="{cls}" d="{d}"{marker}/>')
 def image(name,x,y,w,h): add(f'<image href="/assets/img/figs/f610/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def zone(k,x,y,w,h,body):
  add(f'<g class="f610-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">')
  body()
  add(f'<rect class="f610-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/></g>')
 add('''<div class="nf nf-610" data-nf="610" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1124" role="group" aria-label="Figure 6.10: sources of metric scale in vision-based measurement"><defs><marker id="f610-arrow" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M2 3L12 8L2 13" fill="none" stroke="#3e43e9" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="2000" height="1124" fill="#fff"/>''')
 path('M671 51V1078 M1329 51V1078','f610-divider')
 def stereo():
  text(338,76,'(a) Calibrated stereo',36,'f610-title',357)
  text(323,155,'P',38,'f610-math f610-ink')
  path('M323 200V566 M138 295V541 M507 295V541','f610-guide f610-dashed')
  path('M323 200L149 541','f610-line f610-route')
  path('M323 200L497 541','f610-line f610-route')
  add('<circle cx="323" cy="200" r="10" fill="#29343a"/><circle class="f610-point" cx="229" cy="384" r="9"/><circle class="f610-point" cx="417" cy="384" r="9"/>')
  path('M41 384H306 M352 384H626','f610-guide')
  text(198,349,sub('x','L'),36,'f610-math');text(447,349,sub('x','R'),36,'f610-math');text(351,487,'Z',36,'f610-math')
  for x in [101,470]:
   add(f'<rect class="f610-camera" x="{x}" y="541" width="75" height="44"/><circle class="f610-camera" cx="{x+37.5}" cy="563" r="12"/>')
  text(138,626,'L',32);text(507,626,'R',32)
  path('M67 401V547','f610-blue f610-route',both=True);text(32,487,'f',36,'f610-math')
  path('M143 671H504','f610-blue f610-route',both=True);text(323,721,'B',36,'f610-math')
 zone('stereo',23,35,630,704,stereo)
 def depth():
  text(338,799,'Rectified coordinates',30,width=296)
  text(239,877,'d = '+sub('x','L')+' − '+sub('x','R')+' ,',38,'f610-math',210)
  text(455,877,'Z =',38,'f610-math',60);text(522,858,'f B',28,'f610-math',38)
  path('M502 868H542','f610-blue f610-fraction');text(522,891,'d',30,'f610-math')
  text(338,986,'Known intrinsics + metric baseline',30,width=474)
  text(338,1051,'Triangulation gives metric depth',30,width=441)
 zone('depth',23,757,630,310,depth)
 def height():
  text(1000,76,'(b) Monocular metrology',36,'f610-title',429)
  text(1000,158,'Known height → unknown height',30,width=439)
  image('b/street-people-clean',692,189,616,412)
  path('M692 414H1308','f610-blue f610-horizon')
  path('M824 309V545','f610-blue f610-route',both=True)
  path('M1145 347V487','f610-blue f610-route',both=True)
  text(772,376,sub('h','ref'),36,'f610-math');text(1203,365,'h ?',36,'f610-math')
 zone('height',687,35,626,576,height)
 def transfer():
  text(1000,666,'Shared ground + vertical direction',30,width=465)
  path('M1000 695V751','f610-blue f610-route',arrow=True)
  add('<rect class="f610-box" x="729" y="769" width="542" height="148" rx="7"/>')
  text(1000,829,'Projective height transfer',32,'f610-title',393)
  text(1000,887,'Horizon + reference height',30,width=365)
  text(1000,1008,'One image alone has unknown scale',30,width=506)
 zone('transfer',687,631,626,407,transfer)
 def rectangle():
  text(1661,76,'(c) Reference-assisted estimation',36,'f610-title',589)
  text(1661,159,'Unknown calibration; known reference',30,width=534)
  image('c/tabletop-clean',1353,189,617,412)
  image('c/reference-card',1396,396,180,73)
  image('c/target-rectangle',1599,351,336,127)
  path('M1422 398H1574L1567 465H1397Z M1612 353H1888L1933 469H1601Z','f610-blue')
  for x,y in [(1422,398),(1574,398),(1567,465),(1397,465),(1612,353),(1888,353),(1933,469),(1601,469)]: add(f'<circle class="f610-point" cx="{x}" cy="{y}" r="5.5"/>')
  path('M1397 469V488 M1567 469V488 M1601 474V492 M1933 474V492','f610-blue')
  path('M1401 481H1563','f610-blue f610-route',both=True)
  path('M1605 485H1929','f610-blue f610-route',both=True)
  text(1496,558,sub('L','ref'),36,'f610-math');text(1770,558,'L ?',36,'f610-math')
 zone('rectangle',1347,35,629,576,rectangle)
 def rectify():
  text(1661,666,'Known rectangle + coplanarity',30,width=418)
  path('M1661 695V751','f610-blue f610-route',arrow=True)
  add('<rect class="f610-box" x="1372" y="769" width="576" height="148" rx="7"/>')
  text(1661,829,'Rectify plane; transfer scale',32,'f610-title',437)
  text(1661,887,'Reference dimensions set units',30,width=407)
 zone('rectify',1347,631,629,306,rectify)
 add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)

if __name__=='__main__':
 site=Path(__file__).resolve().parents[2]
 (site/'example/figure610.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure610-1"><title>Figure 6.10 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.10 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/height_estimation_2.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig610()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure610-1';mountNative();</script></html>''')
