"""Figure 6.9: extracted photographs with independent SVG geometry and type."""
import json
from html import escape
from pathlib import Path

INFO = {
    'vanishing': {'t': 'Vanishing-point estimation', 'b': 'Parallel directions in the street converge to a shared image point. Its homogeneous position depends on camera intrinsics K and rotation R: vᵢ ∼ KRdᵢ. Translation does not affect a direction at infinity.'},
    'patterns': {'t': 'Planar calibration patterns', 'b': 'Observe a known checkerboard at varied poses. Corresponding corners across these views constrain camera intrinsics and lens distortion.'},
    'calibration': {'t': 'Fit intrinsics and distortion', 'b': 'Estimate one camera model from all calibration views. The fit combines the known pattern geometry with measured image corners.'},
    'intrinsics': {'t': 'Camera parameters', 'b': 'K contains focal lengths fₓ and fᵧ and principal-point coordinates cₓ and cᵧ. The k coefficients describe radial distortion; the p coefficients describe tangential distortion.'},
    'horizon': {'t': 'Ground-plane vanishing line', 'b': 'Vanishing points for directions parallel to the ground lie on its vanishing line, or horizon. This line constrains the camera orientation relative to the ground plane.'},
    'pitch': {'t': 'Camera pitch', 'b': 'The side-view inset illustrates the angle θ between the camera viewing direction and a horizontal reference. The inset is schematic; its arrow is not a measured ray in the street photograph.'},
}


def fig69():
    out = []
    def add(s): out.append(s)
    def text(x, y, label, size=30, cls='f69-text', width=None):
        length = f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        add(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{label}</text>')
    def sub(a, b): return f'{a}<tspan baseline-shift="sub" font-size="68%">{b}</tspan>'
    def image(name, x, y, w, h):
        add(f'<image href="/assets/img/figs/f69/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    def path(d, cls='f69-line', arrow=False):
        marker = ' marker-end="url(#f69-arrow)"' if arrow else ''
        add(f'<path class="{cls}" d="{d}"{marker}/>')
    def zone(key, x, y, w, h, body):
        add(f'<g class="f69-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        body()
        add(f'<rect class="f69-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="9"/></g>')

    add('''<div class="nf nf-69" data-nf="69" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1031" role="group" aria-label="Figure 6.9: geometric subtasks for height and distance estimation"><defs><marker id="f69-arrow" markerWidth="15" markerHeight="15" refX="11" refY="7.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 3L11 7.5L2 12" fill="none" stroke="#29343a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="2000" height="1031" fill="#fff"/>''')
    path('M671 42V986 M1329 42V986', 'f69-divider')

    def vanishing():
        text(338,114,'(a) Vanishing-point estimation',36,'f69-title',524)
        image('a/street-clean',30,174,617,411)
        path('M30 470L329 375','f69-blue-line f69-route')
        path('M30 497L329 375','f69-blue-line f69-route')
        path('M647 509L329 375','f69-blue-line f69-route')
        add('<circle class="f69-point" cx="329" cy="375" r="10.5"/>')
        text(369,347,'v',38,'f69-math f69-bold')
        text(338,645,'Parallel street edges → shared point',30,width=487)
        text(338,741,sub('v','i')+' ∼ KR'+sub('d','i'),42,'f69-math',179)
        text(338,847,'World direction → image vanishing point',28,width=509)
        text(338,917,'Homogeneous coordinates',28,width=350)
    zone('vanishing',23,168,630,770,vanishing)

    def patterns():
        # Keep the title exactly as printed, including its truncated final word.
        text(1000,115,'(b) Camera calibrat',36,'f69-title',337)
        text(1000,162,'Known planar pattern · varied poses',28,width=460)
        for name,box in [('left',(714,195,144,117)),('center',(906,171,170,132)),('right',(1097,198,174,112))]:
            image('b/checkerboard-'+name,*box)
        for x,y in [(721,202),(830,203),(851,292),(740,304),(914,178),(1068,178),(1068,295),(914,295),(1130,206),(1263,210),(1247,302),(1104,292)]:
            add(f'<circle class="f69-corner" cx="{x}" cy="{y}" r="6"/>')
        path('M800 322V348H1181V322 M991 322V348','f69-divider f69-bracket')
    zone('patterns',705,134,578,218,patterns)

    def calibration():
        path('M991 350V386','f69-line f69-route',True)
        add('<path class="f69-camera" d="M947 406H1034V459H947Z M960 406V395H987V406"/><circle class="f69-camera" cx="991" cy="432" r="16"/>')
        path('M991 471V516','f69-line f69-route',True)
        add('<rect class="f69-fit" x="735" y="535" width="527" height="99" rx="7"/>')
        text(999,592,'Fit intrinsics + distortion',32,width=355)
    zone('calibration',729,354,539,287,calibration)

    def intrinsics():
        text(880,754,'K =',38,'f69-math',62)
        path('M938 676H930V812H938 M1138 676H1146V812H1138','f69-blue-line f69-matrix-bracket')
        rows=[[sub('f','x'),'0',sub('c','x')],['0',sub('f','y'),sub('c','y')],['0','0','1']]
        for y,row in zip([706,754,801],rows):
            for x,label in zip([959,1038,1118],row):
                text(x,y,label,38,'f69-math')
        text(1000,908,sub('k','1')+', '+sub('k','2')+', '+sub('k','3')+' ; '+sub('p','1')+', '+sub('p','2'),38,'f69-math',296)
        text(1000,970,'Radial / tangential distortion',28,width=365)
    zone('intrinsics',803,666,398,312,intrinsics)

    def horizon():
        text(1661,114,'(c) Horizon-line detection',36,'f69-title',440)
        image('c/street-clean',1353,174,617,411)
        path('M1353 375H1970','f69-blue-line f69-horizon f69-route')
        add('<circle class="f69-point" cx="1652" cy="375" r="8"/>')
        text(1661,651,'Ground-plane vanishing line',32,'f69-text f69-blue',414)
    zone('horizon',1347,168,629,496,horizon)

    def pitch():
        add('<rect class="f69-pitch-frame" x="1387" y="720" width="549" height="240" rx="7"/>')
        text(1661,771,'Camera pitch (side view)',30,width=340)
        add('<rect class="f69-camera" x="1430" y="819" width="54" height="37"/>')
        path('M1492 837H1862','f69-divider f69-dashed')
        path('M1426 930H1885','f69-divider f69-ground')
        path('M1492 837L1824 916','f69-line f69-pitch-ray f69-route',True)
        path('M1605 837A113 113 0 0 1 1602 863','f69-blue-line f69-angle')
        text(1668,880,'θ',38,'f69-math')
    zone('pitch',1380,712,563,255,pitch)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[2]
    (site/'example/figure69.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure69-2"><title>Figure 6.9 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{width:100%;display:block;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.9 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/height_estimation_1.webp"><h2 id="redraw">Interactive reconstruction</h2>'''+fig69()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure69-2';mountNative();</script></html>''')
