"""Figure 7.4: constraint-based spatial solving, native geometry at 2000×923."""
from html import escape
from pathlib import Path
import json
import math

SITE = Path(__file__).resolve().parents[2]
INFO = {
    'joints': ('Joint configurations', 'Joint variables describe the robot configuration. A solver selects values that satisfy the task and all relevant limits.'),
    'poses': ('End-effector poses', 'Position and orientation variables specify the desired end-effector pose. Kinematic constraints connect this pose to the joint configuration.'),
    'states': ('States over time', 'A trajectory is a sequence of states. Transition constraints link successive states so that the motion can be executed.'),
    'modes': ('Discrete modes', 'Discrete decisions select contact modes, actions or regions. They are coupled to the continuous geometry of the problem.'),
    'collision': ('Collision avoidance', 'Collision constraints keep the robot and manipulated objects clear of obstacles. The red target illustrates a conflicting configuration.'),
    'reach': ('IK reachability', 'Inverse kinematics tests whether a target pose is reachable under joint and geometric constraints.'),
    'dynamics': ('Dynamics and limits', 'Dynamics, actuator bounds and joint limits restrict feasible motion. The gauge represents an admissible operating range.'),
    'logic': ('Task logic and timing', 'Logical and temporal requirements impose prerequisites and ordering among actions or task states.'),
    'csp': ('Constraint programming', 'Finite-domain variables are assigned by search and constraint propagation. Inconsistent branches are pruned before further computation.'),
    'sat': ('SAT and SMT', 'Boolean or logical formulas encode feasibility. Assignments are checked against the clauses; richer SMT theories can also express arithmetic and geometry.'),
    'milp': ('MILP and MICP', 'Discrete variables select among feasible regions or modes while continuous variables describe positions and motions inside those choices.'),
    'trajectory': ('Trajectory optimization', 'Optimize a motion objective while satisfying obstacle, kinematic and dynamic constraints. A local optimum alone does not prove global feasibility or optimality.'),
    'ik': ('Inverse kinematics solver', 'A target can admit a valid joint configuration or fail under reach and limit constraints. A local solver failure alone is not a proof that no solution exists.'),
    'tamp': ('Hybrid task and motion planning', 'Symbolic pick, move and place actions are coupled with geometric witnesses such as grasps, paths and placements.'),
    'feasible': ('Feasible trajectory', 'A feasible trajectory satisfies the modeled constraints at the required states and transitions, including collision avoidance.'),
    'schedule': ('Task–robot schedule', 'The schedule allocates actions to robots or resources while respecting precedence, timing and mutual exclusion constraints.'),
    'assembly': ('Assembly sequence', 'A sequence specifies an executable order of placements. Each step must satisfy geometric fit, support and manipulation requirements.'),
    'certificates': ('Certificates and solver status', 'Solver output can include a feasible witness, an infeasibility certificate or an optimality-gap bound, depending on the method and problem formulation.'),
}


def fig74():
    out=[]
    add=out.append
    widths={'Decision variables':333,'Constraints':212,'CSP / CP':151,'SAT / SMT':166,
            'MILP / MICP':205,'Trajectory optimization':393,'IK solver':145,'Hybrid TAMP':215,
            'Feasible trajectory':317,'Task–robot schedule':354,'Assembly sequence':340,'Certificates / status':336}

    def text(x,y,value,size=32,cls='text',raw=False):
        length=f' textLength="{widths[value]}" lengthAdjust="spacingAndGlyphs"' if cls=='heading' and value in widths else ''
        add(f'<text class="f74-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle"{length}>{value if raw else escape(value)}</text>')

    def lines(x,y,values,size=32,dy=39):
        for i,value in enumerate(values):text(x,y+i*dy,value,size)

    def path(d,cls='ink',extra=''):
        classes=' '.join('f74-'+v for v in cls.split())
        add(f'<path class="{classes}" d="{d}" {extra}/>')

    def rect(x,y,w,h,cls='panel',rx=7,extra=''):
        add(f'<rect class="f74-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {extra}/>')

    def circle(x,y,r,cls='node'):
        add(f'<circle class="f74-{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def arrow(d,color='ink',small=False):
        path(d,'route '+color,f'marker-end="url(#f74-{color}{"-small" if small else ""}-arrow)"')

    def image(file,x,y,w,h):
        add(f'<image href="/assets/img/figs/f74/{file}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')

    def zone(key,box,draw):
        add(f'<g class="f74-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw();rect(*box,'hit',5);add('</g>')

    def check(x,y,size=23,color='green'):
        path(f'M{x-size*.48} {y}l{size*.35} {size*.42}l{size*.64} {-size*.94}',color+' symbol')

    def cross(x,y,size=15):
        path(f'M{x-size/2} {y-size/2}l{size} {size}M{x-size/2} {y+size/2}l{size} {-size}','red symbol')

    def target(x,y,color='green',r=24):
        circle(x,y,r,color+'-target');circle(x,y,6,color+'-dot')

    def cube(x,y,s=28,d=11,color='#c8cdd2'):
        path(f'M{x} {y}l{d} {-d}h{s}l{-d} {d}Z','cube-top')
        rect(x,y,s,s,'cube-front',0,f'fill="{color}"')
        path(f'M{x+s} {y}l{d} {-d}v{s}l{-d} {d}Z','cube-side')

    def gauge(x,y,r=44,color='green'):
        path(f'M{x} {y}a{r} {r} 0 0 1 {2*r} 0Z','gauge')
        cx=x+r;angle=math.radians(38)
        ax=cx+r*math.cos(angle);ay=y-r*math.sin(angle)
        path(f'M{cx} {y}L{ax} {ay}A{r} {r} 0 0 1 {cx+r} {y}Z',color+'-sector')
        arrow(f'M{cx} {y}L{cx+r*.74} {y-r*.31}','ink',True)

    def trajectory(x,y,scale=1):
        rect(x+78*scale,y-43*scale,47*scale,53*scale,'obstacle',0)
        circle(x+196*scale,y-22*scale,21*scale,'obstacle')
        path(f'M{x+256*scale} {y+5*scale}l{52*scale} {-47*scale}l{40*scale} {47*scale}Z','obstacle')
        points=[(x,y),(x+53*scale,y+28*scale),(x+149*scale,y+25*scale),(x+227*scale,y+36*scale),(x+355*scale,y+18*scale)]
        path('M'+'L'.join(f'{a} {b}' for a,b in points),'blue flow')
        for a,b in points:circle(a,b,5.3,'blue-node')

    add('<div class="nf nf-74" data-nf="74" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 923" role="group" aria-label="Figure 7.4: constraint-based spatial solving"><defs>')
    for key,color in [('ink','#2c373d'),('blue','#4146eb'),('red','#c63d3d'),('green','#348e51')]:
        for small in [False,True]:
            suffix='-small' if small else '';w,h=(11,11) if small else (15,15)
            add(f'<marker id="f74-{key}{suffix}-arrow" markerUnits="userSpaceOnUse" markerWidth="{w}" markerHeight="{h}" refX="{w-3}" refY="{h/2}" orient="auto"><path d="M2 2L{w-3} {h/2}L2 {h-2}" fill="none" stroke="{color}" stroke-width="{3.5 if small else 4.5}" stroke-linejoin="round" stroke-linecap="round"/></marker>')
    add('</defs><rect width="2000" height="923" fill="white"/><g class="f74-scaffold">')
    rect(6,65,436,353);rect(6,468,436,348)
    path('M11 157H437M11 242H437M11 326H437M11 559H437M11 644H437M11 728H437','divider')
    text(223,40,'Decision variables',36,'heading');text(223,455,'Constraints',36,'heading')
    arrow('M458 452H520');arrow('M1445 452H1505')
    for x,label in [(225,'(i) Inputs'),(987,'(ii) Reasoning core'),(1760,'(iii) Outputs')]:text(x,895,label,36,'blue-text')
    add('</g>')

    def joints():
        image('i-inputs/joint-arm',20,77,107,79);lines(302,101,['Joint','configurations'])
    zone('joints',(13,70,424,86),joints)

    def poses():
        image('i-inputs/pose-left-finger',32,172,33,65);image('i-inputs/pose-right-finger',76,172,29,65)
        arrow('M135 207V164','green');arrow('M135 207H172','red');arrow('M135 207L113 224','blue')
        lines(302,186,['End-effector','poses'])
    zone('poses',(13,160,424,80),poses)

    def states():
        arrow('M46 289H83');arrow('M107 289H144')
        for x in [40,100,163]:circle(x,289,8,'state')
        lines(302,271,['States','over time'])
    zone('states',(13,245,424,79),states)

    def modes():
        for x,n in [(37,'1'),(93,'2'),(149,'3')]:cube(x,361);text(x+12,353,n,28)
        lines(302,356,['Discrete','modes'])
    zone('modes',(13,329,424,82),modes)

    def collision():
        image('i-constraints/collision-arm',17,482,101,74);cube(125,520,28,10);target(163,509,'red')
        lines(316,503,['Collision','avoidance'])
    zone('collision',(13,474,424,83),collision)

    def reach():
        image('i-constraints/reach-arm',17,553,122,89);target(169,590)
        lines(316,588,['IK','reachability'])
    zone('reach',(13,560,424,82),reach)

    def dynamics():
        gauge(110,713);image('i-constraints/dynamics-arm',17,652,111,76)
        lines(316,673,['Dynamics /','limits'])
    zone('dynamics',(13,646,424,80),dynamics)

    def logic():
        arrow('M62 763H86');arrow('M122 771L147 785')
        for x,y,label in [(47,763,'A'),(110,763,'B'),(166,791,'C')]:circle(x,y,14,'logic-node');text(x,y+9,label,27)
        lines(316,762,['Task logic /','timing'])
    zone('logic',(13,731,424,80),logic)

    def csp():
        rect(540,47,434,245);text(757,97,'CSP / CP',36,'heading')
        text(646,169,'x<tspan baseline-shift="sub" font-size="25">1</tspan> ∈ {1, 3}',36,'math',True)
        text(646,226,'x<tspan baseline-shift="sub" font-size="25">2</tspan> ∈ {0, 1}',36,'math',True)
        path('M841 132L778 195L752 251M778 195L816 251M841 132L901 195L932 239','edge flow')
        for x,y in [(841,132),(778,195),(901,195)]:circle(x,y,7)
        cross(752,252);cross(816,252);check(933,232)
    zone('csp',(540,47,434,245),csp)

    def sat():
        rect(1002,47,433,245);text(1218,97,'SAT / SMT',36,'heading')
        text(1143,158,'(a ∨ b)',36,'math');text(1143,219,'(¬a ∨ c)',36,'math')
        text(1330,129,'a, b, c',29);text(1330,169,'1, 0, 1',31);text(1330,225,'1, 0, 0',31)
        check(1403,151);cross(1402,212)
    zone('sat',(1002,47,433,245),sat)

    def milp():
        rect(540,317,434,242);text(757,367,'MILP / MICP',36,'heading')
        for x,label in [(635,'R1'),(738,'R2'),(848,'R3')]:
            add(f'<ellipse class="f74-region" cx="{x}" cy="455" rx="79" ry="41"/>');text(x,449,label,29)
        path('M597 471H882','blue dashed flow')
        text(754,542,'z<tspan baseline-shift="sub" font-size="25">i</tspan> ∈ {0, 1}',36,'math',True)
    zone('milp',(540,317,434,242),milp)

    def optimization():
        rect(1002,317,433,242);text(1218,379,'Trajectory optimization',36,'heading')
        trajectory(1036,459);text(1220,539,'min<tspan baseline-shift="sub" font-size="25">x</tspan> J(x)',36,'math',True)
    zone('trajectory',(1002,317,433,242),optimization)

    def ik():
        rect(540,584,434,232);text(757,631,'IK solver',36,'heading')
        image('ii-core/ik-reachable-arm',561,658,113,85);image('ii-core/ik-infeasible-arm',775,662,109,81)
        target(677,688);target(926,688,'red');check(705,718);cross(945,723)
        gauge(590,797);gauge(816,797,color='red')
        text(639,843,'Reach / limits ✓',29);text(872,843,'Infeasible ×',29)
    zone('ik',(540,584,434,267),ik)

    def tamp():
        rect(1002,584,433,232);text(1218,631,'Hybrid TAMP',36,'heading')
        for x,label in [(1023,'pick'),(1165,'move'),(1306,'place')]:rect(x,650,113,57);text(x+56,687,label,32)
        arrow('M1140 678H1157');arrow('M1281 678H1298')
        for x in [1079,1221,1362]:arrow(f'M{x} 713V741')
        path('M1171 788L1221 756L1272 788','blue dashed flow')
        cube(1068,787,23,12,'#a9c9ed');cube(1351,784,23,12,'#a9c9ed')
        image('ii-core/pick-left-finger',1051,739,28,52);image('ii-core/pick-right-finger',1081,739,29,52)
        image('ii-core/place-left-finger',1333,733,28,53);image('ii-core/place-right-finger',1364,733,29,53)
        path('M1324 810H1403')
    zone('tamp',(1002,584,433,232),tamp)

    def feasible():
        rect(1529,50,462,207);text(1760,97,'Feasible trajectory',36,'heading')
        trajectory(1564,187,.9);circle(1937,182,23,'green-ring');check(1937,181,25)
    zone('feasible',(1529,50,462,207),feasible)

    def schedule():
        rect(1529,273,462,192);text(1760,320,'Task–robot schedule',36,'heading')
        for x,y,w,color in [(1585,325,92,'#aac9ed'),(1727,325,85,'#aac9ed'),(1607,359,93,'#a5d2aa'),(1764,359,85,'#a5d2aa'),(1629,394,91,'#f1d98c'),(1802,394,85,'#f1d98c')]:
            rect(x,y,w,23,'bar',0,f'fill="{color}"')
        arrow('M1576 449H1952')
    zone('schedule',(1529,273,462,192),schedule)

    def assembly():
        rect(1529,480,462,160);text(1760,527,'Assembly sequence',36,'heading')
        cube(1576,590,34,12);cube(1730,590,34,12);cube(1740,572,19,10,'#a8cee8')
        cube(1884,590,34,12);cube(1894,572,19,10,'#a8cee8');cube(1894,550,19,10,'#b1dcae')
        arrow('M1658 571H1702');arrow('M1812 571H1855')
    zone('assembly',(1529,480,462,160),assembly)

    def certificates():
        rect(1529,656,462,164);text(1760,703,'Certificates / status',36,'heading')
        for x in [1567,1724]:
            path(f'M{x} 709h47l19 20v43h-66Z','sheet')
            for y in [731,744,757]:path(f'M{x+11} {y}h36','divider')
        circle(1630,772,19,'green-badge');check(1630,771,21)
        circle(1787,772,19,'red-badge');cross(1787,770,17)
        gauge(1868,772,color='red')
        text(1606,808,'Feasible',28);text(1767,808,'Infeasible',28);text(1913,808,'Gap',28)
    zone('certificates',(1529,656,462,164),certificates)

    add('<g class="f74-scaffold"><ellipse class="f74-satisfy" cx="987" cy="303" rx="90" ry="38"/>')
    lines(987,293,['Satisfy /','optimize'],32,38)
    add('</g></svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__=='__main__':
    (SITE/'example/figure74.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure74-1"><title>Figure 7.4 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.4 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/714_constraint.webp" alt="Original Figure 7.4"><h2>Interactive reconstruction</h2>'''+fig74()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure74-1';mountNative();</script></html>''')
