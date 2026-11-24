"""Figure 6.4 artwork only; diagram labels, frames and arrows stay native."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/keypoint_detection_v2.webp'
src = Image.open(SOURCE).convert('RGB')
SPECS = [
    ('tasks/body-pose', (165, 94, 325, 475)),
    ('tasks/facial-landmarks', (447, 102, 713, 461)),
    ('tasks/hand-gesture', (813, 108, 1092, 473)),
    ('tasks/animal-pose', (1174, 211, 1518, 466)),
    ('tasks/object-chair', (1400, 117, 1511, 272)),
    ('tasks/medical-skull', (1560, 126, 1841, 450)),
    ('methods/handcrafted-image', (174, 649, 328, 746)),
    ('methods/heatmap', (553, 652, 662, 769)),
    ('methods/realtime-pose-left', (1188, 614, 1282, 794)),
    ('methods/realtime-pose-right', (1373, 614, 1462, 794)),
    ('methods/generative-noise', (1569, 627, 1676, 766)),
    ('methods/generative-pose', (1746, 627, 1852, 769)),
]
records = []
for name, box in SPECS:
    arr = np.asarray(src.crop(box)).copy()
    low = arr.min(axis=2)
    alpha = np.clip((252 - low.astype(float)) * 20, 0, 255).astype('uint8')
    alpha[low < 240] = 255
    if name == 'tasks/medical-skull':
        # Remove anatomical abbreviations, retaining the skull and landmark dots.
        mask = Image.fromarray(alpha)
        draw = ImageDraw.Draw(mask)
        for x0, y0, x1, y1 in [(1759, 123, 1788, 150), (1817, 204, 1841, 238),
                                (1826, 250, 1841, 278), (1826, 303, 1841, 332),
                                (1826, 337, 1841, 366), (1815, 388, 1841, 417),
                                (1812, 425, 1841, 450), (1674, 404, 1707, 434)]:
            draw.rectangle((x0-box[0], y0-box[1], x1-box[0], y1-box[1]), fill=0)
        alpha = np.asarray(mask)
    if name == 'tasks/animal-pose':
        alpha[:75, 210:] = 0  # chair and its enclosing frame belong to a separate asset
    if name.startswith('methods/realtime-pose-'):
        # The skeleton is blue; neighbouring curved arrows are neutral black.
        neutral = arr.max(axis=2).astype(int) - arr.min(axis=2).astype(int) < 12
        yy = np.arange(arr.shape[0])[:, None] + box[1]
        alpha[neutral & (yy > 642)] = 0
    if name == 'methods/handcrafted-image':
        blue = arr[:, :, 2].astype(int) - arr[:, :, 0].astype(int) > 25
        alpha[blue] = 0  # exclude the corner of the independently drawn feature frame
    out = Image.fromarray(np.dstack((arr, alpha)), 'RGBA')
    dest = ROOT / (name + '.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    assert out.getbbox() and out.getchannel('A').getextrema()[0] == 0
    records.append(dict(file=name+'.png', source_box=box, size=list(out.size)))
(ROOT / 'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)), assets=records), indent=2))
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
sheet = Image.new('RGB', (1280, 1280), '#e2e7ec')
d = ImageDraw.Draw(sheet)
for i, rec in enumerate(records):
    x, y = 10 + i % 3 * 423, 10 + i // 3 * 317
    d.rounded_rectangle((x, y, x+408, y+303), 8, fill='#fafafa', outline='#bac4ce')
    im = Image.open(ROOT / rec['file'])
    im.thumbnail((378, 253), Image.Resampling.LANCZOS)
    sheet.paste(im, (x+(408-im.width)//2, y+8), im)
    d.text((x+12, y+275), rec['file'].removesuffix('.png'), font=font, fill='#223443')
sheet.save(ROOT / 'overview.png')
print(f'Extracted and verified {len(records)} transparent PNG assets')
