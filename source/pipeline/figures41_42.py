"""Build the native Chapter 4 figure fragments and their comparison pages."""
import json
from html import escape

import fitz
import numpy as np
from scipy import ndimage

from extract_figures41_42 import BOOK, ROOT, pdf_image

FIGURES = ROOT / 'assets/figures/elements'
STYLE = '/assets/css/figures41-42.css'
ATLAS_SCALE = 1000 / 1423
ATLAS = 'translate(.051 .051) scale(.6154 .6156)'
SDF = 'translate(787.964 14.14) scale(.26008)'


def n(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.')


def rect(x, y, w, h, extra=''):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" {extra}/>'


def text(value, x, y, size, extra=''):
    return f'<text x="{n(x)}" y="{n(y)}" font-size="{n(size)}" {extra}>{escape(value)}</text>'


def labels(names, positions, baselines, size, scale):
    return {
        key: text(title, x * scale, y * scale, size * scale,
                  f'textLength="{n(width * scale)}" lengthAdjust="spacingAndGlyphs" class="f4142-label"')
        for (key, title, _), (x, width), y in zip(names, positions, baselines)
    }


def image(figure, asset):
    x, y, right, bottom = asset['pdf_box']
    width, height = right - x, bottom - y
    backdrop = rect(x, y, width, height, f'fill="{asset["backdrop"]}"') if 'backdrop' in asset else ''
    path = escape(asset['file'], quote=True)
    return backdrop + (f'<image href="/assets/img/figs/f{figure}/{path}" x="{n(x)}" y="{n(y)}" '
                       f'width="{n(width)}" height="{n(height)}" preserveAspectRatio="none"/>')


def group(transform, content):
    return f'<g transform="{transform}">{content}</g>'


def filmstrip():
    return group(ATLAS, rect(376, 9, 420, 319, 'rx="15" fill="#272729"') + ''.join(
        rect(388 + index * 41.75, 17, 20, 16, 'rx="3" fill="#fff" stroke="#888" stroke-width=".6"')
        for index in range(10)))


def player_controls():
    return group(ATLAS, '<circle cx="587" cy="173" r="38" fill="#292929"/>'
                 '<path d="M578 155V191L606 173Z M392 294V316L410 305Z" fill="#fff"/>'
                 '<path d="M433 305H777" stroke="#808083" stroke-width="6" stroke-linecap="round"/>'
                 '<path d="M433 305H624" stroke="#159bd6" stroke-width="6" stroke-linecap="round"/>'
                 '<circle cx="625" cy="305" r="8.5" fill="#f8f8f8"/>')


def pose():
    # Coordinates are in the original atlas, relative to the keypoint panel.
    outlines = (
        ('#e3e3e3', 1.5, 'M166 45Q169 58 160 63L148 68Q138 71 136 91L131 116 129 153 M182 45Q177 58 187 63L201 69Q211 72 211 96L219 119 229 149 M150 84Q150 106 153 119L148 145Q143 168 153 192L158 215Q155 231 158 251L164 279 M201 84Q201 105 197 120L203 145Q209 166 200 190L194 218Q199 231 194 249L187 273 M158 154Q170 173 177 164Q187 168 195 153 M177 165L174 217 175 240 174 280 M177 165L183 217 181 239 182 275'),
        ('#cc2ec6', 2.2, 'M167 48Q160 42 163 31Q163 21 173.5 18Q185 19 186 31Q187 42 180 48Q174 53 167 48Z M163 35Q157 32 161 41L164 42 M185 35Q190 32 186 41L184 42'),
        ('#1466bc', 2.2, 'M133 157Q124 163 130 172Q134 178 139 176Q140 174 136 172L134 168 136 165Q139 165 138 170Q142 172 141 168Q139 160 136 159 M227 149Q236 154 234 162Q230 169 225 169Q222 168 225 165L230 162 229 158 226 158Q224 165 223 162Q222 157 227 149'),
        ('#277ea7', 1.5, 'M167 277Q164 287 159 292Q157 296 166 298Q175 300 175 295L174 278'),
        ('#d51e25', 2, 'M182 273Q183 284 184 291Q186 296 194 293Q198 291 194 286L187 273'),
    )
    limbs = (
        ('#eda024', 'M174 50V71L148 76 M174 71L201 75'),
        ('#98cb28', 'M148 76L136 117 M201 75L216 115 M174 71L176 148'),
        ('#11bcae', 'M136 117L134 157 M216 115L227 149 M158 154L176 148 194 153'),
        ('#1263c7', 'M158 154L165 218 170 277'),
        ('#dc7e16', 'M194 153L190 217'),
        ('#db2026', 'M190 217L185 273'),
    )
    joints = (
        ('#e89229', [(174, 50), (174, 71), (148, 76), (201, 75), (194, 153)]),
        ('#39bc31', [(136, 117), (216, 115), (176, 148)]),
        ('#16b7b9', [(134, 157), (227, 149)]),
        ('#1663bd', [(158, 154), (165, 218), (170, 277)]),
        ('#d62628', [(190, 217), (185, 273)]),
    )
    lines = ''.join(f'<path d="{path}" stroke="{color}" stroke-width="{width}"/>'
                    for color, width, path in outlines)
    lines += ''.join(f'<path d="{path}" stroke="{color}" stroke-width="4.7"/>' for color, path in limbs)
    circles = ''.join(f'<circle cx="{x}" cy="{y}" r="4.8" fill="white" stroke="{color}" stroke-width="2.6"/>'
                      for color, points in joints for x, y in points)
    return group(f'{ATLAS} translate(1240 417)',
                 rect(0, 0, 375, 310, 'rx="16" fill="#fdfdfd" stroke="#e8e8e8" stroke-width="1.7"') +
                 f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{lines}{circles}</g>')


def flow_marks():
    """Measure compact vectors on the source grid and rebuild their shafts and heads."""
    with fitz.open(BOOK / '2D_representations.pdf') as doc:
        atlas = pdf_image(doc, 6)
    gray = np.asarray(atlas.crop((827, 417, 1198, 727)).convert('L'), dtype=float)
    contrast = ndimage.median_filter(gray, size=11) - gray
    columns = (14, 38, 63, 87, 111, 135, 158, 180, 204, 227, 251, 265, 286, 308, 332, 356)
    rows = (14, 44, 74, 104, 133, 160, 185, 211, 239, 266, 295)
    blanks = {3: {7}, 4: {6, 7, 8}, 5: {6, 7, 8}, 6: {6, 7, 8},
              7: {7}, 8: {7}, 9: {7}, 10: set()}
    marks = []
    for row, y in enumerate(rows):
        for col, x in enumerate(columns):
            if col in blanks.get(row, ()):
                continue
            patch = contrast[y-4:y+5, x-4:x+5]
            labels_, count = ndimage.label(patch > 18, structure=np.ones((3, 3)))
            parts = [np.argwhere(labels_ == index) for index in range(1, count+1)]
            candidates = [part for part in parts if np.min(np.linalg.norm(part - 4, axis=1)) <= 3]
            if not candidates:
                continue
            points = max(candidates, key=len)[:, ::-1]
            center = points.mean(axis=0)
            center_x, center_y = center + (x - 4, y - 4)
            centered = points - center
            spread, axes = np.linalg.eigh(centered.T @ centered)
            direction = axes[:, -1]
            if np.ptp(centered @ direction) < 2.2 or spread[1] < 1.8 * spread[0]:
                marks.append(f'<circle class="f41-flow-dot" cx="{n(center_x)}" cy="{n(center_y)}" r=".77"/>')
                continue
            outward = np.array((x - 178, y - 137))
            if direction @ outward < 0:
                direction = -direction
            projections = centered @ direction
            start = center + (x - 4, y - 4) + (projections.min() - .25) * direction
            end = center + (x - 4, y - 4) + (projections.max() + .25) * direction
            marks.append(f'<path class="rl-route f41-flow-arrow" data-duration="5200" data-travel="620" '
                         f'd="M{n(start[0])} {n(start[1])}L{n(end[0])} {n(end[1])}" marker-end="url(#f41-arrowhead)"/>')
    return group(f'{ATLAS} translate(827 417)', ''.join(marks))


def chart():
    content = ['<path d="M317 250C330 246 322 217 346 215C365 213 366 245 374 248C458 259 517 322 518 407C519 499 444 573 352 573C262 573 189 499 189.5 408C190 331 242 268 317 250Z" fill="none" stroke="#080808" stroke-width="2.7"/>',
               rect(100, 96, 496, 616, 'fill="none" stroke="#080808"'),
               rect(627, 96, 31, 616, 'fill="none" stroke="#080808"')]
    ticks = []
    for x, label in zip((153, 251, 348, 445, 543), ('−0.4', '−0.2', '0.0', '0.2', '0.4')):
        ticks.append(f'M{x} 712v5')
        content.append(text(label, x, 733, 14, 'text-anchor="middle"'))
    for y, label in zip((696, 599, 502, 405, 307, 210, 112), ('−0.6', '−0.4', '−0.2', '0.0', '0.2', '0.4', '0.6')):
        ticks.append(f'M100 {y}h-5')
        content.append(text(label, 90, y + 5, 14, 'text-anchor="end"'))
    for y, label in zip((630, 516, 402, 287, 173), ('−0.3', '−0.2', '−0.1', '0.0', '0.1')):
        ticks.append(f'M658 {y}h5')
        content.append(text(label, 668, y + 5, 14))
    content.extend((
        f'<path d="{" ".join(ticks)}" fill="none" stroke="#080808"/>',
        text('4. SDF Slice (Y=0.00)', 348, 87, 17, 'text-anchor="middle"'),
        text('X-axis', 348, 752, 14, 'text-anchor="middle"'),
        text('Z-axis', 48, 405, 14, 'text-anchor="middle" transform="rotate(-90 48 405)"'),
        text('Signed Distance', 717, 405, 14, 'text-anchor="middle" transform="rotate(-90 717 405)"'),
    ))
    return group(SDF, ''.join(content))


PANELS_41 = (
    ('image', 'Image', 'An RGB image records the color and appearance of the scene at one instant.'),
    ('video', 'Video', 'A sequence of frames records how the scene changes over time.'),
    ('segmentation', 'Segmentation Map', 'Colors distinguish regions such as people, vehicles, roads, and buildings.'),
    ('depth', 'Depth Map', 'Each pixel encodes its distance from the camera.'),
    ('surface-normals', 'Surface Normal Map', 'Colors encode the direction perpendicular to each visible surface.'),
    ('edges', 'Edge Map', 'Bright contours trace changes in the image, including object boundaries.'),
    ('optical-flow', 'Optical Flow Map', 'Colors and arrows encode the apparent displacement of image pixels between frames.'),
    ('keypoints', 'Keypoints', 'Landmarks identify the joints of the body. Their connections show the estimated pose.'),
)
PANELS_42 = (
    ('rgb-d', 'RGB-D Image', 'An RGB-D image pairs appearance with a depth value at each pixel in the camera view.'),
    ('voxel', 'Voxel', 'A regular 3D grid represents the object through the occupancy of its cells.'),
    ('point-cloud', 'Point Cloud', 'A set of 3D points samples the surface of the teapot.'),
    ('mesh', 'Mesh', 'Connected vertices and faces describe the teapot as a continuous surface.'),
    ('sdf', 'SDF', 'A signed distance field gives the distance to the nearest surface, with the sign distinguishing interior from exterior. The black contour marks zero distance.'),
)


def zones(figure, descriptions, captions, boxes, assets, overlays, underlays):
    parts = []
    for (key, title, _), (x, y, right, bottom) in zip(descriptions, boxes):
        images = ''.join(image(figure, asset) for asset in assets if asset['panel'] == key)
        hit = rect(x, y, right-x, bottom-y, 'class="rl-hit" rx="3"')
        parts.append(f'<g class="rl-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(title)}">'
                     f'{underlays.get(key, "")}{images}{overlays.get(key, "")}{captions[key]}{hit}</g>')
    return ''.join(parts)


def figure_markup(figure, manifest):
    if figure == '41':
        descriptions, height, title = PANELS_41, 491.5, 'Two-dimensional representations'
        caption_positions = ((124.996, 74.126), (475.439, 68.923), (781.270, 226.675), (1189.833, 132.530),
                             (39.163, 247.895), (459.118, 117.950), (777.384, 209.965), (1187.452, 118.418))
        captions = labels(descriptions, caption_positions, (331.20,) * 4 + (673.96,) * 4, 27.927, ATLAS_SCALE)
        boxes = ((5, 4, 216, 238), (230, 4, 492, 238), (509, 4, 744, 238), (762, 4, 995, 238),
                 (5, 254, 226, 479), (254, 254, 478, 479), (509, 254, 738, 479), (762, 254, 995, 479))
        definitions = ('<defs><marker id="f41-arrowhead" markerWidth="2.3" markerHeight="2.2" refX="1.8" refY="1.1" '
                       'orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L2.3 1.1L0 2.2L.55 1.1Z" fill="#243b40" opacity=".84"/></marker></defs>')
        overlays = {'video': player_controls(), 'optical-flow': flow_marks(), 'keypoints': pose()}
        underlays = {'video': filmstrip()}
    else:
        descriptions, height, title = PANELS_42, 254, 'Three-dimensional representations'
        caption_positions = ((18.784, 37.816), (99.775, 14.940), (158.416, 31.021), (234.164, 14.339), (307.828, 11.836))
        captions = labels(descriptions, caption_positions, (83.893,) * 5, 6.453, 1000 / 354.96)
        boxes = ((2, 6, 204, 240), (208, 6, 395, 240), (400, 6, 581, 240), (582, 6, 785, 240), (793, 6, 978, 240))
        definitions, overlays, underlays = '', {'sdf': chart()}, {}
    panels = zones(figure, descriptions, captions, boxes, manifest['assets'], overlays, underlays)
    info = json.dumps({key: {'t': name, 'b': body} for key, name, body in descriptions}, ensure_ascii=False)
    return (f'<div class="nf nf-rl nf-f4142 nf-f{figure}" data-nf="f4142">'
            f'<svg class="nf-svg" viewBox="0 0 1000 {height}" xmlns="http://www.w3.org/2000/svg" '
            f'role="group" aria-label="{title}">{definitions}{panels}</svg>'
            f'<div class="nf-card" hidden aria-live="polite"></div><script class="nf-info" type="application/json">{info}</script></div>')


def comparison(figure, markup, original):
    dotted = f'{figure[0]}.{figure[1]}'
    return f'''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Figure {dotted} comparison</title>
<link rel="stylesheet" href="/assets/css/site.css">
<link rel="stylesheet" href="{STYLE}">
<style>
body{{margin:0;background:#f1f4f7;color:#263238;font:16px/1.5 system-ui,sans-serif}}
main{{max-width:1680px;margin:auto;padding:clamp(10px,2vw,28px)}}
h1{{margin:0 0 6px;font-size:clamp(20px,3vw,32px)}} nav{{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:20px}}
.comparison{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
section{{min-width:0;background:#fff;border:1px solid #dce3ec;border-radius:8px;padding:clamp(8px,1.2vw,18px)}}
section h2{{margin:0 0 12px;font:600 16px/1.4 system-ui,sans-serif}}
.original{{display:block;width:100%;height:auto}}
@media(max-width:900px){{.comparison{{grid-template-columns:minmax(0,1fr)}}}}
</style>
<main>
<h1>Figure {dotted} comparison</h1>
<nav aria-label="Figures"><a href="/example/figure41.html">Figure 4.1</a><a href="/example/figure42.html">Figure 4.2</a><a href="/example/figures41-42-assets.html">Assets</a></nav>
<div class="comparison">
<section><h2>Original</h2><img class="original" src="/{original}" alt="Original Figure {dotted}"></section>
<section><h2>Interactive redraw</h2>{markup}</section>
</div>
</main>
<script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=f4142-1'; mountNative();</script>
</html>
'''


def main():
    for figure in ('41', '42'):
        manifest = json.loads((FIGURES / f'figure{figure}/manifest.json').read_text())
        markup = figure_markup(figure, manifest)
        (ROOT / f'source/pipeline/native/figure{figure}.html').write_text(markup + '\n')
        (ROOT / f'example/figure{figure}.html').write_text(comparison(figure, markup, manifest['sources'][0]))


if __name__ == '__main__':
    main()
