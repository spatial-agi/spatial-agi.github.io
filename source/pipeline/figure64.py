"""Figure 6.4: keypoint tasks and detector progression; preview before integration."""
import html
import json
from pathlib import Path

INFO = {
    'body': dict(t='Body pose', b='Body keypoints describe the locations and connections of human joints, forming a compact representation of posture and movement.'),
    'face': dict(t='Facial landmarks', b='Facial landmarks localize the eyes, eyebrows, nose, mouth and face outline. Their geometry supports alignment, expression analysis and tracking.'),
    'hand': dict(t='Hand and gesture', b='Hand landmarks connect the wrist and finger joints. Their relative positions capture articulated hand poses and gestures.'),
    'animal': dict(t='Animal and object keypoints', b='Keypoint definitions extend to animal joints and distinctive object locations, such as the corners and legs of a chair.'),
    'medical': dict(t='Medical and specialized landmarks', b='Anatomical landmarks provide reference locations for measurements and alignment. The skull illustrates a specialized landmark configuration.'),
    'classical': dict(t='Hand-crafted features', b='Harris, SIFT and FAST identify distinctive local image structures using designed response functions and descriptors.'),
    'heatmap': dict(t='Heatmap CNNs', b='Convolutional networks predict spatial heatmaps whose peaks indicate keypoint locations. CPM, Hourglass and HRNet are representative architectures.'),
    'transformer': dict(t='Transformer and foundation models', b='Multi-head self-attention connects information across image regions. ViTPose and Sapiens illustrate transformer-based and large pretrained pose models.'),
    'realtime': dict(t='Real-time pose detection', b='OpenPose, RTMPose and RTMO illustrate efficient pose estimation. The dashed bidirectional links depict relationships between the illustrated joint configurations.'),
    'generative': dict(t='Generative pose models', b='Generative approaches model plausible keypoint configurations. The noise-to-pose illustration shows the progression from a noise sample to a structured pose, as in DiffPose.'),
}


def text(x, y, value, size=28, cls='f64-text'):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{html.escape(value)}</text>'


def fig64(asset_root='/assets/img/figs/f64'):
    manifest = json.loads((Path(__file__).resolve().parents[2] / 'assets/figures/elements/figure64/manifest.json').read_text())
    assets = {a['file']: a for a in manifest['assets']}
    def art(name):
        a = assets[name]
        x, y, _, _ = a['source_box']
        w, h = a['size']
        return f'<image class="f64-art" href="{asset_root}/{name}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def zone(key):
        return f'<g class="f64-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(INFO[key]["t"])}">'
    def hit(x, y, w, h):
        return f'<rect class="f64-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="transparent"/></g>'
    out = ['<div class="nf nf-64" data-nf="64" data-pagefind-ignore="all">', '<svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1126" role="group" aria-label="Figure 6.4: keypoint and landmark detection tasks and methodological progression">',
        '<defs><marker id="f64-blue-arrow" markerWidth="35" markerHeight="43" refX="32" refY="21.5" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L35 21.5L0 43Z" fill="#235b94"/></marker><marker id="f64-small-blue" markerWidth="17" markerHeight="24" refX="15" refY="12" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L17 12L0 24Z" fill="#235b94"/></marker><marker id="f64-black-arrow" markerWidth="11" markerHeight="11" refX="9" refY="5.5" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0L11 5.5L0 11Z" fill="#111"/></marker><marker id="f64-math-arrow" markerWidth="17" markerHeight="18" refX="15" refY="9" markerUnits="userSpaceOnUse" orient="auto"><path d="M1 1L15 9L1 17" fill="none" stroke="#111" stroke-width="2.5"/></marker></defs>',
        '<rect class="f64-task-frame" x="83" y="86" width="1833" height="454" rx="11"/>']
    for x in [406, 771, 1152, 1546]:
        out.append(f'<path class="f64-divider" d="M{x} 104V521"/>')
    top = [('body', 83, 323, 242, 'Body Pose', ['body-pose']), ('face', 406, 365, 581, 'Facial Landmark', ['facial-landmarks']), ('hand', 771, 381, 960, 'Hand / Gesture', ['hand-gesture']), ('animal', 1152, 394, 1351, 'Animal & Object', ['animal-pose', 'object-chair']), ('medical', 1546, 370, 1734, 'Medical / Specialized', ['medical-skull'])]
    for key, x, w, cx, label, names in top:
        out.append(zone(key))
        if key == 'animal':
            out.append('<rect class="f64-inset" x="1393" y="109" width="125" height="170" rx="11"/>')
        out.extend(art('tasks/' + name + '.png') for name in names)
        if key == 'medical':
            for lx, ly, label0 in [(1770,142,'S'),(1828,226,'N'),(1838,269,'Or'),(1834,324,'A'),(1852,356,'ANS'),(1828,411,'B'),(1833,442,'Pog'),(1690,425,'Go')]:
                out.append(text(lx, ly, label0, 20))
        out.extend([text(cx, 512, label), hit(x+3, 94, w-6, 438)])
    panels = [('classical',111,273,247),('heatmap',447,302,598),('transformer',820,282,961),('realtime',1173,309,1327),('generative',1545,326,1708)]
    for key, x, w, cx in panels:
        out.extend([zone(key), f'<rect class="f64-panel" x="{x}" y="592" width="{w}" height="288" rx="22"/>'])
        if key == 'classical':
            out.extend(['<rect class="f64-image-frame" x="162" y="633" width="171" height="122"/>',art('methods/handcrafted-image.png')])
            for sx in [153,324]:
                for sy in [624,746]:
                    out.append(f'<rect class="f64-corner" x="{sx}" y="{sy}" width="18" height="18"/>')
            out.extend([text(cx,820,'Hand-crafted'),text(cx,855,'Features')])
        elif key == 'heatmap':
            for bx, by, bw, bh in [(479,633,19,137),(498,644,19,115),(517,654,19,95),(536,664,15,76),(663,664,18,76),(681,649,19,106),(700,633,20,137)]:
                out.append(f'<rect class="f64-feature" x="{bx}" y="{by}" width="{bw}" height="{bh}"/>')
            out.extend([art('methods/heatmap.png'),text(cx,840,'Heatmap CNNs')])
        elif key == 'transformer':
            for y in [635,680,725]:
                out.extend([f'<rect class="f64-block" x="869" y="{y}" width="179" height="38" rx="6"/>',text(958,y+27,'MHSA Block',21)])
            for y in [608,616,624,773,780,787]:
                out.append(f'<circle class="f64-ellipsis" cx="958" cy="{y}" r="1.9"/>')
            out.extend([text(cx,822,'Transformer &'),text(cx,857,'Foundation')])
        elif key == 'realtime':
            out.extend([art('methods/realtime-pose-left.png'),art('methods/realtime-pose-right.png')])
            for route in ['M1273 650Q1325 613 1378 650','M1284 689Q1325 669 1368 686','M1274 730Q1325 705 1378 730']:
                out.append(f'<path class="f64-arrow f64-dashed" d="{route}" marker-start="url(#f64-black-arrow)" marker-end="url(#f64-black-arrow)"/>')
            out.append(text(cx,841,'Real-time'))
        else:
            out.extend([art('methods/generative-noise.png'),art('methods/generative-pose.png'),'<path class="f64-arrow f64-denoise" d="M1687 697H1743" marker-end="url(#f64-small-blue)"/>',text(1644,808,'ϵ',43,'f64-math'),'<path class="f64-arrow f64-formula-arrow" d="M1678 798H1720" marker-end="url(#f64-math-arrow)"/>',text(1761,808,'x',43,'f64-math'),text(cx,857,'Generative')])
        out.append(hit(x,592,w,288))
    for x in [241,594,958,1324,1707]:
        out.append(f'<path class="f64-stem" d="M{x} 880V927"/>')
    out.append('<path class="f64-timeline" d="M94 927H1910" marker-end="url(#f64-blue-arrow)"/>')
    for x, label in [(241,'Harris / SIFT / FAST'),(594,'CPM / Hourglass / HRNet'),(958,'ViTPose / Sapiens'),(1324,'OpenPose / RTMPose / RTMO'),(1707,'DiffPose')]:
        out.extend([f'<circle class="f64-node" cx="{x}" cy="927" r="11"/>',text(x,986,label)])
    out.extend([text(1000,1060,'Methodological Progression',44,'f64-heading'),'<circle class="f64-timeline-pulse" r="6" opacity="0" aria-hidden="true"/></svg><div class="nf-card" hidden role="status"></div>','<script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>'])
    return ''.join(out)


def preview():
    site = Path(__file__).resolve().parents[2]
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure64-1"><title>Figure 6.4 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1400px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:white}.nf{padding:0;border:0;border-radius:0}@media(max-width:600px){body{padding:8px}}</style><main><h1>Figure 6.4 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/keypoint_detection_v2.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig64()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure64-1';mountNative();</script></html>'''
    (site / 'example/figure64.html').write_text(page)


if __name__ == '__main__':
    preview()
