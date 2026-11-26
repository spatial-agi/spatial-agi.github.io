"""Extract Figure 6.16 photos, retaining all diagram geometry for SVG."""
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE/'assets/figures/figures/part3/section6/layout_parsing_method.webp'

def main():
    src = Image.open(SOURCE).convert('RGBA')
    items = [
        ('perspective/room', (338, 103, 471, 170)),
        ('panorama/room', (338, 299, 471, 367)),
        ('beyond-cuboid/room', (338, 496, 471, 565)),
        ('outdoor/street', (338, 878, 471, 946)),
    ]
    records = []
    for name, bounds in items:
        im = src.crop(bounds)
        p = ROOT/(name+'.png'); p.parent.mkdir(parents=True, exist_ok=True); im.save(p)
        for folder in ['source/src/img/figs/f616', 'assets/img/figs/f616']:
            dest = SITE/folder/(name+'.png'); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p,dest)
        records.append(dict(file=name+'.png',source_box=list(bounds),size=list(im.size),notes='Exact source thumbnail crop; surrounding text, arrows and geometry excluded.'))
    (ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)), source_size=list(src.size),notes='Four separately saved RGBA photographic thumbnails, grouped by lane. Photo backgrounds retained. Corner and edge maps, 3D rooms, boundary signals, footprints, plane-depth patches, bird’s-eye-view diagram, method boxes, timeline ticks, arrows and all text will be drawn independently in the frontend.',assets=records),indent=2)+'\n')
    sheet = Image.new('RGB',(1100,650),'#eef2f6'); d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
    d.text((22,18),'Figure 6.16 — separate photographic assets',font=font,fill='#29343a')
    for i,r in enumerate(records):
        x=20+(i%2)*540; y=66+(i//2)*280
        d.rounded_rectangle((x,y,x+520,y+258),10,fill='white',outline='#c6cfd8')
        im=Image.open(ROOT/r['file']); im=im.resize((399,im.height*3),Image.Resampling.NEAREST)
        sheet.paste(im,(x+60,y+12),im)
        d.text((x+16,y+225),r['file'],font=font,fill='#29343a')
    sheet.save(ROOT/'overview.png')
    cards=''.join('<article><img src="/assets/figures/elements/figure616/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
    (SITE/'example/figure616-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.16 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:14px;text-align:center}article img{width:266px;image-rendering:auto}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><main><h1>Figure 6.16 · extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/layout_parsing_method.webp"><h2 id="assets">Separated photographs</h2><section>'''+cards+'''</section><p>All geometric diagrams, signals, method boxes, timelines, arrows and text will be reconstructed as independent frontend elements.</p></main></html>''')
    print('Saved 4 Figure 6.16 assets and review page.')

if __name__=='__main__':
    main()
