"""Figure 6.11: photographs plus independently drawn pose geometry and chronology."""
import json
from html import escape
from pathlib import Path
INFO={
 'input':{'t':'Video or unordered views','b':'A sequence or image set supplies overlapping observations. Intrinsics K, depth, and IMU measurements may add constraints, depending on the method.'},
 'motion':{'t':'Relative motion','b':'Estimate the transformation ΔT between views and compose motions into a camera trajectory. Monocular motion generally has an unknown metric scale unless additional information fixes it.'},
 'localize':{'t':'Relocalization','b':'Estimate a query camera pose T_q in the coordinate frame of a known scene or map. The map provides the reference frame.'},
 'geometry':{'t':'Cameras and scene geometry','b':'Recover camera poses together with scene structure from overlapping observations. The point cloud and cameras here are schematic.'},
 'a':{'t':'Geometry-first methods','b':'Match observations and refine camera poses and structure with explicit geometry. The timeline lists representative publications; its spacing is not proportional to time and does not indicate computational dependencies.'},
 'b':{'t':'Learned and self-supervised odometry','b':'A network predicts motion and possibly depth. During self-supervised training, view warping produces a reconstruction loss; the dashed feedback path denotes this training signal.'},
 'c':{'t':'Hybrid learned–geometric methods','b':'Learn correspondence or geometric priors while retaining geometric estimation and refinement. Representative methods combine these components in different ways.'},
 'd':{'t':'Map-based relocalization','b':'A query image and known map support pose estimation by geometric solving or learned regression. Publication order does not imply that one method depends on the preceding method.'},
 'e':{'t':'Feed-forward geometric foundation models','b':'Predict camera relations and scene geometry directly from images using learned geometric priors. Some systems also use persistent state or geometric refinement.'},
}

def fig611():
 out=[]
 def add(s):out.append(s)
 def text(x,y,s,size=26,cls='f611-text',width=None):
  length=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
  add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{s}</text>')
 def sub(a,b):return a+f'<tspan baseline-shift="sub" font-size="68%">{b}</tspan>'
 def path(d,cls='f611-blue',arrow=False):
  marker=f' marker-end="url(#f611-{"gray" if "gray" in cls or "timeline" in cls else "arrow"})"' if arrow else ''
  add(f'<path class="{cls}" d="{d}"{marker}/>')
 def dot(x,y,r=5,gray=False):add(f'<circle class="f611-dot{" f611-gray-dot" if gray else ""}" cx="{x}" cy="{y}" r="{r}"/>')
 def camera(x,y,s=1):
  add(f'<g transform="translate({x} {y}) scale({s})"><path class="f611-camera" d="M0 0L36 -23V18Z M28 -18V13"/><circle class="f611-dot" r="6"/></g>')
 def box(x,y,w,h,labels,blue=False,size=26):
  add(f'<rect class="f611-box{" f611-net" if blue else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
  for i,label in enumerate(labels):text(x+w/2,y+h/2+size*.34+(i-(len(labels)-1)/2)*29,label,size)
 def zone(k,x,y,w,h,body):
  add(f'<g class="f611-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">');body();add(f'<rect class="f611-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')
 def photo(name,box_):
  x0,y0,x1,y1=box_;k=1791/2000
  add(f'<image href="/assets/img/figs/f611/{name}.png" x="{x0*k}" y="{y0*k}" width="{(x1-x0)*k}" height="{(y1-y0)*k}"/>')
 def cloud(x,y,s=1):
  for row in range(5):
   for col in range(8):dot(x+col*26*s,y+row*19*s,3.1*s)
  for row in range(8):
   for col in range(5):dot(x+(108+col*11)*s,y+(row*11-2)*s,3.7*s,True)
  for col in range(5):dot(x+(18+col*18)*s,y+78*s,3.3*s,True)
 def timeline(y,entries):
  path(f'M807 {y}H1752','f611-timeline f611-route',True)
  for x,w,labels,year,h in entries:
   box(x,y-10-h,w,h,labels,size=25)
   cx=x+w/2;path(f'M{cx} {y-10}V{y+13}','f611-gray')
   text(cx,y+42,str(year),25,'f611-text f611-blue-text')
 def matching(y):
  for x,yy in [(341,y-22),(331,y-3),(320,y+17)]:
   path(f'M{x} {yy}H{x+89}','f611-blue f611-match');dot(x,yy,4.6);dot(x+89,yy,4.6)
  path(f'M468 {y}H523','f611-blue f611-route',True);camera(557,y)
  for x,yy in [(664,y-36),(708,y+14)]:
   path(f'M585 {y}L{x} {yy}','f611-gray f611-dashed f611-route');dot(x,yy,5.5)
  text(529,y+56,'Match → geometric refinement',25,width=350)
 add('<div class="nf nf-611" data-nf="611" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1554" role="group" aria-label="Figure 6.11: visual odometry and camera pose estimation"><defs>')
 for id_,color in [('arrow','#4545ed'),('gray','#aab3b9')]:
  add(f'<marker id="f611-{id_}" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 2L10 6L2 10" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 add('</defs><rect width="2000" height="1554" fill="white"/><g transform="scale(1.116694584)">')
 text(1163,63,'Alternative pose-estimation outputs',32,'f611-title',569)
 for y in [573,784,935,1087,1239,1390]:path(f'M27 {y}H1764','f611-divider')
 text(391,619,'Family + core mechanism',29,'f611-title',356)
 text(1314,619,'Method chronology (spacing not to scale)',29,'f611-title',572)
 def inputs():
  text(267,63,'Video / unordered views',32,'f611-title',378)
  for x,label in [(100,sub('I','t−1')),(260,sub('I','t')),(421,sub('I','t+1'))]:text(x,108,label,31,'f611-math f611-ink')
  for name,b in [('video-previous',(30,144,193,309)),('video-current',(210,144,373,309)),('video-next',(388,144,552,309)),('image-set-left',(77,381,197,502)),('image-set-center',(212,381,333,502)),('image-set-right',(347,381,467,502))]:photo('input/'+name,b)
  text(270,494,'Sequence or image set',26,width=264);text(270,544,'Optional: K, depth, IMU',26,width=269)
  path('M506 295H546V518H1576','f611-blue f611-route')
 zone('input',24,28,530,526,inputs)
 def motion():
  text(738,136,'Relative motion',29,'f611-title',221)
  for x in [590,697,805]:camera(x,234)
  for x in [636,744]:path(f'M{x} 234H{x+44}','f611-blue f611-route',True)
  text(739,331,'Δ'+sub('<tspan font-style="normal" font-weight="bold">T</tspan>','i→j'),35,'f611-math')
  text(738,409,'VO / trajectory',28,width=181)
  path('M738 518V450','f611-blue f611-route',True)
 zone('motion',571,100,315,434,motion)
 def localize():
  text(1146,136,'Relocalization',29,'f611-title',202)
  photo('relocalization/query',(1107,200,1225,318))
  path('M1107 232H1159','f611-blue f611-route',True)
  path('M1182 182H1342V284H1182Z M1291 182V222H1230V284','f611-gray')
  camera(1229,239,.9)
  text(1146,349,'Query + known map',26,width=230);text(1146,409,sub('<tspan font-style="normal" font-weight="bold">T</tspan>','q'),35,'f611-math')
  path('M1146 518V450','f611-blue f611-route',True)
 zone('localize',979,100,381,434,localize)
 def geometry():
  text(1576,136,'Cameras + geometry',29,'f611-title',290)
  camera(1441,184,.9);camera(1416,284,.9);camera(1680,257,.9);cloud(1482,209)
  text(1576,380,'{'+sub('<tspan font-style="normal" font-weight="bold">T</tspan>','t')+'}',35,'f611-math')
  path('M1576 518V450','f611-blue f611-route',True)
 zone('geometry',1390,100,359,434,geometry)
 def a():
  text(149,702,'(a) Geometry-',29,'f611-title',193);text(149,735,'first',29,'f611-title')
  matching(711)
  timeline(716,[(813,185,['MonoSLAM','PTAM'],2007,71),(1009,189,['ORB-SLAM'],2015,49),(1210,162,['COLMAP'],2016,49),(1383,94,['DSO'],2017,49),(1488,168,['GLOMAP'],2024,49)])
 zone('a',27,631,1737,148,a)
 def b():
  text(149,853,'(b) Learned /',29,'f611-title',177);text(149,887,'self-supervised',29,'f611-title',217)
  box(306,816,124,69,['Net']);box(502,816,184,69,['Pose/depth']);path('M441 852H487','f611-blue f611-route',True)
  path('M689 852H736V926H366V889','f611-gray f611-dashed f611-route',True);text(600,910,'Warp loss',26,width=115)
  timeline(868,[(813,193,['DeepVO'],2017,49),(1017,248,['SfM-Learner'],2017,49)])
 zone('b',27,796,1737,135,b)
 def c():
  text(149,1022,'(c) Hybrid',29,'f611-title',135);matching(1014)
  timeline(1020,[(813,198,['SuperPoint'],2018,49),(1023,198,['SuperGlue'],2020,49),(1232,256,['LoFTR /','DROID-SLAM'],2021,71),(1499,198,['LEAP-VO'],2024,49)])
 zone('c',27,938,1737,143,c)
 def d():
  text(149,1173,'(d) Relocalization',29,'f611-title',242)
  path('M316 1119H435V1185H316Z M397 1119V1145H352V1185','f611-gray');camera(342,1160,.59)
  path('M452 1158H501','f611-blue f611-route',True);box(515,1117,231,79,['Solve / regress'],size=25);text(396,1224,'Query + map',25,width=146)
  timeline(1172,[(813,151,['PoseNet'],2015,49),(976,121,['DSAC'],2017,49),(1107,117,['HLoc'],2019,49),(1235,121,['ACE0'],2024,49),(1367,181,['Reloc3r'],2025,49)])
 zone('d',27,1098,1737,136,d)
 def e():
  text(149,1326,'(e) Feed-forward',29,'f611-title',230)
  for x,y in [(309,1294),(321,1285),(333,1276)]:add(f'<rect class="f611-stack" x="{x}" y="{y}" width="47" height="42"/>')
  path('M394 1309H437','f611-blue f611-route',True);box(452,1274,124,71,['Net'],blue=True);path('M588 1309H631','f611-blue f611-route',True)
  camera(640,1284,.57);cloud(667,1292,.41)
  timeline(1323,[(813,336,['DUSt3R · MASt3R'],2024,49),(1160,584,['MegaSaM · MonST3R · CUT3R','Fast3R · VGGT'],2025,71)])
 zone('e',27,1242,1737,141,e)
 add('</g></svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)

if __name__=='__main__':
 site=Path(__file__).resolve().parents[2]
 (site/'example/figure611.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure611-1"><title>Figure 6.11 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.11 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/visual_odometry_and_camera_pose_estimation.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig611()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure611-1';mountNative();</script></html>''')
