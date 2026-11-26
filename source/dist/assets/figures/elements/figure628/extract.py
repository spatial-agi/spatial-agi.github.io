"""Figure 6.28 photographic/heatmap elements; diagram scaffolding stays frontend."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
SITE=Path(__file__).resolve().parents[4];ROOT=Path(__file__).resolve().parent
SOURCE='assets/figures/figures/part3/section6/visual_language_graounding_method.webp'
im=Image.open(SITE/SOURCE).convert('RGBA')
assets=[]
def save(name,frame,box,notes):
 dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);frame.save(dest)
 for mirror in ['source/src/img/figs/f628','assets/img/figs/f628']:
  p=SITE/mirror/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest,p)
 assets.append(dict(file=name,source_box=box,size=frame.size,notes=notes))
box=(46,47,145,147);crop=im.crop(box);a=np.asarray(crop).copy()
# Restore the thin internal proposal grid by interpolating neighboring pixels.
for x in [32,66]:
 for j in range(x-1,x+2):a[:,j,:3]=np.uint8(a[:,x-3,:3].astype(float)*(x+3-j)/6+a[:,x+3,:3].astype(float)*(j-x+3)/6)
for y in [32,66]:
 for j in range(y-1,y+2):a[j,:,:3]=np.uint8(a[y-3,:,:3].astype(float)*(y+3-j)/6+a[y+3,:,:3].astype(float)*(j-y+3)/6)
save('i-proposal/steak.png',Image.fromarray(a),box,'Original proposal image with thin grid lines removed; original pale appearance retained. Grid and outer frame will be drawn in the frontend.')
box=(506,52,575,159);save('ii-compositional/attention-heatmap.png',im.crop(box),box,'Attention heatmap extracted without its enclosing module border or title.')
canvas=Image.new('RGB',(840,350),'#edf1f5');d=ImageDraw.Draw(canvas)
for i,item in enumerate(assets):
 x=20+i*420;d.text((x,18),item['file'],fill='#263238');frame=Image.open(ROOT/item['file']);frame=frame.resize((frame.width*2,frame.height*2),Image.Resampling.NEAREST);canvas.paste(frame,(x,58),frame)
canvas.save(ROOT/'overview.png')
(ROOT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,source_size=im.size,assets=assets,frontend='Proposal grid, ranking bar chart, compositional tree, heatmap border/title, feature stack, cylinder database, all model boxes, connecting arrows, labels, panel borders and headings.'),indent=2)+'\n')
items=''.join(f'<article><h2>{a["file"]}</h2><div class="checker"><img src="/assets/figures/elements/figure628/{a["file"]}" alt="{a["file"]}"></div><p>{a["notes"]}</p></article>' for a in assets)
(SITE/'example/figure628-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.28 assets</title><style>body{font:16px Arial;background:#f3f5f7;margin:24px;color:#263238}main{max-width:1500px;margin:auto}h1{font-size:24px}h2{font-size:17px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}article{background:white;padding:16px;border-radius:8px}.checker{height:250px;display:grid;place-items:center;background:repeating-conic-gradient(#eee 0% 25%,white 0% 50%) 0/20px 20px}.checker img{height:214px;max-width:100%;object-fit:contain}p{line-height:1.5;font-size:14px}.original{width:100%;background:white}@media(max-width:600px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 6.28 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/visual_language_graounding_method.webp" alt="Original Figure 6.28"><h2>Assets</h2><div class="grid">'''+items+'''</div></main></html>''')
print('2 independent PNG assets and review page generated.')
