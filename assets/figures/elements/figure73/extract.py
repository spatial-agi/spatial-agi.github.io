"""Extract/restore the two pictorial silhouettes; keep graph geometry native."""
from collections import deque
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'assets/figures/figures/part3/section7/713_topo.webp'
original = Image.open(SOURCE).convert('RGBA')
ITEMS = [
    ('i-inputs/sensing-device', (31, 243, 94, 296), 'Sensing device',
     'Restored the neutral outline behind the blue sensor marker and sensing rays. Those annotations will be drawn independently.'),
    ('i-inputs/robot-body', (24, 499, 85, 601), 'Robot / task body',
     'Preserved the original pale fill and dark contour; the curved task constraint stays native.'),
]

for name, box, title, note in ITEMS:
    asset = original.crop(box)
    if name.endswith('sensing-device'):
        # The original blue rays overlap the top/right outline. Restore the
        # simple symmetric enclosure, retaining its source size and gray ink.
        scale = 4
        asset = Image.new('RGBA', (asset.width * scale, asset.height * scale))
        ImageDraw.Draw(asset).rounded_rectangle(
            (3*scale, 2*scale, 59*scale, 49*scale), radius=7*scale,
            outline='#a7b1b7', width=3*scale)
        asset = asset.resize((box[2]-box[0], box[3]-box[1]), Image.Resampling.LANCZOS)
    else:
        # Flood only exterior paper, preserving the enclosed pale gray body.
        pixels = asset.load()
        w, h = asset.size
        queue = deque([(x, y) for x in range(w) for y in (0, h-1)] +
                      [(x, y) for y in range(h) for x in (0, w-1)])
        seen = set()
        while queue:
            x, y = queue.popleft()
            if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
                continue
            seen.add((x, y))
            r, g, b, a = pixels[x, y]
            if min(r, g, b) < 225:
                continue
            pixels[x, y] = (255, 255, 255, 0)
            queue.extend([(x-1, y), (x+1, y), (x, y-1), (x, y+1)])
    target = OUT / (name + '.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    asset.save(target)
    for mirror in [ROOT/'source/src/img/figs/f73', ROOT/'assets/img/figs/f73']:
        dest = mirror / (name+'.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, dest)

frontend = {
    'i-inputs': 'Free-space frame and obstacle, sensor marker and sensing rays, odometry trace, start/goal path, constraint arc, floor plan, labels.',
    'ii-reasoning': 'Visibility graph, Voronoi/skeleton, cell decomposition, roadmap/tree, graph-search weights and selected route, hierarchy graphs, frames, formula and captions.',
    'iii-outputs': 'Collision-free path, topological map, multi-agent time/vertex diagram, coverage/sweep path, frames and labels.',
}
(OUT/'manifest.json').write_text(json.dumps({
    'source': str(SOURCE.relative_to(ROOT)), 'source_size': list(original.size),
    'assets': [{'file': n+'.png', 'source_box': list(b), 'title': t, 'note': note}
               for n, b, t, note in ITEMS], 'frontend': frontend,
}, indent=2))

overview = Image.new('RGB', (920, 340), 'white')
for i, (name, box, title, note) in enumerate(ITEMS):
    card = Image.new('RGBA', (460, 340), 'white')
    draw = ImageDraw.Draw(card)
    draw.text((20, 18), title, fill='#263238')
    for y in range(50, 320, 16):
        for x in range(16, 444, 16):
            draw.rectangle((x, y, min(x+15,443), min(y+15,319)),
                           fill='#eceff2' if ((x-16)//16+(y-50)//16)%2==0 else 'white')
    asset = Image.open(OUT/(name+'.png'))
    asset = asset.resize((asset.width*2, asset.height*2), Image.Resampling.LANCZOS)
    card.alpha_composite(asset, ((460-asset.width)//2, 70+(240-asset.height)//2))
    overview.paste(card.convert('RGB'), (i*460, 0))
overview.save(OUT/'overview.jpg', quality=95)

cards = ''.join(f'<article><h2>{title}</h2><div class="checker"><img src="/assets/figures/elements/figure73/{name}.png" alt="{title}"></div><p>{name}.png</p><p>{note}</p></article>' for name, box, title, note in ITEMS)
notes = ''.join(f'<li><strong>{panel}</strong>: {description}</li>' for panel, description in frontend.items())
(ROOT/'example/figure73-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.3 extracted assets</title><style>body{font:16px Arial;color:#27343a;background:#f3f5f7;margin:24px}main{max-width:1600px;margin:auto}h1{font-size:24px}h2{font-size:18px}.original{display:block;width:100%;background:white;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}article{padding:16px;background:white;border-radius:8px}.checker{height:250px;display:grid;place-items:center;background:repeating-conic-gradient(#eceff2 0% 25%,white 0% 50%) 0/20px 20px}.checker img{height:204px;max-width:100%;object-fit:contain;image-rendering:auto}p,li{line-height:1.6;font-size:14px}li{margin-bottom:8px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 7.3 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/713_topo.webp" alt="Original Figure 7.3"><div class="grid">'''+cards+'''</div><h2>Independent frontend geometry</h2><ul>'''+notes+'''</ul></main></html>''')
