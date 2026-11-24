"""Interactive frontend reconstruction of Figure 8.22."""
import json
from html import escape
from pathlib import Path

INFO = {
    'inbetween': {'t':'Masked infilling and in-betweening','b':'Known motion states are reinserted at every denoising step while missing frames are generated. CondMDI and PriorMDM illustrate this preservation-by-construction family.'},
    'guidance': {'t':'Spatial guidance','b':'A target root path or joint location guides the denoising process. GMD and OmniControl steer generated motion toward spatial constraints.'},
    'optimization': {'t':'Noise optimization','b':'DNO optimizes the initial latent noise through a fixed diffusion decoder. An edit loss measures the target and source motion, and gradients update the noise.'},
    'instruction': {'t':'Text-instruction editing','b':'A natural-language instruction edits a source motion while preserving gait and untargeted joints. MotionFix learns a text editor; language-model methods compose primitive edits.'},
}


def fig822():
    out=[]; add=out.append
    def text(x,y,s,size=30,cls='text',anchor='middle'):
        add(f'<text class="f822-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{s}</text>')
    def path(d,cls='line',arrow=False,flow=False):
        add(f'<path class="f822-{cls}{" f822-route" if flow else ""}" d="{d}"'+(f' marker-end="url(#f822-{"gray" if cls == "feedback" else "arrow"})"' if arrow else '')+'/>')
    def rect(x,y,w,h,cls='frame',rx=5):
        add(f'<rect class="f822-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
    def person(name,x,y,w,h):
        add(f'<image href="/assets/img/figs/f822/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>')
    def zone(key,x,y,w,h,draw):
        add(f'<g class="f822-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')
        draw(); rect(x,y,w,h,'hit',0); add('</g>')
    add('<div class="nf nf-822" data-nf="822" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1724" role="group" aria-label="Figure 8.22: four motion-editing mechanisms"><defs><marker id="f822-arrow" markerWidth="17" markerHeight="17" markerUnits="userSpaceOnUse" refX="13" refY="8.5" orient="auto"><path d="M2 2L14 8.5L2 15Z" fill="#4146eb" stroke="#4146eb" stroke-width="1.5" stroke-linejoin="round"/></marker><marker id="f822-gray" markerWidth="17" markerHeight="17" markerUnits="userSpaceOnUse" refX="13" refY="8.5" orient="auto"><path d="M2 2L14 8.5L2 15Z" fill="#aab2b9" stroke="#aab2b9" stroke-width="1.5" stroke-linejoin="round"/></marker></defs><rect width="2000" height="1724" fill="white"/>')
    add('<g class="f822-scaffold"><path d="M1000 48V1674M30 876H1970" class="f822-divider"/></g>')
    def a():
        text(500,82,'(a) Masked infilling / in-betweening',36,'title')
        rect(76,92,274,273,'frame',0);rect(359,92,276,273,'missing',0);rect(640,92,274,273,'frame',0)
        person('a-inbetween/start',198,108,116,253);person('a-inbetween/end',680,108,133,253)
        text(497,217,'Missing',34,'blue-text');text(497,254,'frames',34,'blue-text')
        path('M498 375V430','arrowline',True,True)
        rect(70,445,854,145,'method');text(497,490,'Reinsert known states at each step',32,'title');text(497,553,'CondMDI · PriorMDM',31)
        path('M498 597V625','arrowline',True,True)
        person('a-inbetween/result-01',257,652,97,210);person('a-inbetween/result-02',451,652,101,210);person('a-inbetween/result-03',644,652,113,210)
    zone('inbetween',30,36,950,820,a)
    def b():
        text(1500,82,'(b) Spatial guidance',36,'title')
        text(1260,168,'Target root path',31,'blue-text');path('M1070 332C1130 295 1170 270 1225 292S1380 397 1464 375','targetpath',True,True);path('M1070 363H1465','sourcepath')
        text(1260,431,'Source path',28)
        text(1744,168,'Target joint',31,'blue-text')
        # Target skeletal pose and highlighted joint.
        path('M1744 231V314M1744 260L1712 293M1744 260L1778 226M1744 314L1715 375M1744 314L1774 368','skeleton');path('M1778 226L1797 215','arrowline',False,True)
        for x,y in [(1744,260),(1744,314),(1712,293),(1778,226),(1715,375),(1774,368)]: add(f'<circle class="f822-joint" cx="{x}" cy="{y}" r="5.5"/>')
        add('<circle class="f822-head" cx="1744" cy="231" r="9"/><circle class="f822-target" cx="1814" cy="208" r="19"/>')
        path('M1276 461V500H1742V461','bracket');path('M1509 500V552','arrowline',True,True)
        rect(1067,567,864,153,'method');text(1499,625,'Guide denoising toward targets',32,'title');text(1499,686,'GMD · OmniControl',31)
        path('M1499 724V773','arrowline',True,True)
        path('M1113 843L1261 822L1465 843L1630 812L1878 834','guide',False,True)
        for x,y in [(1193,817),(1482,817),(1772,817)]:
            path(f'M{x} {y-30}V{y}M{x} {y-19}L{x-11} {y-7}M{x} {y-19}L{x+13} {y-31}M{x} {y}L{x-10} {y+23}M{x} {y}L{x+11} {y+20}','mini-skel')
            add(f'<circle class="f822-mini-skel" cx="{x}" cy="{y-30}" r="8"/>')
            for dx,dy in [(0,-19),(-11,-7),(13,-31),(0,0),(-10,23),(11,20)]: add(f'<circle class="f822-mini-joint" cx="{x+dx}" cy="{y+dy}" r="4.5"/>')
    zone('guidance',1020,36,950,820,b)
    def c():
        text(500,948,'(c) Noise optimization',36,'title');text(500,1023,'DNO · fixed diffusion decoder',31)
        text(138,1071,'z',34,'math-blue')
        rect(57,1098,166,143,'frame');
        noise = ((0, 1, 0, 2, 3), (1, 4, 0, 2, 2), (3, 3, 2, 2, 1), (2, 0, 1, 0, 3))
        for row, cells in enumerate(noise):
            for col, shade in enumerate(cells):
                rect(76+col*25,1129+row*25,19,19,f'noise-cell-{shade}',0)
        rect(307,1098,279,143,'method');text(447,1181,'Decode',34)
        rect(666,1098,264,143,'loss');text(798,1181,'Edit loss',34)
        path('M233 1169H291','arrowline',True,True);path('M591 1169H649','arrowline',True,True)
        text(798,1060,'Target + source',27)
        path('M800 1248V1354H138V1254','loopline',True,True);text(498,1328,'Backpropagate; update noise',29,'blue-text')
        path('M445 1245V1273H955V1535H907','feedback',True,True)
        person('c-optimization/result-01',190,1367,126,272);person('c-optimization/result-02',423,1367,128,272);person('c-optimization/result-03',659,1367,132,272)
        text(500,1694,'Edited motion after optimization',27)
    zone('optimization',30,895,950,819,c)
    def d():
        text(1500,948,'(d) Text-instruction editing',36,'title')
        rect(1067,1002,864,106,'quote');text(1499,1069,'“Raise the right arm higher”',31)
        person('d-instruction/source',1213,1198,99,208);person('d-instruction/edited',1705,1156,110,228)
        path('M1370 1277H1588','arrowline',True,True)
        text(1230,1445,'Source',29);text(1732,1445,'Edited',29,'blue-text')
        text(1500,1510,'Preserve gait and untargeted joints',28)
        path('M1070 1532H1930','divider')
        text(1500,1597,'MotionFix: learned source + text editor',28)
        text(1500,1661,'or LLM: primitive edits → iterative execution',28)
    zone('instruction',1020,895,950,800,d)
    add('</svg><div class="nf-card" hidden role="status"></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+' </script></div>')
    return ''.join(out)


if __name__=='__main__':
    site=Path(__file__).resolve().parents[2]
    original='/assets/figures/figures/part3/section8/four_motion_editing_mechanisms.webp'
    (site/'example/figure822.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure822-1"><title>Figure 8.22 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:1600px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 8.22 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="'''+original+'''\"><h2>Interactive reconstruction</h2>'''+fig822()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure822-1';mountNative();</script></html>''')
