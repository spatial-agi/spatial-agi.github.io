"""Source-coordinate frontend reconstructions for Figures 8.1–8.25.

PDF paths and text are converted to separate editable SVG primitives. Pictorial
plates use the reviewed transparent PNGs. The original raster is comparison only.
Run with PyMuPDF on PYTHONPATH; integration remains a separate approval step.
"""
from pathlib import Path
from html import escape
import json, math, re, unicodedata
import fitz

SITE=Path(__file__).resolve().parents[2]
BOOK=SITE.parent/'Spatial_Intelligence_Book_2025_v14/figures/part3/section8'
INV=json.loads((SITE/'source/pipeline/figures81_825_sources.json').read_text())
BLUE='#3646f0'; INK='#29363f'; GRAY='#a8b3bd'
# All bounds are in a 1000-unit-wide source coordinate system.
# Each entry represents a meaningful mechanism or example, rather than a title.
REGIONS={
1:[('Shared latent pipeline',(0,0,1000,305)),('Adversarial generation',(0,305,333,654)),('Autoregressive generation',(333,305,667,654)),('Diffusion and flow',(667,305,1000,654))],
2:[('Side-branch control',(0,0,333,361)),('Lightweight adapters',(333,0,667,361)),('Gated grounding',(667,0,1000,361)),('Layout-aware attention',(0,361,333,655)),('Inference-time guidance',(333,361,667,655)),('Spatial condition and image',(667,361,1000,655))],
3:[('Context-preserving editing task',(0,0,1000,223)),('Masked denoising',(0,223,333,555)),('Inversion and rewrite',(333,223,667,555)),('Instruction-tuned editing',(667,223,1000,555)),('Exemplar and reference',(0,555,500,854)),('Drag-based optimization',(500,555,1000,854))],
4:[('Image to 3D assets',(0,0,500,419)),('Text to 3D assets',(500,0,1000,419))],
5:[('Conditional 3D object synthesis',(0,0,1000,156)),('3D-native generation',(0,156,500,442)),('2D-prior distillation',(500,156,1000,442)),('Multi-view generation and lifting',(0,442,500,746)),('Learned direct-to-3D routes',(500,442,1000,746))],
6:[('Objaverse objects',(0,0,1000,566))],
7:[('Coherent scene synthesis',(0,0,1000,177)),('Layout and scene graphs',(0,177,500,469)),('View-to-3D reconstruction',(500,177,1000,469)),('View-to-view synthesis',(0,469,500,793)),('Video-model synthesis',(500,469,1000,793))],
8:[],
9:[('Recover a 3D scene',(0,0,1000,183)),('Iterative reconstruction',(0,183,333,731)),('Feed-forward reconstruction',(333,183,667,731)),('Generative completion',(667,183,1000,731))],
10:[('Panoramic intermediate',(0,0,1000,171)),('Panoramic image synthesis',(0,171,500,458)),('Panoramic video synthesis',(500,171,1000,458)),('Panoramic 3D reconstruction',(0,458,500,770)),('Panorama-based scene generation',(500,458,1000,770))],
11:[('Appearance editing',(0,0,200,404)),('Object transformation',(200,0,400,404)),('Shape deformation',(400,0,600,404)),('Scene inpainting',(600,0,800,404)),('Creative editing',(800,0,1000,404))],
12:[('Consistent geometry-aware editing',(0,0,1000,197)),('2D-lifted iterative editing',(0,197,333,590)),('Multi-view guidance',(333,197,667,590)),('3D-native primitive editing',(667,197,1000,590)),('Language-integrated editing',(0,590,500,863)),('Efficient and training-free editing',(500,590,1000,863))],
13:[('Text and video time',(0,0,1000,179)),('Adversarial video generation',(0,179,333,744)),('Autoregressive video tokens',(333,179,667,744)),('Diffusion video denoising',(667,179,1000,744))],
14:[('Text and explicit spatial conditions',(0,0,1000,175)),('Reference images',(0,175,320,389)),('Skeletal pose',(320,175,640,389)),('Depth maps',(0,389,320,600)),('Facial landmarks',(320,389,640,600)),('Sketch sequences',(0,600,320,808)),('Bounding-box tracks',(320,600,640,808)),('Residual adapter injection',(640,175,1000,808))],
15:[('Temporal motion control',(0,0,1000,173)),('Dense optical flow',(0,173,320,434)),('Object trajectories',(320,173,640,434)),('Virtual camera paths',(0,434,320,747)),('Reference motion',(320,434,640,747)),('Alternative injection mechanisms',(640,173,1000,747))],
16:[('Combined application controls',(0,0,1000,180)),('Style reference',(0,180,485,329)),('Interactive points',(0,329,485,453)),('BEV layout',(0,453,485,568)),('Target text',(0,568,485,682)),('Audio',(0,682,485,793)),('Condition fusion',(485,180,1000,793))],
17:[('Video editing task',(0,0,1000,177)),('Training-free inversion',(0,177,1000,352)),('One-shot tuning',(0,352,1000,526)),('Trained editor',(0,526,1000,700)),('Attention and feature reuse',(0,700,1000,874)),('Structural guidance',(0,874,1000,1047))],
18:[('Joint positions',(0,0,245,322)),('Kinematic chains',(245,0,490,322)),('Surface markers',(490,0,735,322)),('Joint rotations',(735,0,1000,322)),('Skinning',(0,340,267,627)),('Body shape',(267,340,500,627)),('Body pose',(500,340,751,627)),('Articulated body',(751,340,1000,627))],
19:[('Articulated motion task',(0,0,1000,177)),('Conditioning modalities',(0,177,500,716)),('Regression',(500,177,1000,388)),('Generative motion model',(500,388,1000,716))],
20:[('Motion corpora and representation',(0,0,625,222)),('Species modulation',(0,222,390,565)),('Conditional motion sampler',(390,222,625,565)),('Species-specific motion',(625,0,1000,693)),('Alternative skeletons',(0,565,625,693))],
21:[('Map and agent histories',(0,0,332,450)),('Vectorized encoder',(332,0,636,281)),('Multimodal trajectory decoder',(332,281,636,474)),('Goal and feasibility',(0,474,636,647)),('Candidate trajectories',(636,0,1000,450)),('Trajectory evaluation',(636,450,1000,647))],
23:[('Dynamic 3D task',(0,0,1000,172)),('Text condition',(0,172,200,404)),('Image condition',(200,172,400,404)),('Video condition',(400,172,600,404)),('Static 3D condition',(600,172,800,404)),('Multiple conditions',(800,172,1000,404)),('Condition fusion',(0,404,1000,500)),('Score distillation',(0,500,530,802)),('Generate then reconstruct',(530,500,1000,802)),('Dynamic 3D output',(0,802,1000,939))],
24:[('Representation world model',(0,35,333,525)),('Generative world model',(333,35,667,525)),('Mental world model',(667,35,1000,525))],
25:[('Rule and grammar generation',(0,0,696,123)),('Symbolic graphics programs',(0,123,696,245)),('Neuro-symbolic synthesis',(0,245,696,367)),('Deterministic rendering',(696,0,866,367)),('Spatial outputs',(866,0,1000,367))],
}
DESCRIPTIONS={
'Adversarial generation':'A generator maps noise and text features into an image latent. A discriminator supplies realism and text-alignment feedback during training; inference uses one generator pass.',
'Autoregressive generation':'A causal transformer predicts each discrete token from previous tokens and the text condition. Sampling follows the source diagram’s token order.',
'Diffusion and flow':'A conditional predictor iteratively denoises a latent or defines a velocity field integrated by an ODE solver.',
'Side-branch control':'A trainable control branch adds residual features to a frozen denoising backbone while preserving its pretrained image prior.',
'Lightweight adapters':'Small trainable encoders convert spatial conditions into multi-scale features injected into the frozen backbone.',
'Gated grounding':'Grounded object tokens enter gated attention blocks alongside visual and text features.',
'Inference-time guidance':'A spatial loss updates the sample during inference using gradients, without retraining the denoiser.',
'Condition fusion':'Encoded conditions can be added, concatenated along channels, or represented as unified condition tokens before generation.',
'Score distillation':'Render the current 4D asset, evaluate it with a frozen diffusion prior, and send score-distillation gradients back to the asset parameters.',
'Generate then reconstruct':'Generate video or multi-view targets and reconstruct a consistent dynamic 3D representation from them.',
'Goal and feasibility':'Goals, road constraints, and collision checks guide conditional trajectory generation and help evaluate candidate futures.',
'Context-preserving editing task':'Edit the requested appearance or geometry while retaining the background, pose, identity, and untargeted scene layout.',
'Iterative reconstruction':'Optimize scene parameters separately for each scene by rendering views and comparing them with observed images.',
'Feed-forward reconstruction':'A trained reconstructor uses weights shared across scenes to infer a 3D representation from new observations in one forward pass.',
'Generative completion':'A conditional 3D prior reconstructs visible content and samples plausible unobserved regions; different samples may complete unseen parts differently.',
'Rule and grammar generation':'Production rules expand a symbolic description into a structured program; the deterministic renderer executes the resulting specification.',
'Symbolic graphics programs':'A domain-specific language specifies objects, relations, geometry, and drawing operations as an executable spatial program.',
'Neuro-symbolic synthesis':'A language model proposes a symbolic program. Execution through a deterministic renderer produces the spatial artifact.',
'Off':'',
}

def fmt(v):return f'{v:.3f}'.rstrip('0').rstrip('.')
def color(v):
 if v is None:return 'none'
 if len(v)==1:v=v*3
 return '#'+''.join(f'{round(c*255):02x}' for c in v[:3])
def rect_tuple(r):return tuple(float(v) for v in r)
def contains(a,b,pad=0):return a[0]-pad<=b[0] and a[1]-pad<=b[1] and a[2]+pad>=b[2] and a[3]+pad>=b[3]

class Figure:
 def __init__(self,n):
  self.n=n;self.id=f'8{n}';self.entry=INV[n-1]
  self.man=json.loads((SITE/f'assets/figures/elements/figure{self.id}/manifest.json').read_text())
  self.w,self.h=self.man['source_sizes'][0];self.h=self.h/self.w*1000;self.w=1000
  if n==18:self.h=627
  self.regions=list(REGIONS.get(n,[]));self.parts=[];self.routes=[];self.fonts=set()
  if n==6:self.regions=[(a['title'].title(),tuple(v/2 if False else v*self.w/self.man['source_sizes'][0][0] for v in a['source_box'])) for a in self.man['assets']]
 def add(self,svg,bounds,z=0):self.parts.append((z,svg,bounds))
 def text(self,x,y,s,size=15,math=False,italic=False,anchor='middle',fill=INK,bold=False,width=None):
  style=f'font-family:{"Cambria Math" if math else "Figure711Sans"};font-size:{size}px;font-style:{"italic" if italic else "normal"};font-weight:{700 if bold else 400};fill:{fill}'
  fit=f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
  self.add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{style}"{fit}>{escape(s)}</text>',(x-100,y-size,x+100,y),2000)
 def line(self,d,bounds,arrow=False,dash=False,stroke=BLUE,sw=1.5):
  extra=' class="f8-flow rl-route"' if arrow else ''
  self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"'+(' stroke-dasharray="5 3"' if dash else '')+(f' marker-end="url(#f{self.id}-head)"' if arrow else '')+extra+'/>',bounds,1000)
 def box(self,x,y,w,h,fill='white',stroke=GRAY):
  self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',(x,y,x+w,y+h),500)
 def assets(self):
  for a in self.man['assets']:
   k=a.get('source_index',0);scale=1000/self.man['source_sizes'][k][0]
   x,y,x1,y1=[v*scale for v in a['source_box']]
   if self.n==18 and k==1:y+=350;y1+=350
   self.add(f'<image href="/assets/img/figs/f{self.id}/{a["file"]}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(x1-x)}" height="{fmt(y1-y)}" preserveAspectRatio="none"/>',(x,y,x1,y1),300)
 def pdf(self,path):
  self.doc=fitz.open(path);pg=self.doc[0];scale=1000/pg.rect.width
  self.h=pg.rect.height*scale
  drawings=pg.get_drawings()
  def is_chainable(d):
   return (d['type']=='s' and d.get('fill') is None and not d.get('closePath')
           and bool(d['items']) and all(it[0] in ('l','c') for it in d['items']))
  def endpoints(d):
   items=d['items'];return items[0][1], items[-1][2] if items[-1][0]=='l' else items[-1][-1]
  def same_style(a,b):
   return (a.get('type')==b.get('type') and a.get('color')==b.get('color')
           and abs((a.get('width') or 0)-(b.get('width') or 0))<1e-5
           and (a.get('dashes') or '')==(b.get('dashes') or ''))
  def reverse_item(it):
   if it[0]=='l':return ('l',it[2],it[1])
   return ('c',it[-1],it[3],it[2],it[1])
  groups=[]; used=set()
  for i,d in enumerate(drawings):
   if i in used or d['rect'].width>pg.rect.width*.99 and d['rect'].height>pg.rect.height*.99:continue
   group=[(i,d)]
   if is_chainable(d):
    start,end=endpoints(d);j=i+1
    while j<len(drawings):
     nxt=drawings[j]
     if not is_chainable(nxt) or not same_style(d,nxt):break
     ns,ne=endpoints(nxt)
     if abs(end-ns)<0.03: oriented=nxt['items'];end=ne
     elif abs(end-ne)<0.03: oriented=[reverse_item(q) for q in reversed(nxt['items'])];end=ns
     else:break
     group.append((j,{**nxt,'items':oriented}));used.add(j);j+=1
   # Render the joined shaft as one SVG path so elbows and light motion stay continuous.
   merged={**d,'items':[item for _,part in group for item in part['items']]}
   merged['rect']=fitz.Rect(min(part['rect'].x0 for _,part in group),min(part['rect'].y0 for _,part in group),max(part['rect'].x1 for _,part in group),max(part['rect'].y1 for _,part in group))
   groups.append((group,merged))
  # Arrow shafts generated by TikZ use a separate 0.85 pt Bezier segment
  # after the 0.65 pt elbow stem, sometimes with a 2 pt tip clearance.
  # Join those pieces too, walking backward only through unbranched endpoints.
  consumed=set()
  for gi,(group,d) in enumerate(groups):
   if gi in consumed or not is_chainable(d):continue
   end_i=group[-1][0]
   head=next((v for v in drawings[end_i+1:end_i+3] if v['fill'] is not None and len(v['items'])==3 and all(it[0]=='l' for it in v['items']) and v['rect'].width<12 and v['rect'].height<12),None)
   if not head:continue
   while True:
    start,end=endpoints(d);candidates=[]
    for pi,(prev_group,prev) in enumerate(groups):
     if pi==gi or pi in consumed or not is_chainable(prev) or prev['color']!=d['color']:continue
     if prev_group[-1][0]>=group[0][0]:continue
     if abs((prev.get('width') or 0)-(d.get('width') or 0))>.25:continue
     ps,pe=endpoints(prev)
     gap=abs(pe-start)
     if gap<=2.05:candidates.append((gap,pi,prev_group,prev))
    if not candidates:break
    candidates.sort(key=lambda x:x[0])
    # At a fork, leave the shared branch alone rather than assigning it to one output.
    gap,pi,prev_group,prev=candidates[0]
    if len(candidates)>1 and abs(candidates[1][0]-gap)<.03:break
    ps,pe=endpoints(prev)
    bridge=[('l',pe,start)] if gap>.02 else []
    d={**d,'items':prev['items']+bridge+d['items'],'rect':prev['rect']|d['rect'],
       'width':prev['width'],'dashes':prev.get('dashes') or d.get('dashes')}
    group=prev_group+group;consumed.add(pi)
   groups[gi]=(group,d)
  for gi,(group,d) in enumerate(groups):
   if gi in consumed:continue
   if d['rect'].width>pg.rect.width*.99 and d['rect'].height>pg.rect.height*.99:continue
   p=[];last=None
   def pt(v):return fmt(v.x*scale)+' '+fmt(v.y*scale)
   for item in d['items']:
    kind=item[0]
    if kind=='re':
     r=item[1];p.append(f'M{fmt(r.x0*scale)} {fmt(r.y0*scale)}H{fmt(r.x1*scale)}V{fmt(r.y1*scale)}H{fmt(r.x0*scale)}Z');last=None;continue
    if kind=='qu':
     q=item[1];p.append('M'+pt(q.ul)+'L'+pt(q.ur)+'L'+pt(q.lr)+'L'+pt(q.ll)+'Z');last=None;continue
    start=item[1]
    if last is None or abs(start-last)>0.02:p.append('M'+pt(start))
    if kind=='l':p.append('L'+pt(item[2]));last=item[2]
    elif kind=='c':p.append('C'+' '.join(pt(v) for v in item[2:]));last=item[-1]
   if d.get('closePath'):p.append('Z')
   bounds=tuple(v*scale for v in d['rect']);ds=d.get('dashes') or ''
   dash=re.search(r'\[([^]]+)\]',ds);da=dash.group(1).strip() if dash else ''
   style=f'fill:{color(d.get("fill"))};stroke:{color(d.get("color"))};stroke-width:{fmt((d.get("width") or 0)*scale)};stroke-linecap:round;stroke-linejoin:round;fill-rule:{"evenodd" if d.get("even_odd") else "nonzero"}'
   if da:style+=';stroke-dasharray:'+','.join(fmt(float(v)*scale) for v in da.split())
   shape=f'<path d="{" ".join(p)}" style="{style}"/>'
   if self.n==9 and 37<=group[0][0]<=44:
    # PDF hatch patterns extend outside their rectangle and require its clip.
    x,y,x1,y1=[v*scale for v in (344.88,106.56,364.32,148.32)]
    cid=f'f89-unseen-{gi}'
    shape=f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/></clipPath></defs><g clip-path="url(#{cid})">{shape}</g>'
    bounds=(x,y,x1,y1)
   self.add(shape,bounds,d['seqno'])
   if self.n==25 and d['type']=='f' and len(d['items'])==7 and group[0][0]>=11:
    # Original arrows are filled seven-edge polygons. Animate their centerlines.
    vertices=[it[1] for it in d['items']]
    start=(vertices[0]+vertices[3])/2;tip=vertices[5]
    self.add(f'<path d="M{pt(start)}L{pt(tip)}" class="f8-flow rl-route" fill="none" stroke="#000" opacity="0"/>',bounds,d['seqno']+.1)
   if self.n==23 and group[0][0] in (20,21,23,24):
    # Use the original branch start, before the shared bus is merged with it.
    # Branch (c) already has a full route to the fusion encoder below.
    start,end=endpoints(group[0][1]);x,y=start.x*scale,start.y*scale
    branch_bounds=(x,y,x,end.y*scale)
    self.add(f'<path d="M{pt(start)}L{pt(end)}L489.231 352.308V381.247" class="f8-flow rl-route" fill="none" stroke="{BLUE}" opacity="0"/>',branch_bounds,d['seqno']+.1)
   # Keep arrowheads as their own shapes, but attach motion to the entire joined shaft.
   if is_chainable(d) and len(group)>0:
    end_i=group[-1][0];following=drawings[end_i+1:end_i+3]
    head=next((v for v in following if v['fill'] is not None and len(v['items'])==3 and all(it[0]=='l' for it in v['items']) and v['rect'].width<12 and v['rect'].height<12),None)
    # Orient animated path from its connected start to end, including all elbow segments.
    route_items=d['items'];route_d=[];last=None
    for item in route_items:
     st=item[1]
     if last is None or abs(st-last)>0.02:route_d.append('M'+pt(st))
     if item[0]=='l':route_d.append('L'+pt(item[2]));last=item[2]
     else:route_d.append('C'+' '.join(pt(v) for v in item[2:]));last=item[-1]
    if head and max(d['rect'].width,d['rect'].height)>1:
     track=f'<path d="{" ".join(route_d)}" class="f8-flow rl-route" fill="none" stroke="#3646f0" opacity="0" style="stroke-width:1px" data-duration="{max(1500,min(4200,max(d["rect"].width,d["rect"].height)*60)):.0f}"/>'
     self.add(track,bounds,d['seqno']+.1)
  # Use PyMuPDF's Unicode-correct text spans. The trace API exposes glyph IDs
  # for some embedded Type-1 math fonts and would map several Greek symbols wrong.
  for block in pg.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     value=span['text'].translate(str.maketrans({'휙':'φ','퐸':'E','퐷':'D','퐺':'G','휃':'θ','휓':'ψ','푝':'p','푛':'n','푧':'z','푇':'T','푡':'t','훼':'α','휎':'σ','휖':'ε','푣':'v','퐼':'I','휄':'ι','푖':'i','푥':'x','푦':'y','푤':'w','푟':'r','푎':'a','푏':'b','푘':'k','푚':'m','푠':'s','푢':'u','푐':'c','푑':'d','푒':'e','휂':'η','푢':'u','푀':'M','휅':'κ','푐':'c','휋':'π','푉':'V','푃':'P','푠':'s','ℎ':'h','ℓ':'l','푅':'R','퐾':'K','Í':'I','푘':'k','푆':'S','푓':'f','훾':'γ','훽':'β','Î':'∏'}))
     if not value.strip():continue
     x0,y0=span['origin']
     if self.n==5 and 124<x0<142 and abs(y0-174.923)<.01:
      value=value.replace('κ','K').replace('c','C')
     if self.n==14 and span['text']=='휅' and abs(y0-176.550)<.01:
      value='K'
     font=span['font'];is_math=not font.startswith('Aptos');size=span['size']*scale
     b=tuple(v*scale for v in span['bbox'])
     family="'Cambria Math'" if is_math else 'Figure711Sans'
     italic=('NewTXMI' in font or 'Italic' in font)
     style=f'font-family:{family};font-size:{fmt(size)}px;font-style:{"italic" if italic else "normal"};font-weight:{700 if "Bold" in font else 400};fill:{color(span["color"]/16777215 if False else ((span["color"]>>16&255)/255,(span["color"]>>8&255)/255,(span["color"]&255)/255))}'
     # The source PDF stores math as many font runs. Keep each run at its exact
     # PDF baseline and constrain Cambria Math to the source run's measured width.
     if self.n==13 and span['text']=='Î':
      # The TeX extensible operator origin is above the inline formula baseline.
      y0=324.05340576171875
     width=(span['bbox'][2]-span['bbox'][0])*scale
     self.add(f'<text x="{fmt(x0*scale)}" y="{fmt(y0*scale)}" textLength="{fmt(width)}" lengthAdjust="spacingAndGlyphs" style="{style}">{escape(value)}</text>',b,span.get('seqno',50000))
  self.assets()
 def finish(self):
  zones=[[] for _ in self.regions];scaffold=[]
  for z,svg,b in sorted(self.parts,key=lambda v:v[0]):
   cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
   candidates=[i for i,(_,r) in enumerate(self.regions) if r[0]<=cx<=r[2] and r[1]<=cy<=r[3]]
   if candidates:
    i=min(candidates,key=lambda i:(self.regions[i][1][2]-self.regions[i][1][0])*(self.regions[i][1][3]-self.regions[i][1][1]));zones[i].append(svg)
   else:scaffold.append(svg)
  info={};out=[]
  for i,((title,b),body) in enumerate(zip(self.regions,zones)):
   key=f'panel-{i}';info[key]={'t':title,'b':DESCRIPTIONS.get(title,f'{title} in Figure 8.{self.n}. Follow the independent connectors to inspect how the illustrated inputs, intermediate representations, and outputs relate.')}
   x,y,x1,y1=b
   out.append(f'<g class="rl-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(title)}">'+''.join(body)+f'<rect class="rl-hit" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/></g>')
  return f'<div class="nf nf-rl nf-f8 nf-{self.id}" data-nf="f8" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {fmt(self.h)}" role="group" aria-label="Figure 8.{self.n}: interactive reconstruction"><defs><marker id="f{self.id}-head" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L7 3.5L0 7Z" fill="{BLUE}"/></marker></defs><rect width="1000" height="{fmt(self.h)}" fill="white"/><g class="f8-scaffold">'+''.join(scaffold)+'</g>'+''.join(out)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(info)+'</script></div>'


def fallback(f):
 n=f.n;f.assets()
 if n==4:
  f.text(249,27,'Image to 3D',20,bold=True);f.text(249,50,'Assets',20,bold=True)
  f.text(750,27,'Text to 3D',20,bold=True);f.text(750,50,'Assets',20,bold=True)
  for x,lines in [(633,['“Vintage camera','with leather case”']),(882,['“Two-storey brick house','with red roof and fence”'])]:
   for j,s in enumerate(lines):f.text(x,268+j*13,s,11)
 if n==6:
  # Individual assets preserve the original occlusion order of this object montage.
  pass
 if n==8:
  specs=[('Two-view Reconstruction',0,160,124),('Multiple-view Reconstruction',160,385,124),('Continuous Reconstruction',385,640,124),('Large-scale Reconstruction',640,827,124),('Image Matching',827,1000,124),('Static 3DGS',0,242,278),('Dynamic 3DGS',242,428,278),('NVS with no 3D information',428,605,278),('Video Diffusion for NVS',605,795,278),('Image Diffusion for NVS',795,1000,278),('3DGS Generation',0,169,429),('NeRF Generation',169,400,429),('Mesh Generation',400,605,429),('SLAM',605,812,429),('Robotics Applications',812,1000,429)]
  for title,x,x1,y in specs:
   top=0 if y==124 else 143 if y==278 else 295
   f.regions.append((title,(x,top,x1,y+5)));f.text((x+x1)/2,y,title,11,width=min(x1-x-8,len(title)*6))
 if n==11:
  # Literature montage frames and all labels are native frontend primitives.
  for i,(title,_) in enumerate(f.regions):
   f.box(i*200+3,3,194,368,fill=['#fff2e7','#eaf5f7','#fffbdc','#f2f8ea','#f4effa'][i],stroke='#c8ced3')
   # Frames are behind the reviewed plates.
   f.parts[-1]=(1,f.parts[-1][1],f.parts[-1][2])
   f.text(i*200+100,394,f'({chr(97+i)})',13)
  labels=[(100,20,'Photorealistic'),(100,201,'Non-photorealistic'),(300,178,'Move and duplicate'),(500,177,'Object deformation'),(700,18,'Object removal'),(700,250,'Object completion'),(900,20,'Dataset Upsize')]
  for x,y,t in labels:f.text(x,y,t,10)
  for d,b in [('M299 98L305 52',(299,52,305,98)),('M299 101L305 135',(299,101,305,135)),('M695 53L702 82',(695,53,702,82)),('M695 134L702 101',(695,101,702,134))]:f.line(d,b,True,sw=1)
 if n==18:
  for i,x in enumerate([130,365,600,868]):f.text(x,22,f'({chr(97+i)})',20)
  f.box(0,287,730,34,'#ddd','#ddd');f.text(365,311,'Keypoint-based',21,bold=True)
  f.box(747,287,250,34,'#ddd','#ddd');f.text(872,311,'Rotation-based',21,bold=True)
  for x,s in [(135,'Skinning'),(383,'Shape'),(625,'Pose'),(876,'Articulated body')]:f.text(x,624,s,16,bold=True)
 if n==24:
  f.h=525
  f.text(500,21,'All three paradigms internalize the structure, dynamics, and semantics of the world; they differ in what they predict.',13,fill='#858585')
  data=[('Representation',['Multimodal','observations'],['Encoder Eₒ','+ latent predictor Pₛ'],['Latent state','S(t+1)'],['predict in latent space','e.g., JEPA, DINO-WM','(Eq. 8.72)']),('Generative',['State and action','(O₁:ₜ, A₁:ₜ)'],['Generative model','pθ(Oₜ₊₁:ₜ₊ₕ | ·)'],['Synthesized futures','Oₜ₊₁:ₜ₊ₕ'],['model future states','e.g., Sora, Genie, Cosmos','(Eq. 8.73)']),('Mental',['Observed agent','behavior Oᴬ'],['Mental-state inference','M(z): beliefs,','desires, intentions'],['Predicted action','Âₜ₊₁'],['reason about minds','(Theory of Mind, BDI)','(Eq. 8.75)'])]
  for i,(title,inp,mid,out,foot) in enumerate(data):
   x=36+i*333;cx=x+130
   f.text(cx,61,f'({chr(97+i)}) {title}',19,bold=True);f.text(cx,85,'world model',19,bold=True)
   for j,(top,lines) in enumerate([(113,inp),(245,mid),(389,out)]):
    h=87 if j==0 else 93 if j==1 else 67
    f.box(x,top,260,h,'#dde9f6' if j==1 else '#f7f7f7','#555')
    for k,s in enumerate(lines):f.text(cx,top+28+k*23,s,18,math=(j>0))
   f.line(f'M{cx} 202V242',(cx-3,202,cx+3,242),True,stroke='#333')
   f.line(f'M{cx} 340V385',(cx-3,340,cx+3,385),True,stroke='#333')
   for k,s in enumerate(foot):f.text(cx,477+k*17,s,14,math=k==0,italic=k==0,fill='#888')


def build(n):
 if n==22:
  from figure822 import fig822
  return fig822()
 f=Figure(n);pdf=BOOK/(Path(f.entry['sources'][0]).stem+'.pdf')
 if pdf.exists():
  f.pdf(pdf)
  # Figure 8.25 retains its original black polygon arrows and native motion routes.
 else:fallback(f)
 return f.finish()

CSS='''
.nf-f8 text{letter-spacing:0}.nf-f8 .rl-hit{stroke-width:0}.nf-f8 .rl-zone{isolation:isolate}
.nf-f8 .rl-pulse{r:2;stroke-width:.45;filter:drop-shadow(0 0 2px white) drop-shadow(0 0 4px #48a5ff)}
.nf-f8 .rl-glow{r:5;filter:blur(2.5px)}.nf-f8 .f8-scaffold{pointer-events:none;transition:opacity .22s}
.nf-f8.is-focus .f8-scaffold{opacity:.1}
@media(prefers-reduced-motion:reduce){.nf-f8 .f8-scaffold{transition:none}}
'''
STYLE='''body{margin:24px;background:#f4f6f8;color:#29353b;font:16px/1.5 Arial}main{max-width:1800px;margin:auto}h1{font-size:24px}h2{font-size:19px}.original{display:block;width:100%;height:auto;background:white}section{background:white;margin:28px 0;padding:18px}nav{display:flex;gap:16px;flex-wrap:wrap}a{color:#3046c9}.compare{display:grid;grid-template-columns:1fr 1fr;gap:20px}.compare>div{min-width:0}@media(max-width:900px){.compare{grid-template-columns:1fr}}@media(max-width:600px){body{margin:10px}section{padding:5px}}'''
def head(title):return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="/assets/css/site.css?v=f8-review4"><link rel="stylesheet" href="/assets/css/figures81-825.css?v=4"><style>{STYLE}</style><main>'
def foot():return '</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=f8-review4";mountNative();</script></html>'
def main():
 (SITE/'source/src/css/figures81-825.css').write_text(CSS);(SITE/'assets/css/figures81-825.css').write_text(CSS)
 overview=[head('Figures 8.1–8.25 · Interactive reconstruction review'),'<h1>Figures 8.1–8.25 · Interactive reconstruction review</h1><nav>']
 overview += [f'<a href="#f8{n}">8.{n}</a>' for n in range(1,26)];overview+=['</nav>']
 stats={}
 for n in range(1,26):
  markup=build(n);entry=INV[n-1];ident=f'8{n}'
  originals=''.join(f'<img class="original" src="/{s}" alt="Original Figure 8.{n}">' for s in entry['sources'])
  page=head(f'Figure 8.{n} comparison')+'<nav><a href="/example/figures81-825.html">All figures</a><a href="#redraw">Reconstruction</a></nav>'+f'<h1>Figure 8.{n} · Original and reconstruction</h1><div class="compare"><div><h2>Original</h2>'+originals+'</div><div><h2 id="redraw">Interactive reconstruction</h2>'+markup+'</div></div>'+foot()
  (SITE/f'example/figure{ident}.html').write_text(page)
  (SITE/f'example/figure{ident}-reconstruction.html').write_text(markup)
  overview += [f'<section id="f{ident}"><h2><a href="/example/figure{ident}.html">Figure 8.{n} · Compare with original</a></h2>'+markup+'</section>']
  stats[ident]={'images':markup.count('<image'),'paths':markup.count('<path'),'texts':markup.count('<text'),'zones':markup.count('role="button"'),'motion_tracks':markup.count('class="f8-flow rl-route"')}
 (SITE/'example/figures81-825.html').write_text(''.join(overview)+foot())
 (SITE/'example/figures81-825-validation.json').write_text(json.dumps(stats,indent=2))
 print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
