"""Faithful native Figure 7.10 using the original 2000 x 437 geometry."""
from html import escape
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/explicit_structured_neural_reasoning_method.webp'
INFO = {
    'mac': ('MAC recurrence', 'Successive Memory, Attention and Composition cells maintain a reasoning state. Each cell uses control to select an operation, reads visual evidence, and writes the updated memory before passing it to the next cell.'),
    'state': ('Neural State Machine', 'Concept detection builds a probabilistic scene graph. The question guides a reading head through successive states and object relations; the finite-automaton transitions expose an inspectable reasoning trace.'),
    'modules': ('Neural Module Network', 'A parser converts the question into a layout. The dog module localizes visual evidence and the where module maps that evidence to an answer. The LSTM language branch and CNN image branch meet at the answer prediction.'),
    'llm': ('Language model as program generator', 'The question is passed to a large language model, which produces a Python program. The generated code selects and calls tools rather than directly performing every visual operation.'),
    'tools': ('Vision-tool API', 'The generated program can invoke an object detector, attribute classifier or captioner. Their results support the final answer, while the code provides a readable record of the tool calls.'),
}


def fig710():
    out = []; add = out.append

    def text(x, y, value, size=23, cls='', anchor='middle', raw=False):
        classes = ' '.join('f710-'+c for c in cls.split())
        add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" class="{classes}">{value if raw else escape(value)}</text>')

    def lines(x, ys, values, size=23, cls=''):
        for y, value in zip(ys, values):
            text(x, y, value, size, cls)

    def rect(x, y, w, h, cls='box', rx=10):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="f710-{cls}"/>')

    def path(d, cls='ink', arrow=False):
        classes = ' '.join('f710-'+c for c in cls.split())
        marker = ' marker-end="url(#f710-arrow)"' if arrow else ''
        add(f'<path d="{d}" class="{classes}"{marker}/>')

    def arrow(d, cls=''):
        path(d, 'route '+cls, True)

    def zone(key, bounds, draw):
        add(f'<g class="f710-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        x, y, w, h = bounds
        add(f'<rect class="f710-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')

    add('<div class="nf nf-710" data-nf="710" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 437" role="group" aria-label="Figure 7.10: four methods for explicit structured neural reasoning"><defs><marker id="f710-arrow" markerUnits="userSpaceOnUse" markerWidth="7" markerHeight="6" refX="6" refY="3" orient="auto"><path d="M0 0.5L6 3L0 5.5Z" fill="#111"/></marker></defs><rect width="2000" height="437" fill="white"/><g class="f710-scaffold">')
    for x, w in ((4,449),(492,430),(964,415),(1422,575)):
        rect(x,2,w,433,'panel',19)
    for x, title in ((228,'1. MAC recurrence'),(707,'2. Neural State Machine'),(1171,'3. Neural Module Network'),(1710,'4. LLM-as-program-generator')):
        text(x,40,title,27,'heading')
    add('</g>')

    def mac():
        text(55,63,'Q',20)
        arrow('M55 71L71 81')
        for x in (15,145,274):
            rect(x,82,112,342,'cell',12)
            text(x+56,126,'MAC cell',23)
            for y, baseline, value in ((164,202,'Control'),(254,292,'Read'),(345,383,'Write')):
                rect(x+11,y,89,67,'box',7)
                text(x+55.5,baseline,value,23)
        arrow('M127 253H145');arrow('M257 253H274');arrow('M386 253L419 254')
        text(430,259,'A',20)
    zone('mac',(12,46,428,380),mac)

    def state():
        lines(734,(100,126),('Reading head','(traversal)'),20)
        arrow('M692 126L669 146')
        rect(508,146,107,139,'box',12)
        lines(561.5,(183,209,235,261),('Concept','detection','(Mask R-','CNN)'),20)
        rect(630,147,129,189,'box',14)
        lines(694.5,(175,200),('Probabilistic','scene graph'),20)
        text(694.5,225,'G = (V, E)',20,'math')
        # Draw directed graph edges below the graph label, leaving all nodes independent.
        arrow('M675 257L705 260')
        arrow('M667 266L675 299')
        arrow('M683 301L709 270')
        arrow('M718 271L729 302')
        for x,y in ((664,256),(715,261),(677,308),(731,312)):
            add(f'<ellipse cx="{x}" cy="{y}" rx="11.5" ry="10" class="f710-node"/>')
        rect(782,147,128,185,'box',14)
        lines(846,(185,210,235),('Finite-','automation','transition'),20)
        text(808,288,'s<tspan baseline-shift="sub" font-size="70%">i</tspan>',25,'symbol',raw=True)
        text(871,288,'s<tspan baseline-shift="sub" font-size="70%">j</tspan>',25,'symbol',raw=True)
        arrow('M615 218H630');arrow('M759 218H778')
    zone('state',(503,70,411,277),state)

    def modules():
        text(1179,85,'Question → Parser → Layout',23)
        rect(982,141,97,42,'box',0)
        lines(1031,(159,173),('Where is','the dog?'),11,'italic')
        rect(1103,151,44,21,'processor',0);text(1125,166,'LSTM',11)
        arrow('M1079 162H1101');arrow('M1147 162H1235');arrow('M1251 162H1272')
        rect(1273,151,73,21,'box',12);text(1309,166,'couch',11)
        add('<circle cx="1243" cy="162" r="6.5" class="f710-node"/>')
        path('M1237 162H1249M1243 156V168','ink')
        # The pale module library and selected dog/where tiles match the source colors.
        rect(1118,199,235,91,'library',0)
        for x,y,w,label,cls in ((1159,213,45,'count','count'),(1219,213,48,'where','where'),(1273,213,41,'color','color'),(1319,213,27,'...','other'),(1159,257,38,'dog','dog'),(1203,257,34,'cat','muted'),(1249,257,59,'standing','muted'),(1314,257,32,'...','muted')):
            rect(x,y,w,21,cls,0);text(x+w/2,y+14,label,10,'tile-'+cls)
        arrow('M1031 183V232H1042')
        rect(1043,222,47,20,'processor',0);text(1066.5,236,'Parser',11)
        path('M1090 232H1102')
        rect(1102,222,46,20,'processor',0);text(1125,236,'Layout',11)
        path('M1125 222V206H1211V224H1219','blue dashed flow')
        path('M1125 242V268H1159','green dashed flow')
        add('<image href="/assets/img/figs/f710/c-module-network/room.png" x="985" y="288" width="95" height="65"/>')
        rect(984,286,97,69,'image-frame',0)
        path('M1105 310H1144L1149 330H1101Z','processor')
        text(1125,325,'CNN',10)
        arrow('M1081 320H1102');arrow('M1149 320H1179V279')
        arrow('M1179 257V237H1243V168')
        arrow('M1149 320H1243V236')
    zone('modules',(975,60,394,305),modules)

    def llm():
        text(1486,143,'Question',23)
        arrow('M1486 153V193')
        rect(1432,194,107,139,'box',12)
        lines(1485.5,(220,250,279,309),('Large','Language','Model','(LLM)'),23)
        rect(1562,141,164,226,'box',6)
        lines(1644,(166,195,224),('Generated','Python','program'),23)
        for y,value in ((268,'obj = find(“zebra”)'),(289,'ans ='),(310,'obj.crop_to_captio'),(331,'n(“animal_pattern”)')):
            text(1568,y,value,15,anchor='start')
        arrow('M1539 262H1562')
    zone('llm',(1430,117,302,258),llm)

    def tools():
        rect(1754,96,138,284,'box',5)
        lines(1823,(122,152),('Vision-tool','API'),23)
        rect(1773,167,105,60,'box',6)
        lines(1825.5,(190,215),('Object','detector'),20)
        rect(1773,240,105,67,'box',6)
        lines(1825.5,(266,292),('Attribute','classifier'),20)
        rect(1773,315,105,56,'box',6);text(1825.5,350,'Captioner',20)
        for d in ('M1726 264L1772 197','M1726 264L1772 273','M1726 264L1772 343'):
            arrow(d)
        arrow('M1892 235H1915')
        rect(1915,218,77,35,'box',3);text(1953.5,242,'Answer',20)
    zone('tools',(1727,86,267,302),tools)
    info=json.dumps({k:{'t':title,'b':body} for k,(title,body) in INFO.items()})
    add(f'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">{info}</script></div>')
    return ''.join(out)


if __name__=='__main__':
    (SITE/'example/figure710.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.10 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure710-1"><style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style><main><h1>Figure 7.10 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="437" alt="Original Figure 7.10"><h2>Interactive reconstruction</h2>{fig710()}</main><script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure710-1';mountNative();</script></html>''')
