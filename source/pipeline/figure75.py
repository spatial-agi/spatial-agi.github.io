"""Figure 7.5: rule-based and programmatic reasoning, native 2000 × 894."""
from pathlib import Path
from html import escape
import json

SITE = Path(__file__).resolve().parents[2]
INFO = {
    'initial': ('Initial state and goal', 'The initial symbolic state describes the current scene. The goal specifies the conditions that must hold after executing the plan.'),
    'skills': ('Action and behavior library', 'Reusable skills expose symbolic preconditions and effects. A task-level controller composes pick, move, place and check operations.'),
    'conditions': ('Preconditions and effects', 'An action is applicable when its preconditions hold. Executing pick changes the symbolic state from a free hand to holding the object.'),
    'planning': ('Symbolic planning', 'Search over symbolic states finds an action sequence from the initial state to a goal. STRIPS and PDDL describe operators and planning problems.'),
    'fsm': ('Finite-state reactive switching', 'Guarded transitions switch among navigation, alignment, grasping and recovery. Failure activates recovery before resetting the nominal behavior.'),
    'tree': ('Behavior tree', 'A fallback tries alternative branches. A sequence runs its children in order; recovery and replanning provide a response when nominal execution fails.'),
    'rules': ('Production rules', 'A rule engine matches conditions against current facts. When ready(x) and hand_free hold, the illustrated rule invokes the pick(x) skill.'),
    'plan': ('Executable action plan', 'A plan orders reusable actions. The second row illustrates a preparation stage followed by placement; concurrency requires compatible resources and effects.'),
    'policy': ('Reactive policy', 'Sensing updates the current state. Decision logic selects a behavior, such as picking or moving, from the current observations and conditions.'),
    'trace': ('Monitored execution and replanning', 'The execution trace records successful and failed actions. A disturbance triggers replanning, followed by a retry and a new check.'),
}


def fig75():
    out=[]
    add=out.append
    widths={'Initial state + goal':319,'Action / behavior library':431,'Preconditions & effects':420,
            'Symbolic planning':331,'FSM / reactive switching':410,'Behavior tree':243,
            'Production rules':300,'Action plan':204,'Reactive policy':268,'Execution trace':279}

    def text(x,y,value,size=32,cls='text',raw=False):
        length=f' textLength="{widths[value]}" lengthAdjust="spacingAndGlyphs"' if cls=='heading' else ''
        add(f'<text class="f75-{cls}" x="{x}" y="{y}" text-anchor="middle" font-size="{size}"{length}>{value if raw else escape(value)}</text>')

    def path(d,cls='ink',extra=''):
        add(f'<path class="{" ".join("f75-"+c for c in cls.split())}" d="{d}" {extra}/>')

    def rect(x,y,w,h,cls='panel',rx=7):
        add(f'<rect class="f75-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def arrow(d,color='ink',large=False,dashed=False):
        path(d,f'{color} route'+(' dashed' if dashed else ''),f'marker-end="url(#f75-{color}{"-large" if large else ""}-arrow)"')

    def box(x,y,w,h,label,size=32):
        rect(x,y,w,h);text(x+w/2,y+h/2+size*.34,label,size)

    def circle(x,y,r=8,cls='node'):
        add(f'<circle class="f75-{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def zone(key,frame,draw):
        add(f'<g class="f75-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{INFO[key][0]}">')
        draw();rect(*frame,'hit',7);add('</g>')

    def check(x,y):path(f'M{x-12} {y}l9 12l19 -26','green symbol')
    def cross(x,y):path(f'M{x-6} {y-6}l12 12M{x-6} {y+6}l12 -12','red symbol')

    add('<div class="nf nf-75" data-nf="75" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 894" role="group" aria-label="Figure 7.5: rule-based and programmatic reasoning"><defs>')
    for color,hexcolor in [('ink','#2c373d'),('blue','#4146eb'),('red','#c63d3d')]:
        for large in [False,True]:
            suffix='-large' if large else '';w,h=(15,15) if large else (11,11)
            add(f'<marker id="f75-{color}{suffix}-arrow" markerUnits="userSpaceOnUse" markerWidth="{w}" markerHeight="{h}" refX="{w-3}" refY="{h/2}" orient="auto"><path d="M2 2L{w-3} {h/2}L2 {h-2}" fill="none" stroke="{hexcolor}" stroke-width="{4 if large else 3}" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    add('</defs><rect width="2000" height="894" fill="white"/><g class="f75-scaffold">')
    arrow('M487 435H539',large=True);arrow('M1473 435H1521',large=True)
    for x,label in [(241,'(i) Inputs'),(1008,'(ii) Reasoning core'),(1767,'(iii) Outputs')]:text(x,870,label,36,'blue-text')
    add('</g>')

    def initial():
        rect(9,45,465,227);text(241,99,'Initial state + goal',36,'heading')
        add('<image href="/assets/img/figs/f75/i-inputs/initial-state-arm.png" x="28" y="123" width="117" height="116"/>')
        path('M165 209H293M179 210V238M279 210V238')
        path('M204 171L216 158H248L235 171Z','cube-top')
        path('M204 171H235V203H204Z','cube-front')
        path('M235 171L248 158V190L235 203Z','cube-side')
        arrow('M311 190H352',large=True);check(400,157);rect(367,199,66,29,'goal')
    zone('initial',(9,45,465,227),initial)

    def skills():
        rect(9,300,465,220);text(241,356,'Action / behavior library',36,'heading')
        for x,w,label in [(27,90,'pick'),(143,92,'move'),(259,91,'place'),(375,88,'check')]:box(x,402,w,53,label)
        for a,b in [(121,136),(239,253),(354,367)]:arrow(f'M{a} 429H{b}')
        text(241,494,'Reusable skills')
    zone('skills',(9,300,465,220),skills)

    def conditions():
        rect(9,551,465,236);text(241,604,'Preconditions & effects',36,'heading')
        rect(25,642,123,91);text(87,679,'at(x,l)',29);text(87,711,'hand free',29)
        box(188,658,98,57,'pick(x)');arrow('M151 686H181');arrow('M290 686H317')
        rect(323,642,123,91);text(385,679,'holding(x)',29);text(385,711,'not free',29)
    zone('conditions',(9,551,465,236),conditions)

    def planning():
        rect(556,27,443,371);text(777,86,'Symbolic planning',36,'heading');text(777,141,'STRIPS / PDDL',34)
        path('M602 250L684 309L772 225L873 293L948 234','edge')
        path('M602 250L678 187L772 225L848 178L948 234','blue flow')
        for x,y in [(602,250),(678,187),(684,309),(772,225),(848,178),(873,293),(948,234)]:circle(x,y)
        text(602,308,'s<tspan baseline-shift="sub" font-size="23">0</tspan>',32,'blue-text',True)
        text(947,293,'goal',32,'blue-text');text(777,361,'Search → action sequence',32,'blue-text')
    zone('planning',(556,27,443,371),planning)

    def fsm():
        rect(1018,27,442,371);text(1239,86,'FSM / reactive switching',36,'heading')
        box(1039,143,151,63,'Navigate');box(1256,143,151,63,'Align')
        box(1039,287,151,63,'Recover');box(1256,287,151,63,'Grasp')
        arrow('M1194 174H1250');text(1224,137,'arrived',29)
        arrow('M1331 209V281');text(1391,250,'aligned',29)
        arrow('M1252 319H1196','red');text(1224,373,'failed',29,'red-text')
        arrow('M1115 283V212');text(1052,250,'reset',29)
    zone('fsm',(1018,27,442,371),fsm)

    def tree():
        rect(556,429,443,358);text(777,488,'Behavior tree',36,'heading')
        arrow('M737 581L700 600');arrow('M830 581L894 600')
        arrow('M697 662L624 694');arrow('M697 662L751 694');arrow('M898 663V692')
        box(685,520,182,60,'Fallback (?)');box(597,604,201,58,'Sequence (→)');box(839,604,119,58,'Recover',29)
        box(562,699,119,54,'Navigate',29);box(694,699,119,54,'Grasp',29);box(839,699,119,54,'Replan',29)
        text(637,812,'✓ success',28,'green-text');text(791,812,'○ running',28);text(941,812,'× failure',28,'red-text')
    zone('tree',(556,429,443,393),tree)

    def rules():
        rect(1018,429,442,358);text(1239,488,'Production rules',36,'heading')
        rect(1045,551,170,82);text(1130,582,'ready(x)');text(1130,619,'hand_free')
        box(1262,551,167,82,'Match / fire');arrow('M1222 592H1252')
        text(1239,681,'IF ready(x) AND hand_free',29);text(1239,735,'THEN invoke pick(x)',31,'blue-text')
    zone('rules',(1018,429,442,358),rules)

    def plan():
        rect(1542,27,446,233);text(1765,83,'Action plan',36,'heading')
        for x,w,label in [(1559,85,'pick'),(1666,84,'move'),(1773,85,'place'),(1879,85,'check')]:box(x,116,w,54,label,31)
        for a,b in [(1647,1659),(1754,1767),(1862,1872)]:arrow(f'M{a} 143H{b}')
        box(1567,187,255,54,'pick + prepare',30);box(1883,187,89,54,'place',31);arrow('M1826 214H1877')
    zone('plan',(1542,27,446,233),plan)

    def policy():
        rect(1542,278,446,235);text(1765,330,'Reactive policy',36,'heading')
        rect(1588,341,64,38);circle(1620,360,7,'blue-node')
        box(1567,379,113,97,'Sense');box(1727,382,110,78,'Logic')
        box(1877,352,92,54,'pick');box(1877,424,92,54,'move')
        arrow('M1684 423H1721');arrow('M1841 422L1871 383');arrow('M1841 422L1871 448')
    zone('policy',(1542,278,446,235),policy)

    def trace():
        rect(1542,533,446,254);text(1765,586,'Execution trace',36,'heading')
        box(1560,622,107,54,'pick');box(1705,622,106,54,'move');box(1855,622,107,54,'check')
        arrow('M1671 649H1698');arrow('M1816 649H1849')
        check(1613,697);cross(1757,694)
        box(1567,715,100,56,'replan',29);box(1849,715,107,56,'retry')
        arrow('M1758 703V709L1673 727','red',dashed=True)
        arrow('M1671 743H1842','blue');arrow('M1903 711V683','blue')
    zone('trace',(1542,533,446,254),trace)

    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    (SITE/'example/figure75.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure75-1"><title>Figure 7.5 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.5 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/715_program.webp" alt="Original Figure 7.5"><h2>Interactive reconstruction</h2>'''+fig75()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure75-1';mountNative();</script></html>''')
