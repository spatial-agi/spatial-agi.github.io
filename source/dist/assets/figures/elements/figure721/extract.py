"""Separate the scene pictograms from Figure 7.21 for source-faithful reconstruction."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SOURCE='assets/figures/figures/part3/section7/LLM_VLM-centric_spatial_reasoning.webp'
ASSETS=[('scene/book.png','Book',(72,563,240,647)),('scene/lamp.png','Lamp',(271,471,364,639)),('scene/cup.png','Cup',(414,551,503,634))]
def main():
 original=Image.open(ROOT/SOURCE).convert('RGB');entries=[]
 overview=Image.new('RGB',(1200,380),'#f3f5f7');d=ImageDraw.Draw(overview);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 for i,(file,title,box) in enumerate(ASSETS):
  crop=original.crop(box);rgba=Image.new('RGBA',crop.size)
  for y in range(crop.height):
   for x in range(crop.width):
    r,g,b=crop.getpixel((x,y))
    if title=='Book':
     alpha=round(min(255,max(0,(b-r)*255/(233-65)))) if b-r>32 else 0
     rgba.putpixel((x,y),(65,69,233,alpha))
    else:
     alpha=max(0,min(255,round((255-r)*255/214)))
     if alpha<8:alpha=0
     rgba.putpixel((x,y),(41,53,59,alpha))
  # The book's lower edge touches the table. Keep only the blue source outline.
  for base in [OUT,ROOT/'source/src/img/figs/f721',ROOT/'assets/img/figs/f721']:
   dest=base/file;dest.parent.mkdir(parents=True,exist_ok=True);rgba.save(dest)
  entries.append(dict(file=file,title=title,source_box=box,size=list(rgba.size)))
  d.text((i*400+20,18),title,fill='#29353b',font=font)
  for yy in range(65,360,16):
   for xx in range(i*400+20,i*400+380,16):d.rectangle((xx,yy,xx+15,yy+15),fill='#e4e9ed' if (xx//16+yy//16)%2 else 'white')
  scale=min(330/rgba.width,260/rgba.height);large=rgba.resize((round(rgba.width*scale),round(rgba.height*scale)),Image.Resampling.LANCZOS)
  overview.paste(large,(i*400+(400-large.width)//2,75+(270-large.height)//2),large)
 overview.save(OUT/'overview.png')
 notes=['Inputs: independently draw text-description box, scene highlight, table, query, and optional evidence boxes.','Reasoning core: draw pretrained model box, four complementary strategy groups, all labels and arrows.','Outputs: draw answer and relation formula, task outputs, evaluation category boxes and separators.']
 (OUT/'manifest.json').write_text(json.dumps(dict(figure='7.21',source=SOURCE,source_size=list(original.size),assets=entries,frontend=notes),indent=2)+'\n')
 cards=''.join(f'<article><h3>{e["title"]}</h3><div class="checker"><img src="/assets/figures/elements/figure721/{e["file"]}" alt="{e["title"]}"></div><p>{e["size"][0]} × {e["size"][1]} · transparent PNG</p></article>' for e in entries)
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.21 · Asset review</title><style>body{margin:24px;background:#f3f5f7;color:#29353b;font:16px/1.6 Arial}main{max-width:1600px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{display:block;width:100%;height:auto}h1{font-size:25px}h2{font-size:20px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.checker{height:280px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e4e9ed 0 25%,white 0 50%) 0/32px 32px}.checker img{max-width:90%;max-height:250px;width:auto;height:auto}li{margin:12px 0}@media(max-width:600px){body{margin:12px}section{padding:12px}.grid{grid-template-columns:1fr}}</style><main><h1>Figure 7.21 · Extracted assets</h1><section><h2>Original</h2><img class="original" src="/'''+SOURCE+'''" width="2000" height="1000" alt="Original Figure 7.21"></section><section><h2>Visual scene · isolated pictograms</h2><p>Book, lamp and cup separated from the query highlight, table and annotations.</p><div class="grid">'''+cards+'''</div></section><section><h2>Independent frontend elements — next step</h2><ul>'''+''.join('<li>'+v+'</li>' for v in notes)+'''</ul></section></main></html>'''
 (ROOT/'example/figure721-assets.html').write_text(page)
 print('Created three isolated PNGs, source/served mirrors and asset review.')
if __name__=='__main__':main()
