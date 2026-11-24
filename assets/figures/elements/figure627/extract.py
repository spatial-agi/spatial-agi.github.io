"""Figure 6.27 imagery extraction; all diagram annotations stay independent."""
from pathlib import Path
import json,shutil,runpy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,label
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
SITE=Path(__file__).resolve().parents[4];ROOT=Path(__file__).resolve().parent
SOURCE='assets/figures/figures/part3/section6/visual_language_graounding_task.webp'
im=Image.open(SITE/SOURCE).convert('RGB')
def fill(a,m):
 coords=np.argwhere(m);ids=np.full(m.shape,-1,dtype=int)
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
 return a

def video(box,index):
 crop=im.crop(box);a=np.asarray(crop,dtype=float).copy();r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 mag=(r>g*1.55)&(b>g*1.4)&(r>85)
 cyan=(g>r*1.45)&(b>r*1.5)&(b>110)
 for mask,col,alpha in [(mag,[255,0,170],.34),(cyan,[0,200,255],.30)]:
  a[mask]=(a[mask]-np.array(col)*alpha)/(1-alpha)
 a=np.clip(a,0,255)
 mask=Image.new('L',crop.size);d=ImageDraw.Draw(mask)
 boxes=[[(75,24,135,121),(28,51,73,89)],[(69,-1,129,121),(38,74,83,109)],[(127,-1,173,121),(28,64,70,97)]][index-1]
 for x0,y0,x1,y1 in boxes:d.line([(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],fill=255,width=7)
 d.rectangle([(67,71,82,83),(77,87,94,99),(64,73,82,87)][index-1],fill=255)
 a=fill(a,np.array(mask)>0)
 return Image.fromarray(np.uint8(np.clip(a,0,255))).convert('RGBA')

def transparent(crop):
 a=np.array(crop.convert('RGBA'));white=np.all(a[:,:,:3]>228,axis=2)
 labels,n=label(white);border=np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]])
 a[np.isin(labels,border[border>0]),3]=0
 return Image.fromarray(a)
assets=[]
def save(name,frame,box,note):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);frame.save(p)
 for mirror in ['source/src/img/figs/f627','assets/img/figs/f627']:
  dest=SITE/mirror/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 assets.append(dict(file=name,source_box=box,size=frame.size,notes=note))
for name,box in [('i-rec-res/steak.png',(32,136,240,275)),('ii-grec-gres/vegetables.png',(308,136,514,275)),('iii-reasoning/wrestling.png',(583,138,793,275)),('iv-video/input.png',(993,140,1187,274))]:
 save(name,im.crop(box).convert('RGBA'),box,'Unannotated source photograph. Output boxes and masks will be drawn separately in the frontend.')
for i,box in enumerate([(847,311,1020,431),(1021,311,1194,431),(1195,311,1366,431)],1):
 save(f'iv-video/frame-{i:02}.png',video(box,i),box,'Video frame restored by reducing translucent annotation tint and filling thin colored outlines; obscured pixels are approximate. Segmentation and tracking overlays will be independent frontend elements.')
box=(1396,64,1532,258);scene=transparent(im.crop(box));save('v-3d/scene.png',scene,box,'Shared clean 3D room reconstruction; exterior white background made transparent. The same scene supports the four annotated outputs.')
# Keep the annotated projections as separately extracted, transparent references.
# They are review references; the reconstruction uses scene.png beneath frontend overlays.
for name,box in [('rec',(1572,99,1672,245)),('res',(1704,100,1804,245)),('gres',(1393,281,1492,427)),('dres',(1684,281,1788,427))]:
 crop=transparent(im.crop(box))
 a=np.array(crop);r,g,b=a[:,:,0].astype(float),a[:,:,1].astype(float),a[:,:,2].astype(float)
 colored=((g>r*1.4)&(g>b*1.3)&(g>130))|((r>g*1.8)&(r>b*1.4)&(r>150))|((b>r*1.5)&(b>g*1.4)&(b>130))
 clean=scene.resize(crop.size,Image.Resampling.LANCZOS);base=np.array(clean)
 replace=binary_dilation(colored,iterations=1)&(a[:,:,3]>0)
 a[replace]=base[replace]
 save(f'v-3d/{name}-scene.png',Image.fromarray(a),box,'3D output projection with colored target annotations restored from the clean shared room. Frontend boxes and masks remain independent.')
 save(f'v-3d/reference-{name}.png',crop,box,'Annotated source projection retained as a reference for frontend overlay geometry and color; not a flattened frontend diagram.')
canvas=Image.new('RGB',(1360,1185),'#edf1f5');d=ImageDraw.Draw(canvas)
for i,a in enumerate(assets):
 x=15+(i%4)*340;y=10+(i//4)*295
 d.text((x,y+5),a['file'],fill='#263238');frame=Image.open(ROOT/a['file']);frame.thumbnail((310,240))
 if frame.width<150:frame=frame.resize((int(frame.width*1.15),int(frame.height*1.15)),Image.Resampling.LANCZOS)
 canvas.paste(frame,(x,y+35),frame)
canvas.save(ROOT/'overview.png')
(ROOT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,source_size=im.size,assets=assets,frontend='Panel frames and titles; referring phrases; arrows; red bounding boxes and segmentation polygons; video tracking boxes, labels and segmentation overlays; 3D target boxes/masks and colored referring-expression text.'),indent=2)+'\n')
items=''.join(f'<article><h2>{a["file"]}</h2><div class="checker"><img src="/assets/figures/elements/figure627/{a["file"]}?v=2" alt="{a["file"]}"></div><p>{a["notes"]}</p></article>' for a in assets)
(SITE/'example/figure627-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.27 assets</title><style>body{font:16px Arial;background:#f3f5f7;margin:24px;color:#263238}main{max-width:1550px;margin:auto}h1{font-size:24px}h2{font-size:16px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}article{background:white;padding:14px;border-radius:8px}.checker{height:220px;display:grid;place-items:center;background:repeating-conic-gradient(#eee 0% 25%,white 0% 50%) 0/20px 20px}.checker img{max-width:100%;max-height:210px}p{line-height:1.45;font-size:13px}.original{width:100%;background:white}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:450px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 6.27 · Extracted assets and 3D overlay references</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/visual_language_graounding_task.webp" alt="Original Figure 6.27"><h2>Assets by panel</h2><div class="grid">'''+items+'''</div></main></html>''')
print(f'{len(assets)} scene/frame assets and annotated 3D references generated.')
