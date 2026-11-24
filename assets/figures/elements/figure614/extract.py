"""Separate Figure 6.14 imagery from frontend boxes, labels and graph arrows."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, gaussian_filter
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/scene_graph.webp'
src = Image.open(SOURCE).convert('RGB')


def interpolate(im, mask):
    """Restore thin annotations using their immediate image neighborhood."""
    a = np.array(im).astype(float)
    ys, xs = np.where(mask)
    ids = {(y, x): i for i, (y, x) in enumerate(zip(ys, xs))}
    matrix = lil_matrix((len(ys), len(ys)))
    boundary = np.zeros((len(ys), 3))
    for i, (y, x) in enumerate(zip(ys, xs)):
        neighbors = [(yy, xx) for yy, xx in [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
                     if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1]]
        matrix[i, i] = len(neighbors)
        for yy, xx in neighbors:
            j = ids.get((yy, xx))
            if j is None:
                boundary[i] += a[yy, xx]
            else:
                matrix[i, j] = -1
    if len(ys):
        a[ys, xs] = spsolve(matrix.tocsr(), boundary)
    return Image.fromarray(np.uint8(a.clip(0, 255)))


def box_mask(im, box, rectangles):
    """Limit removal to the known annotation strips, preserving blue scenery."""
    a = np.array(im).astype(float)
    strips = Image.new('L', im.size)
    draw = ImageDraw.Draw(strips)
    for x0, y0, x1, y1 in rectangles:
        draw.rectangle((x0-box[0], y0-box[1], x1-box[0], y1-box[1]), outline=255, width=5)
    strips = binary_dilation(np.array(strips) > 0, iterations=3)
    blue = (a[:, :, 2] - a[:, :, 0] > 65) & (a[:, :, 2] - a[:, :, 1] > 65)
    return binary_dilation(strips & blue, iterations=2)


def remove_boxes(im, box, rectangles, reference=None):
    mask = box_mask(im, box, rectangles)
    clean = interpolate(im, mask)
    if reference is not None:
        # The source's unannotated video frame is the same horse photograph.
        # Restore the covered pixels from that reference, retaining all original
        # high-resolution pixels outside the narrow detector outlines.
        ref = reference.resize(im.size, Image.Resampling.LANCZOS)
        blend = Image.fromarray(np.uint8(gaussian_filter(mask.astype(float), .5)*255))
        clean = Image.composite(ref, clean, blend)
    return clean


def remove_axes(im):
    mask = Image.new('L', im.size)
    d = ImageDraw.Draw(mask)
    d.line([(53, 201), (53, 155)], fill=255, width=9)
    d.polygon([(53, 147), (45, 163), (62, 163)], fill=255)
    d.line([(53, 201), (94, 201)], fill=255, width=9)
    d.polygon([(102, 201), (89, 193), (89, 209)], fill=255)
    d.line([(53, 201), (26, 181)], fill=255, width=9)
    d.polygon([(22, 179), (28, 195), (37, 182)], fill=255)
    for box in [(44, 124, 61, 146), (6, 161, 23, 188), (105, 188, 125, 213)]:
        d.rectangle(box, fill=255)
    return interpolate(im, binary_dilation(np.array(mask) > 0, iterations=1))


def transparent(im):
    a = np.array(im).astype(float)/255
    alpha = 1-a.min(2)
    alpha[alpha < .055] = 0
    rgb = np.clip(1-(1-a)/np.maximum(alpha[:, :, None], .001), 0, 1)
    return Image.fromarray(np.uint8(np.dstack([rgb, alpha])*255), 'RGBA')


items = [
    ('image/horse-scene', (24, 69, 376, 305), 'horse', 'Horse and rider photograph, with both detection boxes removed.'),
    ('video/frame-1', (424, 162, 536, 237), '', 'First video frame; time label and timeline excluded.'),
    ('video/frame-2', (544, 162, 656, 237), '', 'Second video frame; time label and timeline excluded.'),
    ('video/frame-3', (664, 162, 776, 237), '', 'Third video frame; time label and timeline excluded.'),
    ('3d/room-without-axes', (1224, 69, 1576, 305), 'axes', 'Chair, table and lamp scene; coordinate axes and x/y/z labels removed.'),
    ('universal/image', (1636, 109, 1748, 184), '', 'Image-modality thumbnail; heading excluded.'),
    ('universal/video-frame-1', (1812, 149, 1865, 184), '', 'First universal video thumbnail; heading excluded.'),
    ('universal/video-frame-2', (1867, 149, 1921, 184), '', 'Second universal video thumbnail; heading excluded.'),
    ('universal/point-cloud', (1812, 237, 1908, 280), 'transparent', 'Point-cloud illustration on a transparent background; 3D heading excluded.'),
    ('hoi/cyclist-without-boxes', (24, 670, 425, 938), 'cyclist', 'Cyclist photograph; person and bicycle detection boxes removed.'),
    ('psg/panoptic-cyclist', (1033, 670, 1434, 938), '', 'Original panoptic visualization, preserving the source person, bicycle, road and sky mask colors.'),
]
records = []
for name, box, treatment, note in items:
    im = src.crop(box)
    if treatment == 'horse':
        im = remove_boxes(im, box, [(49, 118, 308, 288), (152, 72, 211, 211)], src.crop((424, 162, 536, 237)))
    elif treatment == 'cyclist':
        im = remove_boxes(im, box, [(87, 778, 346, 913), (153, 678, 281, 896)])
    elif treatment == 'axes':
        im = remove_axes(im)
    im = transparent(im) if treatment == 'transparent' else im.convert('RGBA')
    p = ROOT / (name+'.png')
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p)
    for folder in ['source/src/img/figs/f614', 'assets/img/figs/f614']:
        dest = SITE / folder / (name+'.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    records.append(dict(file=name+'.png', source_box=list(box), size=list(im.size), transparent=treatment=='transparent', notes=note))

(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)), source_size=list(src.size), notes='Eleven individual PNGs grouped by panel. Photos retain their image backgrounds; the point cloud uses transparency. Text, quotation card, formulas, graph nodes, graph arrows, detector boxes, coordinate axes, dividers and timeline elements remain independent frontend geometry.', assets=records), indent=2)+'\n')

font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 19)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
sheet = Image.new('RGB', (1200, 1330), '#eef2f6')
d = ImageDraw.Draw(sheet)
d.text((22, 19), 'Figure 6.14 — separate pictorial assets', font=font, fill='#263238')
for i, record in enumerate(records):
    x = 16+i%3*396; y = 60+i//3*316
    d.rounded_rectangle((x, y, x+382, y+300), 10, fill='white', outline='#c6cfd8')
    im = Image.open(ROOT/record['file'])
    ratio = min(356/im.width, 235/im.height)
    im = im.resize((round(im.width*ratio), round(im.height*ratio)), Image.Resampling.LANCZOS)
    sheet.paste(im, (x+(382-im.width)//2, y+8+(235-im.height)//2), im)
    d.text((x+12, y+253), record['file'], font=small, fill='#263238')
    d.text((x+12, y+277), 'Native: '+str(record['size'][0])+' × '+str(record['size'][1]), font=small, fill='#63717c')
sheet.save(ROOT/'overview.png')
cards = ''.join('<article><img src="/assets/figures/elements/figure614/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
(SITE/'example/figure614-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.14 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#263238;margin:24px}main{max-width:1300px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:16px;text-align:center;min-height:220px;display:flex;align-items:center;justify-content:center;flex-direction:column}article img{max-height:250px}p{overflow-wrap:anywhere}@media(max-width:600px){body{margin:12px}section{grid-template-columns:1fr}}</style><main><h1>Figure 6.14 · extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/scene_graph.webp"><h2 id="assets">Separated assets</h2><section>'''+cards+'''</section></main></html>''')
print('Saved 11 Figure 6.14 PNG assets and review page.')
