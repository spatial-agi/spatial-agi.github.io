"""Extract and restore pictorial cutouts for Figure 7.6 from the source image."""

from html import escape
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
SITE = OUT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section7/716_causal.webp'
ORIGINAL = Image.open(SOURCE).convert('RGB')
ASSETS = [
    ('i-inputs/event-blue-agent', (131, 115, 159, 168), 'Event stream · blue agent'),
    ('i-inputs/event-red-agent', (340, 115, 369, 168), 'Event stream · red agent'),
    ('i-inputs/intervention-arm', (30, 769, 105, 850), 'Interventional data · robot arm'),
    ('i-inputs/intervention-blue-agent', (305, 777, 335, 832), 'Interventional data · blue agent'),
    ('i-inputs/intervention-red-agent', (345, 777, 377, 832), 'Interventional data · red agent'),
    ('i-inputs/intervention-blue-car', (402, 791, 452, 822), 'Interventional data · blue vehicle'),
    ('ii-core/safety-shield', (1047, 770, 1082, 820), 'Verification · safety shield'),
    ('ii-core/multi-agent-left', (1189, 771, 1217, 825), 'Verification · left agent'),
    ('ii-core/multi-agent-right', (1219, 771, 1249, 825), 'Verification · right agent'),
    ('ii-core/diagnosis-lens', (1348, 778, 1384, 833), 'Verification · diagnosis lens'),
    ('iii-outputs/explanation-blue-car', (1551, 389, 1602, 421), 'Explanation · blue vehicle'),
    ('iii-outputs/explanation-red-car', (1633, 389, 1684, 421), 'Explanation · red vehicle'),
    ('iii-outputs/strategy-shield', (1547, 766, 1581, 815), 'Intervention strategy · safety shield'),
    ('iii-outputs/strategy-arm', (1585, 777, 1659, 861), 'Intervention strategy · robot arm'),
]

REUSE = {
    'i-inputs/event-blue-agent.png': [
        (131, 115, 159, 168), (238, 115, 266, 168), (131, 206, 159, 259)
    ],
    'i-inputs/event-red-agent.png': [
        (340, 115, 369, 168), (237, 206, 266, 259), (340, 206, 369, 259)
    ],
    'iii-outputs/explanation-blue-car.png': [
        (1551, 389, 1602, 421), (1541, 595, 1593, 627),
        (1783, 595, 1835, 627), (1767, 784, 1819, 816)
    ],
    'iii-outputs/explanation-red-car.png': [
        (1633, 389, 1684, 421), (1669, 595, 1721, 627),
        (1911, 595, 1963, 627), (1911, 784, 1963, 816)
    ],
}

NATIVE = {
    'Inputs': 'Section frames, timeline, labels, state cubes, grid, measurement boxes and prior-knowledge diagrams.',
    'Reasoning core': 'Causal graphs, formulas, model-score gauge, rule and solver panels, connectors and status labels.',
    'Outputs': 'Causal model, trajectories, dashed arrows, obstacle cubes and success/failure marks.',
}


def cutout(box):
    """Remove the white paper, retaining the soft contours of the pictograms."""
    source = ORIGINAL.crop(box)
    cleaned = []
    for red, green, blue in source.getdata():
        darkest = min(red, green, blue)
        if darkest >= 246:
            cleaned.append((255, 255, 255, 0))
        elif darkest <= 218:
            cleaned.append((red, green, blue, 255))
        else:
            alpha = round((246 - darkest) * 255 / 28)
            rgb = tuple(max(0, min(255, round(255 - (255 - channel) * 255 / alpha)))
                        for channel in (red, green, blue))
            cleaned.append((*rgb, alpha))
    image = Image.new('RGBA', source.size)
    image.putdata(cleaned)
    return image


def make_overview(assets):
    columns = 4
    width, height = 260, 181
    rows = (len(assets) + columns - 1) // columns
    overview = Image.new('RGBA', (width * columns, height * rows), '#f3f5f7')
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15) if Path('/System/Library/Fonts/Supplemental/Arial.ttf').exists() else ImageFont.load_default()
    for index, (asset, entry) in enumerate(assets):
        card = Image.new('RGBA', (width - 12, height - 12), 'white')
        draw = ImageDraw.Draw(card)
        draw.text((12, 11), entry['title'], font=font, fill='#2c373d')
        for y in range(40, 153, 12):
            for x in range(12, 236, 12):
                draw.rectangle((x, y, min(x + 11, 235), min(y + 11, 152)),
                               fill='#e6ebef' if (x // 12 + y // 12) % 2 else '#fff')
        scaled = asset.copy()
        scaled.thumbnail((212, 100))
        if scaled.size == asset.size:
            scale = min(3, 100 / asset.height, 212 / asset.width)
            scaled = asset.resize((round(asset.width * scale), round(asset.height * scale)),
                                  Image.Resampling.LANCZOS)
        card.alpha_composite(scaled, ((card.width - scaled.width) // 2, 40 + (113 - scaled.height) // 2))
        overview.alpha_composite(card, (index % columns * width + 6, index // columns * height + 6))
    overview.convert('RGB').save(OUT / 'overview.jpg', quality=94)


def write_preview(entries):
    cards = []
    for entry in entries:
        title = escape(entry['title'])
        url = '/assets/figures/elements/figure76/' + entry['file']
        cards.append(f'<article><h3>{title}</h3><div class="checker"><img src="{url}" alt="{title}"></div>'
                     f'<p><a href="{url}">Open transparent PNG</a></p></article>')
    notes = ''.join(f'<li><strong>{panel}</strong> · {description}</li>' for panel, description in NATIVE.items())
    template = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Figure 7.6 · Extracted assets</title>
<style>
body{margin:24px;background:#f3f5f7;color:#27343a;font:16px Arial,sans-serif}
main{max-width:1480px;margin:auto}h1{font-size:24px}h2{font-size:19px}h3{font-size:15px}
.original,.overview{display:block;width:100%;height:auto;background:#fff}.overview{max-width:1040px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
article{background:white;border-radius:8px;padding:12px}
.checker{height:130px;display:grid;place-items:center;background:repeating-conic-gradient(#e6ebef 0% 25%,#fff 0% 50%) 0/22px 22px}
.checker img{height:105px;width:90%;object-fit:contain}p,li{line-height:1.5}summary{cursor:pointer;margin:16px 0}
@media(max-width:600px){body{margin:12px}}
</style>
<main><h1>Figure 7.6 · Extracted pictorial assets</h1>
<h2>Original</h2><img class="original" src="/{original}" width="2000" height="930" alt="Original Figure 7.6">
<h2>Transparent PNG overview</h2><img class="overview" src="/assets/figures/elements/figure76/overview.jpg" alt="Extracted robot arms, agents, vehicles and verification icons">
<p>The clean vehicle silhouettes are reused in scenes where a dashed trajectory crosses the body. The clean event agents are reused in the relations row.</p>
<details><summary>Inspect {count} individual PNGs</summary><div class="grid">{cards}</div></details>
<h2>Elements to draw in the frontend</h2><ul>{notes}</ul></main></html>
"""
    for key, value in {
        '{original}': str(SOURCE.relative_to(SITE)), '{count}': str(len(entries)),
        '{cards}': ''.join(cards), '{notes}': notes
    }.items():
        template = template.replace(key, value)
    (SITE / 'example/figure76-assets.html').write_text(template)


def main():
    assets = []
    for name, box, title in ASSETS:
        asset = cutout(box)
        if name == 'ii-core/safety-shield':
            ImageDraw.Draw(asset).rectangle((9, 17, 24, 32), fill=(255, 255, 255, 0))
        if name == 'iii-outputs/strategy-shield':
            ImageDraw.Draw(asset).rectangle((8, 18, 24, 33), fill=(255, 255, 255, 0))
        file = name + '.png'
        entry = {'file': file, 'source_box': box, 'title': title}
        if file in REUSE:
            entry['placement_boxes'] = REUSE[file]
        assets.append((asset, entry))
        for base in (OUT, SITE / 'source/src/img/figs/f76', SITE / 'assets/img/figs/f76'):
            dest = base / file
            dest.parent.mkdir(parents=True, exist_ok=True)
            asset.save(dest)
    entries = [entry for _, entry in assets]
    (OUT / 'manifest.json').write_text(json.dumps({
        'source': str(SOURCE.relative_to(SITE)),
        'source_size': ORIGINAL.size,
        'assets': entries,
        'frontend': NATIVE,
    }, indent=2) + '\n')
    make_overview(assets)
    write_preview(entries)


if __name__ == '__main__':
    main()
