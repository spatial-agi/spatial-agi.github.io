"""Native reconstruction of Figure 7.11, preserving the 2000 × 1031 source geometry."""
from html import escape
import json
from pathlib import Path
SITE=Path(__file__).resolve().parents[2]
ORIGINAL='assets/figures/figures/part3/section7/geometry-aware_neural_spatial_reasoning.webp'
INFO={
 'classification':('Rotation-invariant classification','Rotating the input digit changes its pose but preserves the predicted class. An invariant classifier satisfies f(Rx) = f(x).'),
 'grasping':('SE(3)-equivariant grasping','A rigid transformation of the object must produce the corresponding transformation of the grasp. The gripper and its directions co-transform with the point cloud.'),
 'molecule':('Invariant molecular property','Rigid motion and reindexing of the atoms preserve the molecular identity and its scalar property E. Atom positions change while the predicted scalar remains the same.'),
 'alignment':('Learned alignment · STN','A localization network predicts transformation parameters θ. A grid generator and differentiable sampler align the features. This alignment is learned and does not guarantee exact invariance.'),
 'group':('Discrete group convolution · G-CNN','Rotated copies of shared filters produce orientation channels. Transforming the input permutes these channels in a predictable way for the chosen discrete rotation group.'),
 'steerable':('Steerable filters','Filters are linear combinations of basis kernels. Transforming their coefficients steers the filter response continuously, enabling equivariance to continuous rotations.'),
 'points':('Unordered point sets · PointNet','A shared MLP processes each point independently. Symmetric max pooling aggregates the point features, so reordering the same points leaves the resulting code unchanged.'),
 'messages':('3D equivariant messages','Messages combine relative geometry with scalar and vector features. Under a rigid transformation, vector features and messages co-transform consistently with the geometry.')}
def fig711():
 out=[];a=out.append
 def text(x,y,v,size=30,cls='',raw=False,extra=''):
  if 'heading' in cls: size *= .875
  elif 'math' not in cls and 'digit' not in cls and size != 48: size *= .9
  a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" class="'+ ' '.join('f711-'+c for c in cls.split())+f'" {extra}>{v if raw else escape(v)}</text>')
 def lines(x,ys,vs,size=30,cls=''):
  for y,v in zip(ys,vs):text(x,y,v,size,cls)
 def rect(x,y,w,h,cls='box',rx=7):a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="f711-{cls}"/>')
 def path(d,cls='ink',marker=None):a(f'<path d="{d}" class="'+ ' '.join('f711-'+c for c in cls.split())+'"'+(f' marker-end="url(#f711-{marker})"' if marker else '')+'/>')
 def arrow(d,gray=False):path(d,'route gray' if gray else 'route','gray' if gray else 'arrow')
 def circle(x,y,r,cls='node'):a(f'<circle cx="{x}" cy="{y}" r="{r}" class="f711-{cls}"/>')
 def zone(k,b,draw):
  a(f'<g class="f711-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k][0])}">');draw();rect(*b,'hit',6);a('</g>')
 a('<div class="nf nf-711" data-nf="711" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1031" role="group" aria-label="Figure 7.11: symmetry-driven tasks and geometric neural mechanisms"><defs>')
 for ident,color in [('arrow','#4145e9'),('gray','#aab2b8'),('dark','#29353b')]:
  a(f'<marker id="f711-{ident}" markerWidth="14" markerHeight="13" refX="11" refY="6.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 2L11 6.5L2 11" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 a('</defs><rect width="2000" height="1031" fill="white"/><g class="f711-scaffold">')
 path('M665 30V416M1335 30V416M17 422H1983M400 445V1001M800 445V1001M1200 445V1001M1600 445V1001','divider')
 for x,v in [(331,'(i) Rotation-invariant classification'),(1000,'(ii) SE(3)-equivariant grasping'),(1670,'(iii) Invariant molecular property')]:text(x,61,v,36,'heading')
 for x,vs in [(200,('(a) Learned','alignment')),(600,('(b) Discrete group','convolution')),(1000,('(c) Steerable','filters')),(1400,('(d) Unordered','point sets')),(1800,('(e) 3D equivariant','messages'))]:lines(x,(475,510),vs,36,'heading')
 a('</g>')
 def classification():
  for cx,angle,label in [(86,0,'0°'),(234,-90,'90°'),(382,180,'180°')]:
   rect(cx-58.5,129,117,130)
   text(cx,215,'5',80,'digit',extra=f'transform="rotate({angle} {cx} 194)"')
   text(cx,293,label,28)
  arrow('M461 194H503');rect(523,142,102,105,'blue-box');text(574,206,'5',48)
  text(332,369,'f (Rx) = f (x)',39,'math blue-text')
 zone('classification',(20,110,620,285),classification)
 def grasping():
  a('<image href="/assets/img/figs/f711/ii-grasping/point-cloud-original.png" x="756" y="165" width="126" height="101"/>')
  a('<image href="/assets/img/figs/f711/ii-grasping/point-cloud-rotated.png" x="1065" y="180" width="153" height="112"/>')
  path('M769 159V120H868V159M1067 211L1039 183L1109 113L1137 141','blue-ink')
  arrow('M901 237V216');arrow('M910 246H932');arrow('M1215 171L1201 157');arrow('M1229 171L1243 157')
  arrow('M938 194H1006');text(978,147,'g',38,'math blue-text');text(1000,369,'f (gx) = g f (x)',39,'math blue-text')
 zone('grasping',(740,103,525,291),grasping)
 def molecule():
  path('M1400 237L1471 182L1542 237M1773 289L1738 206L1811 153')
  for x,y,r,label,idx in [(1400,237,23,'H','2'),(1471,182,23,'O','1'),(1542,237,23,'H','3'),(1773,289,23,'H','1'),(1738,206,23,'O','3'),(1811,153,23,'H','2')]:
   circle(x,y,r,'oxygen' if label=='O' else 'atom');text(x,y+9,label,29);text(x,y-r-10,idx,28,'gray-text')
  arrow('M1575 203H1633');lines(1895,(192,223),('Same','scalar E'),32,'blue-text')
  text(1668,369,'E(π(gX)) = E(X)',39,'math blue-text')
 zone('molecule',(1365,88,611,310),molecule)
 def alignment():
  arrow('M33 619H18V739H70',True);rect(34,573,332,77,'blue-box');text(200,619,'Localization → θ',32)
  arrow('M200 661V679');rect(83,695,234,81);text(200,743,'Grid + sampler',32)
  arrow('M200 787V805');text(200,860,'Aligned features',32,'blue-text');text(200,935,'STN',36,'heading');text(200,995,'Learned, not guaranteed',28)
 zone('alignment',(12,550,375,455),alignment)
 def group():
  for x,ang in [(446,0),(535,-90),(625,180),(714,90)]:
   circle(x,625,29,'filter');a(f'<path d="M{x-2} 620L{x+8} 625L{x-2} 630Z" class="f711-blue-fill" transform="rotate({ang} {x} 625)"/>')
  text(600,706,'Shared rotated filters',30)
  for x,y in [(492,763),(532,749),(572,735),(612,722)]:rect(x,y,114,71,'blue-box')
  text(600,885,'Orientation channels',30,'blue-text');text(600,947,'G-CNN',36,'heading');text(600,1001,'Discrete rotations',29)
 zone('group',(410,565,379,441),group)
 def steerable():
  circle(874,625,25,'basis');circle(1011,625,14,'basis')
  a('<g class="f711-kernel">')
  for angle in (0,90,180,270):a(f'<ellipse cx="1120" cy="611" rx="8" ry="14" class="f711-basis" transform="rotate({angle} 1120 625)"/>')
  a('</g>');text(1000,706,'Combine basis kernels',30)
  text(919,788,'K =',38,'math blue-text');text(985,794,'∑',66,'math blue-text');text(985,831,'m',28,'math blue-text')
  text(1065,788,'a<tspan baseline-shift="sub" font-size="70%">m</tspan>ψ<tspan baseline-shift="sub" font-size="70%">m</tspan>',38,'math blue-text',True)
  text(1000,879,'Transform coefficients',30);text(1000,947,'Steerable CNN',36,'heading');text(1000,1001,'Continuous rotations',29)
 zone('steerable',(810,565,379,441),steerable)
 def points():
  for x,y in [(1292,585),(1252,628),(1311,656)]:circle(x,y,9,'point')
  arrow('M1338 622H1350');rect(1366,573,185,101,'blue-box');lines(1458,(615,646),('Shared','MLP'),32)
  arrow('M1458 687V713');rect(1264,732,284,81);text(1406,780,'Max over points',32)
  text(1400,881,'Same set → same code',30,'blue-text');text(1400,947,'PointNet',36,'heading');text(1400,1001,'Permutation invariance',29)
 zone('points',(1210,552,379,454),points)
 def messages():
  arrow('M1662 662L1771 590');arrow('M1914 647L1787 589')
  for x,y in [(1662,662),(1779,585),(1914,647)]:
   circle(x,y,14,'message-node');path(f'M{x+5} {y-7}L{x+15} {y-20}','vector','dark')
  lines(1800,(735,783),('Relative geometry +','scalar / vector features'),30)
  text(1800,860,'Co-transform messages',30,'blue-text')
  lines(1800,(938,990),('TFN / SE(3)-','Transformer'),36,'heading')
 zone('messages',(1610,548,379,458),messages)
 a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
 return ''.join(out)
if __name__=='__main__':
 (SITE/'example/figure711.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.11 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure711-3"><style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style><main><h1>Figure 7.11 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="1031" alt="Original Figure 7.11"><h2>Interactive reconstruction</h2>{fig711()}</main><script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure711-3';mountNative();</script></html>''')
