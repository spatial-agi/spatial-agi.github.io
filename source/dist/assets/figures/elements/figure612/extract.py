"""Extract Figure 6.12 imagery, leaving diagram annotations for the frontend."""
import json, shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/pose_estimation.webp'
src=Image.open(SOURCE).convert('RGB')
def clean(im):
 a=np.array(im).astype(float)
 mask=binary_dilation((a.max(2)-a.min(2)>35)&(a.min(2)<210),iterations=2)
 ys,xs=np.where(mask);idx={(y,x):i for i,(y,x) in enumerate(zip(ys,xs))};m=lil_matrix((len(ys),len(ys)));b=np.zeros((len(ys),3))
 for i,(y,x) in enumerate(zip(ys,xs)):
  ns=[(yy,xx) for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<a.shape[0] and 0<=xx<a.shape[1]];m[i,i]=len(ns)
  for yy,xx in ns:
   j=idx.get((yy,xx))
   if j is None:b[i]+=a[yy,xx]
   else:m[i,j]=-1
 if len(ys):a[ys,xs]=spsolve(m.tocsr(),b)
 return Image.fromarray(np.uint8(a.clip(0,255)))
def transparent(im):
 a=np.array(im).astype(float)/255
 alpha=1-a.min(2)
 alpha[alpha<.07]=0
 rgb=np.clip(1-(1-a)/np.maximum(alpha[:,:,None],.001),0,1)
 return Image.fromarray(np.uint8(np.dstack([rgb,alpha])*255),'RGBA')
items=[
 ('input/rgb-scene',(98,43,466,258),False,True,'Blue detection box removed; scene retained.'),
 ('input/rgbd-color',(63,314,274,419),False,False,'Color component of RGB-D input.'),
 ('input/rgbd-depth',(284,314,496,419),False,False,'Depth component of RGB-D input.'),
 ('priors/cad-drill',(679,198,792,331),True,False,'CAD wireframe drill, without dashed box or label.'),
 ('priors/reference-top',(1008,224,1051,267),True,False,'First drill view, film border excluded.'),
 ('priors/reference-bottom',(1008,280,1051,324),True,False,'Second drill view, film border excluded.'),
 ('priors/reference-right',(1070,253,1114,306),True,False,'Third drill view, film border excluded.'),
 ('output/posed-scene',(1247,101,1650,411),False,False,'Scene containing blue reconstructed drill; pose equation and frame excluded.'),
 ('output/drill-without-axes',(1728,170,1861,311),True,True,'Wireframe drill; colored axes removed by local interpolation. Axes will be redrawn.'),
 ('instance/cad-drill',(237,589,313,678),True,False,'Instance-level CAD mesh; arrow excluded.'),
 ('instance/posed-drill',(367,592,446,675),True,False,'Drill with blue geometric overlay; surrounding frame excluded.'),
 ('category/cup-small',(397,725,446,776),True,False,'Small cup; dashed arrow excluded.'),
 ('category/cup-tall',(462,725,517,792),True,False,'Tall cup; dashed arrow excluded.'),
 ('category/cup-wide',(547,748,612,817),True,False,'Wide cup; dashed arrow excluded.'),
 ('foundation/drill',(249,883,287,929),True,False,'Drill reference; film border excluded.'),
 ('foundation/cup',(306,887,343,924),True,False,'Cup reference; film border excluded.'),
 ('foundation/chair',(361,880,398,930),True,False,'Chair reference; film border excluded.'),
]
records=[]
for name,box,cut,restore,note in items:
 im=src.crop(box)
 if restore:im=clean(im)
 if name=='output/drill-without-axes':
  # Bridge wireframe segments hidden by the original coordinate axes.
  hi=im.resize((im.width*4,im.height*4),Image.Resampling.BICUBIC);draw=ImageDraw.Draw(hi)
  lines=[[(72,8),(79,9),(85,10)],[(71,24),(80,25),(86,25)],[(71,34),(80,35),(86,35)],[(71,46),(80,46),(87,45)],[(72,56),(79,55),(85,53)],[(85,10),(81,21),(79,35),(80,46),(84,53)],[(76,52),(82,59),(86,68),(89,79)],[(83,60),(89,63),(94,67)],[(87,73),(91,79),(94,85)],[(77,60),(79,67),(81,74)]]
  for line in lines:draw.line([(x*4,y*4) for x,y in line],fill=(100,100,100),width=5)
  im=hi.resize(im.size,Image.Resampling.LANCZOS)
 im=transparent(im) if cut else im.convert('RGBA')
 p=ROOT/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 for folder in ['source/src/img/figs/f612','assets/img/figs/f612']:
  dest=SITE/folder/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 records.append(dict(file=name+'.png',source_box=list(box),size=list(im.size),transparent=cut,notes=note))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),notes='Seventeen original-style pictorial assets. Scene/depth images retain rectangular backgrounds; isolated line illustrations use transparent backgrounds. All text, equations, axes, arrows, dashed/card/film borders and method boxes are frontend elements.',assets=records),indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
sheet=Image.new('RGB',(1200,1800),'#e9eef3');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 x=14+i%3*396;y=14+i//3*296
 d.rounded_rectangle((x,y,x+382,y+280),10,fill='white',outline='#bac6d1')
 im=Image.open(ROOT/r['file']);im.thumbnail((358,218),Image.Resampling.LANCZOS)
 sheet.paste(im,(x+(382-im.width)//2,y+6+(218-im.height)//2),im)
 a,b=r['file'].split('/');d.text((x+12,y+233),a+' /',font=font,fill='#29343a');d.text((x+12,y+254),b,font=font,fill='#29343a')
sheet.save(ROOT/'overview.png')
articles=''.join('<article><img src="/assets/figures/elements/figure612/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
(SITE/'example/figure612-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.12 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#263238;margin:24px}main{max-width:1300px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:16px;text-align:center;min-height:240px;display:flex;align-items:center;justify-content:center;flex-direction:column}article img{max-height:220px}p{overflow-wrap:anywhere}@media(max-width:600px){section{grid-template-columns:1fr}}</style><main><h1>Figure 6.12 · extracted pictorial assets</h1><h2>Original</h2><img src="/assets/figures/figures/part3/section6/pose_estimation.webp"><h2 id="assets">Separated assets</h2><section>'''+articles+'''</section></main></html>''')
print('Saved',len(records),'Figure 6.12 assets.')
