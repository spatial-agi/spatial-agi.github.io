"""Separate Figure 6.17 scene frames; leave diagram annotations for SVG."""
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/action_detection.webp'

def main():
 src=Image.open(SOURCE).convert('RGBA')
 items=[]
 edges=[40,210,383,564,739,915,1090,1258,1424,1577]
 for i,(left,right) in enumerate(zip(edges,edges[1:]),1):
  items.append((f'overview/frame-{i:02}',(left+5,203,right-5,344)))
 items.append(('classification/tennis-serve',(112,609,409,789)))
 for panel,edges in [('localization',[541,648,756,863,966,1068,1165]),('detection',[1244,1355,1466,1576,1685,1796,1904])]:
  for i,(left,right) in enumerate(zip(edges,edges[1:]),1):
   items.append((f'{panel}/frame-{i:02}',(left+4,692,right-4,780)))
 records=[]
 for name,bounds in items:
  asset=src.crop(bounds); p=ROOT/(name+'.png'); p.parent.mkdir(parents=True,exist_ok=True); asset.save(p)
  for folder in ['source/src/img/figs/f617','assets/img/figs/f617']:
   dest=SITE/folder/(name+'.png'); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
  records.append(dict(file=name+'.png',source_box=list(bounds),size=list(asset.size),notes='RGBA scene crop, excluding film frame, timeline and annotations; original scene background retained.'))
 (ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),source_size=list(src.size),notes='22 separately saved scene frames, grouped by panel. Film sprockets, panel borders, temporal bars, guide lines, arrows, all labels and formulas will be independently drawn in the frontend. Photographic/illustrated scene backgrounds are retained to preserve the source style.',assets=records),indent=2)+'\n')
 sheet=Image.new('RGB',(1400,1130),'#eef2f6'); d=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20); title=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',25)
 d.text((22,16),'Figure 6.17 — separated scene frames',font=title,fill='#29343a')
 groups=[('overview',60,3,183),('classification',640,1,210),('localization',640,3,140),('detection',640,3,140)]
 # Overview occupies the upper three rows. The bottom panels each have one column group.
 for panel,y,cols,rowh in groups:
  xbase={'overview':20,'classification':20,'localization':480,'detection':940}[panel]
  width=440 if panel=='classification' else (440 if panel=='overview' else 440)
  d.text((xbase,y),panel,font=title,fill='#29343a')
  subset=[r for r in records if r['file'].startswith(panel+'/')]
  for i,r in enumerate(subset):
   if panel=='overview': x=20+(i%3)*460; yy=y+35+(i//3)*rowh; cw=440; ch=174
   elif panel=='classification': x=xbase; yy=y+35; cw=440; ch=278
   else: x=xbase+(i%2)*220; yy=y+35+(i//2)*140; cw=210; ch=130
   d.rounded_rectangle((x,yy,x+cw,yy+ch),8,fill='white',outline='#c6cfd8')
   im=Image.open(ROOT/r['file']); im.thumbnail((cw-24,ch-40),Image.Resampling.LANCZOS)
   sheet.paste(im,(x+(cw-im.width)//2,yy+8),im)
   d.text((x+10,yy+ch-28),Path(r['file']).stem,font=font,fill='#29343a')
 sheet.save(ROOT/'overview.png')
 sections=''
 for group in ['overview','classification','localization','detection']:
  sections+=f'<h2>{group.title()}</h2><section>'
  for r in records:
   if r['file'].startswith(group+'/'):
    sections+='<article><img src="/assets/figures/elements/figure617/'+r['file']+'"><p>'+r['file']+'</p></article>'
  sections+='</section>'
 (SITE/'example/figure617-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.17 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:14px;text-align:center}article img{height:150px;width:auto;object-fit:contain}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><main><h1>Figure 6.17 · extracted scene assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/action_detection.webp"><div id="assets">'''+sections+'''</div><p>Film borders, temporal bars, guides, arrows, text and formulas will be independently reconstructed in the frontend.</p></main></html>''')
 print(f'Saved {len(records)} assets and review page.')
if __name__=='__main__': main()
