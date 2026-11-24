"""Source-aligned Figure 6.26: audio-visual spatial localization."""
import json
import math
from html import escape
from pathlib import Path
SITE=Path(__file__).resolve().parents[2]
INFO={
'vssl':{'t':'Visual sound-source localization','b':'Match the sound to a region in the image. The highlighted radio illustrates a sounding object; the task output is an image region rather than a metric 3D position.'},
'asd':{'t':'Active speaker detection','b':'Track faces and determine who is speaking at each time. Audio and visible mouth activity help distinguish a speaking face from a silent one.'},
'seld':{'t':'Audio-visual sound event localization and detection','b':'Predict the event class, its active time interval and direction of arrival (DOA). A direction identifies a bearing; it does not by itself determine distance.'},
'depth':{'t':'2.5D localization','b':'Associate an image location (u, v) with depth or range. The depth cue lifts the selected location beyond the image plane; metric scale depends on the available depth information.'},
'tracking':{'t':'3D localization and tracking','b':'Recover a source position and its trajectory over time. Range cues or triangulation constraints are needed to turn a bearing into a 3D position.'},
'correspondence':{'t':'Cross-modal correspondence','b':'Compare an audio representation with local visual features in a shared space. Contrastive alignment uses matching and non-matching pairs to learn which image regions correspond to a sound.'},
'synchrony':{'t':'Audio–lip synchrony','b':'Align changes in the audio signal with mouth motion over time. Temporal audio-visual fusion produces speaking scores for tracked faces.'},
'joint':{'t':'Joint spatial event prediction','b':'Fuse audio and visual information, then use joint output heads for event activity and direction of arrival. Range is an optional prediction when suitable cues are available.'},
'geometry':{'t':'Geometric lifting and fusion','b':'Combine a bearing with depth or triangulation using calibrated constraints between the array and camera. The resulting 3D points can then be tracked through time.'},
}
def fig626():
 out=[];add=out.append
 def text(x,y,t,size=31,cls='text'):
  add(f'<text class="f626-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(t)}</text>')
 def rect(x,y,w,h,cls='module',rx=0):add(f'<rect class="f626-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
 def path(d,cls='blue',arrow=False,flow=False):
  add(f'<path class="f626-{cls}{" f626-route" if flow else ""}" d="{d}"'+(f' marker-end="url(#f626-{"ink" if cls.startswith("ink") else "blue"})"' if arrow else '')+'/>')
 def circle(x,y,r,cls='point'):add(f'<circle class="f626-{cls}" cx="{x}" cy="{y}" r="{r}"/>')
 def image(name,x,y,w,h):add(f'<image href="/assets/img/figs/f626/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def wave(x,y,w,amplitude=17,cycles=15,cls='wave',peaks=None):
  pts=[]
  for i in range(401):
   u=i/400
   env=math.exp(-((u-.5)/.28)**2) if peaks is None else sum(math.exp(-((u-c)/.065)**2) for c in peaks)
   v=y-amplitude*env*math.sin(u*cycles*2*math.pi)
   pts.append(f'{"M" if i==0 else "L"}{x+w*u:.2f} {v:.2f}')
  path(''.join(pts),cls,flow=True)
 def array(x,y,r=33):
  circle(x,y,r,'array')
  for angle in [-90,-18,54,126,198]:
   a=math.radians(angle);circle(round(x+20*math.cos(a),2),round(y+20*math.sin(a),2),4.5,'ink-fill')
 def camera(x,y,w=56,h=46):
  rect(x,y,w,h,'camera',7);path(f'M{x+w-4} {y+12}L{x+w+17} {y+2}V{y+h-2}L{x+w-4} {y+h-12}','ink')
 def zone(k,x,y,w,h,draw):
  add(f'<g class="f626-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">');draw();rect(x,y,w,h,'hit',6);add('</g>')
 add('<div class="nf nf-626" data-nf="626" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1031" role="group" aria-label="Figure 6.26: audio-visual spatial localization"><defs>')
 for name,color in [('blue','#4146eb'),('ink','#2c373d')]:
  add(f'<marker id="f626-{name}" markerUnits="userSpaceOnUse" markerWidth="17" markerHeight="17" refX="12" refY="8" orient="auto"><path d="M3 3L12 8L3 13" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 add('</defs><rect width="2000" height="1031" fill="white"/><g class="f626-scaffold">')
 for x in [400,800,1200,1600]:path(f'M{x} 24V419','divider')
 for x in [499,1000,1502]:path(f'M{x} 494V995','divider')
 for x,t in [(200,'(i) VSSL'),(600,'(ii) ASD'),(1000,'(iii) AV-SELD'),(1400,'(iv) 2.5D'),(1800,'(v) 3D / tracking')]:text(x,55,t,36,'title')
 for x,lines in [(250,['(A) Cross-modal','correspondence']),(750,['(B) Audio–lip','synchrony']),(1250,['(C) Joint spatial','event prediction']),(1750,['(D) Geometric','lifting / fusion'])]:
  for i,t in enumerate(lines):text(x,530+i*35,t,36,'title')
 # Neutral task-to-family associations have no arrowheads or moving marks.
 path('M199 424L247 481M599 424L746 481M999 424L1247 481M1400 423V453H1800V423M1747 453V481','connector')
 add('</g>')
 def vssl():
  image('i-vssl/radios',38,121,324,173);rect(37,120,326,175,'image-border')
  rect(58,175,106,84,'selection');wave(76,332,248,17,15)
  text(200,395,'Sound → image region',33)
 zone('vssl',25,106,350,304,vssl)
 def asd():
  image('ii-asd/conversation',438,112,324,173);rect(437,111,326,175,'image-border')
  rect(458,126,93,118,'selection');text(523,322,'speaking',31,'blue-text');text(674,322,'silent',31)
  wave(470,354,260,12,15);text(600,401,'Face track + speaking state',31)
 zone('asd',409,101,382,310,asd)
 def seld():
  circle(966,215,93,'axis');circle(966,215,49,'axis');path('M864 215H1069M966 113V317','axis')
  text(999,109,'speech',31,'blue-text');path('M966 215L1052 148','blue',True,True);text(1092,164,'DOA',31,'blue-text')
  path('M860 342H1140','axis');rect(911,335,163,13,'activity')
  text(1000,395,'Event + time + direction',32)
 zone('seld',820,77,365,335,seld)
 def depth():
  image('iv-depth/person-room',1245,119,172,171);rect(1243,117,176,175,'image-border');rect(1255,135,43,130,'selection')
  circle(1281,197,7);path('M1281 197H1432','dashed',flow=True);path('M1432 197H1467','blue',True,True)
  rect(1478,158,87,78,'module',8);text(1522,205,'z',31);text(1495,294,'depth',31,'blue-text')
  text(1400,350,'(u, v) + depth / range',31,'blue-text');text(1400,395,'Metric scale if available',31)
 zone('depth',1212,105,376,307,depth)
 def tracking():
  path('M1706 248L1760 191','dashed',flow=True);array(1686,271);camera(1855,251);path('M1796 154L1885 275','gray-dashed')
  path('M1760 191L1796 154L1846 132L1895 160','trajectory',flow=True)
  for x,y in [(1760,191),(1796,154),(1846,132),(1895,160)]:circle(x,y,7)
  text(1800,350,'3D position + trajectory',32);text(1800,395,'Position needs range cues',30,'blue-text')
 zone('tracking',1617,106,370,305,tracking)
 def correspondence():
  wave(46,631,133,15,16,'ink-wave');path('M191 631L248 660','blue',True,True)
  for row in range(2):
   for col in range(3):rect(46+43*col,674+37*row,37,31,'feature')
  path('M191 714L248 696','blue',True,True);rect(260,642,110,86,'module',7);text(315,693,'sim.',33)
  path('M376 686H412','blue',True,True)
  for row in range(2):
   for col in range(2):rect(427+25*col,665+25*row,22,22,'active-cell' if row==1 and col==0 else 'feature-small')
  text(249,795,'Match audio to local features',32)
  rect(41,829,413,84,'module',8);text(248,880,'Contrastive alignment',36)
  text(249,983,'Weak labels; negative pairs',31)
 zone('correspondence',26,601,459,393,correspondence)
 def synchrony():
  text(750,616,'Audio / lip activity',30);wave(553,662,361,20,15,peaks=[.29,.72])
  path('M553 732H595C625 732 635 709 654 705C673 700 685 731 712 732H734C769 732 786 710 808 705C828 702 849 729 874 731L914 732','ink-wave',flow=True)
  path('M658 635V737M813 635V737','guide')
  text(750,795,'Align sound and mouth motion',32)
  rect(543,829,413,84,'module',8);text(750,880,'Temporal AV fusion',36)
  text(750,983,'Face tracks → speaking scores',31)
 zone('synchrony',519,587,462,407,synchrony)
 def joint():
  rect(1036,632,178,109,'module',7);text(1125,678,'AV',34);text(1125,712,'fusion',34)
  for d in ['M1214 686L1255 646','M1214 686L1255 703','M1214 686L1255 762']:path(d,'blue',True,True)
  text(1315,650,'activity',30);text(1299,711,'DOA',30,'blue-text');text(1343,773,'range (opt.)',30)
  rect(1041,829,413,84,'module',8);text(1248,880,'Joint output heads',36)
  text(1249,983,'Activity over time + spatial cues',31)
 zone('joint',1025,608,455,386,joint)
 def geometry():
  text(1612,631,'array',31);text(1904,631,'camera',31)
  path('M1592 705L1775 646','bearing',flow=True);array(1572,717);camera(1907,694);path('M1775 646L1937 718','ink-dashed',flow=True);circle(1775,646,15,'source')
  text(1750,795,'Bearing + depth / triangulation',32)
  rect(1543,829,413,84,'module',8);text(1750,880,'Calibrated constraints',36)
  text(1750,983,'3D point → temporal tracking',31)
 zone('geometry',1524,601,463,393,geometry)
 add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)
if __name__=='__main__':
 (SITE/'example/figure626.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure626-1"><title>Figure 6.26 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.26 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/audio_video_spatial_localization.webp" alt="Original audio-visual spatial localization"><h2>Interactive reconstruction</h2>'''+fig626()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure626-1';mountNative();</script></html>''')
