"""Extract the eleven road frames of Figure 6.21, grouped by observation setting."""
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/scene_flow_estimation.webp'
ITEMS = [
    ('single-image/frame', (32, 100, 230, 205), False),
    ('stereo/left', (427, 110, 581, 198), True),
    ('stereo/right', (617, 110, 771, 198), True),
    ('monocular-video/t0', (848, 110, 974, 198), True),
    ('monocular-video/t1', (1042, 110, 1167, 198), True),
    ('multi-view/view-01', (1242, 91, 1373, 146), False),
    ('multi-view/view-02', (1417, 91, 1549, 146), False),
    ('multi-view/view-03', (1242, 165, 1373, 219), False),
    ('multi-view/view-04', (1417, 165, 1549, 219), False),
    ('self-supervised/next-frame', (1251, 510, 1349, 598), True),
    ('self-supervised/current-frame', (1460, 510, 1558, 598), True),
]


def main():
    source = Image.open(SOURCE).convert('RGBA')
    # Every annotated inset uses the same road photograph. Restore annotation-covered
    # pixels from the clean, larger single-image inset at corresponding scene coordinates.
    clean = source.crop((32, 100, 230, 205))
    records = []
    for name, box, restore in ITEMS:
        asset = source.crop(box)
        if restore:
            reference = clean.resize(asset.size, Image.Resampling.LANCZOS)
            mask = Image.new('L', asset.size)
            for y in range(asset.height):
                for x in range(asset.width):
                    r, g, b, _ = asset.getpixel((x, y))
                    if b - r > 25 and b - g > 13:
                        mask.putpixel((x, y), 255)
            bounds = mask.getbbox()
            if bounds:
                # Include the translucent interior, not just the blue box outline.
                left, top, right, bottom = bounds
                ImageDraw.Draw(mask).rectangle((max(0,left-1), max(0,top-1), min(asset.width-1,right), min(asset.height-1,bottom)), fill=255)
                mask = mask.filter(ImageFilter.GaussianBlur(.6))
                asset = Image.composite(reference, asset, mask)
        p = ROOT / (name + '.png'); p.parent.mkdir(parents=True, exist_ok=True); asset.save(p)
        for mirror in ['source/src/img/figs/f621', 'assets/img/figs/f621']:
            target = SITE / mirror / (name + '.png'); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
        records.append(dict(file=name+'.png', source_box=list(box), size=list(asset.size),
                            notes='RGBA road photograph; external border excluded.' + (' Blue annotation and translucent interior restored from the clean single-image view.' if restore else '')))
    (ROOT / 'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),source_size=list(source.size), assets=records,
        notes='Eleven individual scene images grouped by panel. All blue tracking boxes, labels, formulas, arrows, energy curves, CNN/GRU modules, motion-field nodes, method boxes and separators will be reconstructed as frontend geometry.'), indent=2)+'\n')
    groups = ['single-image', 'stereo', 'monocular-video', 'multi-view', 'self-supervised']
    sheet = Image.new('RGB', (1220, 1190), '#eef2f6'); d = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 25)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    d.text((20, 14), 'Figure 6.21 - extracted road-scene assets', font=title, fill='#29343a')
    sections = ''
    for row, group in enumerate(groups):
        y=62+row*222; d.text((20,y),group,font=title,fill='#29343a')
        sections += f'<h2>{group}</h2><section>'
        for col,r in enumerate(r for r in records if r['file'].startswith(group+'/')):
            x=20+col*300
            d.rounded_rectangle((x,y+36,x+284,y+204),8,fill='white',outline='#ccd4dc')
            im=Image.open(ROOT/r['file']); im.thumbnail((260,118)); im=im.resize((round(im.width*min(260/im.width,118/im.height)),round(im.height*min(260/im.width,118/im.height))),Image.Resampling.LANCZOS)
            sheet.paste(im,(x+(284-im.width)//2,y+44),im)
            d.text((x+12,y+175),Path(r['file']).stem,font=font,fill='#29343a')
            sections += f'<article><img src="/assets/figures/elements/figure621/{r["file"]}"><p>{r["file"]}</p></article>'
        sections += '</section>'
    sheet.save(ROOT/'overview.png')
    (SITE/'example/figure621-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.21 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1500px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%;background:white}section{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}article{background:white;border:1px solid #ccd4dc;border-radius:8px;padding:14px;text-align:center}article img{height:150px;width:100%;object-fit:contain}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{grid-template-columns:repeat(2,minmax(0,1fr))}article img{height:100px}}</style><main><h1>Figure 6.21 · extracted road-scene assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/scene_flow_estimation.webp">'''+sections+'''<p>Tracking annotations have been removed using the clean source road view. Text, formulas, borders, arrows and all schematic geometry will be drawn independently in the frontend.</p></main></html>''')
    print(f'Saved {len(records)} assets, manifest, contact sheet and review page.')


if __name__ == '__main__':
    main()
