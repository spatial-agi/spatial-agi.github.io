"""Extract the three shared, unannotated photographic frames of Figure 6.23."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
SOURCE = 'assets/figures/figures/part3/section6/object_tracking_method.webp'
im = Image.open(SITE / SOURCE).convert('RGBA')
assets = []
overview = Image.new('RGB', (900, 400), '#edf1f5')
draw = ImageDraw.Draw(overview)
for i, (top, bottom) in enumerate([(58, 165), (165, 272), (272, 379)]):
    box = (1606, top, 1708, bottom)
    frame = im.crop(box)
    relative = f'shared-frames/frame-{i:02}.png'
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.save(target)
    for mirror in ['source/src/img/figs/f623', 'assets/img/figs/f623']:
        dest = SITE / mirror / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, dest)
    enlarged = frame.resize((255, 268), Image.Resampling.NEAREST).convert('RGB')
    overview.paste(enlarged, (25 + i * 300, 65))
    draw.text((25 + i * 300, 30), f'Frame {i + 1} (original pixels)', fill='#243342')
    draw.text((25 + i * 300, 350), f'frame-{i:02}.png | 102 x 107', fill='#243342')
    assets.append({'file': relative, 'source_box': box, 'size': frame.size,
                   'panels': ['i', 'ii', 'iii', 'iv'],
                   'notes': 'Unannotated original photograph from panel (iv). Photographic background retained; film border excluded. RGBA PNG.'})
overview.save(ROOT / 'overview.png')
(ROOT / 'manifest.json').write_text(json.dumps({
    'source': SOURCE, 'source_size': im.size, 'assets': assets,
    'frontend': 'Film-strip borders, tracking rectangles, ID labels, matching/update boxes, detector and association blocks, queries, shared backbone, task heads, all arrows, separators and text.'
}, indent=2) + '\n')
