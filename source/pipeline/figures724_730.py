"""Editable, source-aligned reconstructions of Figures 7.24–7.30.

Run this module to regenerate the comparison pages. Integration is a separate,
user-approved step. Pictorial assets and source coordinates come from manifests.
"""
from pathlib import Path
from html import escape
import json
import re
from fontTools.ttLib import TTFont

_FONT = TTFont(Path(__file__).resolve().parents[2]/"assets/fonts/figure711-sans.woff2")
_CMAP = _FONT.getBestCmap()
_METRICS = _FONT["hmtx"].metrics
def text_weight(label):
    return sum(_METRICS[_CMAP.get(ord(c), "space")][0] for c in label)

SITE = Path(__file__).resolve().parents[2]
BLUE = '#4145e9'
GRAY = '#aab2b8'
INK = '#29353b'

class Figure:
    def __init__(self, number):
        self.n = number
        self.manifest = json.loads((SITE/f'assets/figures/elements/figure{number}/manifest.json').read_text())
        self.w, self.h = self.manifest['source_size']
        self.out = []
        self.info = {}
    def text(self,x,y,label,size=32,width=None,kind='',anchor='middle'):
        fit = f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="fb-{kind}" style="font-size:{size}px"{fit}>{escape(label)}</text>'
    def lines(self,x,y,labels,size=32,gap=None,width=None,kind='',anchor='middle'):
        longest=max((text_weight(v) for v in labels),default=1)
        return ''.join(self.text(x,y+i*(gap or size*1.13),v,size,round(width*text_weight(v)/longest,2) if width else None,kind,anchor) for i,v in enumerate(labels))
    def math(self,x,y,label,size=38,width=None,blue=True):
        # Keep mathematical variables italic and operators/descriptive words upright.
        # Named module subscripts (RL, LLM, percept, ...) are labels, not variables.
        def symbols(value):
            out=[]
            for token in re.split(r'([A-Za-zÎŝẑπϕθτ]+)', value):
                if not token:
                    continue
                italic = len(token) == 1 and re.fullmatch(r'[A-Za-zÎŝẑπϕθτ]', token)
                out.append('<tspan class="fb-math-italic">'+escape(token)+'</tspan>' if italic else escape(token))
            return ''.join(out)

        def expression(value):
            parts=[]
            for token in re.split(r'(_\{[^}]*\})', value):
                if token.startswith('_{'):
                    parts.append('<tspan baseline-shift="-7" font-size="70%">'+symbols(token[2:-1])+'</tspan>')
                else:
                    parts.append(symbols(token))
            return ''.join(parts)

        label=label.translate(str.maketrans({'ℳ':'M','𝒫':'P','ℱ':'F','𝒯':'T'}))
        if label.startswith('M_{') and self.n in [729,730]:
            prefix,suffix=label.split(':',1)
            label=expression(prefix)+':<tspan style="font-family:Arial,Helvetica,sans-serif;font-style:normal">'+escape(suffix)+'</tspan>'
        elif label.startswith('policy π'):
            label='<tspan style="font-family:Arial,Helvetica,sans-serif;font-style:normal">policy </tspan>'+expression('π')+'<tspan style="font-family:Arial,Helvetica,sans-serif;font-style:normal"> over long-</tspan>'
        else:
            label=expression(label)
        fit=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        return f'<text x="{x}" y="{y}" text-anchor="middle" class="fb-math'+(' fb-blue' if blue else '')+f'" style="font-size:{size}px"{fit}>{label}</text>'
    def rect(self,x,y,w,h,selected=False,rx=8,fill=None,stroke=None,sw=3):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or ("#ebecfd" if selected else "white")}" stroke="{stroke or (BLUE if selected else GRAY)}" stroke-width="{sw}"/>'
    def box(self,x,y,w,h,label,size=32,selected=False,width=None,kind='',rx=8,fill=None,stroke=None):
        labels=label if isinstance(label,list) else [label]
        return self.rect(x,y,w,h,selected,rx,fill,stroke)+self.lines(x+w/2,y+h/2+size*.34-(len(labels)-1)*size*.565,labels,size,width=width,kind=kind)
    def line(self,d,color=GRAY,sw=2,dash=None):
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
    def route(self,d,color='blue',dash=False,sw=3.5,both=False,duration=2300):
        return f'<path d="{d}" class="rl-route fb-route-{color}" style="stroke-width:{sw}px" marker-end="url(#f{self.n}-{color})"'+(f' marker-start="url(#f{self.n}-{color}-start)"' if both else '')+(' data-bidirectional="true"' if both else '')+(' stroke-dasharray="12 6"' if dash else '')+f' data-duration="{duration}"/>'
    def node(self,x,y,r=12,color='blue',solid=False):
        c=BLUE if color=='blue' else GRAY
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c if solid else "#ebecfd" if color=="blue" else "white"}" stroke="{c}" stroke-width="3.5"/>'
    def assets(self,prefix):
        out=''
        for a in self.manifest['assets']:
            if a['file'].startswith(prefix):
                x,y,x1,y1=a['source_box']
                out+=f'<image href="/assets/img/figs/f{self.n}/{a["file"]}" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/>'
        return out
    def zone(self,key,title,body,bounds,description):
        self.info[key]={'t':title,'b':description}
        x,y,w,h=bounds
        self.out.append(f'<g class="rl-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(title)}">{body}<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')
    def scaffold(self,body):self.out.append('<g class="fb-scaffold">'+body+'</g>')
    def finish(self):
        defs=''
        for name,c in [('blue',BLUE),('gray',GRAY),('ink',INK),('red','#b44949'),('cobalt','#103cd8')]:
            for start in [False,True]:
                defs+=f'<marker id="f{self.n}-{name}'+('-start' if start else '')+f'" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="'+('auto-start-reverse' if start else 'auto')+f'" markerUnits="userSpaceOnUse"><path d="M3 4L14 9L3 14Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/></marker>'
        return f'<div class="nf nf-rl nf-batch nf-{self.n}" data-nf="{self.n}" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="group" aria-label="Figure 7.{self.n-700}: interactive reconstruction"><defs>{defs}</defs><rect width="{self.w}" height="{self.h}" fill="white"/>'+''.join(self.out)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(self.info)+'</script></div>'


def fig724():
    f=Figure(724);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math
    f.scaffold(f.line('M652 30V922M1443 30V922M17 523H1980')+t(332,61,'(i) Scene + request',36,326,'heading')+t(1043,61,'(ii) Generate and execute code',36,539,'heading')+t(1724,61,'(iii) Result + evidence',36,365,'heading')+t(326,138,'Understanding',36,262,'heading')+t(185,584,'Planning',36,154,'heading'))
    z=f.assets('i-understanding/')+f.rect(208,228,110,127,rx=0,fill='none',stroke=BLUE,sw=4)+t(326,460,'Count red cubes left of the green sphere.',30,575)+r('M624 268H686')
    f.zone('understanding','Scene and spatial query',z,(31,148,658,329),'Locate red cubes, ground the green sphere, then evaluate the left-of relation. The blue box identifies the qualifying red cube. The scene is illustrative.')
    z=b(704,117,678,89,'LLM / MLLM program synthesis',36,width=512,selected=True)+b(704,231,678,191,'',32)+ln(735,282,['r = find("red cube")','g = find("green sphere")[0]','answer = count(left_of(r, g))'],31,52,anchor='start')+r('M1043 427V437')+t(1043,491,'Perception API + relation operator',30,481,'blue')+r('M1387 323H1480')
    f.zone('perception-code','Generate and execute the perception program',z,(697,109,791,397),'The model generates a short program. Object detection supplies candidate objects, a relation operator tests their positions, and count reads out the result. Incorrect module outputs can propagate into the answer.')
    z=b(1507,166,444,170,'',selected=True)+t(1729,233,'Answer: 1',36,174,'heading')+t(1729,300,'Selected object + call trace',30,378)+t(1728,417,'Inspect detections and relations',30,446)
    f.zone('answer','Answer with inspectable evidence',z,(1496,154,467,282),'One red cube satisfies the query. Inspect the selected detection and the relation call trace to check how the result was produced.')
    z=f.assets('i-planning/')+ln(492,648,['Stack red','on blue.'],32,width=141,kind='blue')+ln(492,777,['Instruction +','robot API'],30,width=180)+r('M624 699H686')
    f.zone('planning','Scene and action instruction',z,(27,601,663,302),'The instruction asks the robot to stack the red block on the blue block. The robot API exposes the actions available to an executable program.')
    z=b(704,563,678,90,'Executable action program',36,selected=True,width=449)+b(704,680,678,167,'')+ln(735,722,['robot.pick("red_block")','robot.place_on("blue_block")','obs = robot.observe()'],31,52,anchor='start')+t(1043,893,'Interpreter → controller → environment',30,510,'blue')+r('M1387 699H1480')
    f.zone('action-code','Executable action program',z,(697,555,791,350),'Execute pick, place_on, and observe through the robot API. The interpreter calls the controller, which acts on the environment and returns a new observation.')
    z=f.assets('iii-result/')+ln(1891,643,['Check','result'],30,width=91,kind='blue')+ln(1891,772,['State +','errors'],30,width=95)
    f.zone('action-result','Observe the resulting state',z,(1515,599,436,299),'The resulting scene shows red on blue. Inspect the new state and any action errors before accepting the result or revising the program.')
    z=f.line('M1959 803H1979V933',sw=2)+r('M1979 933H1043V911',sw=3,duration=4800)+t(1521,970,'Execution feedback → inspect / revise program',30,629,'blue')
    f.zone('feedback','Execution feedback',z,(1032,903,953,78),'Execution feedback returns state observations and errors to program inspection. Use the evidence to revise the program before retrying.')
    f.scaffold(t(492,970,'APIs are illustrative; module errors can propagate.',29,663))
    return f.finish()


def fig725():
    f=Figure(725);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math;n=f.node
    f.scaffold(f.line('M606 30V913M1505 30V913')+t(290,61,'(i) Scene + tool catalogue',36,442,'heading')+t(1035,61,'(ii) LLM / VLM orchestration',36,474,'heading')+t(1768,61,'(iii) Evidence and result',36,407,'heading'))
    z=b(27,123,527,114,['Place the larger blue cube','in the left compartment.'],32,selected=True,width=382)+f.assets('i-scene/')+f.rect(68,366,141,152,rx=0,fill='none',stroke=BLUE,sw=4)+f.line('M68 366H209V518H68Z',BLUE,4,'12 7')+f.rect(288,526,94,103,rx=0,fill='none',stroke=BLUE,sw=4)+t(289,829,'Tools expose input–output contracts',30,499)+m(288,896,'𝒯 = {T_{1}, …, T_{k}}',38,269)+r('M566 188H640')
    # The cabinet target uses a dashed frame, independent of the photographic plate.
    z=z.replace(f.rect(68,366,141,152,rx=0,fill='none',stroke=BLUE,sw=4),'')
    f.zone('scene','Scene, request, and tool catalogue',z,(21,114,620,795),'Select the larger blue cube and the left cabinet compartment. The tool catalogue specifies input–output contracts for each available operation.')
    z=b(661,123,752,130,'Select tool + construct arguments',36,selected=True,width=562)+m(1037,318,'(i_{t}, q_{t}) = π_{ϕ}(s_{t})',40,257)+r('M1424 148H1538')+t(1485,102,'STOP',28,72,'blue')
    f.zone('selection','Select a tool and construct its arguments',z,(653,111,891,228),'The orchestration policy selects a tool index and its arguments from the current state. STOP produces a final answer or plan with a tool-call trace.')
    z=t(851,412,'Execution',36,172,'heading')+r('M740 506L793 479')+r('M831 482L889 520')+n(720,517,11)+n(812,468,11)+n(910,532,11)+t(851,595,'Planner / robot skill',30,269)
    f.zone('execution','Execution tools',z,(709,375,295,236),'Execution tools invoke a planner or robot skill and return action status. Their results provide evidence for the next orchestration step.')
    z=t(1235,412,'Representation',36,267,'heading')+f.line('M1132 523L1231 465L1329 523',BLUE,3.5)+n(1132,523,12,'gray')+n(1231,465,12,'gray')+n(1329,523,12,'gray')+t(1235,595,'Sketch / render / scene graph',30,383)
    f.zone('representation','Representation tools',z,(1038,375,386,236),'Representation tools produce a sketch, render, or scene graph. The resulting spatial artifact can make a hypothesis easier to inspect.')
    z=t(850,673,'Validation',36,180,'heading')+b(692,723,317,74,'Solver / simulator',30,width=245)+t(750,854,'pass',30,64,'green')+t(934,854,'fail',30,43,'red')
    f.zone('validation','Validation tools',z,(681,635,339,229),'A solver or simulator evaluates constraints and feasibility. A pass or fail result becomes an inspectable check verdict.')
    z=t(1236,673,'Memory',36,145,'heading')+f.line('M1112 742H1202M1112 760H1202M1112 779H1202',GRAY,3)+r('M1218 760H1250')+f.rect(1264,723,105,77,True)+t(1235,853,'Retrieve relevant context',30,330)
    f.zone('memory','Memory tools',z,(1066,635,342,231),'Memory retrieval returns relevant prior context. Retrieval is conditioned on the current query rather than exposing the entire memory bank.')
    z=r('M1420 844H1462V188H1427',sw=3,duration=5200)+m(1038,919,'r_{t} = T_{iₜ}(q_{t})',36,171)+m(1000,988,'h_{t} = h_{t−1} ∥ (s_{t}, i_{t}, q_{t}, r_{t})',38,383)
    f.zone('history','Tool return and history update',z,(800,881,406,121),'The selected tool returns a result. Append the state, tool index, arguments, and return to history, then use the accumulated evidence to select the next tool or stop.')
    # The feedback route is interactive with the orchestration cycle; keep its hit box narrow.
    f.zone('retry','Continue orchestration',r('M1420 844H1462V188H1427',sw=3,duration=5200),(1418,175,53,681),'When more evidence is needed, the return path continues tool selection with the updated history.')
    # Avoid drawing the same return arrow twice.
    f.out[-2]=f.out[-2].replace(r('M1420 844H1462V188H1427',sw=3,duration=5200),'')
    z=b(1557,126,412,129,['Answer / plan','+ tool-call trace'],36,selected=True,width=252)+m(1762,339,'y = g(h_{T})',40,160)+t(1762,417,'Inspectable returns',32,306,'heading')+ln(1762,500,['Action status','Spatial artifact','Check verdict','Retrieved context'],32,74)+f.line('M1562 772H1964')+ln(1762,833,['Use result or retry','when evidence is insufficient'],30,28,width=394)
    f.zone('evidence','Evidence and final result',z,(1548,118,430,753),'The final answer or plan is read out from the history. Inspect action status, spatial artifacts, check verdicts, and retrieved context. Retry when the evidence is insufficient.')
    return f.finish()


def fig726():
    f=Figure(726);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math;n=f.node
    f.scaffold(f.line('M609 27V1198M1338 27V1198')+t(297,58,'(i) Inputs + memory bank',36,430,'heading')+t(972,58,'(ii) Retrieval and update',36,415,'heading')+t(1675,58,'(iii) Retrieved outputs',36,377,'heading'))
    z=b(27,111,543,104,['Where were the keys','five minutes ago?'],32,selected=True,width=306)+f.assets('i-inputs/')+t(156,533,'Kitchen: −5 min',29,205,'blue')+t(433,533,'Hallway: now',29,181)+r('M584 166H649')
    f.zone('query','A query over current and historical observations',z,(22,104,631,445),'The question refers to five minutes ago. Kitchen and hallway observations are indexed by time and place, so a historical answer must be distinguished from the current location.')
    f.scaffold(t(299,612,'Memory bank',36,239,'heading'))
    z=t(298,680,'Vector store',34,205,'heading')
    for row,label in enumerate(['view','keys','room']):
        for col in range(6): z+=f.rect(52+26*col,718+56*row,20,28,row==1,rx=0,sw=2)
        z+=t(250,739+56*row,label,29,anchor='start')
        z+=r('M500 788L405 '+str(739+56*row),'blue' if row==1 else 'gray',sw=3)
    z+=t(519,739,'query',29,77,'blue')
    f.zone('vectors','Vector memory retrieval',z,(44,646,516,222),'A query retrieves matching vector entries. The highlighted keys row illustrates selecting object-relevant context rather than unrelated views or rooms.')
    z=t(298,917,'Spatial scene graph',34,326,'heading')+b(49,945,166,56,'room',29)+b(360,945,167,56,'surface',29)+b(206,1024,167,56,'object',29,selected=True)+r('M223 972H345','gray')+r('M155 1005L205 1034','gray')+r('M421 1005L372 1034')
    f.zone('scene-graph','Spatial scene graph memory',z,(41,882,495,205),'A graph stores entities and their spatial relations. Retrieve the relevant room, support surface, and object relations together.')
    z=t(299,1133,'Episodic archive',34,271,'heading')+b(83,1151,142,53,'−5 min',28,selected=True)+b(258,1151,142,53,'−2 min',28)+b(433,1151,142,53,'now',28)
    f.zone('archive','Episodic archive',z,(75,1098,507,113),'The episodic archive retains observations from different times. The highlighted five-minute-old entry matches the temporal constraint in the query.')
    z=b(665,111,609,102,'Planner → Retriever',36,selected=True,width=315)+t(969,272,'Query by object, time and place',31,449)+r('M1286 166H1351')
    f.zone('retriever','Planner and retriever',z,(657,102,697,180),'The planner forms a retrieval request using the object, time, and place mentioned in the question. Retrieved evidence informs the answer and the next action.')
    z=t(970,357,'Spatial RAG',36,204,'heading')+r('M958 406L834 464')+r('M979 406L1103 465','gray')+r('M815 480L757 525','gray')+r('M835 479L894 524')
    for x,y,c in [(969,400,'blue'),(824,471,'blue'),(1114,471,'gray'),(747,532,'gray'),(905,532,'blue')]:z+=n(x,y,11,c)
    z+=t(970,595,'Retrieve only relevant context',30,419)
    f.zone('rag','Spatial retrieval-augmented generation',z,(731,322,483,286),'Spatial RAG selects a small set of relevant memory entries. Blue marks an illustrative selected branch; gray entries remain outside the retrieved context.')
    z=t(971,670,'Dynamic 3D scene graph',36,435,'heading')
    for d,c,dash in [('M738 764L861 714L988 772','gray',False),('M988 772L1009 849L1191 831L1145 723','blue',False),('M988 772L1145 723','blue',True)]:z+=f.line(d,BLUE if c=='blue' else GRAY,3.5,'12 6' if dash else None)
    for x,y,c in [(738,764,'gray'),(861,714,'gray'),(988,772,'blue'),(1009,849,'blue'),(1191,831,'blue'),(1145,723,'blue')]:z+=n(x,y,13,c)
    z+=t(971,920,'Select subgraph; revise relations',30,451)
    f.zone('dynamic-graph','Dynamic 3D scene graph',z,(717,635,496,296),'Select the relevant subgraph and revise relations as observations change. A dashed link marks an illustrative relation being considered or updated.')
    z=t(972,990,'Layered / unified memory',36,446,'heading')
    for x,label,sel in [(689,'Working',True),(883,'Recent',False),(1077,'Long-term',False)]:z+=b(x,1028,179,68,label,30,selected=sel)
    z+=r('M872 1062H881')+r('M1065 1062H1075')+r('M889 1102H874','gray')+r('M1083 1102H1068','gray')+t(972,1166,'Retrieve, consolidate, update',30,403)
    f.zone('layers','Layered and unified memory',z,(681,957,584,222),'Working, recent, and long-term memory exchange relevant context. Retrieval, consolidation, and update keep the memory useful across different time scales.')
    z=t(1672,141,'Action plan',36,197,'heading')+r('M1451 218L1523 238')+r('M1568 238L1641 212')+n(1428,209,10)+n(1547,246,10)+n(1665,202,10)+t(1834,234,'Go → inspect',31,177)+t(1673,306,'Historical lead; recheck before acting',30,491)
    f.zone('plan','A historical lead for the action plan',z,(1410,105,520,214),'Retrieved history provides a lead for where to inspect. Recheck the current scene before acting because historical object locations may no longer be valid.')
    z=t(1673,400,'Retrieved subgraph',36,341,'heading')+b(1385,434,222,71,'kitchen',30)+b(1705,434,222,71,'counter',30)+b(1542,557,222,71,'keys',30,selected=True)+r('M1617 469H1689','gray')+r('M1786 516L1740 547')+t(1547,548,'−5 min',29,86,'blue')
    f.zone('subgraph','Retrieved spatial subgraph',z,(1379,365,558,272),'The retrieved subgraph links the kitchen, counter, and keys. The time label ties this relation to the observation from five minutes ago.')
    z=t(1674,721,'Episodic evidence',36,320,'heading')+f.assets('iii-evidence/')+t(1796,808,'5 min ago:',30,151,'blue')+ln(1796,869,['Keys on the','kitchen counter'],30,width=224)
    f.zone('episodic-evidence','Episodic visual evidence',z,(1392,686,543,281),'The stored kitchen image supports the historical claim that the keys were on the counter. This evidence should not be confused with a live observation.')
    z=t(1672,1050,'Strategy / cognitive map',36,422,'heading')+b(1385,1083,569,84,'Search recently visited places first',30,selected=True,width=480)
    f.zone('strategy','Search strategy from memory',z,(1377,1015,586,162),'Memory can guide a search strategy: inspect recently visited places first while verifying whether the object is still there.')
    f.scaffold(f.line('M1371 345H1970M1371 665H1970M1371 997H1970'))
    f.zone('update','Update the memory',m(1001,1255,'ℳ_{t} = Write(ℳ_{t−1}, o_{t}, s_{t}, c_{t})',38,443),(773,1216,457,56),'Write new observations, inferred state, and context back to memory. Memory should evolve as new evidence arrives.')
    return f.finish()


def fig727():
    f=Figure(727);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math;n=f.node
    f.scaffold(f.line('M548 36V829M1434 36V829M20 859H1980',sw=2.5)+t(272,61,'(i) Inputs',36,159,'heading')+t(990,61,'(ii) Agentic orchestration',36,434,'heading')+t(1707,61,'(iii) Outputs',36,206,'heading')+t(1000,910,'Complementary mechanisms supporting the loop',36,869,'heading')+f.line('M500 953V1263M1000 953V1263M1500 953V1263'))
    z=ln(272,139,['Find the keys, then','unlock the front door.'],34,width=340,kind='blue')+f.assets('i-inputs/')+t(272,555,'Current observation + robot state',30,432)+m(272,617,'o_{t},  (θ_{1}, …, θ_{7})',36,274,False)+r('M562 277H600')
    f.zone('inputs','Task and current observation',z,(48,100,555,529),'Find the keys and then unlock the front door. The input combines the current visual observation with the robot state. New observations may change the plan.')
    z=t(271,685,'Tools + external memory',32,386,'heading')+t(271,742,'search() · pick() · navigate()',29,360)+f.line('M64 797L151 775L209 809',GRAY,3)+n(64,797,11)+n(151,775,11)+n(209,809,11)+t(134,845,'Scene graph',29,161)+t(363,845,'Vectors',29,103)
    for row in range(3):
        for col in range(5):z+=f.rect(292+31*col,770+16*row,23,10,rx=0,fill=BLUE if (row+col)%3==1 else '#ebecfd',stroke='none',sw=0)
    f.zone('tools','Tools and external memory',z,(44,650,452,200),'Search, pick, and navigate tools ground the agent in the environment. A scene graph and vector memory provide external context for planning.')
    f.zone('core','Planning core and policy',b(609,107,760,94,'',selected=True)+m(990,163,'Planning core 𝒫 + policy π',40,424),(600,99,778,112),'A planning core and policy coordinate the perceive, reason, act, and reflect loop. The current history and observations guide the next decision.')
    for key,x,y,title,formula,selected,desc in [
        ('perceive',618,261,'1 Perceive','o_{t} = Perceive(env)',False,'Perception transforms the current environment into an observation. This stage grounds reasoning in evidence from the scene.'),
        ('reason',1037,261,'2 Reason','s_{t} = 𝒫(o_{t}, h_{t−1})',True,'Reasoning combines the new observation and history to infer a useful state and decide what should happen next.'),
        ('act',1037,499,'3 Act','a_{t} ∼ π(· | s_{t})',False,'The policy selects an action conditioned on the inferred state. Executing it changes the environment and makes new feedback available.'),
        ('reflect',618,499,'4 Reflect','r_{t} = ℱ(s_{t}, a_{t}, o_{t+1})',False,'Reflection compares the action and its new observation with the expected result. Feedback can revise the state and the next plan.')]:
        z=b(x,y,339,157,'',selected=selected)+t(x+169.5,y+59,title,36,{'1 Perceive':190,'2 Reason':173,'3 Act':98,'4 Reflect':166}[title],'heading')+m(x+169.5,y+122,formula,35,282 if key=='reflect' else 257,False)
        paths={'perceive':'M969 339H1021','reason':'M1206 430V479','act':'M1025 579H973','reflect':'M788 487V435'}
        z+=r(paths[key])
        f.zone(key,title,z,(x-8,y-8,411 if key in ['perceive','reflect'] else 347,219 if key=='reason' else 174),desc)
    f.scaffold(t(993,478,'observe → execute → revise',29,343,'blue'))
    z=t(990,728,'Environmental feedback updates history',30,559)+m(990,800,'h_{t} = h_{t−1} ∪ {(o_{t}, s_{t}, a_{t}, r_{t})}',38,442)
    f.zone('history','Environmental feedback and history',z,(702,690,579,123),'Append observations, inferred state, actions, and feedback to the agent history. The updated history affects the next pass through the loop.')
    z=t(1707,140,'Action sequence / revised plan',32,479,'heading')+r('M1384 277H1452')
    for d in ['M1523 203L1621 230','M1646 230L1751 201','M1775 202L1889 230']:z+=r(d)
    for x,y,label in [(1511,200,'search'),(1634,234,'pick'),(1763,198,'go'),(1901,234,'unlock')]:z+=n(x,y,11,solid=True)+t(x,y+54,label,29)
    f.zone('plan','Action sequence and revised plan',z,(1380,105,565,192),'The illustrative plan searches for the keys, picks them up, travels to the door, and unlocks it. Feedback can revise this sequence.')
    z=t(1707,350,'Accumulated skills',32,300,'heading')
    for x,y in [(1507,412),(1523,391),(1538,369)]:z+=b(x,y,382,59,'')
    z+=t(1729,406,'unlock_door()',31,224,'blue')
    f.zone('skills','Accumulated skills',z,(1498,315,432,167),'Reusable skills such as unlock_door() can accumulate over tasks. Their validity still depends on the current state and preconditions.')
    z=t(1707,520,'Predicted states (optional)',32,413,'heading')+b(1486,554,136,68,'closed',30,selected=True)+b(1655,554,136,68,'unlocked',30,selected=True)+b(1840,554,136,68,'open',30,selected=True)+r('M1630 588H1640')+r('M1803 588H1825')
    f.zone('prediction','Optional predicted states',z,(1478,486,506,147),'A model can predict a progression from closed to unlocked to open. These are candidate future states, not a replacement for observing execution.')
    z=t(1707,689,'Feedback example',32,298,'heading')+t(1707,746,'“Keys not on counter”',32,326,'red')+t(1707,803,'→ Search the hallway',32,307,'blue')
    f.zone('feedback','Feedback revises the search',z,(1527,655,366,161),'A failed expectation, such as keys missing from the counter, prompts a revised search location. The agent should update its state rather than repeat the same assumption.')
    f.scaffold(t(250,978,'(a) Spatial grounding',36,361,'heading')+t(750,978,'(b) Interactive feedback',36,417,'heading')+t(1250,978,'(c) Multi-agent sharing',36,394,'heading')+t(1750,978,'(d) Action + world models',36,445,'heading'))
    z=b(34,1013,160,73,'console',30)+b(283,1013,148,73,'keys',30,selected=True)+r('M272 1049H206')+t(240,1020,'on',29)+t(250,1143,'Affordance · coordinates · graph',29,416)+b(68,1166,363,68,'Reachable → pick',32,selected=True,width=258)
    f.zone('grounding','Spatial grounding',z,(27,1000,452,243),'Ground an object in a support relation, coordinate system, and affordance. Reachability determines whether a pick action is available.')
    z=b(538,1015,185,77,'Attempt',32)+b(781,1015,176,77,'Critique',32)+r('M735 1052H767','red')+r('M868 1095V1136H630V1108','red',sw=3)+t(750,1186,'Revise state + retry',32,279,'blue')+t(750,1248,'ReAct · Reflexion · DEPS',29,311)
    f.zone('interactive-feedback','Interactive feedback',z,(529,1005,439,252),'An attempted action receives critique. Use the critique to revise the state and retry; the red return path closes the feedback loop.')
    z=r('M1116 1056L1213 1094')+r('M1383 1056L1287 1094')+r('M1249 1134V1144')+n(1086,1050,20)+n(1249,1105,20)+n(1412,1050,20)+t(1250,1204,'Shared map / reference frame',30,414)+t(1250,1253,'Align perspectives + coordinate',29,402)
    f.zone('sharing','Multi-agent sharing',z,(1034,1008,432,255),'Agents share a map or reference frame. Align perspectives and coordinates before combining observations or coordinating actions.')
    z=b(1542,1013,169,76,'VLA',36,selected=True)+r('M1722 1052H1778')+t(1877,1060,'action',32)+b(1582,1123,92,68,'',selected=True)+b(1732,1123,93,68,'',selected=True)+b(1883,1123,93,68,'',selected=True)+m(1628,1167,'z_{t+0}',32,62,False)+m(1779,1167,'z_{t+1}',32,62,False)+m(1930,1167,'z_{t+2}',32,62,False)+r('M1686 1158H1717')+r('M1837 1158H1868')+t(1750,1254,'Simulate → assess → select',30,370)
    f.zone('world-action','Action and world models',z,(1534,1005,450,260),'A vision-language-action model produces actions. A world model can roll out future latent states so candidate actions can be simulated, assessed, and selected.')
    return f.finish()


def fig728():
    f=Figure(728);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math;n=f.node
    f.scaffold(f.line('M603 36V551M1311 36V551M500 664V1067M1001 664V1067M1501 664V1067')+t(292,59,'(i) Query + context',36,320,'heading')+t(956,59,'(ii) World model as a tool',36,459,'heading')+t(1657,59,'(iii) Spatial readout',36,350,'heading'))
    z=f.assets('i-query/')+ln(455,169,['Stack red','on blue.'],34,width=149,kind='blue')+ln(455,272,['Goal /','spatial query'],30,width=182)+t(165,462,'Initial observation',30,234)+t(452,465,'Scene geometry',30,214)+m(295,533,'c, q;   a_{0:T−1} (optional)',36,365,False)+r('M615 261H633')+r('M364 418V339','gray',sw=3)+r('M371 426H500','gray',sw=3)+f.rect(398,382,38,38,rx=0,fill='#f5dfe0',stroke='#b44949')+f.rect(464,382,37,38,rx=0,fill='#ebecfd',stroke=BLUE)
    f.zone('query','Query and scene context',z,(12,130,622,417),'The query asks for red on blue. Context can include the current observation, scene geometry, and an optional candidate action sequence.')
    z=b(649,140,613,239,'',selected=True)+t(956,208,'Pretrained simulator',36,367,'heading')+m(956,279,'ℙ(s_{0:T} | a_{0:T−1}, c)',40,286)+t(956,344,'Full states or partial observations',30,436)+t(956,449,'Query → imagine / predict',32,378,'blue')+t(956,511,'Construction and training: §8.6',30,432)+r('M956 553V587')
    f.zone('simulator','World model as a pretrained simulator',z,(641,132,629,456),'Condition the simulator on scene context and candidate actions to predict full states or partial observations. The figure describes the inference interface; model construction and training are discussed separately.')
    z=m(1645,154,'y = g(c, f)',44,197)+t(1648,236,'Understanding: inferred relation',32,508,'heading')+b(1355,264,165,75,'red',32,fill='#f5dfe0')+b(1750,264,165,75,'blue',32,selected=True)+r('M1532 302H1734',sw=3)+t(1638,273,'on',30)
    f.zone('relation','Read out the inferred spatial relation',z,(1347,113,577,236),'A readout combines context with predictive feedback to infer a relation. Here the inferred relation is red on blue.')
    z=t(1648,409,'Planning: selected plan / policy',32,492,'heading')+b(1349,441,162,75,'pick',32,stroke=BLUE)+b(1563,441,162,75,'move',32,stroke=BLUE)+b(1778,441,162,75,'place',32,stroke=BLUE)+r('M1523 479H1547')+r('M1737 479H1762')
    f.zone('plan','Read out a selected plan or policy',z,(1341,375,608,152),'Compare predictive feedback to select a pick, move, and place plan. Predictions support action selection but still require checks against real execution.')
    z=f.line('M248 603H1751',BLUE,4)+t(1408,582,'Predictive feedback interfaces',29,431,'blue')
    for x in [248,749,1249,1750]:z+=r(f'M{x} 612V649')
    f.zone('interfaces','Predictive feedback interfaces',z,(235,562,1531,92),'The same world model can expose predicted images, structured states, action trajectories, or latent embeddings as feedback to a downstream readout.')
    for x,label,width in [(248,'(a) Future observations',409),(750,'(b) Future states',291),(1250,'(c) Action trajectories',381),(1750,'(d) Predictive latents',389)]:f.scaffold(t(x,706,label,36,width,'heading'))
    z=t(248,760,'Imagined frames / viewpoints',29,382)+f.assets('a-observations/')+r('M233 861H264')+m(125,990,'Î_{t}',36,32,False)+m(379,990,'Î_{t+1}',36,58,False)+t(248,1034,'Pixels → spatial evidence',32,365,'blue')
    f.zone('observations','Future observations',z,(19,731,461,314),'Predicted frames or viewpoints provide pixel-based evidence about a possible future. The two frames illustrate a red block being stacked on blue.')
    z=t(749,774,'Pose / geometry over time',30,365)+f.line('M545 896H710M791 896H956',GRAY,3)+f.rect(559,849,48,46,rx=0,fill='#f5dfe0',stroke='#b44949')+f.rect(643,849,48,46,rx=0,fill='#ebecfd',stroke=BLUE)+f.rect(888,848,48,47,rx=0,fill='#ebecfd',stroke=BLUE)+f.rect(888,802,48,47,rx=0,fill='#f5dfe0',stroke='#b44949')+r('M727 849H765')+m(631,948,'s_{t}',36,29,False)+m(879,948,'ŝ_{t+1}',36,54,False)+t(749,1034,'Structured / 4D rollout',32,334,'blue')
    f.zone('states','Future structured states',z,(536,740,431,305),'A structured rollout predicts object pose and geometry over time. This interface exposes state changes without requiring a rendered image.')
    z=r('M1065 855L1173 798')+r('M1198 793H1362')+r('M1065 868L1174 910','gray')+r('M1198 914H1362','gray')+n(1053,861,11,solid=True)+n(1184,793,11,solid=True)+n(1374,793,11,solid=True)+n(1184,914,11,'gray')+n(1374,914,11,'gray')+t(1414,800,'✓',35,kind='green')+t(1414,922,'×',30,kind='red')+t(1249,978,'Roll out → score → select',30,350)+t(1249,1034,'Action-conditioned futures',32,400,'blue')
    f.zone('trajectories','Candidate action trajectories',z,(1034,763,414,284),'Roll out candidate action-conditioned futures, score them, and select a feasible trajectory. Blue is an illustrative accepted path; gray is a rejected alternative.')
    z=b(1641,789,156,74,'Predict',32,selected=True)+r('M1615 827H1625')+r('M1809 827H1841')
    for x,vals in [(1560,[1,0,1,0]),(1858,[1,1,0,1])]:
        for i,val in enumerate(vals):z+=f.rect(x,787+26*i,47,20,rx=0,fill=BLUE if val else '#ebecfd',sw=1.5)
    z+=m(1584,943,'z_{t}',36,29,False)+m(1881,943,'ẑ_{t+1}',36,59,False)+t(1744,1034,'Embedding; no pixel decoding',32,420,'blue')
    f.zone('latents','Predictive latent embeddings',z,(1525,764,444,281),'Predict future latent embeddings directly. This interface can support a spatial readout without decoding pixels.')
    z=f.line('M749 1053V1082M1249 1053V1082M1750 1053V1082',BLUE,3)+r('M248 1053V1082H1971V140H1853',sw=3,duration=6500)+m(1873,109,'f',36,20)
    f.zone('predictive-feedback','Return predictive feedback to the readout',z,(1956,130,28,965),'Predictive feedback from the four interfaces returns to the spatial readout. The readout uses it for understanding or planning. This is model feedback, not a new observation from the real environment.')
    return f.finish()


def fig729():
    f=Figure(729);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math
    for key,x,y,w,h,prefix,labels,desc in [
        ('controller',16,5,354,387,'rl-controller/',[], 'The RL controller maintains a policy over long-horizon decisions. Policy proposals and executed trajectories connect control with the hypothesis generator.'),
        ('hypothesis',799,2,403,387,'hypothesis/',[], 'The LLM or VLM proposes hypotheses and policy refinements. It exchanges evidence with the controller and a physics or symbolic verifier.'),
        ('verification',1630,5,354,387,'verification/',[], 'A physics engine or symbolic solver checks the feasibility of a hypothesis and returns a verdict with a rationale.')]:
        z=f.rect(x,y,w,h,rx=30,stroke='#080808',sw=2)+f.assets(prefix)
        if key=='controller':z+=m(193,263,'ℳ_{RL}: RL controller,',36,310,False)+m(193,307,'policy π over long-',36,291,False)+t(193,352,'horizon decisions',36,294)
        if key=='hypothesis':z+=m(1000,285,'ℳ_{LLM}: Hypothesis',36,308,False)+t(1000,330,'generator (LLM / VLM)',36,349)
        if key=='verification':z+=m(1807,263,'ℳ_{verify}: Physics',36,269,False)+ln(1807,309,['engine / symbolic','solver'],36,46,width=285)
        f.zone(key,{'controller':'RL controller','hypothesis':'Hypothesis generator','verification':'Physics and symbolic verifier'}[key],z,(x,y,w,h),desc)
    for key,title,d,x,y,labels,width,desc in [
        ('proposal','Policy proposal and refinement','M798 94H372',592,80,['Policy proposal →','refinement'],286,'The hypothesis generator proposes a policy refinement to the RL controller.'),
        ('trajectory','Executed trajectory and next state','M371 325H797',587,307,['Executed trajectory →','next state'],351,'The executed trajectory and next state provide grounded evidence for the hypothesis generator.'),
        ('check','Hypothesis feasibility check','M1203 94H1628',1418,80,['hypothesis→','feasibility check'],263,'The generator sends a hypothesis to a physics engine or symbolic solver for a feasibility check.'),
        ('verdict','Verdict and rationale','M1629 325H1204',1417,315,['Verdict + rationale →','refinement'],363,'The verifier returns a verdict and rationale. The generator can use this evidence to refine its hypothesis.')]:
        z=r(d,'cobalt',sw=4)+ln(x,y,labels,36,46,width=width)
        f.zone(key,title,z,(x-width/2-8,y-37,width+16,99),desc)
    z=b(326,474,1348,89,'',rx=7,fill='#eef1f5',stroke='#080808')+t(1000,535,'Reward + verification signal → orchestration policy π update',36,1030,'cobalt')+r('M326 519H193V394','cobalt',True,4,duration=3500)+r('M1674 519H1807V394','cobalt',True,4,duration=3500)
    f.zone('update','Reward and verification update the orchestration policy',z,(183,394,1635,170),'Reward and verification signals update the orchestration policy. The dashed return paths connect this update with the controller and verification modules.')
    return f.finish()


def fig730():
    f=Figure(730);t=f.text;ln=f.lines;b=f.box;r=f.route;m=f.math
    for key,x,y,w,h,prefix,title,desc in [
        ('perception',68,83,468,418,'perception/','Perception module','Perception extracts visual, depth, or segmentation evidence for the central hypothesis generator.'),
        ('hypothesis',751,133,533,439,'hypothesis/','Hypothesis generator','The LLM or VLM coordinates specialist modules, proposes hypotheses, and revises them using returned evidence.'),
        ('world',1478,83,468,418,'world/','World model','The world model predicts consequences and provides simulated spatial feedback to the hypothesis generator.'),
        ('symbolic',73,626,468,485,'symbolic/','Symbolic and constraint solver','Symbolic, PDDL, or constraint tools check explicit relations and action preconditions.'),
        ('action',778,730,468,381,'action/','Action and rendering module','An action, rendering, or execution module grounds a proposal in an executable operation and returns its result.'),
        ('memory',1482,626,468,485,'memory/','Spatial memory','Spatial memory retrieves relevant prior observations, maps, and relations for the current hypothesis.')]:
        z=f.rect(x,y,w,h,rx=34,stroke='#080808',sw=2.5)+f.assets(prefix)
        if key=='perception':z+=m(302,333,'ℳ_{percept}: perception',46,449,False)+ln(302,397,['(vision, depth,','segmentation)'],44,58,width=288)
        if key=='hypothesis':z+=m(1017,477,'ℳ_{LLM}: Hypothesis',46,418,False)+t(1017,535,'generator (LLM / VLM)',44,471)
        if key=='world':z+=m(1712,433,'ℳ_{world}: world model',46,452,False)
        if key=='symbolic':z+=m(307,936,'ℳ_{symb}: symbolic /',46,404,False)+ln(307,995,['PDDL / constraint','solver'],44,60,width=380)
        if key=='action':z+=m(1012,997,'ℳ_{act}: action /',46,329,False)+t(1012,1056,'renderer / executor',44,425)
        if key=='memory':z+=m(1717,966,'ℳ_{mem}: spatial',46,315,False)+t(1717,1025,'memory',44,179)
        f.zone(key,title,z,(x,y,w,h),desc)
    for key,title,d,bounds,desc in [
        ('vision-exchange','Perception and hypothesis exchange','M543 309L731 377',(537,300,199,88),'The hypothesis generator requests perceptual evidence and receives grounded visual information.'),
        ('world-exchange','World model and hypothesis exchange','M1315 351L1442 321',(1308,308,142,57),'World-model predictions and queries flow between the specialist and the hypothesis generator.'),
        ('symbolic-exchange','Symbolic reasoning exchange','M540 664L731 548',(533,539,204,133),'The symbolic module receives a candidate constraint problem and returns an explicit result.'),
        ('action-exchange','Action and execution exchange','M1001 575V728',(983,574,36,155),'The central generator submits executable operations and receives execution or rendering feedback.'),
        ('memory-exchange','Spatial memory exchange','M1315 548L1442 648',(1308,539,142,119),'Memory queries and retrieved context flow between the generator and the spatial memory module.')]:
        f.zone(key,title,r(d,'cobalt',sw=5.5,both=True),bounds,desc)
    z=r('M1463 55H1934Q1995 55 1995 118V1082Q1995 1144 1934 1144H67Q5 1144 5 1082V118Q5 55 66 55H583','cobalt',sw=7,duration=11000)+'<path d="M583 24L618 55L583 86Z" fill="#103cd8"/>'+f.line('M618 55H673','#103cd8',7)+t(1058,66,'Perceive → Reason → Act → Reflect',46,744,'cobalt')
    f.zone('cycle','Perceive, reason, act, and reflect',z,(677,14,779,63),'The outer loop coordinates perception, reasoning, action, and reflection. Specialist modules contribute evidence to a continuing cycle rather than a single one-way pass.')
    return f.finish()


FIGURES={724:fig724,725:fig725,726:fig726,727:fig727,728:fig728,729:fig729,730:fig730}


def comparison(number):
    f=Figure(number)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.'+str(number-700)+' comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figures724-730-4"><style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:white}nav{font:16px Arial;display:flex;gap:18px;flex-wrap:wrap}a{color:#3046c9}@media(max-width:600px){body{margin:12px}}</style><main><nav><a href="/example/figures724-730.html">All figures</a><a href="#redraw">Jump to reconstruction</a></nav><h1>Figure 7.'+str(number-700)+' · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'+f.manifest['source']+f'" width="{f.w}" height="{f.h}" alt="Original Figure 7.{number-700}"><h2 id="redraw">Interactive reconstruction</h2>'+FIGURES[number]()+'</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=figures724-730-4";mountNative();</script></html>'


def main():
    for number in FIGURES:
        (SITE/f'example/figure{number}.html').write_text(comparison(number))
        (SITE/f'source/pipeline/figure{number}.py').write_text(f'"""Figure 7.{number-700} reconstruction, shared batch generator."""\nfrom figures724_730 import fig{number}\n')
    titles=['Code / DSL spatial reasoning','Tool-augmented spatial reasoning','Retrieval and memory-augmented reasoning','Agentic spatial reasoning','World-model-based spatial reasoning','Foundation model and RL hybrid','Agentic hybrid orchestration']
    out=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 7.24–7.30 · Reconstruction review</title><link rel="stylesheet" href="/assets/css/site.css?v=figures724-730-4"><style>body{margin:24px;background:#f4f6f8;color:#29353b;font-family:Arial}main{max-width:2000px;margin:auto}h1{font-size:24px}h2{font-size:20px}section{background:white;margin:28px 0;padding:18px}nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#3046c9}@media(max-width:600px){body{margin:12px}section{padding:6px}}</style><main><h1>Figures 7.24–7.30 · Interactive reconstruction review</h1><nav>']
    out += [f'<a href="#f{n}">7.{n-700}</a>' for n in FIGURES]
    out += ['</nav>']
    for n,title in zip(FIGURES,titles):out += [f'<section id="f{n}"><h2><a href="/example/figure{n}.html">Figure 7.{n-700} · {title} · Compare with original</a></h2>'+FIGURES[n]()+'</section>']
    out += ['</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=figures724-730-4";mountNative();</script></html>']
    (SITE/'example/figures724-730.html').write_text(''.join(out))
    print('Generated 7 comparison pages and the batch review.')

if __name__=='__main__':main()
