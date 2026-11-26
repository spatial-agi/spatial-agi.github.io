"""Extract original Figure 8.22 people; all diagram geometry remains frontend-owned."""
import json
import shutil
from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = 'assets/figures/figures/part3/section8/four_motion_editing_mechanisms.webp'
ITEMS = [
    ('a-inbetween/start', (198, 108, 314, 361)),
    ('a-inbetween/end', (680, 108, 813, 361)),
    ('a-inbetween/result-01', (257, 652, 354, 862)),
    ('a-inbetween/result-02', (451, 652, 552, 862)),
    ('a-inbetween/result-03', (644, 652, 757, 862)),
    ('c-optimization/result-01', (190, 1367, 316, 1639)),
    ('c-optimization/result-02', (423, 1367, 551, 1639)),
    ('c-optimization/result-03', (659, 1367, 791, 1639)),
    ('d-instruction/source', (1213, 1198, 1312, 1406)),
    ('d-instruction/edited', (1705, 1156, 1815, 1384)),
]


def cutout(image):
    """Remove the exterior white matte, retaining interior shoe whites and soft shadows."""
    image = image.convert('RGBA')
    w, h = image.size
    pixels = image.load()
    seen = set()
    queue = deque([(x, y) for x in range(w) for y in (0, h-1)] +
                  [(x, y) for y in range(h) for x in (0, w-1)])
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or min(pixels[x, y][:3]) < 244:
            continue
        seen.add((x, y))
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                queue.append((nx, ny))
    for x, y in seen:
        pixels[x, y] = (255, 255, 255, 0)
    return image


def main():
    original = Image.open(SITE / SOURCE)
    records = []
    for name, box in ITEMS:
        asset = cutout(original.crop(box))
        dest = ROOT / (name + '.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        asset.save(dest)
        for folder in ('source/src/img/figs/f822', 'assets/img/figs/f822'):
            served = SITE / folder / (name + '.png')
            served.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, served)
        records.append(dict(file=name+'.png', source_box=box, size=asset.size,
                            notes='Original person and contact shadow; exterior white background removed. No labels, arrows or diagram borders.'))
    (ROOT/'manifest.json').write_text(json.dumps(dict(source=SOURCE, source_size=original.size, assets=records,
        frontend='Panel b skeletons and paths; all text, formulas, borders, noise tiles, arrows and connector lines.'), indent=2)+'\n')
    sheet = Image.new('RGB', (1400, 780), '#eef2f6')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    draw.text((22, 16), 'Figure 8.22 - original person cutouts (10 transparent PNG assets)', font=font, fill='#29343a')
    for i, record in enumerate(records):
        x, y = 20 + (i % 5)*276, 56 + (i//5)*360
        draw.rounded_rectangle((x,y,x+260,y+344),8,fill='white',outline='#cbd3db')
        asset=Image.open(ROOT/record['file'])
        asset.thumbnail((220,290),Image.Resampling.LANCZOS)
        sheet.paste(asset,(x+(260-asset.width)//2,y+12),asset)
        group, name=record['file'].split('/')
        draw.text((x+10,y+300),group,font=font,fill='#29343a')
        draw.text((x+10,y+323),name,font=font,fill='#29343a')
    sheet.save(ROOT/'overview.png')
    sections=''
    for group in ['a-inbetween','c-optimization','d-instruction']:
        sections+=f'<h2>{group}</h2><section>'
        for r in records:
            if r['file'].startswith(group+'/'):
                sections+=f'<article><img src="/assets/figures/elements/figure822/{r["file"]}"><p>{r["file"]}</p></article>'
        sections+='</section>'
    (SITE/'example/figure822-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 8.22 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1500px;margin:auto}h1{font-size:24px}h2{font-size:19px}.original{width:100%;height:auto;background:white}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}article{border:1px solid #ccd4dc;border-radius:8px;padding:14px;text-align:center;background:repeating-conic-gradient(#f1f1f1 0% 25%,white 0% 50%) 0 0/20px 20px}article img{height:280px;max-width:100%;object-fit:contain}p{overflow-wrap:anywhere;background:#ffffffde}@media(max-width:600px){body{margin:12px}section{grid-template-columns:1fr 1fr}article img{height:210px}}</style><main><h1>Figure 8.22 · extracted original assets</h1><h2>Original</h2><img class="original" src="/'''+SOURCE+'''">'''+sections+'''<p>Panel (b) skeletons and paths, all arrows, labels, formulas, noise tiles and borders will be drawn independently in the frontend.</p></main></html>''')
    print('Saved 10 transparent PNG assets, manifest, overview and review page.')


if __name__ == '__main__':
    main()
