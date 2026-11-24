"""Figure 6.3: segmentation methods, reconstructed as an interactive SVG."""
import html
import json
from pathlib import Path

INFO = {
    'pre': dict(t='Pre-deep-learning methods', b='Before learned feature hierarchies, segmentation relied on hand-designed boundaries and regions. Active contours, graph cuts and conditional random fields remain influential ideas.'),
    'fcn': dict(t='Fully convolutional networks', b='Fully convolutional networks replace dense classification layers with spatial prediction maps. U-Net, SegNet and PSPNet develop encoder-decoder or multi-scale variants.'),
    'dilated': dict(t='Dilated and multi-scale context', b='Dilated convolutions enlarge the receptive field without reducing feature-map resolution. DeepLab introduced this approach across multiple atrous rates.'),
    'region': dict(t='Region-based set prediction', b='Query-based models predict a set of masks from image features. Mask R-CNN, MaskFormer and Mask2Former represent this transition.'),
    'foundation': dict(t='Foundation and promptable models', b='Promptable segmentation models accept points, boxes or image prompts and return masks. SAM, SAM 2, X-Decoder and OMGSeg illustrate this family.'),
}

PANELS = [
    ('pre', 'Pre-Deep Learning', 18, 20, 388, 328),
    ('fcn', 'Fully Convolutional Networks', 426, 20, 342, 328),
    ('dilated', 'Dilated and Multi-Scale Context', 790, 20, 351, 328),
    ('region', 'Region-Based + Set-prediction', 1163, 20, 356, 328),
    ('foundation', 'Foundation / Promptable', 1542, 20, 435, 328),
]


def _text(x, y, value, size=25, anchor='middle', cls='f63-text'):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{html.escape(value)}</text>'


def fig63(asset_root='/assets/img/figs/f63'):
    out = [
        '<div class="nf nf-63" data-nf="63" data-pagefind-ignore="all">',
        '<svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 522" role="group" aria-label="Figure 6.3: methodological progression of image and video segmentation">',
        '<defs><marker id="f63-arrow" markerWidth="34" markerHeight="38" refX="30" refY="19" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L34 19L0 38Z" fill="#174f9d"/></marker><marker id="f63-black-arrow" markerWidth="14" markerHeight="12" refX="12" refY="6" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0L14 6L0 12L4 6Z" fill="#111"/></marker></defs>',
    ]
    anchors = [205, 587, 960, 1335, 1747]
    for i, (key, title, x, y, w, h) in enumerate(PANELS):
        out.append(f'<g class="f63-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(INFO[key]["t"])}">')
        out.append(f'<rect class="f63-panel" x="{x}" y="{y}" width="{w}" height="{h}" rx="22"/>')
        if key == 'pre':
            out.append(f'<image href="{asset_root}/classical-snake.png" x="40" y="42" width="195" height="205" preserveAspectRatio="xMidYMid meet"/>')
            out.append(f'<image href="{asset_root}/graph-cuts.png" x="267" y="67" width="116" height="164" preserveAspectRatio="xMidYMid meet"/>')
        elif key == 'fcn':
            # Encoder-decoder feature maps, links and arrows are independent SVG primitives.
            blocks = [(445, 67, 15, 188), (464, 82, 15, 158), (482, 120, 15, 119), (500, 135, 15, 97), (518, 162, 15, 64), (536, 175, 15, 45), (575, 194, 30, 14), (630, 175, 15, 45), (648, 162, 15, 64), (666, 135, 15, 97), (684, 120, 15, 119), (702, 82, 15, 158), (720, 67, 15, 188)]
            for bx, by, bw, bh in blocks:
                out.append(f'<rect class="f63-feature" x="{bx}" y="{by}" width="{bw}" height="{bh}"/>')
            out.append('<path class="f63-connector" d="M551 201H575M605 201H630"/>')
            for start, end, y in [(489, 688, 91), (525, 652, 142)]:
                out.append(f'<path class="f63-arrow f63-flow-route" d="M{start} {y}H{end}" marker-end="url(#f63-black-arrow)"/>')
        elif key == 'dilated':
            out.append(f'<image href="{asset_root}/dilated-context.png" x="801" y="112" width="325" height="139" preserveAspectRatio="xMidYMid meet"/>')
            out.extend([_text(858, 99, 'rate = 1', 19), _text(965, 99, 'rate = 2', 19), _text(1083, 99, 'rate = 4', 19)])
        elif key == 'region':
            out.extend([_text(1230, 67, 'queries', 18), _text(1505, 64, 'predicted masks', 18, 'end')])
            out.append(f'<image href="{asset_root}/region-queries.png" x="1178" y="78" width="111" height="36" preserveAspectRatio="xMinYMid meet"/>')
            out.append(_text(1313, 104, '…', 27))
            out.append('<rect class="f63-box" x="1185" y="144" width="175" height="71" rx="13"/>')
            out.extend([_text(1272, 174, 'Transformer', 20, cls='f63-box-text'), _text(1272, 200, 'Encoder–Decoder', 20, cls='f63-box-text')])
            out.append('<path class="f63-arrow" d="M1224 114V140" marker-end="url(#f63-black-arrow)"/>')
            for starty, endy, delay in [(170, 94, 0), (179, 145, 180), (188, 192, 360), (198, 244, 540)]:
                out.append(f'<path class="f63-arrow f63-flow-route" data-delay="{delay}" d="M1360 {starty}L1436 {endy}" marker-start="url(#f63-black-arrow)" marker-end="url(#f63-black-arrow)"/>')
            out.append(f'<image href="{asset_root}/region-predicted-masks.png" x="1428" y="67" width="62" height="200" preserveAspectRatio="xMidYMid meet"/>')
        elif key == 'foundation':
            out.extend([_text(1588, 83, 'prompt', 18, 'start'), _text(1588, 188, 'image', 18, 'start')])
            out.append(f'<image href="{asset_root}/foundation-prompt.png" x="1560" y="94" width="58" height="53" preserveAspectRatio="xMidYMid meet"/>')
            out.append(f'<image href="{asset_root}/foundation-input-image.png" x="1558" y="194" width="77" height="73" preserveAspectRatio="xMidYMid meet"/>')
            out.append('<rect class="f63-box f63-foundation-box" x="1666" y="98" width="146" height="164" rx="22"/>')
            out.extend([_text(1739, 158, 'Segmentation', 19, cls='f63-box-text'), _text(1739, 187, 'Foundation', 19, cls='f63-box-text'), _text(1739, 216, 'Model', 19, cls='f63-box-text')])
            for route in ['M1623 121L1660 137', 'M1630 227L1660 215', 'M1816 179H1860']:
                out.append(f'<path class="f63-arrow" d="{route}" marker-end="url(#f63-black-arrow)"/>')
            out.append(f'<image href="{asset_root}/foundation-output-mask.png" x="1868" y="136" width="91" height="84" preserveAspectRatio="xMidYMid meet"/>')
        title_fit = f' textLength="{w - 24}" lengthAdjust="spacingAndGlyphs"' if key == 'region' else ''
        out.append(f'<text class="f63-title" x="{x + w / 2:g}" y="324" text-anchor="middle"{title_fit}>{html.escape(title)}</text>')
        out.append(f'<rect class="f63-hit" x="{x}" y="{y}" width="{w}" height="h" rx="22"/>'.replace('height="h"', f'height="{h}"'))
        out.append('</g>')
    out.append('<path class="f63-stem" d="M205 348V385M587 348V385M960 348V385M1335 348V385M1747 348V385"/>')
    out.append('<path class="f63-timeline" d="M20 386H1954" marker-end="url(#f63-arrow)"/>')
    for x in anchors:
        out.append(f'<circle class="f63-node" cx="{x}" cy="386" r="12"/>')
    methods = [
        ('Thresholding /', 'Watershed / Snakes /', 'Graph Cuts / CRF'),
        ('FCN / U-Net / SegNet /', 'PSPNet'),
        ('DeepLab v1 / v2', '/ v3 / v3+'),
        ('Mask R-CNN /', 'MaskFormer /', 'Mask2Former / K-Net'),
        ('SAM / SAM 2 / X-Decoder', '/ OMGSeg'),
    ]
    for x, lines in zip(anchors, methods):
        out.append(f'<text class="f63-method" x="{x}" y="{428 if len(lines) == 2 else 420}" text-anchor="middle">')
        for i, line in enumerate(lines):
            out.append(f'<tspan x="{x}" dy="{0 if i == 0 else 32}">{html.escape(line)}</tspan>')
        out.append('</text>')
    out.append('<circle class="f63-pulse" r="7" aria-hidden="true"/><g class="f63-pulses" aria-hidden="true"></g></svg><div class="nf-card" hidden role="status"></div>')
    out.append('<script type="application/json" class="nf-info">' + json.dumps(INFO, ensure_ascii=False) + '</script></div>')
    return ''.join(out)


def preview():
    site = Path(__file__).resolve().parents[2]
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure63-7"><title>Figure 6.3 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1400px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:white}.nf{padding:0;border:0;border-radius:0}</style><main><h1>Figure 6.3 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/segmentation-method.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig63() + '''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure63-7';mountNative();</script></html>'''
    (site / 'example/figure63.html').write_text(page)


if __name__ == '__main__':
    preview()
