"""Extract the pictorial layers for review before redrawing Figures 4.1 and 4.2."""
import json
from html import escape
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from extract_figures91_924 import STYLE

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT.parent / 'Spatial_Intelligence_Book_2025_v14/figures/part2'


def pdf_image(doc, xref):
    pix = fitz.Pixmap(doc, xref)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def rounded(image, radius=16):
    size = image.size
    mask = Image.new('L', (size[0]*4, size[1]*4))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, mask.width-1, mask.height-1), radius*4, fill=255)
    image = image.convert('RGBA')
    image.putalpha(mask.resize(size, Image.Resampling.LANCZOS))
    return image


def remove_marks(image, mask, sigma):
    """Interpolate the color field from neighboring unmarked pixels."""
    pixels = np.asarray(image, dtype=float)
    keep = (~mask).astype(float)
    weight = ndimage.gaussian_filter(keep, sigma)
    for channel in range(3):
        estimate = ndimage.gaussian_filter(pixels[..., channel]*keep, sigma) / np.maximum(weight, 1e-6)
        pixels[..., channel][mask] = estimate[mask]
    return Image.fromarray(np.uint8(np.clip(pixels+.5, 0, 255)))


def restore_video_middle(atlas, box):
    image = atlas.crop(box)
    # The opaque play icon covers the walker. Sample the adjacent frame at
    # the same relative position; feather the join while keeping the original
    # middle frame outside the obscured area.
    donor = atlas.crop((387, 42, 517, 280)).resize(image.size)
    yy, xx = np.indices((image.height, image.width))
    radius = np.hypot(xx+box[0]-587, yy+box[1]-173)
    mask = Image.fromarray(np.uint8(np.clip((44-radius)/4, 0, 1)*255))
    return Image.composite(donor, image, mask)


def two_dimensional(doc):
    atlas = pdf_image(doc, 6)
    layer = doc[0].get_image_info(xrefs=True)[0]['bbox']
    sx, sy = (layer[2]-layer[0])/atlas.width, (layer[3]-layer[1])/atlas.height
    def entry(panel, name, image, box):
        x, y, r, b = box
        return panel, name, image, (layer[0]+x*sx, layer[1]+y*sy, layer[0]+r*sx, layer[1]+b*sy)

    boxes = [
        ('image', 'street-scene', (9, 10, 348, 328)),
        ('segmentation', 'class-map', (828, 10, 1207, 331)),
        ('depth', 'depth-map', (1239, 10, 1616, 332)),
        ('surface-normals', 'normal-map', (9, 414, 365, 727)),
        ('edges', 'edge-map', (413, 414, 776, 727)),
        ('optical-flow', 'motion-color-field', (827, 417, 1198, 727)),
    ]
    for panel, name, box in boxes:
        image = atlas.crop(box)
        if panel == 'optical-flow':
            luminance = np.asarray(image.convert('L'), dtype=float)
            local = ndimage.median_filter(luminance, size=11)
            seeds = (local-luminance > 18)
            seeds[:9, :] = seeds[-9:, :] = False
            seeds[:, :9] = seeds[:, -9:] = False
            # Only remove compact dark marks. Preserve extended scene edges.
            labels, _ = ndimage.label(seeds, structure=np.ones((3, 3)))
            sizes = np.bincount(labels.ravel())
            mask = (labels > 0) & (sizes[labels] <= 70)
            image = remove_marks(image, ndimage.binary_dilation(mask, iterations=2), 2.2)
        yield entry(panel, name, rounded(image), box)

    frames = [(387, 42, 517, 280), (521, 42, 652, 280), (655, 42, 785, 280)]
    for i, box in enumerate(frames, 1):
        image = restore_video_middle(atlas, box) if i == 2 else atlas.crop(box)
        yield entry('video', f'frame-{i:02}', rounded(image, 3), box)


def transparent_teapot(image, xref):
    pixels = np.asarray(image, dtype=float)
    if xref == 4:
        threshold = np.max(pixels, axis=2) <= 4
    elif xref == 10:
        # Use fractional opacity for fine points, preserving their appearance
        # when composited back onto the original near-white background.
        white = float(np.median(pixels[:10]))
        alpha = np.clip(1-pixels.mean(axis=2)/white, 0, 1)
        result = Image.new('RGBA', image.size, 'black')
        result.putalpha(Image.fromarray(np.uint8(alpha*255+.5)))
        return result
    else:
        white = np.median(pixels[:10], axis=(0, 1))
        threshold = np.max(np.abs(pixels-white), axis=2) <= 5
    mask = Image.fromarray(np.uint8(~threshold)*255)
    result = image.convert('RGBA')
    result.putalpha(mask)
    return result


def three_dimensional(doc):
    placements = {i['xref']: i['bbox'] for i in doc[0].get_image_info(xrefs=True)}
    for xref, panel in [(4, 'rgb-d'), (9, 'voxel'), (10, 'point-cloud'), (6, 'mesh')]:
        image = pdf_image(doc, xref)
        yield panel, 'teapot', transparent_teapot(image, xref), placements[xref]

    chart = pdf_image(doc, 7)
    x, y, r, b = placements[7]
    sx, sy = (r-x)/chart.width, (b-y)/chart.height
    for name, (l, t, rr, bb) in [('distance-field', (101, 156, 596, 652)), ('color-scale', (628, 97, 658, 712))]:
        image = chart.crop((l, t, rr, bb))
        if name == 'distance-field':
            contour = np.max(np.asarray(image), axis=2) < 80
            image = remove_marks(image, ndimage.binary_dilation(contour, iterations=3), 3)
        yield 'sdf', name, image.convert('RGBA'), (x+l*sx, y+t*sy, x+rr*sx, y+bb*sy)


def review_figure(number, stem, extractor, note):
    key, ident = f'4.{number}', f'4{number}'
    original = f'assets/figures/figures/part2/{stem}.webp'
    out = ROOT / f'assets/figures/elements/figure{ident}'
    entries = []
    with fitz.open(BOOK / f'{stem}.pdf') as doc:
        scale = 1000/doc[0].rect.width
        for panel, name, image, box in extractor(doc):
            file = f'{panel}/{name}.png'
            for base in (out, ROOT/f'source/src/img/figs/f{ident}', ROOT/f'assets/img/figs/f{ident}'):
                path = base/file
                path.parent.mkdir(parents=True, exist_ok=True)
                image.save(path, optimize=True)
            entry = dict(file=file, panel=panel, title=name.replace('-', ' '), size=list(image.size),
                         pdf_box=[round(coord*scale, 3) for coord in box])
            if panel == 'rgb-d':
                entry['backdrop'] = '#000000'
            entries.append(entry)
    with Image.open(ROOT/original) as source:
        manifest = dict(figure=key, sources=[original], source_sizes=[list(source.size)],
                        source_pdf=str((BOOK/f'{stem}.pdf').relative_to(ROOT.parent)), assets=entries,
                        frontend=[note])
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    cards = []
    for asset in entries:
        file = asset['file']
        background = ' style="background:#000"' if asset.get('backdrop') else ''
        cards.append(f'<article><h3>{escape(file)}</h3><div class="checker"{background}><img src="/assets/figures/elements/figure{ident}/{file}" alt="{escape(asset["title"])}"></div></article>')
    return (f'<section id="f{ident}"><h2>Figure {key}</h2><img class="original" src="/{original}" '
            f'alt="Original Figure {key}"><p>{len(entries)} PNG assets. {escape(note)}</p>'
            f'<div class="grid">{"".join(cards)}</div></section>')


def main():
    scenes = review_figure(1, '2D_representations', two_dimensional,
        'The central video frame was restored with material from the adjacent frame where the play icon obscured it. Filmstrip, controls, optical-flow arrows, keypoint skeleton, and labels will be drawn in the frontend.')
    teapots = review_figure(2, '3d_representation', three_dimensional,
        'The RGB-D teapot is displayed against the original black backdrop. The SDF contour, axes, ticks, and labels will be drawn in the frontend.')
    (ROOT/'example/figures41-42-assets.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Figures 4.1 and 4.2 · Asset review</title><style>{STYLE}</style><main>'
        '<h1>Figures 4.1 and 4.2 · Asset review</h1><nav><a href="#f41">Figure 4.1</a> <a href="#f42">Figure 4.2</a></nav>'
        f'{scenes}{teapots}</main></html>')


if __name__ == '__main__':
    main()
