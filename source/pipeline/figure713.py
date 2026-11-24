"""Faithful SVG reconstruction of the reinforcement-learning loop (Figure 7.13)."""
from pathlib import Path
from html import escape
import json
SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/rl_overview.webp'
INFO = {
 'agent': {'t': 'Agent and policy', 'b': 'The agent uses its policy πθ(a | o) to choose an action from an observation. Learning updates θ to improve the expected long-term return.'},
 'action': {'t': 'Action at time t', 'b': 'The agent sends action aₜ to the environment. The action changes the state and determines what the agent will observe next.'},
 'env': {'t': 'Environment', 'b': 'The environment responds to the agent’s action with a new observation and reward. In spatial tasks, these may describe motion, geometry, contacts or task progress.'},
 'next': {'t': 'Next observation and reward', 'b': 'After action aₜ, the environment returns observation oₜ₊₁ and reward rₜ₊₁. The dashed separator distinguishes the printed time indices along the feedback route.'},
 'current': {'t': 'Current observation and reward', 'b': 'Observation oₜ conditions the current decision. Reward rₜ provides feedback from the preceding transition. The next observation and reward become current at the following step.'},
}
def fig713():
 parts = []
 def text(x,y,s,raw=False):
  return f'<text x="{x}" y="{y}" text-anchor="middle">{s if raw else escape(s)}</text>'
 def math(v,sub):
  return f'<tspan class="f713-math">{v}<tspan baseline-shift="-10" font-size="70%">{sub}</tspan></tspan>'
 def zone(k,body,box):
  x,y,w,h=box
  parts.append(f'<g class="f713-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k]["t"])}">{body}<rect class="f713-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></g>')
 def arrow(x1,x2,y):
  direction=1 if x2>x1 else -1
  base=x2-direction*19
  return f'<path class="f713-route" d="M{x1} {y}H{base}"/><path class="f713-head" d="M{x2} {y}L{base} {y-10}V{y+10}Z"/>'
 parts.append('<div class="nf nf-713 f713-redraw" data-nf="713" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 478" role="group" aria-label="Figure 7.13: reinforcement learning loop"><rect width="2000" height="478" fill="white"/>')
 zone('agent','<rect class="f713-box" x="2" y="55" width="450" height="353" rx="29"/>'+text(227,148,'Agent')+'<rect class="f713-box" x="32" y="182" width="395" height="111" rx="10"/>'+text(239,254,'Policy '+math('π','θ')+'<tspan class="f713-math">(a | o)</tspan>',True),(2,55,450,353))
 zone('action',arrow(452,1548,91)+text(1046,69,'Action '+math('a','t'),True),(460,5,1080,116))
 zone('env','<rect class="f713-box" x="1549" y="55" width="449" height="353" rx="28"/>'+text(1787,210,'Environment')+text(1780,304,'<tspan class="f713-math">ℰ</tspan>',True),(1549,55,449,353))
 zone('next',arrow(1549,1049,363)+text(1305,315,'Observation '+math('o','t+1'),True)+text(1268,427,'Reward '+math('r','t+1'),True)+'<path class="f713-divider" d="M1049 303V410"/>',(1042,264,502,183))
 zone('current',arrow(1049,452,363)+text(726,315,'Observation '+math('o','t'),True)+text(679,427,'Reward '+math('r','t'),True),(459,264,580,183))
 parts.append('</svg><div class="nf-card" role="status" hidden></div><script type="application/json" class="nf-info">'+json.dumps(INFO)+'</script></div>')
 return ''.join(parts)
if __name__ == '__main__':
 (SITE/'example/figure713.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.13 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure713-3"><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.13 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="478" alt="Original Figure 7.13"><h2>Interactive reconstruction</h2>'''+fig713()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure713-3';mountNative();</script></html>''')
