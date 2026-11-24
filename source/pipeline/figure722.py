"""Figure 7.22: editable VLA perception–action loop with original scene assets."""
from pathlib import Path
from html import escape
import json

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/VLA_spatial_reasoning.webp'
INFO = {
    'instruction': ('Language instruction', 'The goal is to stack the red block on the blue block. Language specifies the intended spatial relation, while visual and robot-state inputs ground the instruction in the workspace.'),
    'initial': ('Initial scene', 'The red and blue blocks start side by side. The robot must interpret their geometry and plan a feasible manipulation. This is an illustrative initial state, not a recorded experimental observation.'),
    'state': ('Robot and gripper state', 'Joint positions qₜ, joint velocities q̇ₜ, and gripper state gₜ describe the robot’s current configuration. Depth, 3D geometry, or keypoints can provide additional spatial evidence.'),
    'fusion': ('Vision–language–state fusion', 'The VLA policy combines the visual observation, language instruction, and robot state to generate a conditioned action sequence.'),
    'autoregressive': ('Autoregressive generation', 'An autoregressive policy predicts actions in sequence, conditioning each next action on the preceding context and actions. The a₁ → a₂ → a₃ chain illustrates this generation order.'),
    'diffusion': ('Diffusion generation', 'A diffusion policy denoises a noisy action sequence Aₖ into A₀, conditioned on spatial observations and the task. The arrow represents denoising rather than an executed robot motion.'),
    'hybrid': ('Hybrid generation', 'A hybrid combines autoregressive or latent representations with an action decoder. Spatial features can condition this decoder as well as the other generation mechanisms.'),
    'refinement': ('Optional RL refinement', 'Rewards and critics can refine a VLA policy through reinforcement learning. This is an optional training strategy compatible with the action generators above.'),
    'representation': ('Action representation', 'Actions may encode end-effector translation Δp, rotation ΔR, gripper command g, or joint targets q*. They can be represented as tokens, pose waypoints, or action chunks.'),
    'controller': ('Decoder / robot controller', 'The decoder or controller translates the policy’s action representation into robot commands. The downward arrow connects this stage to execution in the workspace.'),
    'result': ('Observe the resulting state', 'The intended outcome places the red block on top of the blue block. The scene illustrates the target relation; execution produces new observations for the next cycle.'),
    'planner': ('Value maps and keypoints', 'An alternative planning interface uses spatial value maps or relational keypoints. A planner turns these representations into commands for the robot controller.'),
    'feedback': ('Environment feedback', 'New visual and proprioceptive observations close the perception–action loop. After acting, the policy can use the updated state to condition its next action sequence.'),
}


def fig722():
    out = []
    a = out.append

    def text(x,y,value,size=32,cls='',width=None,raw=False):
        fit = f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}" style="font-size:{size}px"{fit}>'+(value if raw else escape(value))+'</text>'

    def path(d,cls='f722-divider'):
        return f'<path d="{d}" class="{cls}"/>'

    def route(d,gray=False,head=True,duration=None):
        return f'<path d="{d}" class="rl-route'+(' f722-gray' if gray else '')+'"'+(f' marker-end="url(#f722-{"gray" if gray else "blue"})"' if head else '')+(f' data-duration="{duration}"' if duration else '')+'/>'

    def box(x,y,w,h,blue=False):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="f722-box'+(' f722-selected' if blue else '')+'"/>'

    def math(x,y,v,size=36,blue=False,width=None):
        return text(x,y,v,size,'f722-math'+(' f722-blue' if blue else ''),width,True)

    def sub(v,s):
        return v+f'<tspan baseline-shift="-5" font-size="70%">{s}</tspan>'

    def zone(k,body,bounds):
        x,y,w,h=bounds
        a(f'<g class="rl-zone" data-k="{k}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[k][0])}">{body}<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')

    a('<div class="nf nf-rl nf-722" data-nf="722" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1047" role="group" aria-label="Figure 7.22: VLA-based spatial reasoning as a perception–action loop"><defs>')
    for name,color in [('blue','#4145e9'),('gray','#aab2b8')]:
        a(f'<marker id="f722-{name}" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M3 4L14 9L3 14Z" fill="{color}" stroke="{color}" stroke-width="2.3" stroke-linejoin="round"/></marker>')
    a('</defs><rect width="2000" height="1047" fill="white"/><g class="f722-scaffold">'+path('M572 27V903M1431 27V903')
      +text(279,58,'(i) Embodied inputs',34,'f722-heading',337)
      +text(1000,58,'(ii) VLA policy',34,'f722-heading',236)
      +text(1730,58,'(iii) Action and execution',34,'f722-heading',430)
      +text(1000,739,'Spatial features can condition each decoder',30,'f722-blue',603)+'</g>')

    body=box(28,114,498,114,True)+text(277,163,'Stack the red block',32,width=285)+text(277,194,'on the blue block.',32,width=264)
    body+=route('M538 189L612 177')
    zone('instruction',body,(27,108,500,125))
    body='<image href="/assets/img/figs/f722/i-inputs/initial-scene.png" x="42" y="265" width="446" height="424"/>'
    body+=text(279,712,'Initial scene',30,'f722-blue',168)+route('M532 429L620 233')
    zone('initial',body,(40,257,453,463))
    body=box(28,735,498,84)+text(277,785,'Robot state + gripper state',32,width=389)
    body+=math(279,872,sub('q','t')+', '+sub('q̇','t')+', '+sub('g','t'),36,width=145)
    body+=text(279,931,'Optional depth / 3D / keypoints',30,'f722-blue',429)
    zone('state',body,(28,731,499,210))

    body=box(624,117,751,114,True)+text(1000,182,'Vision–language–state fusion',36,width=490)
    body+=text(1000,297,'Generate a conditioned action sequence',32,width=600)+route('M1384 175H1471')
    zone('fusion',body,(617,109,765,203))
    body=text(751,378,'Autoregressive',34,'f722-heading',264)
    for y,num in [(409,'1'),(514,'2'),(619,'3')]:
        body+=box(689,y,123,68)+math(751,y+42,sub('a',num),36)
    body+=route('M751 484V495')+route('M751 589V600')
    zone('autoregressive',body,(612,341,279,359))
    body=text(1006,378,'Diffusion',34,'f722-heading',158)
    for y,s,blue in [(443,'K',False),(653,'0',True)]:
        body+=f'<circle cx="1006" cy="{y}" r="40" class="f722-box'+(' f722-selected' if blue else '')+'"/>'+math(1006,y+10,sub('A',s),36)
    body+=route('M1006 501V591')+text(1094,554,'denoise',30,'f722-blue',106)
    zone('diffusion',body,(916,341,234,359))
    body=text(1255,378,'Hybrid',34,'f722-heading',114)+box(1166,406,179,78)+text(1255,451,'AR / latent',30,width=142)
    body+=route('M1255 495V560')+box(1166,578,179,99,True)+text(1255,620,'Action',32,width=92)+text(1255,651,'decoder',32,width=120)
    zone('hybrid',body,(1157,341,197,352))
    body=box(631,785,738,96)+text(1000,840,'Optional RL refinement: reward / critic',32,width=564)
    body+=text(1000,924,'Training strategy, compatible with generators',30,width=582)
    zone('refinement',body,(624,776,752,161))

    body=box(1492,117,477,185,True)+text(1730,175,'Action representation',34,'f722-heading',386)
    body+=math(1730,241,'<tspan font-style="normal">Δ</tspan>p, <tspan font-style="normal">Δ</tspan>R, g　<tspan font-style="normal">or</tspan>　q<tspan baseline-shift="super" font-size="65%">*</tspan>',36,True,width=298)
    body+=text(1730,287,'Tokens / pose waypoints / chunks',30,width=445)+route('M1729 303V316')
    zone('representation',body,(1487,109,489,211))
    body=box(1492,326,477,84)+text(1730,375,'Decoder / robot controller',32,width=383)+route('M1729 410V421')
    zone('controller',body,(1487,322,489,109))
    body='<image href="/assets/img/figs/f722/iii-execution/result-scene.png" x="1562" y="452" width="338" height="325"/>'
    body+=text(1730,814,'Observe the resulting state',32,width=376)
    zone('result',body,(1534,446,395,376))
    body=route('M1491 883H1464V369H1480',True,duration=3300)+box(1492,843,477,83)+text(1730,891,'Value map / keypoints → planner',30,width=421)
    zone('planner',body,(1487,837,489,96))
    body=route('M1888 830H1976V979',True,False,duration=2600)+route('M1976 984H24V459',duration=7500)
    body+=text(1000,1020,'Environment feedback: new visual and proprioceptive observations',30,'f722-blue',929)
    zone('feedback',body,(15,975,1970,61))
    a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:dict(t=v[0],b=v[1]) for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__=='__main__':
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.22 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure722-1"><style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}@media(max-width:600px){body{margin:12px}}</style><main><h1>Figure 7.22 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="1047" alt="Original Figure 7.22"><h2>Interactive reconstruction</h2>'''+fig722()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure722-1';mountNative();</script></html>'''
    (SITE/'example/figure722.html').write_text(page)
    print('Generated Figure 7.22 comparison.')
