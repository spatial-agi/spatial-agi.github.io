"""Figure 7.14: independently drawn SVG value-based RL workflow."""
from pathlib import Path
from html import escape
import json
SITE=Path(__file__).resolve().parents[2]
ORIGINAL='assets/figures/figures/part3/section7/value-based-rl.webp'
INFO={
 'state':{'t':'State input','b':'The current state s is passed to the Q-network. In a spatial task, this state may encode visual observations, geometry or a map.'},
 'qnetwork':{'t':'Q-network','b':'Q(s, a; θ) estimates the expected discounted return for taking action a in state s. The network parameters θ are learned from transition data.'},
 'action':{'t':'Greedy action selection','b':'The action with the largest estimated Q-value is selected and sent to the environment. The diagram shows the greedy decision rule; training can also include exploration.'},
 'environment':{'t':'Environment','b':'The environment executes the action and produces a new state and reward.'},
 'feedback':{'t':'Transition feedback','b':'The next state s′ and reward r provide the transition information used to construct the Bellman target.'},
 'target':{'t':'Bellman target','b':'The target combines the immediate reward r with the discounted best next-state value. The primed parameters θ′ indicate the target-network parameters used in the printed formula.'},
 'loss':{'t':'Training loss','b':'The squared difference between the Bellman target y and the current estimate Q(s, a; θ) trains the Q-network. The two incoming arrows supply the target and the prediction.'}}
def fig714():
 out=[]
 def txt(x,y,value,cls='',size=None):
  return f'<text x="{x}" y="{y}" text-anchor="middle" class="f714-{cls}"'+(f' style="font-size:{size}px"' if size else '')+'>'+value+'</text>'
 def rect(x,y,w,h):return f'<rect class="f714-box" x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/>'
 def arrow(d,x,y,angle=0):return f'<path class="f714-route" d="{d}"/><path class="f714-head" d="M0 0L-17 -9V9Z" transform="translate({x} {y}) rotate({angle})"/>'
 def zone(k,body,hit):
  # A precise path supplies the feedback hit region; other regions use rectangles.
  if isinstance(hit,str):h=f'<path class="f714-hit f714-hit-route" d="{hit}"/>'
  else:
   x,y,w,h=hit;h=f'<rect class="f714-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
  out.append(f'<g class="f714-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">{body}{h}</g>')
 out.append('<div class="nf nf-714" data-nf="714" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 571" role="group" aria-label="Figure 7.14: value-based reinforcement learning workflow"><rect width="2000" height="571" fill="white"/>')
 zone('state',rect(21,2,393,227)+txt(207,97,'State')+txt(222,177,'<tspan font-style="italic">s</tspan>','math')+arrow('M414 123H523',540,123),(21,2,516,227))
 zone('qnetwork',rect(540,2,393,227)+txt(733,85,'Q-network')+txt(732,158,'Q(s, a; <tspan font-style="italic">θ</tspan>)','math'),(540,2,393,227))
 action=txt(1265,97,'Action <tspan class="f714-math">a<tspan baseline-shift="20" font-size="65%">∗</tspan> = argmax<tspan baseline-shift="-10" font-size="70%">a</tspan> Q(s, a; <tspan font-style="italic">θ</tspan>)</tspan>')
 action=action.replace('text-anchor="middle"','text-anchor="middle" textLength="638" lengthAdjust="spacingAndGlyphs"')
 zone('action',action+arrow('M933 115H1587',1604,115),(941,42,655,97))
 zone('environment',rect(1605,2,393,227)+txt(1806,89,'Environment')+txt(1801,169,'ℰ','math',60),(1605,2,393,227))
 zone('feedback',arrow('M1801 229V466H1187',1170,466,180)+txt(1509,428,'State <tspan class="f714-math">s<tspan baseline-shift="20" font-size="65%">′</tspan>,</tspan> reward <tspan class="f714-math">r</tspan>'),'M1801 237V466H1187M1330 409H1690')
 target=rect(539,342,631,226)+txt(851,420,'Bellman Target')
 for x,value in [(584,'y'),(638,'='),(695,'r'),(741,'+'),(790,'<tspan font-style="italic">γ</tspan>'),(858,'max'),(1018,'Q(s′, a′; <tspan font-style="italic">θ′</tspan>)')]:
  target+=txt(x,500,value,'math')
 target+=txt(858,530,'a','math',35)
 zone('target',target+arrow('M539 455H431',414,455,180),(418,342,752,226))
 loss=rect(21,342,393,226)+txt(219,415,'Train Loss')+txt(220,498,'(y − Q(s, a; <tspan font-style="italic">θ</tspan>))<tspan baseline-shift="21" font-size="65%">2</tspan>','math')+arrow('M671 231V287H152V325',152,342,90)
 # The narrow top extension includes the Q-network prediction route without swallowing the whitespace.
 zone('loss',loss+'<rect class="f714-hit" x="21" y="342" width="393" height="226" rx="18"/>','M671 240V287H152V325')
 out.append('</svg><div class="nf-card" role="status" hidden></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(out)
if __name__=='__main__':
 (SITE/'example/figure714.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.14 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure714-1"><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.14 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="571" alt="Original Figure 7.14"><h2>Interactive reconstruction</h2>'''+fig714()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure714-1';mountNative();</script></html>''')
