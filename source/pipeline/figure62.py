"""Figure 6.2: four original segmentation panels with live labels and inspection."""
import html
import json
from pathlib import Path

INFO = {
    'raw': dict(t='Raw image', b='The input photograph shows three people standing at the shoreline. Each segmentation method operates on this shared scene.'),
    'semantic': dict(t='Semantic segmentation', b='Every pixel receives a semantic class. Pixels belonging to the same category share one label, regardless of instance identity.'),
    'instance': dict(t='Instance segmentation', b='Detected object instances receive separate masks. The boxes indicate the localized people, while colors distinguish their instances.'),
    'panoptic': dict(t='Panoptic segmentation', b='Panoptic segmentation combines semantic regions with distinct instance masks in one coherent pixel-level output.'),
}


def fig62():
    panels = [
        ('raw', 'Raw Image', 22, 308),
        ('semantic', 'Semantic Segmentation', 525, 308),
        ('instance', 'Instance Segmentation', 1042, 308),
        ('panoptic', 'Panoptic Segmentation', 1545, 308),
    ]
    out = ['<div class="nf nf-62" data-nf="62" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1126" role="group" aria-label="Figure 6.2: semantic, instance and panoptic segmentation on a shared scene">']
    for key, label, x, y in panels:
        out.append(f'<g class="f62-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{html.escape(INFO[key]["t"])}">')
        out.append(f'<rect class="f62-hit" x="{x}" y="{y}" width="437" height="282" rx="7" fill="transparent"/>')
        out.append(f'<image class="f62-panel" href="/assets/img/figs/f62/{key}.png" x="{x}" y="{y}" width="437" height="282"/>')
        out.append(f'<rect class="f62-border" x="{x}" y="{y}" width="437" height="282" rx="7" fill="none" stroke="#d4d8dc" stroke-width="1.3"/>')
        out.append(f'<text class="f62-label" x="{x+218.5}" y="650" text-anchor="middle">{html.escape(label)}</text>')
        out.append('</g>')
    out.append('<g class="f62-pulses" aria-hidden="true"></g></svg><div class="nf-card" hidden role="status"></div>')
    out.append('<script type="application/json" class="nf-info">'+json.dumps(INFO,ensure_ascii=False)+'</script></div>')
    return ''.join(out)


def preview():
    site=Path(__file__).resolve().parents[2]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css"><title>Figure 6.2 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1200px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:white}.nf{padding:0;border:0;border-radius:0}</style><main><h1>Figure 6.2 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/segmentation.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig62()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js';mountNative();</script></html>'''
    page=page.replace('/assets/css/site.css','/assets/css/site.css?v=figure62-1').replace('/assets/js/nfig.js','/assets/js/nfig.js?v=figure62-1')
    (site/'example/figure62.html').write_text(page)


if __name__=='__main__':
    preview()
