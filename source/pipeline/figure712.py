"""Figure 7.12: native optimization diagrams and extracted pictorial PNGs."""
from pathlib import Path
from html import escape
import json
SITE=Path(__file__).resolve().parents[2]
ORIGINAL='assets/figures/figures/part3/section7/differentiable_optimization_layers_for_spatial_reasoning.webp'
INFO={
'assignment':('QP relaxation of binary assignment','A partially specified Sudoku is encoded as a relaxed binary assignment problem. A quadratic-programming solver produces assignments subject to the puzzle constraints.'),
'mpc':('Differentiable convex MPC','The control sequence is optimized through a convex model-predictive-control layer. Differentiating through that layer lets upstream parameters learn from the resulting trajectory.'),
'ba':('Differentiable bundle adjustment','Camera poses and scene points are jointly refined by nonlinear least squares. Observation rays connect cameras to points, and the optimized geometry can participate in end-to-end learning.'),
'optnet':('OptNet QP solver','Input features parameterize a quadratic program through Q, q, A and b. The forward solve returns z*. Backpropagation uses implicit differentiation of the KKT optimality system.'),
'cvxpy':('CVXPY solver','A disciplined convex program is converted into cone form and solved by a conic solver. Gradients follow from the cone-system optimality conditions.'),
'ddn':('Deep Declarative Networks','The forward layer returns the optimizer of an objective rather than an explicit feed-forward formula. The implicit function theorem differentiates its optimality conditions.'),
'satnet':('SATNet','Logical constraints are passed to a relaxed SAT solver. The backward pass differentiates the solver’s fixed-point conditions so that the optimization layer can train with the surrounding network.')}
def fig712():
 o=[];a=o.append
 def text(x,y,v,size=23,cls='',raw=False,extra=''):
  a(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" class="'+ ' '.join('f712-'+c for c in cls.split())+f'" {extra}>{v if raw else escape(v)}</text>')
 def lines(x,ys,vs,size=23,cls=''):
  for y,v in zip(ys,vs):text(x,y,v,size,cls)
 def rect(x,y,w,h,cls='box',r=20):a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="f712-{cls}"/>')
 def path(d,cls='ink',arrow=False):a(f'<path d="{d}" class="'+ ' '.join('f712-'+c for c in cls.split())+'"'+(' marker-end="url(#f712-arrow)"' if arrow else '')+'/>')
 def arrow(d,dashed=False):path(d,'route dashed' if dashed else 'route',True)
 def image(file,x,y,w,h):a(f'<image href="/assets/img/figs/f712/{file}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def dot(x,y,r=5):a(f'<circle cx="{x}" cy="{y}" r="{r}" class="f712-dot"/>')
 def zone(k,b,draw):
  a(f'<g class="f712-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[k][0])}">');draw();rect(*b,'hit',5);a('</g>')
 def zstar(x,y):text(x,y,'z<tspan baseline-shift="super" font-size="65%">∗</tspan>',27,'math',True)
 a('<div class="nf nf-712" data-nf="712" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 742" role="group" aria-label="Figure 7.12: differentiable optimization layers for spatial reasoning"><defs><marker id="f712-arrow" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="9" refX="9" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9Z" fill="#123dd3"/></marker></defs><rect width="2000" height="742" fill="white"/><g class="f712-scaffold">')
 path('M66 333H1965M790 20V333M1357 23V333M522 333V736M1085 333V736M1564 333V736','divider')
 text(28,159,'Task Formulations',28,'blue-text',extra='transform="rotate(90 28 159)"');text(28,517,'Method Formulations',28,'blue-text',extra='transform="rotate(90 28 517)"')
 a('</g>')
 def assignment():
  for x,rows in [(66,('1??4','?41?','?14?','4??1')),(521,('1234','3412','2143','4321'))]:
   rect(x,30,215,216,'grid',0)
   for i in range(1,4):path(f'M{x+i*53.75} 30V246M{x} {30+i*54}H{x+215}','grid-line')
   for row,vals in enumerate(rows):
    for col,v in enumerate(vals):text(x+26.875+col*53.75,66+row*54,v,26)
  rect(320,70,162,137,'box',23);lines(401,(116,145,174),('QP Solver','(relaxed binary','assignment)'))
  arrow('M282 138H320');arrow('M482 138H521');text(411,302,'(1) QP relaxation of binary assignment',26)
 zone('assignment',(61,23,686,288),assignment)
 def mpc():
  image('ii-mpc/cart-pole-initial.png',849,66,119,157);image('ii-mpc/cart-pole-target.png',1159,54,119,169)
  for x,w in [(838,146),(1140,155)]:
   path(f'M{x} 221H{x+w}')
   for xx in range(x,x+w-9,18):path(f'M{xx+13} 223L{xx-3} 235')
  rect(1005,90,120,105,'box',20);lines(1065,(133,162),('Convex','MPC Layer'))
  arrow('M965 149H1005');arrow('M1125 149H1163')
  for x in (1007,1063,1120):arrow(f'M{x} 237V204')
  for x,label in [(903,'t'),(1225,'t+H')]:text(x,263,f'x<tspan baseline-shift="sub" font-size="70%">{label}</tspan>',29,'math',True)
  for x,label in [(1007,'t'),(1063,'t+1'),(1120,'t+2')]:text(x,257,f'u<tspan baseline-shift="sub" font-size="70%">{label}</tspan>',29,'math',True)
  text(1072,304,'(2) Differentiable Convex MPC',26)
 zone('mpc',(827,48,477,264),mpc)
 def ba():
  for prefix,cameras,points in [('input',[(1391,55,61,58),(1484,27,36,57),(1557,41,40,60)],[(1504,224),(1498,256),(1522,242),(1520,196),(1536,217),(1554,235)]),('output',[(1748,57,63,56),(1842,27,37,57),(1916,41,41,60)],[(1842,204),(1863,239),(1879,212),(1881,258),(1901,245),(1911,220)])]:
   origins=[(cameras[0][0]+51,114),(cameras[1][0]+15,88),(cameras[2][0]+17,103)]
   for (ox,oy),ids in zip(origins,[(0,2),(1,3),(4,5)]):
    for i in ids:path(f'M{ox} {oy}L{points[i][0]} {points[i][1]}','ray')
   for label,(x,y,w,h) in zip(('left','center','right'),cameras):image(f'iii-bundle-adjustment/{prefix}-camera-{label}.png',x,y,w,h)
   for x,y in points:dot(x,y)
  rect(1605,130,163,105,'box',18);lines(1686,(165,194,223),('Differentiable','Bundle','Adjustment'))
  arrow('M1565 182H1605');arrow('M1768 182H1808');text(1659,302,'(3) BA as Differentiable Nonlinear Least Squares',26)
 zone('ba',(1382,23,592,289),ba)
 def optnet():
  rect(73,379,114,120);lines(130,(432,461),('Input','Features'))
  rect(311,379,132,120);lines(377,(418,447,476),('Batched','GPU QP','Solver'))
  arrow('M187 439H301');text(245,420,'(Q, q, A, b)',28,'math')
  arrow('M443 437H481');zstar(493,440)
  rect(259,535,186,122,'backward');lines(352,(564,593,622,651),('Backward via','KKT-system','implicit','differentiation'))
  arrow('M378 499V535',True);arrow('M498 453V674H130V500');text(321,717,'(1) OpNet QP Solver',26)
 zone('optnet',(65,367,444,359),optnet)
 def cvxpy():
  rect(538,379,141,120);lines(608,(419,448,477),('Disciplined','Convex','Program'))
  rect(709,379,136,121);lines(777,(430,459),('Cone-form','Conversion'))
  rect(875,375,135,120);lines(943,(426,455,484),('ECOS / SCS','Conic','Solver'))
  arrow('M679 441H706');arrow('M845 442H873');arrow('M1010 437H1045');zstar(1058,440)
  rect(768,534,246,94,'backward',18);lines(891,(562,591,620),('Backward via cone-','system optimality','differentiation'))
  arrow('M947 495V534',True);arrow('M1062 454V672H608V500');text(813,717,'(2) CVXPY Solver',26)
 zone('cvxpy',(530,365,548,361),cvxpy)
 def ddn():
  rect(1097,375,114,120);lines(1154,(428,457),('Input','Features'))
  rect(1238,372,254,186,'box',15);text(1365,396,'Argmin Layer');text(1365,428,'z<tspan baseline-shift="sub" font-size="65%">∗</tspan>(θ) = argmin<tspan font-size="65%">f</tspan> (z; θ)',26,'math',True)
  for r in (54,32,13):a(f'<circle cx="1360" cy="497" r="{r}" class="f712-contour"/>')
  path('M1311 479L1355 510L1363 505','trajectory');dot(1311,479,5);dot(1355,510,5);dot(1363,505,4)
  arrow('M1211 434H1238');arrow('M1492 434H1520');zstar(1542,440)
  rect(1167,593,346,69,'backward',13);lines(1340,(621,650),('Implicit function theorem on','optimality conditions'))
  arrow('M1362 558V593',True);arrow('M1542 446V676H1154V496');text(1318,717,'(3) Deep Declarative Networks',26)
 zone('ddn',(1091,363,464,363),ddn)
 def satnet():
  rect(1586,375,134,238,'box',24);lines(1653,(416,445),('Logical','constraints'))
  text(1653,506,'C<tspan baseline-shift="sub" font-size="70%">1</tspan>',29,'math',True);text(1653,546,'C<tspan baseline-shift="sub" font-size="70%">2</tspan>',29,'math',True);text(1653,594,'...',29)
  rect(1764,396,134,92,'box',16);lines(1831,(432,461),('Relaxed','SAT Solver'))
  arrow('M1720 447H1764');arrow('M1898 440H1937');zstar(1965,445)
  rect(1743,522,217,108,'backward',20);lines(1852,(558,587,616),('Backward via fixed-','point implicit','differentiation'))
  arrow('M1835 488V522',True);arrow('M1968 461V666H1653V614');text(1782,717,'(4) SATNet',26)
 zone('satnet',(1577,365,410,361),satnet)
 a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
 return ''.join(o)
if __name__=='__main__':
 (SITE/'example/figure712.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.12 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure712-1"><style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style><main><h1>Figure 7.12 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="742" alt="Original Figure 7.12"><h2>Interactive reconstruction</h2>{fig712()}</main><script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure712-1';mountNative();</script></html>''')
