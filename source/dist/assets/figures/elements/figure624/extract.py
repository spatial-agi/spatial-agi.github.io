"""Extract the shared kitchen sequence from Figure 6.24 without diagram borders."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
SOURCE = 'assets/figures/figures/part3/section6/temporal_localization.webp'
im = Image.open(SITE / SOURCE).convert('RGBA')
overview = Image.new('RGB', (960, 420), '#edf1f5')
draw = ImageDraw.Draw(overview)
assets = []
for i, box in enumerate([(553, 238, 671, 356), (685, 238, 803, 356), (818, 238, 936, 356)]):
    frame = im.crop(box)
    relative = f'shared-video/frame-{i:02}.png'
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.save(target)
    for mirror in ['source/src/img/figs/f624', 'assets/img/figs/f624']:
        dest = SITE / mirror / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, dest)
    overview.paste(frame.resize((280, 280), Image.Resampling.NEAREST).convert('RGB'), (20+i*320, 65))
    draw.text((20+i*320, 30), f'Frame {i+1} | original pixels', fill='#243342')
    draw.text((20+i*320, 365), f'frame-{i:02}.png | 118 x 118', fill='#243342')
    assets.append({'file': relative, 'source_box': box, 'size': frame.size,
                   'panels': ['tal-i', 'tal-ii', 'tal-iii', 'tal-iv', 'tsg-a', 'tsg-b', 'tsg-c'],
                   'notes': 'Original unannotated scene from TAL panel (ii). External image border removed. Photographic scene retained, RGBA PNG.'})
overview.save(ROOT / 'overview.png')
(ROOT / 'manifest.json').write_text(json.dumps({
    'source': SOURCE, 'source_size': im.size, 'assets': assets,
    'frontend': 'All text and formulas; window selection; image borders; arrows and time axes; classifiers, proposals, scores and temporal segments; feature pyramids and boundary offsets; transformer blocks and query circles; temporal map and hatching; graph nodes and edges; corpus icons and retrieval blocks.'
}, indent=2) + '\n')
