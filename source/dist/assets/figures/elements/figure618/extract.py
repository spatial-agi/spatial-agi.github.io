"""Extract Figure 6.18 photographic frames, retaining diagrams for frontend SVG."""
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/action_detection_method_1.webp'

def main():
 src=Image.open(SOURCE).convert('RGBA')
 items=[('classification/serve-01',(30,244,143,336)),('classification/serve-02',(146,244,259,336)),('classification/serve-03',(262,244,375,336)),('two-stream/rgb',(446,261,508,311))]
 for panel,y1,y2 in [('localization',710,755),('detection',1128,1174)]:
  for i,(left,right) in enumerate([(30,85),(88,143),(146,201),(204,259),(262,317),(320,375)],1):
   items.append((f'{panel}/frame-{i:02}',(left,y1,right,y2)))
 records=[]
 for name,bounds in items:
  asset=src.crop(bounds)
  if name.startswith('detection/'):
   # Restore blue temporal guides from the clean corresponding frame above.
   clean=src.crop((bounds[0],710,bounds[2],755)).resize(asset.size,Image.Resampling.LANCZOS)
   pixels=asset.load()
   for yy in range(asset.height):
    for xx in range(asset.width):
     red,green,blue,alpha=pixels[xx,yy]
     if blue-red>35 and blue-green>15:
      for dy in [-1,0,1]:
       for dx in [-1,0,1]:
        px,py=xx+dx,yy+dy
        if 0<=px<asset.width and 0<=py<asset.height:pixels[px,py]=clean.getpixel((px,py))
  p=ROOT/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);asset.save(p)
  for folder in ['source/src/img/figs/f618','assets/img/figs/f618']:
   dest=SITE/folder/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  records.append(dict(file=name+'.png',source_box=list(bounds),size=list(asset.size),notes='RGBA photographic crop; source scene background retained. All external annotations excluded.'))
 (ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),source_size=list(src.size),notes='16 photographic elements grouped by panel. Text, method boxes, timelines, flow vectors, feature blocks, arrows, interval bars, curves, histograms, anchors and decoder geometry will be independently reconstructed in the frontend.',assets=records),indent=2)+'\n')
 sheet=Image.new('RGB',(1200,830),'#eef2f6');d=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18);title=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',24)
 d.text((20,15),'Figure 6.18 — separated photographic assets',font=title,fill='#29343a')
 for group,y in [('classification',60),('two-stream',280),('localization',470),('detection',650)]:
  d.text((20,y),group,font=title,fill='#29343a')
  rows=[r for r in records if r['file'].startswith(group+'/')];cw=380 if len(rows)<4 else 185
  for i,r in enumerate(rows):
   x=20+i*(cw+10);yy=y+34;ch=170 if group=='classification' else 130
   d.rounded_rectangle((x,yy,x+cw,yy+ch),8,fill='white',outline='#c6cfd8')
   im=Image.open(ROOT/r['file']);im=im.resize((im.width*2,im.height*2),Image.Resampling.LANCZOS);im.thumbnail((cw-20,ch-38))
   sheet.paste(im,(x+(cw-im.width)//2,yy+6),im);d.text((x+10,yy+ch-27),Path(r['file']).stem,font=font,fill='#29343a')
 sheet.save(ROOT/'overview.png')
 sections=''
 for group in ['classification','two-stream','localization','detection']:
  sections+=f'<h2>{group.title()}</h2><section>'
  for r in records:
   if r['file'].startswith(group+'/'):
    sections+='<article><img src="/assets/figures/elements/figure618/'+r['file']+'"><p>'+r['file']+'</p></article>'
  sections+='</section>'
 (SITE/'example/figure618-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.18 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:14px;text-align:center}article img{height:140px;width:auto;object-fit:contain}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><main><h1>Figure 6.18 · extracted photographic assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/action_detection_method_1.webp"><div id="assets">'''+sections+'''</div><p>All arrows, flow vectors, feature blocks, temporal intervals, plots, timelines, method boxes and text will be independently reconstructed in the frontend.</p></main></html>''')
 print(f'Saved {len(records)} assets and review page.')
if __name__=='__main__':main()
