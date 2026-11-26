"""Extract the source imagery; all diagram annotations remain frontend elements."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/spatial_relation_extraction.webp'
src = Image.open(SOURCE).convert('RGB')


def remove_annotations(im):
    """Restore just the blue boxes and O1/O2 labels using local interpolation."""
    a = np.array(im).astype(float)
    mask = (a[:, :, 2] - a[:, :, 0] > 45) & (a[:, :, 2] - a[:, :, 1] > 35) & (a[:, :, 2] > 110)
    mask = binary_dilation(mask, iterations=2)
    ys, xs = np.where(mask)
    indices = {(y, x): i for i, (y, x) in enumerate(zip(ys, xs))}
    matrix = lil_matrix((len(ys), len(ys)))
    boundary = np.zeros((len(ys), 3))
    for i, (y, x) in enumerate(zip(ys, xs)):
        neighbors = [(yy, xx) for yy, xx in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
                     if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1]]
        matrix[i, i] = len(neighbors)
        for yy, xx in neighbors:
            j = indices.get((yy, xx))
            if j is None:
                boundary[i] += a[yy, xx]
            else:
                matrix[i, j] = -1
    a[ys, xs] = spsolve(matrix.tocsr(), boundary)
    # Follow the curtain's vertical texture and the wall's horizontal trim when
    # restoring labels, avoiding compression halos around the original glyphs.
    for y in range(116, 156):
        left = a[y, 433:438].mean(0)
        right = a[y, 489:494].mean(0)
        a[y, 438:489] = np.linspace(left, right, 51)
    for x in range(163, 209):
        top = a[95:99, x].mean(0)
        bottom = a[140:144, x].mean(0)
        a[99:140, x] = np.linspace(top, bottom, 41)
    return Image.fromarray(np.uint8(a.clip(0, 255)))


def transparent(im):
    a = np.array(im).astype(float) / 255
    alpha = 1 - a.min(2)
    alpha[alpha < .055] = 0
    rgb = np.clip(1 - (1 - a) / np.maximum(alpha[:, :, None], .001), 0, 1)
    return Image.fromarray(np.uint8(np.dstack([rgb, alpha]) * 255), 'RGBA')


items = [
    ('input/scene', (30, 104, 671, 533), False, True, 'Main scene, with blue target boxes and object labels removed.'),
    ('input/video-frame-1', (40, 641, 117, 693), False, False, 'First video frame, without caption.'),
    ('input/video-frame-2', (123, 641, 201, 693), False, False, 'Second video frame, without caption.'),
    ('input/point-cloud', (247, 620, 371, 683), True, False, 'Colored object and scene point cloud; transparent background, no caption.'),
    ('input/rgbd-color', (442, 636, 527, 693), False, False, 'RGB component, separated from the depth map.'),
    ('input/rgbd-depth', (538, 631, 622, 693), False, False, 'Depth component, without caption.'),
]
records = []
for name, box, cut, restore, note in items:
    im = src.crop(box)
    if restore:
        im = remove_annotations(im)
    im = transparent(im) if cut else im.convert('RGBA')
    path = ROOT / (name + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    for folder in ['source/src/img/figs/f613', 'assets/img/figs/f613']:
        target = SITE / folder / (name + '.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    records.append(dict(file=name+'.png', source_box=list(box), size=list(im.size), transparent=cut, notes=note))

(ROOT / 'manifest.json').write_text(json.dumps(dict(
    source=str(SOURCE.relative_to(SITE)),
    source_size=list(src.size),
    notes='Six separate pictorial PNGs. Photographs and the depth map retain their rectangular image backgrounds; the point cloud is transparent. All text, formulas, target boxes, axes, diagram symbols, model cards, arrows and timeline lines will be drawn independently in the frontend.',
    assets=records), indent=2) + '\n')

font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
sheet = Image.new('RGB', (1200, 870), '#eef2f6')
d = ImageDraw.Draw(sheet)
d.text((24, 20), 'Figure 6.13 — separated image assets', font=font, fill='#263238')
for i, record in enumerate(records):
    x = 18 + i % 3 * 394
    y = 64 + i // 3 * 396
    d.rounded_rectangle((x, y, x+376, y+376), 12, fill='white', outline='#c6cfd8')
    im = Image.open(ROOT / record['file'])
    # Enlarge only the contact-sheet display; PNG files keep native pixels.
    scale = min(350 / im.width, 290 / im.height)
    im = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
    sheet.paste(im, (x+(376-im.width)//2, y+14+(290-im.height)//2), im)
    d.text((x+14, y+325), record['file'], font=small, fill='#263238')
    d.text((x+14, y+350), 'Native size: '+str(record['size'][0])+' × '+str(record['size'][1]), font=small, fill='#63717c')
sheet.save(ROOT / 'overview.png')

cards = ''.join('<article><img src="/assets/figures/elements/figure613/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
(SITE / 'example/figure613-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.13 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#263238;margin:24px}main{max-width:1300px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:16px;text-align:center;min-height:220px;display:flex;align-items:center;justify-content:center;flex-direction:column}article img{max-height:250px}p{overflow-wrap:anywhere}@media(max-width:600px){body{margin:12px}section{grid-template-columns:1fr}}</style><main><h1>Figure 6.13 · extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/spatial_relation_extraction.webp"><h2 id="assets">Separated assets</h2><section>'''+cards+'''</section></main></html>''')
print('Saved six Figure 6.13 pictorial assets and review page.')
