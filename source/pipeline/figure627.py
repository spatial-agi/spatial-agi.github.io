"""Faithful, independently annotated Figure 6.27 reconstruction."""
import json
from html import escape
from pathlib import Path
SITE=Path(__file__).resolve().parents[2]
INFO={
'rec':{'t':'Referring expression comprehension and segmentation','b':'A single image and referring expression identify one target. REC returns its bounding box; RES returns its pixel mask. Here both outputs identify the steak.'},
'generalized':{'t':'Generalized referring expression grounding','b':'The expression can refer to zero, one or several targets. The example returns multiple red vegetables, each with its own box and mask.'},
'reasoning':{'t':'Reasoning grounding','b':'The phrase “the loser” requires interpreting the situation before localizing the referred person. The output is a region or segmentation mask.'},
'video':{'t':'Video referring and reasoning grounding','b':'Ground the named entities across successive frames while maintaining their identities. Separate overlays identify the man, laptop and mouse as appearance and pose change.'},
'3d-rec':{'t':'3D referring expression comprehension','b':'Use the language description to select the television in the 3D scene. The green outline denotes the localized object.'},
'3d-res':{'t':'3D referring expression segmentation','b':'The same television description is grounded as a set of 3D points or a surface mask rather than a bounding box.'},
'3d-gres':{'t':'Generalized 3D referring segmentation','b':'Resolve the chair using its relationship to the table. The green regions mark the referred object within the reconstructed room.'},
'3d-dres':{'t':'Description-driven 3D grounding','b':'Combine object attributes and spatial relations: the gray trash can is next to the thin table under the television. Colored words correspond to the illustrated scene regions.'},
}
def fig627():
 out=[];add=out.append
 def text(x,y,t,size=28,cls='text',raw=False):add(f'<text class="f627-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{t if raw else escape(t)}</text>')
 def rect(x,y,w,h,cls='panel',rx=0):add(f'<rect class="f627-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
 def image(name,x,y,w,h):add(f'<image href="/assets/img/figs/f627/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
 def path(d,cls='mask-red'):add(f'<path class="f627-{cls}" d="{d}"/>')
 def arrow(x,y,end):add(f'<path class="f627-route" d="M{x} {y}V{end}" marker-end="url(#f627-arrow)"/>')
 def zone(k,x,y,w,h,draw):
  add(f'<g class="f627-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">');draw();rect(x,y,w,h,'hit',5);add('</g>')
 add('<div class="nf nf-627" data-nf="627" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 475" role="group" aria-label="Figure 6.27: vision-language grounding task variants"><defs><marker id="f627-arrow" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 1L6 4L0 7Z" fill="#0053da"/></marker></defs><rect width="2000" height="475" fill="white"/><g class="f627-scaffold">')
 for x,y,w,h in [(1,1,255,457),(281,3,255,457),(560,3,255,457),(833,3,546,457),(1391,3,591,457)]:rect(x,y,w,h,'panel',16)
 for x,t in [(124,'(i) REC / RES'),(408,'(ii) GREC / GRES'),(687,'(iii) Reasoning'),(1090,'(iv) Video'),(1711,'(v) 3D')]:text(x,47,t,32,'title')
 image('v-3d/scene',1396,64,136,194)
 add('</g>')
 def rec():
  text(130,123,'steak');image('i-rec-res/steak',32,136,208,139);arrow(136,276,302)
  image('i-rec-res/steak',31,304,209,139)
  path('M51 356L60 348L73 355L86 352L101 357L113 351L126 354L140 348L155 351L169 347L180 354L186 370L197 382L210 391L222 405L222 423L211 436L192 442L174 440L154 433L131 429L109 419L91 412L71 395L56 382L49 371Z')
  rect(48,343,179,102,'box-red')
 zone('rec',23,91,224,358,rec)
 def generalized():
  text(406,123,'red carrot');image('ii-grec-gres/vegetables',308,136,206,139);arrow(417,277,304)
  image('ii-grec-gres/vegetables',308,309,209,139)
  for d in ['M416 331Q430 324 443 337Q455 351 441 363Q426 370 415 357Z','M394 339Q409 332 420 347Q433 365 414 371Q398 374 391 362Z','M392 383Q404 369 418 382Q430 398 413 409Q395 415 389 399Z','M368 398Q380 386 391 400Q401 416 384 427Q369 429 364 414Z']:path(d)
  for x,y,w,h in [(412,325,39,42),(389,335,43,38),(390,374,33,34),(362,392,33,36)]:rect(x,y,w,h,'box-red')
 zone('generalized',300,91,222,359,generalized)
 def reasoning():
  text(687,123,'the loser');image('iii-reasoning/wrestling',583,137,210,138);arrow(694,277,304)
  image('iii-reasoning/wrestling',583,309,210,139)
  path('M607 425L617 415L620 402L629 393L639 383L650 379L665 385L676 394L684 402L696 407L709 419L724 421L731 433L719 438L701 437L683 432L673 438L653 434L641 438L623 433L605 437Z')
  rect(603,372,134,67,'box-red')
 zone('reasoning',576,91,224,359,reasoning)
 def video():
  text(1086,123,'man, laptop, mouse');image('iv-video/input',993,140,194,134);arrow(1091,278,305)
  for i,(x,w) in enumerate([(847,173),(1021,173),(1195,171)],1):image(f'iv-video/frame-{i:02}',x,311,w,120)
  for d in ['M942 339L952 339L959 346L961 360L973 367L978 391L973 409L979 431H923L923 413L931 398L929 386L919 382L921 374L938 380L944 372L940 359L937 348Z','M1108 313L1120 315L1126 325L1132 335L1141 344L1145 365L1138 386L1142 409L1134 431H1096L1099 408L1095 389L1098 366L1090 353L1091 334L1098 331Z','M1337 311H1366V431H1328L1326 408L1330 385L1322 370L1324 354L1313 344L1318 337L1334 348L1340 342L1331 332Z']:path(d,'mask-person')
  for d in ['M875 364L894 365L916 397H882Z','M1062 385L1076 388L1098 416H1063Z','M1225 375L1244 378L1263 404H1225Z']:path(d,'mask-laptop')
  for x,y,w,h in [(922,336,61,95),(1091,312,59,119),(1322,312,44,119)]:rect(x,y,w,h,'box-person')
  for x,y,w,h in [(875,363,44,37),(1060,385,43,35),(1223,375,42,33)]:rect(x,y,w,h,'box-laptop')
  for x,y in [(914,382),(1099,400),(1263,387)]:rect(x,y,10,6,'box-mouse',1)
 zone('video',843,91,525,350,video)
 def rec3d():
  image('v-3d/rec-scene',1572,99,100,146);path('M1620 108L1647 109L1647 124L1620 123Z','box-green')
  path('M1658 104L1664 100M1658 104L1662 104M1658 104V100','green-arrow');text(1628,271,'3D-REC',24)
 zone('3d-rec',1569,91,105,184,rec3d)
 def res3d():
  image('v-3d/res-scene',1704,100,100,145);path('M1753 109L1779 109L1778 123L1752 123Z','mask-green');path('M1725 104L1720 100M1725 104L1721 104M1725 104V100','green-arrow');text(1768,271,'3D-RES',24)
  for i,t in enumerate(['a black TV,','placed on the','wall of the','kitchen.']):text(1898,133+i*31,t,24)
 zone('3d-res',1699,91,273,184,res3d)
 def gres3d():
  image('v-3d/gres-scene',1393,281,99,146)
  path('M1444 310L1451 314L1455 321L1442 323Z M1446 386L1455 385L1454 392L1446 393Z','mask-green');text(1454,452,'3D-GRES',24)
  for i,t in enumerate(['The brown chair','is located at the','end of the table.']):text(1582,332+i*31,t,24)
 zone('3d-gres',1393,278,285,181,gres3d)
 def dres3d():
  image('v-3d/dres-scene',1684,281,104,146)
  path('M1731 288L1758 289L1757 302L1731 301Z','mask-red3d');path('M1731 305L1757 305L1754 314L1730 314Z','mask-green');path('M1758 302L1764 302L1764 319L1758 317Z','mask-blue')
  text(1740,452,'3D-DRES',24)
  lines=['There is a tall','gray <tspan fill="#245ed0">trash can</tspan>. It','sits next to the','thin <tspan fill="#00ae50">table</tspan> that is','under the <tspan fill="red">TV</tspan>.']
  for i,t in enumerate(lines):text(1888,301+i*30.5,t,24,raw=True)
 zone('3d-dres',1683,278,293,181,dres3d)
 add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)
if __name__=='__main__':
 (SITE/'example/figure627.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure627-1"><title>Figure 6.27 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1800px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.27 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/visual_language_graounding_task.webp" alt="Original vision-language grounding task variants"><h2>Interactive reconstruction</h2>'''+fig627()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure627-1';mountNative();</script></html>''')
