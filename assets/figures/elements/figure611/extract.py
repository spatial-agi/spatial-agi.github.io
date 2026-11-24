"""Separate the seven photographs; all schematic marks remain frontend geometry."""
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/visual_odometry_and_camera_pose_estimation.webp'
src=Image.open(SOURCE).convert('RGBA')
items=[
 ('input/video-previous',(30,144,193,309),'Previous video frame; label excluded.'),
 ('input/video-current',(210,144,373,309),'Current video frame; label excluded.'),
 ('input/video-next',(388,144,552,309),'Next video frame; label excluded.'),
 ('input/image-set-left',(77,381,197,502),'Left unordered view; no caption.'),
 ('input/image-set-center',(212,381,333,502),'Center unordered view; no caption.'),
 ('input/image-set-right',(347,381,467,502),'Right unordered view; no caption.'),
 ('relocalization/query',(1107,200,1225,318),'Query photograph; output arrow and map excluded.'),
]
records=[]
for name,box,note in items:
 im=src.crop(box);p=ROOT/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 for folder in ['source/src/img/figs/f611','assets/img/figs/f611']:
  dest=SITE/folder/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 records.append(dict(file=name+'.png',source_box=list(box),size=list(im.size),notes=note))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),notes='Photographs are rectangular RGBA PNG assets at original resolution. Camera icons, correspondence points and lines, maps, point clouds, image-stack symbols, network boxes, timelines, dates, arrows, equations and labels will be independent frontend elements.',assets=records),indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
sheet=Image.new('RGB',(960,900),'#edf1f5');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 x=16+i%3*314;y=16+i//3*294
 d.rounded_rectangle((x,y,x+298,y+278),10,fill='white',outline='#c4ced8')
 im=Image.open(ROOT/r['file']);im=im.resize((im.width*1,im.height*1),Image.Resampling.LANCZOS)
 sheet.paste(im,(x+(298-im.width)//2,y+24+(200-im.height)//2),im)
 a,b=r['file'].split('/');d.text((x+12,y+230),a+' /',fill='#29343a',font=font);d.text((x+12,y+251),b,fill='#29343a',font=font)
sheet.save(ROOT/'overview.png')
articles=''.join('<article><img src="/assets/figures/elements/figure611/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
(SITE/'example/figure611-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.11 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#263238;margin:24px}main{max-width:1300px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:20px;text-align:center;min-height:220px;display:flex;align-items:center;justify-content:center;flex-direction:column}article img{image-rendering:auto}p{overflow-wrap:anywhere}@media(max-width:600px){section{grid-template-columns:1fr}}</style><main><h1>Figure 6.11 · extracted pictorial assets</h1><h2>Original</h2><img src="/assets/figures/figures/part3/section6/visual_odometry_and_camera_pose_estimation.webp"><h2 id="assets">Separated assets</h2><section>'''+articles+'''</section></main></html>''')
print('Saved',len(records),'Figure 6.11 assets.')
