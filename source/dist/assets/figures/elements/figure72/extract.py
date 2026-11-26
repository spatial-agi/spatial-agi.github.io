"""Separate the pictorial end-effectors in Figure 7.2 from diagram annotations."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'assets/figures/figures/part3/section6/physical_reasoning.webp'
ITEMS=[('a-grasp/left-finger',(51,182,140,266),'Left grasping finger'),('a-grasp/right-finger',(470,183,559,267),'Right grasping finger'),('b-pushing/pusher',(701,148,802,247),'Planar pushing end-effector and contact point')]
im=Image.open(SOURCE).convert('RGBA')
for name,box,title in ITEMS:
 asset=im.crop(box);px=asset.load()
 for y in range(asset.height):
  for x in range(asset.width):
   r,g,b,a=px[x,y]
   # Neutral ink is retained; remove white paper and any blue force-line fringe.
   if min(r,g,b)>220 or (b-r>25 and b-g>15):px[x,y]=(r,g,b,0)
 if name.startswith('a-grasp/'):
  # Discard the contact dot where it touches the edge of each crop.
  edge = range(asset.width - 4, asset.width) if 'left' in name else range(4)
  for y in range(17, 31):
   for x in edge:
    px[x, y] = (255, 255, 255, 0)
 target=OUT/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True);asset.save(target)
 for mirror in [ROOT/'source/src/img/figs/f72',ROOT/'assets/img/figs/f72']:
  dest=mirror/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,dest)
manifest={'source':str(SOURCE.relative_to(ROOT)),'source_size':list(im.size),'assets':[{'file':n+'.png','source_box':list(b),'title':t} for n,b,t in ITEMS],'frontend':'Grasped block, contact points, friction cones, force arrows, wrench-space polygon, pushed-object outline, motion cone, limit-surface mesh and axes, stacked blocks, ground hatch, support interval, gravity, dimensions, tick/check symbols, all text and formulas, panel borders.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
overview=Image.new('RGB',(1080,300),'#f3f5f7')
for i,(name,box,title) in enumerate(ITEMS):
 card=Image.new('RGBA',(360,300),'white');asset=Image.open(OUT/(name+'.png'));asset=asset.resize((asset.width*2,asset.height*2))
 card.alpha_composite(asset,((360-asset.width)//2,62))
 ImageDraw.Draw(card).text((16,18),title,fill='#263238');overview.paste(card.convert('RGB'),(i*360,0))
overview.save(OUT/'overview.jpg',quality=94)
articles=''.join(f'<article><h2>{title}</h2><div class="checker"><img alt="{title}" src="/assets/figures/elements/figure72/{name}.png"></div><p>{name}.png</p></article>' for name,box,title in ITEMS)
(ROOT/'example/figure72-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.2 extracted assets</title><style>body{font:16px Arial;color:#27343a;background:#f3f5f7;margin:24px}main{max-width:1600px;margin:auto}h1{font-size:24px}h2{font-size:18px}.original{display:block;width:100%;background:white;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{padding:16px;background:white;border-radius:8px}.checker{height:250px;display:grid;place-items:center;background:repeating-conic-gradient(#eee 0% 25%,white 0% 50%) 0/20px 20px}.checker img{height:198px;max-width:100%;object-fit:contain}p{line-height:1.5;font-size:14px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 7.2 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" alt="Original Figure 7.2" src="/assets/figures/figures/part3/section6/physical_reasoning.webp"><div class="grid">'''+articles+'''</div><p>All geometric diagram elements, arrows, borders, text and formulas will be drawn independently in the frontend. Panel (c) consists entirely of geometric diagram elements and needs no bitmap asset.</p></main></html>''')
