"""Figure 6.12: independently reconstructed pose diagram at source resolution."""
import json
from html import escape
from pathlib import Path

INFO={
 'input':dict(t='RGB and RGB-D input',b='Estimate the pose of rigid objects from a color image or an image with depth. The blue rectangle indicates the object of interest.'),
 'prior':dict(t='Object-specific priors',b='A CAD mesh, a canonical coordinate frame, or a few reference views supplies the object geometry or appearance needed by the pose estimator. These are alternative types of prior.'),
 'output':dict(t='Six-degree-of-freedom pose',b='The output transformation T_o consists of rotation R and translation t. It maps the object frame into the camera frame. The scene overlay illustrates the recovered alignment.'),
 'instance':dict(t='Instance-level, CAD-aware estimation',b='A known object mesh supports correspondence-based solving and render-and-compare refinement. Boxes summarize representative methods in the order shown in the source figure.'),
 'category':dict(t='Category-level canonical-frame estimation',b='Different objects in a category are mapped into a shared canonical frame. These methods estimate pose and often object size despite variation in shape.'),
 'foundation':dict(t='Model-free and foundation-era estimation',b='A few reference views or a CAD reference provide information about a new object. A pretrained model uses that information to estimate pose without training a separate model for each object.')
}

def fig612():
 out=[]
 def add(s):out.append(s)
 def text(x,y,label,size=22,cls='f612-text',width=None):
  length=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
  add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{label}</text>')
 def sub(a,b):return a+f'<tspan baseline-shift="sub" font-size="68%">{b}</tspan>'
 def path(d,cls='f612-line',arrow=None):
  marker=f' marker-end="url(#f612-{arrow})"' if arrow else ''
  add(f'<path class="{cls}" d="{d}"{marker}/>')
 def rect(x,y,w,h,cls='f612-frame',rx=0):
  add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
 def img(name,x,y,w,h):
  add(f'<image href="/assets/img/figs/f612/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def zone(k,x,y,w,h,body):
  add(f'<g class="f612-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">')
  body()
  rect(x,y,w,h,'f612-hit',8)
  add('</g>')
 def axes(x,y,ends,labels):
  for color,(ex,ey),(tx,ty),label in zip(['blue','green','red'],ends,labels,['Z','Y','X']):
   path(f'M{x} {y}L{ex} {ey}',f'f612-axis f612-{color} f612-route',color)
   text(tx,ty,label,26,f'f612-math f612-{color}-text')
  add(f'<circle cx="{x}" cy="{y}" r="4" fill="#1d57ad"/>')
 def film(x,y,w,h,divs):
  rect(x,y,w,h,'f612-film')
  for yy in [y+4,y+h-6]:
   for xx in range(int(x+4),int(x+w-3),8):
    rect(xx,yy,4,4,'f612-perf')
  for xx in divs:path(f'M{xx} {y+8}V{y+h-8}','f612-film-line')
 def methods(y,entries,last,ty):
  for i,(x,w,name,year) in enumerate(entries):
   rect(x,y,w,69,'f612-method',13)
   size=18 if len(name)<14 else 17
   text(x+w/2,y+28,name,size,width=min(w-6,len(name)*9.5))
   text(x+w/2,y+52,str(year),18)
   if i<len(entries)-1:
    path(f'M{x+w+2} {y+34}H{entries[i+1][0]-3}','f612-line f612-route','black')
  x=entries[-1][0]+entries[-1][1]
  path(f'M{x+2} {y+34}H{last}','f612-blue f612-dashed f612-route','blue')
  text(1868,ty,'2017 → 2024 +',26,'f612-text f612-blue-text',176)
 add('<div class="nf nf-612" data-nf="612" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1100" role="group" aria-label="Figure 6.12: 6-DoF object pose estimation"><defs>')
 for name,color in [('black','#111'),('blue','#084ddd'),('green','#419653'),('red','#c53535')]:
  add(f'<marker id="f612-{name}" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1L13 7L1 13Z" fill="{color}"/></marker>')
 add('</defs><rect width="2000" height="1100" fill="#fff"/>')
 rect(1,17,1969,520,'f612-outer',21)
 rect(1,562,1969,449,'f612-outer',21)
 path('M16 696H1959 M16 843H1959','f612-divider')
 def inputs():
  img('input/rgb-scene',98,43,368,215)
  rect(96,41,372,219)
  rect(259,111,116,127,'f612-detection')
  text(289,288,'RGB Image',23)
  img('input/rgbd-color',63,314,211,105);rect(60,312,216,109)
  img('input/rgbd-depth',284,314,212,105);rect(282,312,216,109)
  text(284,447,'RGB-D Image',23)
  text(284,504,'RGB-(D) Image of rigid object(s)',30,width=431)
  path('M590 249H629','f612-line f612-thick f612-route','black')
 zone('input',42,32,598,485,inputs)
 def prior():
  rect(649,90,503,351,'f612-pipeline',15)
  text(898,143,'6-DoF Pose Pipeline',30,width=280)
  for x,w in [(667,137),(815,156),(981,154)]:rect(x,176,w,245,'f612-prior',11)
  img('priors/cad-drill',679,198,113,133)
  text(737,375,'CAD',23);text(737,404,'mesh',23)
  axes(871,289,[(871,233),(912,273),(912,310)],[(871,223),(931,278),(931,326)])
  text(894,375,'Canonical',23);text(894,404,'frame',23)
  film(1002,206,117,133,[1062])
  path('M1003 273H1062','f612-film-line')
  img('priors/reference-top',1008,224,43,43)
  img('priors/reference-bottom',1008,280,43,44)
  img('priors/reference-right',1070,253,44,53)
  text(1059,375,'Few reference',23,width=146);text(1059,404,'view(s)',23)
  path('M1171 249H1217','f612-line f612-thick f612-route','black')
  text(1130,511,'Task: recover '+sub('<tspan class="f612-math f612-ink">T</tspan>','o')+' in <tspan class="f612-math f612-ink">SE(3)</tspan> for each rigid object given an RGB-(D) image',29,width=945)
 zone('prior',645,83,578,440,prior)
 def output():
  text(1324,63,sub('<tspan font-weight="bold">T</tspan>','o')+' =',32,'f612-math f612-blue-text')
  path('M1377 29H1371V81H1377 M1466 29H1472V81H1466','f612-blue')
  text(1397,46,'R',32,'f612-math f612-blue-text f612-bold')
  text(1457,46,'t',32,'f612-math f612-blue-text f612-bold')
  text(1397,84,'0<tspan baseline-shift="super" font-size="65%">T</tspan>',30,'f612-math f612-blue-text')
  text(1457,84,'1',30,'f612-math f612-blue-text')
  text(1540,63,'∈ SE(3)',32,'f612-math f612-blue-text',112)
  img('output/posed-scene',1247,101,403,310);rect(1244,99,408,314)
  rect(1708,105,234,225,'f612-pose-frame',13)
  img('output/drill-without-axes',1728,170,133,141)
  axes(1807,232,[(1807,155),(1889,231),(1874,281)],[(1808,144),(1908,236),(1895,297)])
  path('M1736 347C1725 380 1707 391 1668 403','f612-blue f612-thick f612-route','blue')
  text(1843,386,'Output 6-DoF',30,'f612-text f612-blue-text',189);text(1843,424,'pose',30,'f612-text f612-blue-text')
 zone('output',1237,22,714,414,output)
 def instance():
  rect(16,585,193,86,'f612-family',5)
  text(112,620,'(i) Instance-level',22,width=168);text(112,650,'(CAD-aware)',22)
  img('instance/cad-drill',237,589,76,89)
  path('M323 633H345','f612-line f612-route','black')
  img('instance/posed-drill',367,592,79,83);rect(358,585,103,93)
  methods(586,[(612,88,'PoseCNN',2017),(747,89,'SSD-6D',2017),(882,89,'DeepIM',2018),(1017,89,'PVNet',2019),(1152,122,'DenseFusion',2019),(1321,94,'CosyPose',2020),(1461,88,'GDR-Net',2021),(1602,89,'EPro-PnP',2022)],1770,629)
 zone('instance',10,574,1950,112,instance)
 def category():
  rect(16,721,193,86,'f612-family',5)
  text(112,758,'(ii) Category-',22);text(112,787,'level (NOCS)',22)
  axes(286,781,[(286,740),(319,766),(319,800)],[(286,734),(336,766),(337,815)])
  for d in ['M296 780L392 765','M296 781L458 782','M296 783L543 806']:
   path(d,'f612-gray f612-dashed f612-route','black')
  for n,x,y,w,h in [('small',397,725,49,51),('tall',462,725,55,67),('wide',547,748,65,69)]:
   img('category/cup-'+n,x,y,w,h)
  methods(735,[(670,88,'NOCS',2019),(803,89,'FS-Net',2021),(936,88,'GPV-Pose',2022),(1068,89,'SAR-Net',2022),(1201,89,'IST-Net',2023),(1334,89,'GenPose',2023),(1467,119,'SecondPose',2024),(1630,89,'AG-Pose',2024)],1770,779)
 zone('category',10,710,1950,120,category)
 def foundation():
  rect(16,868,193,85,'f612-family',5)
  text(112,904,'(iii) Model-free /',22);text(112,933,'foundation-era',22)
  film(242,869,206,72,[298,354,410])
  img('foundation/drill',249,883,38,46);img('foundation/cup',306,887,37,37);img('foundation/chair',361,880,37,50)
  text(427,909,'⋯',22)
  text(347,969,'Few reference view(s)',22);text(347,997,'or single CAD reference',22)
  path('M461 910H483','f612-line f612-route','black')
  rect(493,863,160,96,'f612-model',8)
  text(573,905,'Foundation model',19,width=155);text(573,930,'(large pretrained)',18,width=143)
  path('M661 910H681','f612-line f612-route','black')
  text(708,917,sub('T','o'),28,'f612-math f612-blue-text')
  methods(876,[(750,91,'OnePose',2022),(889,113,'OnePose++',2022),(1049,89,'Gen6D',2022),(1186,97,'MegaPose',2022),(1331,151,'FoundationPose',2024),(1530,89,'SAM-6D',2024),(1666,88,'Diff9D',2024)],1779,919)
 zone('foundation',10,854,1950,150,foundation)
 add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)

if __name__=='__main__':
 site=Path(__file__).resolve().parents[2]
 (site/'example/figure612.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure612-1"><title>Figure 6.12 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.12 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/pose_estimation.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig612()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure612-1';mountNative();</script></html>''')
