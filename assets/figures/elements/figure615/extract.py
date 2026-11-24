"""Extract Figure 6.15 photographs; leave diagram geometry to the frontend."""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/layout_parsing.webp'


def main():
    src = Image.open(SOURCE).convert('RGBA')
    items = [
        ('perspective/room', (24, 82, 641, 391), 'Perspective room photograph; headings and labels excluded.'),
        ('panorama/room', (689, 82, 1305, 391), 'Panoramic room photograph, preserving the original projection; headings and labels excluded.'),
        ('urban/street', (1353, 82, 1970, 391), 'Urban street photograph; headings and labels excluded.'),
    ]
    records = []
    for name, box, note in items:
        im = src.crop(box)
        target = ROOT / (name + '.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        im.save(target)
        for folder in ['source/src/img/figs/f615', 'assets/img/figs/f615']:
            dest = SITE / folder / (name + '.png')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
        records.append(dict(file=name+'.png', source_box=list(box), size=list(im.size), notes=note))
    (ROOT/'manifest.json').write_text(json.dumps(dict(
        source=str(SOURCE.relative_to(SITE)), source_size=list(src.size),
        notes='Three separate RGBA PNG photographs. Their original rectangular photo backgrounds are retained. Polygonal room layouts, dashed occluded edges, vertices, surface maps, hatch patterns, legends, arrows, separators and all text will be drawn independently in the frontend.',
        assets=records), indent=2)+'\n')
    sheet = Image.new('RGB', (1200, 800), '#eef2f6')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 23)
    small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 19)
    draw.text((24, 20), 'Figure 6.15 — separate photographic assets', font=font, fill='#29343a')
    for i, record in enumerate(records):
        y = 66+i*240
        draw.rounded_rectangle((20, y, 1180, y+224), 10, fill='white', outline='#c6cfd8')
        im = Image.open(ROOT/record['file'])
        im.thumbnail((440, 204), Image.Resampling.LANCZOS)
        sheet.paste(im, (32, y+10), im)
        draw.text((500, y+70), record['file'], font=font, fill='#29343a')
        draw.text((500, y+113), f"Native: {record['size'][0]} × {record['size'][1]}", font=small, fill='#63717c')
    sheet.save(ROOT/'overview.png')
    cards = ''.join('<article><img src="/assets/figures/elements/figure615/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
    (SITE/'example/figure615-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.15 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:14px;text-align:center}p{overflow-wrap:anywhere}@media(max-width:600px){body{margin:12px}section{grid-template-columns:1fr}}</style><main><h1>Figure 6.15 · extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/layout_parsing.webp"><h2 id="assets">Separated photographs</h2><section>'''+cards+'''</section><p>Room polygons, surface-label maps, hatch patterns, legends, text and arrows will be reconstructed as independent frontend elements.</p></main></html>''')
    print('Saved 3 Figure 6.15 photo assets and review page.')


if __name__ == '__main__':
    main()
