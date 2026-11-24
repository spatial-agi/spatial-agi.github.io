"""Interactive reconstruction of Figure 6.19: example SLAM outputs."""
import json
from html import escape
from pathlib import Path


INFO = {
    "visual": {
        "t": "Real-time Visual SLAM",
        "b": "The left result combines a feature-tracked camera frame with a sparse map and the estimated camera trajectory. The loop-shaped path shows the system revisiting the mapped area.",
    },
    "lidar": {
        "t": "LiDAR SLAM",
        "b": "The right result shows a dense point-cloud map built from LiDAR observations. Its color gradient encodes range, while the inset shows the sensor's view along the mapped route.",
    },
}


def fig619():
    out = []
    add = out.append

    def image(name, x, y, width, height):
        add(f'<image href="/assets/img/figs/f619/{name}.png" x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="none"/>')

    def zone(key, x, y, width, height, title, draw):
        add(f'<g class="f619-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(title)}">')
        draw()
        add(f'<rect class="f619-hit" x="{x}" y="{y}" width="{width}" height="{height}"/>')
        add('</g>')

    add('<div class="nf nf-619" data-nf="619" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1125" role="group" aria-label="Figure 6.19: visual and LiDAR SLAM results"><rect width="2000" height="1125" fill="#fff"/>')

    def visual():
        image("visual-slam", 72, 56, 1107, 624)
        add('<text class="f619-panel-title" x="834" y="126" font-size="45" text-anchor="middle" textLength="548" lengthAdjust="spacingAndGlyphs">Real-time Visual SLAM</text>')
        add('<path class="f619-motion-route" d="M735 334 C773 357 774 413 769 456 C762 501 748 519 722 538 C666 580 622 603 572 616 C520 626 483 608 452 592 C416 569 397 523 379 476 C362 434 372 411 376 423 C389 392 443 384 497 386 C580 375 663 351 735 334"/>')

    def lidar():
        image("lidar-slam", 1261, 56, 620, 624)
        add('<text class="f619-panel-title" x="1715" y="126" font-size="45" text-anchor="middle" textLength="260" lengthAdjust="spacingAndGlyphs">LiDAR SLAM</text>')
        add('<path class="f619-motion-route" d="M1350 615 C1355 553 1350 451 1348 366 C1410 364 1475 370 1535 370 C1620 370 1690 370 1745 370 C1776 370 1807 360 1828 350"/>')

    zone("visual", 72, 56, 1107, 624, "Real-time Visual SLAM", visual)
    zone("lidar", 1261, 56, 620, 624, "LiDAR SLAM", lidar)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">' + json.dumps(INFO) + '</script></div>')
    return ''.join(out)


if __name__ == "__main__":
    site = Path(__file__).resolve().parents[2]
    source = site / "assets/figures/figures/part3/section6/slam.webp"
    (site / "example/figure619.html").write_text(
        '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure619-1"><title>Figure 6.19 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.19 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/slam.webp"><h2 id="redraw">Interactive reconstruction</h2>'''
        + fig619()
        + '''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure619-1';mountNative();</script></html>'''
    )
