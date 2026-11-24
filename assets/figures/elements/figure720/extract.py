"""Extract the two source vehicle pictograms; leave all diagram primitives editable."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SOURCE='assets/figures/figures/part3/section7/multi-agent_spatial_reasoning.webp'
ASSETS=[('b-motion-forecasting/vehicle-upper.png','Upper vehicle',(828,171,883,205)),('b-motion-forecasting/vehicle-lower.png','Lower vehicle',(983,258,1039,292))]
def main():
 im=Image.open(ROOT/SOURCE).convert('RGB');entries=[]
 overview=Image.new('RGB',(1000,330),'#f3f5f7');draw=ImageDraw.Draw(overview)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 for i,(file,title,box) in enumerate(ASSETS):
  crop=im.crop(box);rgba=Image.new('RGBA',crop.size)
  # Preserve the source's dark blue-gray outline and its antialiasing on transparent white.
  for y in range(crop.height):
   for x in range(crop.width):
    r,g,b=crop.getpixel((x,y));alpha=max(0,min(255,round((255-r)*255/(255-41))))
    if alpha<10:alpha=0
    rgba.putpixel((x,y),(41,53,59,alpha))
  for base in [OUT,ROOT/'source/src/img/figs/f720',ROOT/'assets/img/figs/f720']:
   dest=base/file;dest.parent.mkdir(parents=True,exist_ok=True);rgba.save(dest)
  entries.append(dict(file=file,title=title,source_box=box,size=list(rgba.size)))
  draw.text((i*500+25,20),title,fill='#29353b',font=font)
  for yy in range(65,305,16):
   for xx in range(i*500+25,i*500+475,16):
    draw.rectangle((xx,yy,xx+15,yy+15),fill='#e4e9ed' if (xx//16+yy//16)%2 else '#fff')
  enlarged=rgba.resize((rgba.width*6,rgba.height*6),Image.Resampling.LANCZOS)
  overview.paste(enlarged,(i*500+(500-enlarged.width)//2,85),enlarged)
 overview.save(OUT/'overview.png')
 frontend={
 'a':'Local-sight shading and dashed contours; three circular agents, triangular opponents and tactical arrows.',
 'b':'Road boundaries, lane divider, history lines, dashed future trajectories and labels; use the two isolated vehicles.',
 'c':'Patrol nodes and numbers, topology, failed-agent mark and reconfiguration arrows.',
 'd':'Policy boxes, action symbols, centralized critic, connecting arrows and text.',
 'e':'Individual value boxes, state-aware mixer, VDN equation and QMIX inequality.',
 'f':'Graph nodes, edges, directed messages and aggregation formula.',
 'g':'Agent/time grid, selected output cell, attention arrows and annotations.'}
 (OUT/'manifest.json').write_text(json.dumps(dict(figure='7.20',source=SOURCE,source_size=list(im.size),assets=entries,frontend=frontend),indent=2)+'\n')
 cards=''.join(f'<article><h3>{e["title"]}</h3><div class="checker"><img src="/assets/figures/elements/figure720/{e["file"]}" alt="{e["title"]}"></div><p>{e["size"][0]} × {e["size"][1]} · transparent PNG</p></article>' for e in entries)
 notes=''.join(f'<li><b>({k})</b> {v}</li>' for k,v in frontend.items())
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.20 · Asset review</title><style>body{margin:24px;background:#f3f5f7;color:#29353b;font:16px/1.6 Arial}main{max-width:1600px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{display:block;width:100%;height:auto}h1{font-size:25px}h2{font-size:20px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.checker{height:230px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e4e9ed 0 25%,white 0 50%) 0/32px 32px}.checker img{width:75%;image-rendering:auto}li{margin:12px 0}@media(max-width:600px){body{margin:12px}section{padding:12px}.grid{grid-template-columns:1fr}}</style><main><h1>Figure 7.20 · Extracted assets</h1><section><h2>Original</h2><img class="original" src="/'''+SOURCE+'''" width="2000" height="1134" alt="Original Figure 7.20"></section><section><h2>(b) Interactive motion forecasting · vehicles</h2><p>Vehicle pictograms isolated from their history lines and candidate future paths.</p><div class="grid">'''+cards+'''</div></section><section><h2>Independent frontend elements — next step</h2><ul>'''+notes+'''</ul></section></main></html>'''
 (ROOT/'example/figure720-assets.html').write_text(page)
 print('Created two transparent vehicle assets, mirrors, manifest and asset review page.')
if __name__=='__main__':main()
