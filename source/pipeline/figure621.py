"""Interactive reconstruction of Figure 6.21: image-based scene flow."""
import json
from html import escape
from pathlib import Path

INFO = {
    'single': {'t': 'Single-image ambiguity', 'b': 'A single image reveals appearance and layout, but cannot determine whether apparent displacement comes from object motion, camera motion, or depth. Scene flow needs additional geometric or temporal cues.'},
    'stereo': {'t': 'Stereo depth cues', 'b': 'A calibrated stereo pair provides disparity and depth cues. A second time step is still required to recover 3D motion.'},
    'mono': {'t': 'Monocular video', 'b': 'Monocular scene-flow methods track image motion over time and combine it with estimated depth or geometric priors.'},
    'multiview': {'t': 'Multi-view video', 'b': 'A synchronized multi-view rig adds spatial geometry to temporal observations, constraining 3D motion from several viewpoints.'},
    'supervision': {'t': 'Supervision signals', 'b': 'Training signals range from synthetic ground-truth flow to photometric and geometric consistency, and view-synthesis objectives.'},
    'variational': {'t': 'Variational and piecewise-rigid methods', 'b': 'Classical formulations minimize a motion energy. Piecewise-rigid scene flow segments the scene into patches with locally rigid motion.'},
    'cnn': {'t': 'Stereo and temporal CNNs', 'b': 'End-to-end stereo and temporal networks jointly predict dense scene-flow quantities. DispNet and SENSE are representative systems.'},
    'recurrent': {'t': 'Recurrent SE(3) refinement', 'b': 'A recurrent update block refines pixelwise rigid motion using stereo-derived or RGB-D depth and image pairs. RAFT-3D is a representative method.'},
    'self': {'t': 'Monocular self-supervision', 'b': 'The predicted motion warps one frame into another. Photometric and geometric losses train scene flow without dense motion labels.'},
    'fields': {'t': 'Motion fields and view synthesis', 'b': 'Dynamic radiance fields model 4D deformation and synthesize views over time. The diagram relates scene flow to dynamic 4D reconstruction.'},
}


def fig621():
    out=[]; add=out.append
    def text(x,y,s,size=29,cls='text',anchor='middle'):
        add(f'<text class="f621-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{s}</text>')
    def path(d,cls='ink',arrow=False,flow=False):
        add(f'<path class="f621-{cls}{" f621-route" if flow else ""}" d="{d}"'+(f' marker-end="url(#f621-{"ink-arrow" if cls == "ink" else "arrow"})"' if arrow else '')+'/>')
    def rect(x,y,w,h,cls='outline',rx=0):
        add(f'<rect class="f621-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
    def circle(x,y,r,cls='point'):
        add(f'<circle class="f621-{cls}" cx="{x}" cy="{y}" r="{r}"/>')
    def image(name,x,y,w,h):
        add(f'<image href="/assets/img/figs/f621/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
    def zone(k,x,y,w,h,draw):
        add(f'<g class="f621-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">'); draw(); rect(x,y,w,h,'hit'); add('</g>')
    add('<div class="nf nf-621" data-nf="621" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1077" role="group" aria-label="Figure 6.21: image-based scene flow estimation"><defs><marker id="f621-arrow" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="11" refY="7.5" orient="auto"><path d="M2 2.5L11 7.5L2 12.5" fill="none" stroke="#4146eb" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker><marker id="f621-ink-arrow" markerWidth="15" markerHeight="15" markerUnits="userSpaceOnUse" refX="11" refY="7.5" orient="auto"><path d="M2 2.5L11 7.5L2 12.5" fill="none" stroke="#2c363d" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="2000" height="1077" fill="white"/>')
    add('<g class="f621-scaffold">')
    for x in [388,808,1203,1597]: path(f'M{x} 34V274','divider')
    path('M16 305H1980','rule'); path('M24 1000H1978','rule')
    path('M400 329V979M797 329V979M1197 329V979M1597 329V979','divider')
    text(790,1050,'Image-based scene-flow estimation',32)
    text(1800,1050,'Related 4D reconstruction',32)
    add('</g>')

    def top_single():
        text(194,64,'Single image',39,'title'); image('single-image/frame',30,98,202,110)
        text(297,169,'?',66,'question'); text(194,270,'Motion is ambiguous',31,'red')
    def top_stereo():
        text(598,64,'Stereo pair',39,'title')
        text(506,98,'I<tspan baseline-shift="sub" font-size="21">L</tspan>',35,'math'); text(694,98,'I<tspan baseline-shift="sub" font-size="21">R</tspan>',35,'math')
        image('stereo/left',424,106,160,96); image('stereo/right',614,106,160,96)
        rect(488,149,38,28,'bbox'); rect(678,149,38,28,'bbox')
        text(598,270,'Depth cues; time still needed',29,'blue-text')
    def top_mono():
        text(1004,64,'Monocular video',39,'title')
        text(908,98,'t<tspan baseline-shift="sub" font-size="21">0</tspan>',32,'math'); text(1100,98,'t<tspan baseline-shift="sub" font-size="21">1</tspan>',32,'math')
        image('monocular-video/t0',844,106,132,96); image('monocular-video/t1',1038,106,132,96)
        rect(899,149,35,28,'bbox'); rect(1093,149,35,28,'bbox')
        path('M989 178H1025','blue',True,True)
        text(1004,270,'Track motion across time',29,'blue-text')
    def top_multi():
        text(1400,64,'Multi-view video',39,'title')
        for name,x,y in [('view-01',1238,88),('view-02',1414,88),('view-03',1238,162),('view-04',1414,162)]: image(f'multi-view/{name}',x,y,138,61)
        text(1400,270,'Time + spatial geometry',29,'blue-text')
    def top_supervision():
        text(1795,64,'Supervision',39,'title')
        text(1795,132,'Synthetic ground truth',30); text(1795,184,'Photo / geometry',30); text(1795,236,'View synthesis',30)
    for args in [('single',0,24,388,276,top_single),('stereo',389,24,419,276,top_stereo),('mono',809,24,394,276,top_mono),('multiview',1204,24,393,276,top_multi),('supervision',1598,24,390,276,top_supervision)]: zone(*args)

    def bottom_variational():
        text(200,373,'(1) Variational /',35,'title'); text(200,409,'piecewise-rigid',35,'title')
        # Energy curve and axes with a highlighted descent into its minimum.
        path('M54 609H344','ink',True); path('M61 464C110 559 150 600 200 600C250 600 290 559 339 464','curve')
        path('M199 600V469','ink',True); path('M156 583Q178 596 199 600Q219 596 243 582','energy')
        path('M64 469C112 560 151 600 199 600','descent',flow=True); circle(199,600,10,'minimum'); text(244,463,'E',31,'math')
        text(200,666,'Minimize',31,'blue-text'); text(200,697,'motion energy',31,'blue-text')
        text(200,769,'Vedula · Wedel',30); text(200,832,'Huguet & Devernay',30); text(200,894,'Vogel PRSF',34,'title'); text(200,954,'Basha (multi-view)',30)
    def bottom_cnn():
        text(598,373,'(2) Stereo +',35,'title'); text(598,409,'temporal CNNs',35,'title')
        for x,y,h,blue in [(457,492,130,False),(507,503,109,True),(557,515,84,False),(606,532,52,False)]: rect(x,y,32,h,'feature-blue' if blue else 'feature')
        path('M654 560H708','blue',True,True); rect(717,502,57,117,'output')
        for y in [529,558,587]: path(f'M729 {y}l28 -8','flow',True,True)
        text(598,665,'Joint dense',31,'blue-text'); text(598,697,'prediction',31,'blue-text')
        rect(428,715,344,101,'method',12); text(600,777,'DispNet / SENSE',35,'title')
        text(600,877,'Deep Rigid Instance',29); text(600,946,'FlyingThings3D data',29,'muted')
    def bottom_recurrent():
        text(997,373,'(3) Recurrent',35,'title'); text(997,409,'SE(3) refinement',35,'title')
        rect(847,504,143,90,'module',10); text(918,558,'GRU',38,'title')
        rect(1050,504,116,90,'transform',10); text(1108,558,'T<tspan baseline-shift="super" font-size="21">k+1</tspan>',34,'math-blue')
        path('M992 548H1038','blue',True,True)
        path('M1108 498V462H916V490','blue',True,True)
        text(997,665,'Refine pixelwise',31,'blue-text'); text(997,697,'rigid motion',31,'blue-text')
        rect(859,715,282,101,'method',12); text(1000,777,'RAFT-3D',36,'title')
        text(997,877,'Stereo-derived / RGB-D',28); text(997,946,'Depth + image pairs',29)
    def bottom_self():
        text(1397,373,'(4) Monocular /',35,'title'); text(1397,409,'self-supervised',35,'title')
        text(1397,472,'warp + compare',30,'blue-text')
        image('self-supervised/next-frame',1249,507,105,95); image('self-supervised/current-frame',1458,507,105,95)
        rect(1284,536,30,25,'bbox'); rect(1493,536,30,25,'bbox')
        path('M1363 557H1441','blue',True,True)
        text(1302,633,'I<tspan baseline-shift="sub" font-size="20">t+1</tspan>',33,'math'); text(1510,633,'I<tspan baseline-shift="sub" font-size="20">t</tspan>',33,'math')
        text(1397,683,'Photo + geometry loss',30,'blue-text')
        rect(1228,715,344,101,'method',12); text(1400,777,'Self-Mono-SF',35,'title')
        text(1397,877,'Mono-SF',29); text(1397,946,'Depth prior + geometry',29)
    def bottom_fields():
        text(1798,373,'(5) Motion fields +',35,'title'); text(1798,409,'view synthesis',35,'title')
        # Two animated point-flow tracks, with depth-separated gray source points.
        for x,y in [(1661,545),(1718,517),(1662,612),(1719,594)]: circle(x,y,8,'gray-point')
        path('M1671 543L1803 518','field',True,True); path('M1728 517L1858 526','field',True,True)
        path('M1672 611L1825 600','field',True,True); path('M1728 594L1862 585','field',True,True)
        for x,y in [(1809,517),(1864,526),(1831,600),(1868,585)]: circle(x,y,8,'blue-point')
        text(1798,665,'Learn 4D',31,'blue-text'); text(1798,697,'deformation',31,'blue-text')
        rect(1662,715,274,101,'method',12); text(1799,777,'NSFF',36,'title')
        text(1798,877,'D-NeRF · Nerfies',29); text(1798,946,'4D Gaussian Splatting',29)
    for args in [('variational',0,319,399,666,bottom_variational),('cnn',400,319,396,666,bottom_cnn),('recurrent',798,319,398,666,bottom_recurrent),('self',1198,319,398,666,bottom_self),('fields',1598,319,390,666,bottom_fields)]: zone(*args)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site=Path(__file__).resolve().parents[2]
    original=site/'assets/figures/figures/part3/section6/scene_flow_estimation.webp'
    (site/'example/figure621.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure621-1"><title>Figure 6.21 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.21 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/scene_flow_estimation.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig621()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure621-1';mountNative();</script></html>''')
