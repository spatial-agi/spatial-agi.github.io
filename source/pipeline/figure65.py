"""Figure 6.5: scene classification, assembled from approved artwork and SVG."""
import html
import json
from pathlib import Path

INFO = {
    'single': dict(t='Single-label classification', b='Assign one scene category to the whole image. Here, the kitchen photograph receives the label “kitchen”.'),
    'multi': dict(t='Multi-label classification', b='Describe several aspects of one scene with multiple labels. The example combines a place, an indoor setting and a time-of-day attribute.'),
    'domain': dict(t='Domain-specific classification', b='Scene categories depend on the application domain, illustrated by farmland, highways, forests and animal imagery.'),
    'caption': dict(t='Compositional output', b='Scene captioning produces a description that combines objects, attributes and context into a natural-language sentence.'),
    'handcrafted': dict(t='Hand-crafted descriptions', b='GIST, bag-of-visual-words and spatial pyramid matching aggregate designed image descriptors. Spatial partitions retain coarse scene layout.'),
    'cnn': dict(t='Deep CNN', b='AlexNet, VGG and ResNet learn increasingly abstract image features through successive convolutional stages, supporting whole-scene recognition.'),
    'transformer': dict(t='Vision transformer', b='A transformer encoder connects image patch tokens through attention. ViT and CLIP illustrate this family of scene representations.'),
    'graph': dict(t='Structured scene representation', b='Objects and their relationships make scene layout explicit. Multi-scale feature networks and graph convolutional networks support structure-aware scene classification.'),
    'llm': dict(t='Multimodal large language model', b='A vision encoder supplies image tokens alongside text tokens to a language model. Models such as LLaVA and Qwen-VL generate scene labels and descriptions.'),
}


def label(x, y, value, size=30, cls='f65-text', anchor='middle'):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{html.escape(value)}</text>'


def fig65(asset_root='/assets/img/figs/f65'):
    site = Path(__file__).resolve().parents[2]
    assets = {a['file']: a for a in json.loads((site/'assets/figures/elements/figure65/manifest.json').read_text())['assets']}
    def art(name):
        a=assets[name]; x,y,_,_=a['source_box']; w,h=a['size']
        return f'<image class="f65-art" href="{asset_root}/{name}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    def begin(key):
        return f'<g class="f65-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(INFO[key]["t"])}">'
    def end(x,y,w,h):
        return f'<rect class="f65-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="19" fill="transparent"/></g>'
    def tag(x,y,w,text):
        return f'<rect class="f65-tag" x="{x}" y="{y}" width="{w}" height="58" rx="14"/>'+label(x+w/2,y+39,text,30,'f65-blue')
    def arrow(d):
        return f'<path class="f65-arrow f65-route" d="{d}" marker-end="url(#f65-arrowhead)"/>'
    out=['<div class="nf nf-65" data-nf="65" data-pagefind-ignore="all">','<svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 976" role="group" aria-label="Figure 6.5: scene classification tasks and methodological progression">',
         '<defs><marker id="f65-arrowhead" markerWidth="8" markerHeight="7" refX="7" refY="3.5" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L8 3.5L0 7L2 3.5Z" fill="#111"/></marker><marker id="f65-timeline-head" markerWidth="23" markerHeight="23" refX="21" refY="11.5" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L23 11.5L0 23L5 11.5Z" fill="#0647f4"/></marker></defs>',
         '<rect class="f65-frame" x="1" y="1" width="1978" height="526" rx="17"/>']
    for x in [445,912,1502]:
        out.append(f'<path class="f65-divider" d="M{x} 27V492"/>')
    out.extend([begin('single'),art('tasks/single-label-kitchen.png'),tag(122,333,156,'kitchen'),label(216,485,'Single-label Classification',30,'f65-title'),end(3,3,440,522)])
    out.extend([begin('multi'),art('tasks/multi-label-kitchen.png'),tag(475,336,114,'kitchen'),tag(615,336,114,'indoor'),tag(757,336,139,'morning'),label(690,481,'Multi-label Classification',30,'f65-title'),end(447,3,463,522)])
    out.append(begin('domain'))
    for name,x,y,caption in [('farmland',1068,223,'farmland'),('highway',1360,223,'highway'),('forest',1068,434,'forest'),('animal',1360,434,'animal')]:
        out.extend([art('tasks/'+name+'.png'),label(x,y,caption,30,'f65-blue')])
    out.extend([label(1209,482,'Domain-specific classification',30,'f65-title'),end(914,3,586,522)])
    out.extend([begin('caption'),art('tasks/caption-kitchen.png'),'<rect class="f65-tag" x="1517" y="304" width="439" height="126" rx="17"/>'])
    for y,s in [(339,'A modern kitchen with marble'),(377,'countertops and morning light'),(416,'streaming through the window.')]:
        out.append(label(1736,y,s,30,'f65-blue'))
    out.extend([label(1736,465,'Compositional Output',30,'f65-title'),label(1736,505,'(Scene Captioning)',30,'f65-title'),end(1504,3,473,522)])
    panels=[('handcrafted',1,315,158),('cnn',384,316,542),('transformer',768,377,956),('graph',1213,325,1375),('llm',1606,373,1792)]
    for key,x,w,cx in panels:
        out.extend([begin(key),f'<rect class="f65-frame f65-panel" x="{x}" y="551" width="{w}" height="322" rx="20"/>'])
        if key=='handcrafted':
            out.extend([art('methods/handcrafted-background.png'),'<rect class="f65-grid" x="29" y="590" width="252" height="188"/>'])
            for d in ['M85 590V681','M162 590V681','M239 590V681','M29 681H281','M106 681V735','M183 681V735','M29 735H281','M125 735V778','M203 735V778','M129 659H196V702H129Z','M151 668H176V692H151Z']:
                out.append(f'<path class="f65-grid" d="{d}"/>')
            out.extend(['<rect class="f65-scan" x="30" y="591" width="249" height="3" opacity="0"/>',label(cx,822,'Hand-crafted'),label(cx,860,'descriptions')])
        elif key=='cnn':
            for bx,by,bw,bh,dx,dy in [(401,657,31,122,54,-53),(486,700,32,78,53,-53),(572,715,19,55,32,-33)]:
                out.append(f'<path class="f65-cuboid" d="M{bx} {by}v{bh}h{bw}v-{bh}Z M{bx} {by}l{dx} {dy}h{bw}l-{dx} {-dy} M{bx+bw} {by+bh}l{dx} {dy}v-{bh} M{bx+bw+dx} {by+dy}v{bh}"/>')
            out.extend([arrow('M456 672H499'),arrow('M546 700H583'),arrow('M604 724H648'),label(671,730,'…',30),label(cx,841,'Deep CNN')])
        elif key=='transformer':
            for tx in [790,848,906,964,1022,1081]:
                out.append(f'<rect class="f65-token" x="{tx}" y="609" width="46" height="45" rx="8"/>')
            out.extend(['<rect class="f65-box" x="790" y="686" width="337" height="80" rx="13"/>',label(958,735,'Transformer Encoder',27),label(cx,841,'Vision Transformer')])
        elif key=='graph':
            out.extend([art('methods/scene-graph-background.png'),'<rect class="f65-grid" x="1251" y="591" width="252" height="188"/>'])
            nodes=[(1323,640),(1421,640),(1366,713),(1288,738),(1434,741)]
            for a,b in [(0,1),(0,2),(0,3),(1,2),(1,4),(2,3),(2,4)]:
                ax,ay=nodes[a];bx,by=nodes[b]
                out.append(f'<path class="f65-link f65-route" d="M{ax} {ay}L{bx} {by}"/>')
            for nx,ny in nodes:
                out.append(f'<circle class="f65-graph-node" cx="{nx}" cy="{ny}" r="12.5"/>')
            for nx,ny,s in [(1305,619,'table'),(1429,623,'window'),(1370,679,'counter'),(1321,769,'stove'),(1458,765,'oven')]:
                out.append(label(nx,ny,s,20))
            out.append(label(cx,841,'Structure Scene'))
        else:
            out.extend(['<rect class="f65-box f65-vision" x="1627" y="582" width="162" height="73" rx="13"/>',label(1708,610,'Vision',27),label(1708,642,'Encoder',27),label(1880,643,'Text',27)])
            for i,tx in enumerate([1628,1686,1744,1801,1859,1917]):
                out.append(f'<rect class="f65-token {"f65-vision" if i<3 else ""}" x="{tx}" y="658" width="46" height="44" rx="8"/>')
            out.extend(['<rect class="f65-box" x="1627" y="708" width="336" height="80" rx="13"/>',label(1795,757,'Large Language Model',27),label(cx,841,'Multimodal LLM')])
        out.append(end(x,551,w,322))
    out.append('<path class="f65-timeline" d="M1 906H1975" marker-end="url(#f65-timeline-head)"/>')
    for x,s in [(150,'GIST / BoVW / SPM'),(549,'AlexNet / VGG / ResNet'),(958,'ViT / CLIP'),(1383,'FPN / GCN'),(1810,'LLaVA / Qwen-VL')]:
        out.extend([f'<circle class="f65-node" cx="{x}" cy="905" r="9"/>',label(x,948,s)])
    out.extend(['<circle class="f65-timeline-pulse" r="5" opacity="0" aria-hidden="true"/></svg><div class="nf-card" hidden role="status"></div>','<script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>'])
    return ''.join(out)


def preview():
    site=Path(__file__).resolve().parents[2]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure65-1"><title>Figure 6.5 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1400px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:white}.nf{padding:0;border:0;border-radius:0}@media(max-width:600px){body{padding:8px}}</style><main><h1>Figure 6.5 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/scene_classification.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig65()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure65-1';mountNative();</script></html>'''
    (site/'example/figure65.html').write_text(page)


if __name__=='__main__':
    preview()
