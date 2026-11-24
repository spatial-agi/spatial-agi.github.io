"""Faithful, independently editable SVG redraws of the five RL workflows."""
from pathlib import Path
from html import escape
import json
SITE=Path(__file__).resolve().parents[2]
SOURCES={715:('policy-based-rl.webp',579,'Policy-based RL'),716:('AC-based-rl.webp',542,'Actor–critic RL'),717:('ppo-based-rl.webp',825,'PPO'),718:('dpo-based-rl.webp',649,'DPO'),719:('grpo-based-rl.webp',618,'GRPO')}
def sub(v,s):return f'{v}<tspan baseline-shift="-10" font-size="70%">{s}</tspan>'
def sup(v,s):return f'{v}<tspan baseline-shift="20" font-size="70%">{s}</tspan>'
def pi(which='θ'):return sub('π',which)
def policy(which='θ'):return pi(which)+'(a | s)'
def st(t='t'):return sub('s',t)
def rt(t='t'):return sub('r',t)
def at(t='t'):return sub('a',t)
class Drawing:
 def __init__(self,n,font=44):
  self.n=n;self.info={};self.o=[];self.font=font
 def text(self,x,y,s,size=None,math=False,blue=False,anchor='middle',width=None,extra=''):
  cls=('rl-math ' if math else '')+('rl-blue ' if blue else '')
  return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}" style="font-size:{size or self.font}px"'+(f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else '')+f' {extra}>{s}</text>'
 def box(self,x,y,w,h,r=18,thin=False):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="rl-box'+(' rl-thin' if thin else '')+'"/>'
 def line(self,d):return f'<path class="rl-line" d="{d}"/>'
 def arrow(self,points):
  import math
  x,y=points[-1];px,py=points[-2];angle=math.degrees(math.atan2(y-py,x-px));length=math.hypot(x-px,y-py);head=16
  end=(x-(x-px)*head/length,y-(y-py)*head/length)
  d='M'+'L'.join(f'{xx:g} {yy:g}' for xx,yy in points[:-1]+[end])
  return f'<path class="rl-route" d="{d}"/><path class="rl-head" d="M0 0L-16 -8V8Z" transform="translate({x} {y}) rotate({angle})"/>'
 def image(self,file,x,y,w,h):return f'<image href="/assets/img/figs/f{self.n}/{file}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
 def hit(self,box):
  if isinstance(box,str):return f'<path class="rl-hit rl-hit-route" d="{box}"/>'
  x,y,w,h=box;return f'<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
 def zone(self,k,title,desc,body,*hits):
  self.info[k]={'t':title,'b':desc}
  self.o.append(f'<g class="rl-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(title)}">{body}'+''.join(self.hit(h) for h in hits)+'</g>')
 def finish(self):
  file,h,title=SOURCES[self.n]
  return f'<div class="nf nf-rl nf-{self.n}" data-nf="{self.n}" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 {h}" role="group" aria-label="Figure 7.{self.n-700}: {title} workflow"><rect width="2000" height="{h}" fill="white"/>'+''.join(self.o)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(self.info)+'</script></div>'

def fig715():
 d=Drawing(715);t=d.text;b=d.box;a=d.arrow;z=d.zone
 z('state','Current state','The current state sₜ provides the policy with the information needed to choose an action.',b(1,1,398,229)+t(188,98,'State')+t(206,177,st(),50,True)+a([(399,124),(525,124)]),(1,1,523,229))
 z('policy','Policy','The policy πθ(a | s) maps the observed state to an action distribution. Its parameters θ are updated by the policy gradient.',b(525,1,398,229)+t(724,85,'Policy')+t(723,158,policy(),50,True),(525,1,398,229))
 z('action','Action','An action sampled from the policy is executed in the environment.',a([(923,115),(1601,115)])+t(1257,98,'Action <tspan class="rl-math">'+at()+'</tspan>'),(931,42,662,94))
 z('environment','Environment','The environment produces a next state and reward after the action.',b(1601,1,398,229)+t(1803,89,'Environment')+t(1800,172,'ℰ',60,True),(1601,1,398,229))
 z('feedback','Next state and reward','The environment returns sₜ₊₁ and rₜ. These transition outcomes supply the policy-gradient computation shown below.',a([(1800,231),(1800,287),(792,287),(792,344)])+t(1290,249,'State <tspan class="rl-math">'+st('t+1')+'</tspan>, reward <tspan class="rl-math">'+rt()+'</tspan>'),'M1800 237V287H792V333',(1076,201,451,63))
 gradient='∇<tspan baseline-shift="-10" font-size="70%">θ</tspan>J(θ) = '+sub('𝔼',pi())+'[∇<tspan baseline-shift="-10" font-size="70%">θ</tspan> log '+pi()+'('+at()+'|'+st()+'), '+sub('R','t')+']'
 z('gradient','Policy-gradient update','Trajectory returns weight the gradient of log action probability. Computing this gradient updates θ to improve expected return.',b(295,344,994,229)+t(792,406,'Policy-gradient')+t(783,485,gradient,50,True,width=730)+t(790,545,'(Compute gradient and update <tspan class="rl-math">θ</tspan>)',34,extra='fill="#484848"')+a([(724,344),(724,231)]),(295,344,994,229),'M724 336V246')
 z('buffer','Trajectory buffer','The buffer stores state, action and reward sequences. These trajectories provide the return estimates used for the policy-gradient update.',b(1502,344,398,229)+t(1702,432,'Trajectory buffer')+t(1701,520,sup('{('+st()+', '+at()+', '+rt()+')}','T')+'<tspan dx="-21" baseline-shift="-10" font-size="70%">t=1</tspan>',50,True)+a([(1502,459),(1289,459)]),(1502,344,398,229),'M1490 459H1306')
 return d.finish()

def fig716():
 d=Drawing(716);t=d.text;b=d.box;a=d.arrow;z=d.zone
 z('state','State input','The same state conditions both the actor and critic. The critic estimates value while the actor chooses an action.',b(1,1,398,229)+t(188,98,'State')+t(207,177,st(),50,True)+a([(399,123),(725,120)])+a([(200,230),(200,425),(291,425)]),(1,1,398,229),'M411 123L708 120','M200 242V425H275')
 z('actor','Actor','The actor’s policy πθ(a | s) chooses actions and is updated using the advantage signal.',b(726,5,397,229)+t(922,87,'Actor')+t(920,160,policy(),50,True),(726,5,397,229))
 z('action','Action','The actor sends an action aₜ to the environment.',a([(1123,120),(1601,124)])+t(1325,94,'Action <tspan class="rl-math">'+at()+'</tspan>'),(1133,45,457,100))
 z('environment','Environment','The environment executes the action and produces the next state and reward.',b(1601,9,398,229)+t(1806,96,'Environment')+t(1800,177,'ℰ',60,True),(1601,9,398,229))
 z('feedback','Environment feedback','The next state sₜ₊₁ and reward rₜ enter the advantage estimate.',a([(1893,238),(1893,417),(1603,417)])+t(1738,397,'State <tspan class="rl-math">'+st('t+1')+'</tspan>')+t(1737,455,'reward <tspan class="rl-math">'+rt()+'</tspan>'),'M1893 247V417H1620',(1631,350,226,119))
 z('critic','Critic value estimate','The critic Vφ(s) supplies a value estimate that reduces variance in the actor update.',b(291,311,281,228)+t(432,385,'Critic')+t(430,461,sub('V','φ')+'(s)',50,True)+a([(572,425),(673,425)]),(291,311,281,228),'M585 425H656')
 advantage=sub('A','φ')+'('+st()+', '+at()+') ≈ '+sub('R','t')+' + γ'+sub('V','φ')+'('+st('t+1')+') − '+sub('V','φ')+'('+st()+')'
 z('advantage','Advantage signal','The printed advantage combines a return term and discounted next-state value, minus the current value baseline. This signal guides the actor update.',b(673,311,940,228)+t(1143,365,'Advantage')+t(1141,474,advantage,50,True,width=789)+a([(925,304),(925,234)]),(673,311,940,228),'M925 294V250')
 return d.finish()

def fig717():
 d=Drawing(717,42);t=d.text;b=d.box;a=d.arrow;z=d.zone
 old=pi('θ<tspan baseline-shift="-7" font-size="80%">old</tspan>')
 z('old','Old policy','The old policy is held fixed while collecting rollouts and computing probability ratios.',b(42,1,263,237)+t(175,74,'Old Policy')+t(168,169,old+'(a | s)',48,True),(42,1,263,237))
 z('sample','Sample trajectories','Sample trajectories under the old policy before updating the current policy.',a([(305,147),(556,147)])+t(448,131,'Sample',42,blue=True)+t(448,185,'trajectories',42,blue=True),(314,89,249,109))
 body=b(590,1,428,469)+t(804,65,'Rollout Buffer')
 for y,label in [(92,'('+st('1')+', '+at('1')+', '+rt('1')+', '+st('2')+' )'),(164,'('+st('2')+', '+at('2')+', '+rt('2')+', '+st('3')+' )'),(236,'⋮'),(307,'('+st()+', '+at()+', '+rt()+', '+st('t+1')+' )')]:body+=b(630,y,348,66,0,True)+t(804,y+47,label,48,True)
 body+=t(818,439,'(Compute Advantages <tspan class="rl-math">'+sub('A','t')+'</tspan>)',32)+a([(1018,144),(1359,144)])
 z('buffer','Rollout buffer and advantages','Store transition sequences and compute an advantage estimate Aₜ for each decision. These data are reused during the policy update.',body,(590,1,428,469),'M1032 144H1342')
 ratio=sub('r','t')+'(θ) = '+pi()+'('+at()+'|'+st()+')/'+old+'('+at()+'|'+st()+')'
 z('ratio','Probability ratio','The ratio compares the current and old probabilities of the sampled action. It measures how far the updated policy has moved from the rollout policy.',b(1359,1,638,237)+t(1680,82,'Probability Ratio')+t(1678,168,ratio,48,True,width=580)+a([(1678,238),(1680,384)]),(1359,1,638,237),'M1678 251L1680 366')
 obj=b(1361,384,638,339,26)+t(1680,446,'Clipped Surrogate Objective')
 obj+=t(1391,560,sup('L','PPO')+'(θ)',48,True,anchor='start')
 obj+=t(1391,613,'= 𝔼[min('+sub('r','t')+'(θ)'+sub('A','t')+', clip('+sub('r','t')+'(θ), 1',45,True,anchor='start',width=574)
 obj+=t(1391,666,'− ε, 1 + ε)'+sub('A','t')+')]',45,True,anchor='start')
 z('objective','Clipped surrogate objective','PPO maximizes the smaller of the unclipped and clipped advantage-weighted ratios. Clipping limits the incentive for large changes in action probability.',obj,(1361,384,638,339))
 update=t(1111,594,'Policy Update',42,blue=True)+t(1128,684,'θ ← θ + α∇<tspan baseline-shift="-10" font-size="70%">θ</tspan>'+sup('L','PPO'),46,True,True)+a([(1360,616),(862,616)])
 z('update','Policy update','Optimize the clipped objective with gradient ascent to obtain the new policy parameters.',update,(930,548,408,150),'M1346 616H879')
 z('new','New policy','The updated policy πθ(a | s) is used for the next rollout cycle.',b(600,499,263,235)+t(732,571,'New Policy')+t(727,664,policy(),48,True),(600,499,263,235))
 z('sync','Synchronize the old policy','Copy θ into θold before sampling the next batch of trajectories.',a([(600,617),(174,617),(174,241)])+t(389,587,sub('θ','old')+' ← θ',46,True,True),(298,540,249,66),'M585 617H174V257')
 return d.finish()

def fig718():
 d=Drawing(718,38);t=d.text;b=d.box;a=d.arrow;z=d.zone
 z('prompt','Prompt','A prompt z conditions the response-generation process.',b(1,2,233,209)+t(116,66,'Prompt <tspan class="rl-math" font-style="italic">z</tspan>')+d.image('prompt/document.png',84,104,67,82)+a([(234,117),(308,117)]),(1,2,233,209),'M246 117H292')
 z('reference','Reference policy','The reference policy πref provides the baseline response probabilities used by DPO.',b(308,7,233,208)+t(423,71,'Reference')+t(423,119,'Policy')+t(423,181,pi('ref'),42,True),(308,7,233,208))
 z('sample','Sample response pairs','Generate two candidate responses from the reference policy for preference comparison.',a([(545,107),(764,105)])+a([(541,118),(775,338)])+t(647,84,'Sample',38,blue=True)+t(656,216,'Sample',38,blue=True,extra='transform="rotate(47 656 216)"'),(571,43,177,53),'M554 107L748 105M551 128L762 326')
 for k,x,y,label,arrowy in [('response1',775,7,'1',117),('response2',775,235,'2',345)]:
  body=b(x,y,232,208)+t(890,y+42,sub('y',label),44,True)
  for yy in (y+78,y+108,y+138):body+=d.line(f'M817 {yy}H965')
  body+=t(890,y+174,'...',42,True)+a([(1007,arrowy),(1084,arrowy)])
  z(k,'Candidate response '+label,'A sampled response is presented for human comparison. The response card and its lines are independent frontend elements.',body,(x,y,232,208),f'M1019 {arrowy}H1068')
 human=b(1085,5,421,438)+t(1297,68,'Human Preference')
 for x,y,label in [(1104,106,'1'),(1321,104,'2')]:
  human+=b(x,y,179,209,15)+t(x+90,y+43,sub('y',label),44,True)
  for yy in (y+78,y+108,y+138):human+=d.line(f'M{x+15} {yy}H{x+163}')
  human+=t(x+88,y+173,'...',42,True)
 human+=d.image('human-preference/thumb-up.png',1153,316,77,64)+d.image('human-preference/thumb-down.png',1371,323,76,68)
 human+=t(1296,418,sub('y','w')+' ≻ '+sub('y','l')+' <tspan class="rl-sans">(here: </tspan>'+sub('y','1')+' ≻ '+sub('y','2')+'<tspan class="rl-sans"> )</tspan>',40,True)+a([(1506,234),(1577,234)])
 z('preference','Human preference','A human ranks the responses. Here y₁ is preferred to y₂, so they become the winning response yw and losing response yl.',human,(1085,5,421,438),'M1518 234H1561')
 reward=b(1577,7,421,438)+t(1784,70,'Human Preference')
 for yy,suffix in [(136,'w'),(309,'l')]:
  reward+=t(1695,yy,'reward<tspan class="rl-math">'+sub('',suffix)+'</tspan>',38)
  reward+=t(1624,yy+76,'= β log',40,True,anchor='start')
  reward+=t(1850,yy+45,pi()+'('+sub('y',suffix)+'|x)',40,True)+d.line(f'M1755 {yy+64}H1944')+t(1850,yy+103,pi('ref')+'('+sub('y',suffix)+'|x)',40,True)
 reward+=d.line('M1596 259H1978')+a([(1788,445),(1788,557),(1649,557)])
 z('reward','Implicit rewards','Each implicit reward is β times the log probability ratio between the trained and reference policies. The winning and losing rewards enter the preference loss.',reward,(1577,7,421,438),'M1788 456V557H1665')
 loss=b(945,470,704,174)+t(1297,538,'Bradley-Terry (DPO) Loss')+t(1294,619,sub('ℒ','DPO')+' = - log σ(<tspan class="rl-sans">reward</tspan><tspan baseline-shift="-10" font-size="70%">w</tspan> -<tspan class="rl-sans">reward</tspan><tspan baseline-shift="-10" font-size="70%">l</tspan>)',40,True,width=610)
 z('loss','Bradley–Terry preference loss','The negative log sigmoid of the reward difference encourages the winning response to have a higher implicit reward than the losing response.',loss,(945,470,704,174))
 update=a([(945,556),(315,556)])+t(630,541,'Gradient Update (offline):',38,blue=True)+t(630,589,'∇<tspan baseline-shift="-10" font-size="70%">θ</tspan>'+sub('ℒ','DPO')+' <tspan class="rl-sans">update</tspan>'+pi(),40,True,True)
 z('update','Offline gradient update','Preference pairs train the policy offline through the DPO loss, without requiring online environment rollouts.',update,(399,495,468,110),'M930 556H331')
 z('policy','Trainable policy','The policy πθ is optimized using the preference loss. The return route to the reference-policy stage is retained exactly as printed.',b(82,470,233,174)+t(198,530,'Policy')+t(196,595,pi(),44,True)+a([(82,557),(60,557),(60,342),(425,342),(425,215)]),(82,470,233,174),'M78 557H60V342H425V231')
 return d.finish()

def fig719():
 d=Drawing(719,40);t=d.text;b=d.box;a=d.arrow;z=d.zone
 z('prompt','Prompt','Prompt q conditions a group of sampled outputs.',b(21,52,213,217)+t(122,114,'Prompt <tspan class="rl-math">q</tspan>')+d.image('prompt/document.png',92,155,68,85)+a([(234,154),(357,154)]),(21,52,213,217),'M247 154H341')
 def response(x,y,label,reward=False):
  body=b(x,y,79,257 if reward else 218,6)+t(x+39,y+45,sub('o',label),42,True)
  for yy in [y+81,y+112,y+144]:body+=d.line(f'M{x+12} {yy}H{x+62}')
  body+=t(x+39,y+179,'...',40,True)
  if reward:body+=t(x+39,y+227,sub('r',label),40,True)
  return body
 old=b(358,5,465,406,14)+t(590,51,'Old Policy <tspan class="rl-math">'+pi('θ<tspan baseline-shift="-5" font-size="80%">old</tspan>')+'</tspan>')+t(592,98,'Sample a group of <tspan class="rl-math" font-style="italic">G</tspan> outputs',30)
 for x,label in [(415,'1'),(519,'2'),(676,'G')]:old+=response(x,142,label)
 old+=t(638,252,'...',40,True)+a([(823,154),(943,154)])
 z('old','Sample a group of outputs','The old policy generates G outputs for the same prompt. Group-relative scoring compares these candidates within the group.',old,(358,5,465,406),'M835 154H927')
 reward=b(943,5,418,406,14)+t(1155,51,'Reward Model')+t(1168,99,'Assign scalar reward <tspan class="rl-math">'+sub('r','i')+'</tspan>',30)
 for x,label in [(979,'1'),(1083,'2'),(1240,'G')]:reward+=response(x,143,label,True)
 reward+=t(1199,257,'...',40,True)+a([(1361,154),(1524,154)])
 z('reward','Reward model','The reward model assigns each sampled output a scalar score rᵢ. These scores provide the group statistics for the advantage estimate.',reward,(943,5,418,406),'M1374 154H1508')
 advantage=b(1524,10,307,307,10)+t(1679,58,'Group-relative')+t(1678,107,'Advantage')+t(1539,246,sub('A','i')+' =',38,True,anchor='start')+t(1722,219,sub('r','i')+'-mean(r)',38,True)+d.line('M1638 236H1808')+t(1722,271,'std(r)',38,True)+a([(1678,317),(1678,463)])
 z('advantage','Group-relative advantage','Normalize each reward using the mean and standard deviation of the sampled group. This baseline avoids learning a separate critic.',advantage,(1524,10,307,307),'M1678 330V447')
 clip=b(1473,469,507,136,22)+t(1723,502,'Clipped Surrogate')+t(1724,566,'min('+sub('r','t')+sub('A','t')+', clip('+sub('r','t')+', 1-ε, 1 + ε)'+sub('A','t')+')',38,True,width=477)+a([(1473,537),(1270,537)])
 z('clipped','Clipped surrogate','The clipped surrogate limits policy changes while weighting each output by its group-relative advantage.',clip,(1473,469,507,136),'M1459 537H1286')
 objective=b(762,475,508,136,24)+t(1015,508,'Object (to maximize)')+t(1017,558,'with KL Penalty')+t(1024,590,sub('ℒ','GRPO'),38,True)+a([(762,543),(393,543)])
 z('objective','Objective with KL penalty','Combine the surrogate objective with a KL penalty that constrains deviation from the reference behavior.',objective,(762,475,508,136),'M748 543H409')
 z('new','New policy','Maximizing the KL-regularized group-relative objective updates the trainable policy πθ.',b(19,497,374,102,26)+t(206,562,'New Policy <tspan class="rl-math">'+pi()+'</tspan>'),(19,497,374,102))
 return d.finish()

GENERATORS={715:fig715,716:fig716,717:fig717,718:fig718,719:fig719}
def preview(n):
 file,h,title=SOURCES[n]
 return f'<section id="figure{n}"><h1>Figure 7.{n-700} · {title}</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/{file}" width="2000" height="{h}" alt="Original Figure 7.{n-700}"><h2>Interactive reconstruction</h2>{GENERATORS[n]()}</section>'
STYLE='''<style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}.nf{padding:0;border:0}section{margin:32px 0 54px}nav{display:flex;flex-wrap:wrap;gap:18px;font:16px Arial;margin:24px 0}nav a{color:#2343c2}@media(max-width:600px){body{margin:12px}}</style>'''
def page(content,title):return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="/assets/css/site.css?v=figure715-719-1">{STYLE}<main>{content}</main><script type="module">import {{mountNative}} from "/assets/js/nfig.js?v=figure715-719-1";mountNative();</script></html>'
if __name__=='__main__':
 for n in GENERATORS:
  (SITE/f'example/figure{n}.html').write_text(page(preview(n),f'Figure 7.{n-700} comparison'))
  # Thin exports keep each figure importable by the existing build pipeline.
  (SITE/f'source/pipeline/figure{n}.py').write_text(f'"""Figure 7.{n-700} native reconstruction."""\nfrom figure715_719 import fig{n}\n')
 nav='<h1>Figures 7.15–7.19 · Original and interactive reconstructions</h1><nav>'+''.join(f'<a href="#figure{n}">Figure 7.{n-700}</a>' for n in GENERATORS)+'</nav>'
 (SITE/'example/figure715-719.html').write_text(page(nav+''.join(preview(n) for n in GENERATORS),'Figures 7.15–7.19 comparison'))
 print('Generated five reconstructions and individual/batch comparison previews.')
