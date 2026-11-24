"""Figure 7.23: spatial tasks and editable reasoning-trace structures."""
from pathlib import Path
from html import escape
import json

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/chain-of-thought_spatial_reasoning.webp'
INFO = {
    'deduction': ('Textual spatial deduction', 'In a north-up frame, A is west of B and B is north of C. Combining the two relations places A northwest of C. The arrows show the stated westward and northward relations.'),
    'visual': ('Visual scene reasoning', 'Count red cubes to the left of the green sphere. Only the boxed red cube satisfies both the object description and the spatial relation, so the answer is 1. The white cube and white cylinder do not qualify.'),
    'embodied': ('Embodied planning', 'The task is to find the mug in the kitchen. A plan guides an action, which produces a new observation. New evidence can revise the next plan; the photograph is an illustrative scene.'),
    'cot': ('Chain of Thought (CoT)', 'A linear trace records successive intermediate commitments. Each step builds on the preceding step, so incorrect spatial assumptions can propagate along the chain.'),
    'tot': ('Tree of Thoughts (ToT)', 'A tree branches into alternative intermediate hypotheses. Candidates can be evaluated before choosing a branch. Blue marks an illustrative selected route; gray branches represent alternatives.'),
    'got': ('Graph of Thoughts (GoT)', 'A graph lets multiple branches merge and reuse intermediate results. The two paths here converge on a shared result rather than forming independent final answers.'),
    'pot': ('Program of Thought (PoT)', 'Generate code, execute it, then read the result. Program execution grounds the intermediate trace in an external computation rather than relying only on a verbal explanation.'),
    'coa': ('Chain of Action (CoA)', 'Plan, act, and observe form a closed loop. The return arrow carries new observations back to planning. Actions ground the reasoning trace in interaction with the environment.'),
    'trace': ('Intermediate trace and final answer', 'The trace τ = (t₁, …, tL) is a sequence of intermediate states. The readout g combines context c, query q, and trace τ to produce the final answer ŷ. A trace topology alone does not guarantee correctness.'),
    'evidence': ('Check the answer and evidence', 'A plausible intermediate trace does not establish spatial correctness. Check the final answer against grounded evidence, such as the stated relations, the visible scene, executable results, or new observations.'),
}


def fig723():
    out=[]
    a=out.append

    def text(x,y,value,size=32,cls='',width=None,raw=False):
        fit=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}" style="font-size:{size}px"{fit}>'+(value if raw else escape(value))+'</text>'

    def route(d,gray=False,duration=2100,ink=False,thin=False,inline=False):
        color='ink' if ink else 'gray' if gray else 'blue'
        marker='inline' if inline else color
        return f'<path d="{d}" class="rl-route f723-{color}-route'+(' f723-thin' if thin else '')+f'" marker-end="url(#f723-{marker})" data-duration="{duration}"/>'

    def node(x,y,r=17,gray=False):
        return f'<circle cx="{x}" cy="{y}" r="{r}" class="f723-node'+(' f723-alternative' if gray else '')+'"/>'

    def box(x,y,w,h,selected=False):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="f723-box'+(' f723-selected' if selected else '')+'"/>'

    def asset(file,x,y,w,h):
        return f'<image href="/assets/img/figs/f723/{file}" x="{x}" y="{y}" width="{w}" height="{h}"/>'

    def zone(k,body,bounds):
        x,y,w,h=bounds
        a(f'<g class="rl-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k][0])}">{body}<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')

    a('<div class="nf nf-rl nf-723" data-nf="723" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1124" role="group" aria-label="Figure 7.23: spatial reasoning tasks and intermediate-trace structures"><defs>')
    for name,color in [('blue','#4145e9'),('gray','#aab2b8'),('ink','#29353b')]:
        a(f'<marker id="f723-{name}" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M4 4L14 9L4 14Z" fill="{color}" stroke="{color}" stroke-width="2.3" stroke-linejoin="round"/></marker>')
    a('<marker id="f723-inline" markerWidth="16" markerHeight="18" refX="13" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M6 3L13 9L6 15" fill="none" stroke="#4145e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    a('</defs><rect width="2000" height="1124" fill="white"/>')
    a('<g class="f723-scaffold"><path d="M665 30V503M1335 30V503M17 517H1983M400 621V983M800 621V983M1200 621V983M1600 621V983" class="f723-divider"/>')
    a(text(331,61,'(a) Textual spatial deduction',36,'f723-heading',495))
    a(text(1000,61,'(b) Visual scene reasoning',36,'f723-heading',458))
    a(text(1668,61,'(c) Embodied planning',36,'f723-heading',390))
    a(text(1000,581,'LLM / VLM: structured intermediate states',36,'f723-heading',735))
    a(text(1632,1037,'PoT / CoA: execution-grounded extensions',30,width=569)+'</g>')

    body=text(332,146,'A is west of B; B is north of C.',32,width=424)
    for x,y,v in [(154,228,'A'),(369,228,'B'),(369,360,'C')]:
        body+=node(x,y,20)
    body+=route('M359 228H165',duration=2600)+route('M369 347V240',duration=2100)
    for x,y,v in [(154,228,'A'),(369,228,'B'),(369,360,'C')]:
        body+=text(x,y+10,v,32)
    body+=text(508,195,'N',30)+route('M508 324V232',ink=True,duration=2400)
    body+=text(332,463,'Answer: A is northwest of C',32,'f723-blue',401)
    zone('deduction',body,(105,110,455,366))

    body=asset('b-visual/scene.png',744,95,505,245)
    # Retain the photographic plate for contact shadows, and separately layer its objects.
    for file,x,y,w,h in [('white-cube',769,150,106,119),('red-cube',893,155,97,113),('green-sphere',1007,151,113,114),('white-cylinder',1131,139,97,128)]:
        body+=asset('b-visual/'+file+'.png',x,y,w,h)
    body+='<rect x="892" y="154" width="99" height="114" class="f723-selection"/>'
    body+=text(1001,386,'Red cubes left of the green sphere?',32,width=505)
    body+=text(1000,463,'Answer: 1',32,'f723-blue',146)
    zone('visual',body,(735,88,528,388))

    body=asset('c-embodied/kitchen.png',1380,120,276,278)
    body+=asset('c-embodied/blue-mug.png',1587,237,44,38)
    body+=text(1827,161,'Find the mug',32,width=194)+text(1827,193,'in the kitchen.',32,width=208)
    body+=text(1786,291,'Plan',32,'f723-blue',64)+text(1880,291,'act',32,'f723-blue',43)
    body+=route('M1829 280H1847',duration=1500,thin=True,inline=True)
    body+=text(1843,322,'observe',32,'f723-blue',115)+route('M1757 311H1775',duration=1500,thin=True,inline=True)
    body+=text(1667,463,'Revise using new observations',32,width=435)
    zone('embodied',body,(1369,109,573,368))

    body=text(200,655,'CoT',36,'f723-heading',69)
    body+=route('M200 759V774',duration=1400)+route('M200 836V851',duration=1400)
    for y in [733,809,886]: body+=node(200,y)
    body+=text(200,955,'Linear trace',32,width=177)
    zone('cot',body,(100,618,200,350))

    body=text(600,655,'ToT',36,'f723-heading',64)
    for x,y,gray in [(600,726,False),(516,800,False),(686,800,True),(465,883,True),(575,883,False),(683,883,True),(747,883,True)]:
        body+=node(x,y,13,gray)
    body+=route('M590 735L526 792')+route('M609 735L676 792',True)
    body+=route('M509 812L472 871',True)+route('M524 812L567 871')
    body+=route('M686 814L683 869',True)+route('M695 811L738 872',True)
    body+=text(600,955,'Branch and evaluate',32,width=292)
    zone('tot',body,(438,618,325,350))

    body=text(1000,655,'GoT',36,'f723-heading',69)
    for x,y in [(1000,726),(908,803),(1092,803),(1000,886)]: body+=node(x,y,16)
    body+=route('M988 737L919 793')+route('M1012 737L1081 793')
    body+=route('M920 814L989 875')+route('M1080 814L1011 875')
    body+=text(1000,955,'Merge / reuse results',32,width=301)
    zone('got',body,(841,618,318,350))

    body=text(1400,655,'PoT',36,'f723-heading',65)
    for y,value,selected in [(701,'Generate code',False),(791,'Execute',True),(880,'Read result',False)]:
        body+=box(1255,y,290,68,selected)+text(1400,y+42,value,32,width={'Generate code':210,'Execute':114,'Read result':167}[value])
    body+=route('M1400 774V783',duration=1400)+route('M1400 863V872',duration=1400)
    zone('pot',body,(1245,618,310,341))

    body=text(1800,655,'CoA',36,'f723-heading',73)
    for y,value,selected in [(701,'Plan',False),(791,'Act',True),(880,'Observe',False)]:
        body+=box(1686,y,228,68,selected)+text(1800,y+42,value,32,width={'Plan':61,'Act':49,'Observe':118}[value])
    body+=route('M1800 774V783',duration=1400)+route('M1800 863V872',duration=1400)
    body+=route('M1917 914H1957V735H1931',duration=3500,thin=True)
    zone('coa',body,(1675,618,294,341))

    body=text(491,1038,'τ = (t<tspan baseline-shift="-6" font-size="70%">1</tspan>, …, t<tspan baseline-shift="-6" font-size="70%">L</tspan>),',38,'f723-math f723-blue',252,True)
    body+=text(803,1038,'ŷ = g(c, q, τ)',38,'f723-math f723-blue',208,True)
    zone('trace',body,(350,1003,573,45))
    body=text(1000,1100,'Check the answer and evidence: a plausible trace alone does not establish spatial correctness.',30,width=1313)
    zone('evidence',body,(330,1066,1340,47))
    a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:dict(t=v[0],b=v[1]) for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__=='__main__':
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.23 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure723-1"><style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}@media(max-width:600px){body{margin:12px}}</style><main><h1>Figure 7.23 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="1124" alt="Original Figure 7.23"><h2>Interactive reconstruction</h2>'''+fig723()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure723-1';mountNative();</script></html>'''
    (SITE/'example/figure723.html').write_text(page)
    print('Generated Figure 7.23 comparison.')
