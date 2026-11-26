"""Extract photographic elements; restore thin diagram overlays with harmonic fill."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
SITE=Path(__file__).resolve().parents[4]
ROOT=Path(__file__).resolve().parent
SOURCE='assets/figures/figures/part3/section6/audio_video_spatial_localization.webp'
im=Image.open(SITE/SOURCE).convert('RGB')
def restore(crop,rectangles=(),circles=(),lines=()):
 mask=Image.new('L',crop.size);d=ImageDraw.Draw(mask)
 for x0,y0,x1,y1 in rectangles:d.line([(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],fill=255,width=13)
 for box in circles:d.ellipse(box,fill=255)
 for points in lines:d.line(points,fill=255,width=6)
 m=np.array(mask)>0;a=np.array(crop,dtype=float);coords=np.argwhere(m);ids=np.full(m.shape,-1,dtype=int)
 for i,(y,x) in enumerate(coords):ids[y,x]=i
 mat=lil_matrix((len(coords),len(coords)));rhs=np.zeros((len(coords),3))
 for i,(y,x) in enumerate(coords):
  n=0
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
   yy,xx=y+dy,x+dx
   if 0<=yy<m.shape[0] and 0<=xx<m.shape[1]:
    n+=1
    if m[yy,xx]:mat[i,ids[yy,xx]]=-1
    else:rhs[i]+=a[yy,xx]
  mat[i,i]=n
 if len(coords):a[m]=spsolve(mat.tocsr(),rhs)
 return Image.fromarray(np.uint8(np.clip(a,0,255))).convert('RGBA')
specs=[
 ('i-vssl/radios.png',(39,122,362,294),dict(rectangles=[(16,51,127,140)]),'Radio scene; hard blue detection box removed. Soft acoustic activation retained as part of the source visualization.'),
 ('ii-asd/conversation.png',(438,112,762,285),dict(rectangles=[(17,11,117,134)]),'Two-person conversation; speaking-face box removed.'),
 ('iv-depth/person-room.png',(1245,119,1417,290),dict(rectangles=[(7,12,56,149)],circles=[(27,69,45,86)],lines=[[(37,78),(171,78)]]),'Person in a room; tracking box, selected point and dashed depth connector removed.'),
]
assets=[]
for name,box,opts,note in specs:
 crop=restore(im.crop(box),**opts);dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);crop.save(dest)
 for mirror in ['source/src/img/figs/f626','assets/img/figs/f626']:
  target=SITE/mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest,target)
 assets.append(dict(file=name,source_box=box,size=crop.size,notes=note))
canvas=Image.new('RGB',(1160,330),'#f0f3f6');d=ImageDraw.Draw(canvas)
for i,a in enumerate(assets):
 x=20+i*385;d.text((x,18),a['file'],fill='#263238');crop=Image.open(ROOT/a['file']);crop.thumbnail((350,240));canvas.paste(crop,(x,58),crop)
canvas.save(ROOT/'overview.png')
(ROOT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,source_size=im.size,assets=assets,frontend='All titles, labels, boxes, waveforms, charts, axes, arrows, symbols, array/camera icons, trajectories and method diagrams are independent frontend elements.'),indent=2)+'\n')
items=''.join(f'<article><h2>{a["file"]}</h2><div class="checker"><img src="/assets/figures/elements/figure626/{a["file"]}?v=2" alt="{a["file"]}"></div><p>{a["notes"]}</p></article>' for a in assets)
(SITE/'example/figure626-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.26 assets</title><style>body{font:16px Arial;background:#f3f5f7;margin:24px;color:#263238}main{max-width:1500px;margin:auto}h1{font-size:24px}h2{font-size:17px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}article{background:white;padding:16px;border-radius:8px}.checker{height:240px;display:grid;place-items:center;background:repeating-conic-gradient(#eee 0% 25%,white 0% 50%) 0/20px 20px}.checker img{max-width:100%;max-height:225px;image-rendering:auto}p{line-height:1.5;font-size:14px}.original{width:100%;background:white}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 6.26 · Extracted photographic assets</h1><div class="grid">'''+items+'''</div><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/audio_video_spatial_localization.webp" alt="Original Figure 6.26"></main></html>''')
print('3 extracted/restored PNG assets and comparison review page generated.')
