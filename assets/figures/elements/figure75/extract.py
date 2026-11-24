"""Extract Figure 7.5 pictorial assets; retain diagram geometry for the frontend."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'assets/figures/figures/part3/section7/715_program.webp'
original = Image.open(SOURCE).convert('RGBA')
box = (28, 123, 145, 239)
asset = original.crop(box)
pixels = asset.load()
for y in range(asset.height):
    for x in range(asset.width):
        r, g, b, a = pixels[x, y]
        if min(r, g, b) > 238:
            pixels[x, y] = (255, 255, 255, 0)
name = 'i-inputs/initial-state-arm.png'
dest = OUT / name
dest.parent.mkdir(parents=True, exist_ok=True)
asset.save(dest)
for base in [ROOT / 'source/src/img/figs/f75', ROOT / 'assets/img/figs/f75']:
    target = base / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dest, target)

frontend = {
    'i-inputs': 'Table, object cube, goal outline and check; skill boxes and arrows; precondition/effect boxes and formulas; all panel frames and labels.',
    'ii-core': 'Symbolic planning graph and selected path; FSM states, transitions and labels; behavior-tree nodes, branches and status legend; production-rule boxes and formulas.',
    'iii-outputs': 'Action plan and parallel-step boxes; reactive-policy sensor, logic and branches; execution trace, failure/replan/retry paths; all frames, arrows and labels.'
}
(OUT / 'manifest.json').write_text(json.dumps({
    'source': str(SOURCE.relative_to(ROOT)), 'source_size': list(original.size),
    'assets': [{'file': name, 'source_box': list(box), 'title': 'Initial state robot arm'}],
    'frontend': frontend
}, indent=2))

overview = Image.new('RGBA', (640, 410), 'white')
d = ImageDraw.Draw(overview)
d.text((20, 18), 'Figure 7.5 / (i) Inputs / Initial state robot arm', fill='#2c373d')
for y in range(55, 380, 16):
    for x in range(20, 620, 16):
        d.rectangle((x, y, min(x+15, 619), min(y+15, 379)), fill='#edf0f3' if (x//16+y//16)%2 else 'white')
large = asset.resize((asset.width*2, asset.height*2), Image.Resampling.LANCZOS)
overview.alpha_composite(large, ((640-large.width)//2, 55+(325-large.height)//2))
overview.convert('RGB').save(OUT / 'overview.jpg', quality=95)
notes = ''.join(f'<li><strong>{k}</strong>: {v}</li>' for k,v in frontend.items())
(ROOT / 'example/figure75-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.5 extracted assets</title><style>body{font:16px Arial;color:#27343a;background:#f3f5f7;margin:24px}main{max-width:1600px;margin:auto}h1{font-size:24px}h2{font-size:18px}.original{display:block;width:100%;background:white}.overview{display:block;max-width:100%;width:640px;background:white}p,li{line-height:1.6}li{margin-bottom:10px}article{background:white;padding:20px;margin-top:24px;border-radius:8px}.checker{display:grid;place-items:center;width:280px;height:240px;max-width:100%;background:repeating-conic-gradient(#edf0f3 0% 25%,white 0% 50%) 0/20px 20px}.checker img{width:234px;max-width:100%;height:auto}@media(max-width:600px){body{margin:12px}}</style><main><h1>Figure 7.5 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/715_program.webp" alt="Original Figure 7.5"><h2>Pictorial asset overview</h2><img class="overview" src="/assets/figures/elements/figure75/overview.jpg" alt="Extracted robot arm"><article><h2>(i) Inputs · Initial state robot arm</h2><div class="checker"><img src="/assets/figures/elements/figure75/i-inputs/initial-state-arm.png" alt="Transparent initial state robot arm"></div><p><a href="/assets/figures/elements/figure75/i-inputs/initial-state-arm.png">Open transparent PNG</a> · 117 × 116 pixels</p></article><h2>Independent frontend geometry</h2><ul>'''+notes+'''</ul></main></html>''')
