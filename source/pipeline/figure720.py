"""Figure 7.20: independently drawn multi-agent tasks and mechanisms."""
from pathlib import Path
from html import escape
import json
SITE=Path(__file__).resolve().parents[2]
ORIGINAL='assets/figures/figures/part3/section7/multi-agent_spatial_reasoning.webp'
INFO={
 'cooperation':('Cooperative micromanagement','Agents act from partial local observations. Their individual actions must combine into coordinated team tactics, as illustrated by the converging blue arrows.'),
 'forecasting':('Interactive motion forecasting','Observed motion histories condition several possible future trajectories for each vehicle. Dashed blue paths represent candidate futures rather than executed actions.'),
 'patrol':('Resilient multi-robot patrol','When agent 5 is lost, the surviving agents reconfigure their coordination links to maintain spatial coverage. Red identifies the lost agent; dashed links show affected connections.'),
 'critic':('Centralized critic, local execution','During training, a joint-action critic can use global state and the agents’ actions. At execution time, each agent uses its own local policy. MADDPG and COMA exemplify this training arrangement.'),
 'decomposition':('Value decomposition','VDN sums per-agent values. QMIX instead learns a state-aware monotonic mixer, with ∂Qtot/∂Qi ≥ 0, so that local greedy choices agree with the joint value maximization.'),
 'graph':('Graph coordination','An agent aggregates messages from its neighbors, using local topology and communication. Dashed edges indicate intermittent interactions; the blue arrows show messages entering the highlighted agent.'),
 'attention':('Sequence attention','Attention relates agents across observed time. Blue connections select context for an output action or forecast. An execution-time access mask limits which observations are available.')}
def fig720():
 o=[];a=o.append
 def t(x,y,v,size=32,cls='',raw=False,width=None):
  return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}" style="font-size:{size}px"'+(f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else '')+'>'+ (v if raw else escape(v))+'</text>'
 def line(d,cls='f720-ink'):return f'<path d="{d}" class="{cls}"/>'
 def route(d,gray=False,head=True):return f'<path d="{d}" class="rl-route'+(' f720-gray' if gray else '')+'"'+(f' marker-end="url(#f720-{"gray" if gray else "blue"})"' if head else '')+'/>'
 def box(x,y,w,h,blue=False):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="f720-box'+(' f720-selected' if blue else '')+'"/>'
 def circle(x,y,r,blue=False,red=False):return f'<circle cx="{x}" cy="{y}" r="{r}" class="f720-node'+(' f720-selected' if blue else '')+(' f720-lost' if red else '')+'"/>'
 def sub(v,s):return v+f'<tspan baseline-shift="sub" font-size="70%">{s}</tspan>'
 def zone(k,body,b):
  x,y,w,h=b;a(f'<g class="rl-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k][0])}">{body}<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/></g>')
 a('<div class="nf nf-rl nf-720" data-nf="720" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1134" role="group" aria-label="Figure 7.20: multi-agent spatial reasoning tasks and mechanisms"><defs>')
 for name,color in [('blue','#4145e9'),('gray','#aab2b8')]:a(f'<marker id="f720-{name}" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M3 3L12 8L3 13" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 a('</defs><rect width="2000" height="1134" fill="white"/><g class="f720-scaffold">'+line('M667 31V461M1334 31V461M15 492H1984M500 514V1102M1001 514V1102M1501 514V1102','f720-divider')+'</g>')
 body=t(333,64,'(a) Cooperative micromanagement',38,'f720-heading',width=640)
 body+='<rect x="32" y="136" width="214" height="191" fill="#f0f2f4"/>'
 body+=line('M154 128C179 160 179 198 151 234C176 270 173 309 149 337M270 186C299 224 294 260 271 289','f720-dashed f720-gray')
 for x,y in [(94,178),(210,237),(90,285)]:body+=circle(x,y,18,True)
 for x,y in [(534,162),(408,224),(525,295)]:body+=f'<path d="M{x} {y-12}L{x+11} {y+11}H{x-11}Z" class="f720-triangle"/>'
 for path in ['M132 180L371 216','M249 236L371 225','M122 287L246 317']:body+=route(path)
 body+=t(136,382,'Local sight',width=158)+t(463,382,'Joint tactics',32,'f720-blue',width=173)+t(333,443,'SMAC: coordinated actions',34,width=425)
 zone('cooperation',body,(16,23,638,433))
 body=t(1001,64,'(b) Interactive motion forecasting',38,'f720-heading',width=618)
 body+=line('M718 145H1281M718 298H1281','f720-road')+line('M719 223H1281','f720-dashed f720-gray')
 body+=line('M762 188H829M918 275H984')
 for file,x,y,w,h in [('vehicle-upper.png',828,171,55,34),('vehicle-lower.png',983,258,56,34)]:body+=f'<image href="/assets/img/figs/f720/b-motion-forecasting/{file}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
 for path in ['M883 188Q973 184 1059 159','M883 188H1057','M883 188Q973 193 1059 217','M1039 275Q1127 271 1213 246','M1039 275H1213','M1039 275Q1127 280 1213 305']:body+=route(path,head=False).replace('class="rl-route','class="rl-route f720-future')
 body+=t(1000,378,'History → possible futures',32,'f720-blue',width=374)+t(1000,443,'WOMD / nuScenes: prediction',34,width=469)
 zone('forecasting',body,(692,23,622,435))
 body=t(1667,64,'(c) Resilient multi-robot patrol',38,'f720-heading',width=561)
 body+=line('M1438 227L1590 149L1797 175L1892 321','f720-topology')+line('M1438 227L1593 330L1892 321','f720-dashed f720-gray')
 body+=line('M1565 357L1621 303','f720-loss-mark')
 for x,y,num in [(1438,227,1),(1590,149,2),(1797,175,3),(1892,321,4),(1593,330,5)]:body+=circle(x,y,24,blue=num!=5,red=num==5)+t(x,y+9,str(num),30)
 body+=route('M1448 225L1784 177')+route('M1448 231L1879 317')
 body+=t(1668,400,'Reconfigure after agent loss',32,'f720-blue',width=415)+t(1667,459,'Maintain spatial coverage',34,width=400)
 zone('patrol',body,(1361,23,620,444))
 body=t(250,557,'(d) Centralized critic',38,'f720-heading',width=378)
 for x,num in [(29,1),(188,2),(347,3)]:
  body+=box(x,625,123,88,True)+t(x+61,679,sub('π',str(num)),44,'rl-math',True)
  body+=f'<path d="M{x+61} 605L{x+66} 616H{x+56}Z" class="f720-action"/>'
 for path in ['M99 719L237 766','M249 725V757','M399 719L263 766']:body+=route(path,True)
 body+=box(90,767,318,94)+t(249,824,'Joint-action critic',34,width=266)+t(249,916,'Global state + actions',32,width=320)+t(249,986,'Critic used in training',32,'f720-blue',width=310)+t(249,1050,'MADDPG / COMA',38,'f720-heading',width=320)+t(249,1103,'Execute local policies',30,width=318)
 zone('critic',body,(20,524,461,586))
 body=t(750,557,'(e) Value decomposition',38,'f720-heading',width=448)
 for x,label in [(531,'1'),(693,'2'),(855,'n')]:body+=box(x,625,117,88)+t(x+58,679,sub('Q',label),44,'rl-math',True)
 for path in ['M598 719L738 767','M751 725V758','M905 719L765 767']:body+=route(path,True)
 body+=box(596,767,311,94,True)+t(751,824,'State-aware mixer',34,width=283)
 body+=t(751,937,sub('Q','tot')+' = ∑<tspan baseline-shift="sub" font-size="70%">i</tspan> '+sub('Q','i')+'　<tspan font-style="normal">(VDN)</tspan>',42,'rl-math',True)
 body+=t(635.5,990,'∂Q<tspan baseline-shift="-4" font-size="70%">tot</tspan>',30,'rl-math f720-blue',True,width=72)+line('M598 1003H673','f720-fraction')+t(635.5,1030,'∂Q<tspan baseline-shift="-4" font-size="70%">i</tspan>',30,'rl-math f720-blue',True,width=60)+t(793,1012,'≥ 0　<tspan font-style="normal">(QMIX)</tspan>',38,'rl-math f720-blue',True)
 body+=t(751,1094,'Local greedy execution',30,width=339)
 zone('decomposition',body,(515,524,470,586))
 body=t(1250,557,'(f) Graph coordination',38,'f720-heading',width=408)
 body+=line('M1069 726L1195 629L1360 677','f720-topology')+line('M1360 677L1421 797','f720-dashed f720-gray')
 for x,y in [(1069,726),(1195,629),(1360,677),(1421,797),(1208,800)]:body+=circle(x,y,18,blue=x==1208)
 for path in ['M1078 731L1196 792','M1196 638L1206 785','M1412 797L1223 800']:body+=route(path)
 body+=t(1250,887,'Neighbor messages',34,'f720-blue',width=307)
 body+=t(1250,955,sub('m','i')+' = ∑<tspan baseline-shift="sub" font-size="65%">j∈𝒩<tspan baseline-shift="sub" font-size="75%">i</tspan>(t)</tspan> ψ('+sub('h','i')+', '+sub('h','j')+')',40,'rl-math',True,width=378)
 body+=t(1250,1047,'GNN / Graph-MARL',38,'f720-heading',width=352)+t(1250,1102,'Local topology + communication',30, width=464)
 zone('graph',body,(1016,524,471,586))
 body=t(1750,557,'(g) Sequence attention',38,'f720-heading',width=417)+t(1750,601,'Agents × observed time',30)
 for row in range(3):
  for col in range(3):body+=box(1606+col*117,625+row*65,84,45,blue=row==2 and col==2)
 for path in ['M1657 653L1868 765','M1772 655L1868 765','M1658 715L1865 774']:body+=route(path)
 body+=t(1750,871,'Masked context → output',32,'f720-blue',width=362)+t(1750,941,'Actions or forecasts',32,width=311)+t(1750,1043,'Multi-agent Transformer',38,'f720-heading',width=446)+t(1750,1102,'Respect execution-time access',30,width=445)
 zone('attention',body,(1516,524,471,586))
 a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:dict(t=v[0],b=v[1]) for k,v in INFO.items()})+'</script></div>')
 return ''.join(o)
if __name__=='__main__':
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.20 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure720-1"><style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}@media(max-width:600px){body{margin:12px}}</style><main><h1>Figure 7.20 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="1134" alt="Original Figure 7.20"><h2>Interactive reconstruction</h2>'''+fig720()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure720-1';mountNative();</script></html>'''
 (SITE/'example/figure720.html').write_text(page)
 print('Generated Figure 7.20 comparison.')
