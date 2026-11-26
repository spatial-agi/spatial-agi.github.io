"""Extract Figure 6.20 photographic elements; keep diagram geometry for SVG."""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/slam_method.webp'


def restore_markers(asset):
    """Interpolate only the narrow blue correspondence overlays from nearby pixels."""
    mask = Image.new('L', asset.size)
    for y in range(asset.height):
        for x in range(asset.width):
            r, g, b, _ = asset.getpixel((x, y))
            if b - r > 35 and b - g > 18:
                mask.putpixel((x, y), 255)
    mask = mask.filter(ImageFilter.MaxFilter(3))
    clean = asset.copy()
    for y in range(asset.height):
        for x in range(asset.width):
            if not mask.getpixel((x, y)):
                continue
            top, bottom = y - 1, y + 1
            while top >= 0 and mask.getpixel((x, top)):
                top -= 1
            while bottom < asset.height and mask.getpixel((x, bottom)):
                bottom += 1
            top, bottom = max(0, top), min(asset.height - 1, bottom)
            a, b = asset.getpixel((x, top)), asset.getpixel((x, bottom))
            t = (y - top) / max(1, bottom - top)
            clean.putpixel((x, y), tuple(round(v * (1 - t) + w * t) for v, w in zip(a, b)))
    return clean


def main():
    source = Image.open(SOURCE).convert('RGBA')
    items = [
        ('odometry/frame-01', (381, 280, 493, 391)),
        ('odometry/frame-02', (596, 280, 708, 391)),
        ('loop-closing/current', (381, 655, 468, 742)),
        ('loop-closing/history-01', (550, 670, 622, 742)),
        ('loop-closing/history-02', (638, 673, 706, 740)),
    ]
    records = []
    for name, box in items:
        asset = source.crop(box)
        if name.startswith('odometry/'):
            asset = restore_markers(asset)
        target = ROOT / (name + '.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        asset.save(target)
        for folder in ['source/src/img/figs/f620', 'assets/img/figs/f620']:
            dest = SITE / folder / (name + '.png')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
        records.append(dict(file=name + '.png', source_box=list(box), size=list(asset.size),
                            notes='RGBA scene crop. Photographic backgrounds retained; external annotations excluded.'
                            + (' Blue correspondence overlays locally restored by interpolation.' if name.startswith('odometry/') else '')))
    (ROOT / 'manifest.json').write_text(json.dumps(dict(
        source=str(SOURCE.relative_to(SITE)), source_size=list(source.size), assets=records,
        notes='Five individual photographic assets grouped by module. Sensor icons, pose-graph nodes and edges, mapping symbols, output trajectory, borders, text and arrows will be drawn independently in the frontend.'
    ), indent=2) + '\n')

    sheet = Image.new('RGB', (1200, 630), '#eef2f6')
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 25)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    draw.text((24, 18), 'Figure 6.20 - separated photographic assets', font=title, fill='#29343a')
    for group, y in [('odometry', 65), ('loop-closing', 345)]:
        draw.text((24, y), group, font=title, fill='#29343a')
        for i, r in enumerate(r for r in records if r['file'].startswith(group + '/')):
            x = 24 + i * 390
            draw.rounded_rectangle((x, y + 38, x + 370, y + 245), 8, fill='white', outline='#c6cfd8')
            im = Image.open(ROOT / r['file'])
            im = im.resize((160, 160), Image.Resampling.LANCZOS)
            sheet.paste(im, (x + 105, y + 48), im)
            draw.text((x + 14, y + 216), Path(r['file']).stem, font=font, fill='#29343a')
    sheet.save(ROOT / 'overview.png')
    sections = ''
    for group in ['odometry', 'loop-closing']:
        sections += f'<h2>{group.title()}</h2><section>'
        for r in records:
            if r['file'].startswith(group + '/'):
                sections += f'<article><img src="/assets/figures/elements/figure620/{r["file"]}"><p>{r["file"]}</p></article>'
        sections += '</section>'
    (SITE / 'example/figure620-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.20 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%;background:white}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:8px;padding:14px;text-align:center}article img{height:180px;width:auto;object-fit:contain}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{grid-template-columns:1fr}}</style><main><h1>Figure 6.20 · extracted photographic assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/slam_method.webp">''' + sections + '''<p>Five individual scene crops. Correspondence markers were removed from the odometry frames. All diagram geometry, sensor icons, text, arrows and selection borders will be reconstructed independently in the frontend.</p></main></html>''')
    print(f'Saved {len(records)} assets and review page.')


if __name__ == '__main__':
    main()
