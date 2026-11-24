"""Editable, source-registered reconstructions of Figures 12.1–14.5.

Approved PNG plates retain their independent placement; text, formula runs,
paths and arrow motion are SVG elements. Generate review previews only.
"""
from pathlib import Path
from html import escape
import json, re, unicodedata
import fitz
from lxml import etree
import figures91_924 as native
from figures101_1116 import Figure as PreviousFigure

SITE=Path(__file__).resolve().parents[2]
INV=json.loads((SITE/'source/pipeline/figures121_145_sources.json').read_text())
PANELS={
'12.1':[
('Acquire observations',(.01,.01,.25,.59),'CT, MRI, ultrasound, endoscopy and pathology provide observations of the patient or specimen.'),
('Perceive anatomy',(.27,.01,.49,.59),'Segmentation and localization identify anatomical structures and the target region.'),
('Model and plan',(.51,.01,.72,.59),'Patient-specific reconstruction supports simulation and treatment planning.'),
('Guided intervention',(.74,.01,.99,.59),'A clinician uses tracked tools, imaging and aligned guidance to carry out the plan.'),
('Live alignment loop',(.01,.61,.99,.99),'Live imaging and tracking update patient-frame alignment; intervention changes the patient state and prompts new observations.')],
'12.2':[
('Segmentation',(.01,.01,.32,.99),'A volume is mapped to voxel labels, organ masks and three-dimensional anatomy. The depicted labels are illustrative.'),
('Detection and localization',(.34,.01,.65,.99),'A candidate region is located in voxel coordinates and mapped into patient coordinates using image geometry.'),
('Multimodal registration',(.67,.01,.99,.99),'Moving and reference images jointly determine a transform; aligned landmarks and surfaces provide a consistency check.')],
'12.3':[
('Anatomical reconstruction',(.01,.01,.32,.99),'A segmented volume becomes a patient anatomy mesh through surface extraction, shape priors or an implicit representation.'),
('Patient-specific model',(.34,.01,.67,.99),'Anatomy and physiological measurements personalize a model for simulation. New observations can update its parameters.'),
('Treatment planning',(.69,.01,.99,.99),'Simulation supports plan selection. Cardiac catheter targeting and radiotherapy dose prediction are alternative examples.')],
'12.4':[
('Anatomical registration',(.01,.01,.33,.75),'Preoperative anatomy and patient reference observations determine a patient-frame transform.'),
('Tracking and guidance',(.35,.01,.66,.48),'A calibrated tracked tool and patient reference provide the tool pose used by patient-frame fusion.'),
('Endoscopic geometry',(.68,.01,.99,.78),'Endoscopic imagery yields depth and dynamic geometry, registered to the patient before optional downstream use.'),
('Fusion and AR guidance',(.35,.49,.66,.99),'The registered model and tracked-tool pose are fused for aligned AR anatomy and tip guidance.'),
('Intraoperative update',(.01,.77,.33,.99),'New observations can update registration when tissue shifts; display calibration supports the presentation of guidance.'),
('Robot control',(.70,.81,.99,.99),'The optional robot controller consumes the fused state rather than raw endoscopic imagery.')],
'12.5':[
('Physics: representation',(.16,.06,.43,.32),'Spatial fields represent physical state and geometry.'),
('Chemistry: representation',(.44,.06,.69,.32),'Molecular and periodic structures encode spatial arrangements of atoms.'),
('Life science: representation',(.70,.06,.99,.32),'Proteins, cells and tissues provide complementary biological structures.'),
('Physics: dynamics',(.16,.34,.43,.59),'Observed fields constrain a dynamical model, such as a wave equation.'),
('Chemistry: dynamics',(.44,.34,.69,.59),'Quantum or interatomic dynamics connect molecular structure to evolution and properties.'),
('Life science: dynamics',(.70,.34,.99,.59),'Biological dynamics model changes in a structured biological state.'),
('Physics: design and control',(.16,.61,.43,.86),'Inverse design and control choose structures or inputs that produce desired physical behavior.'),
('Chemistry: design',(.44,.61,.69,.86),'Generative design proposes candidate molecules or materials subject to spatial constraints.'),
('Life science: design',(.70,.61,.99,.86),'Biomolecular and tissue design are alternative examples at different biological scales.')],
'12.6':[
('Recover a continuous field',(.01,.01,.32,.99),'Sparse observations constrain a reconstructed continuous physical field.'),
('Fit and discover dynamics',(.34,.01,.66,.99),'A learned operator rolls the field forward in time. A separate law-extraction step proposes a candidate governing law.'),
('Optimize control',(.68,.01,.99,.99),'A differentiable simulator supplies objective gradients to an optimizer, which adjusts control inputs toward the target state.')],
'12.7':[
('Symmetry-aware representation',(.01,.01,.32,.91),'Molecular and periodic geometry support E(3)-equivariant features while respecting transformations of coordinates.'),
('Molecular simulation',(.34,.01,.66,.91),'Coordinate gradients of an invariant learned energy provide forces for molecular dynamics and related property prediction.'),
('Three-dimensional generative design',(.68,.01,.99,.91),'Reverse diffusion denoises atom coordinates into a candidate structure, potentially modeling atom types jointly.')],
'12.8':[
('Reconstruct biological structure',(.01,.01,.32,.99),'Sequence-to-structure prediction and cryo-EM projection-to-density reconstruction are complementary routes to three-dimensional biological structure.'),
('Binding-pose geometry',(.34,.01,.66,.99),'Translation, rotation and bond torsion describe a ligand pose within a protein pocket.'),
('De novo protein design',(.68,.01,.99,.99),'A generated protein backbone is followed by sequence design under motif or function constraints.')],
'13.1':[
('User and scene observations',(.01,.01,.26,.62),'User needs and the observed environment supply the context for assistance.'),
('Instruction',(.01,.65,.26,.88),'A natural-language request specifies the intended task and target state.'),
('Perception and persistent memory',(.31,.01,.68,.54),'Scene observations populate persistent room-object memory, including object identities and spatial associations.'),
('Ground and plan',(.31,.56,.68,.92),'The request is grounded to remembered objects and a target state before a task plan is selected.'),
('Assistive outputs',(.72,.01,.99,.92),'Household management, shared-space collaboration and audio or haptic cues are alternative outputs; user responses close the loop.')],
'13.2':[
('Observe and update',(.01,.01,.28,.43),'RGB-D or phone observations update a representation of rooms and objects.'),
('Persistent home memory',(.32,.01,.70,.49),'The assistant maintains room-object associations, identities and observation times.'),
('Ground the task and act',(.74,.01,.99,.79),'A request is grounded to specific object identifiers and a goal, then executed with navigation, grasping and placement.'),
('Search and recall',(.01,.50,.28,.82),'A query about an object triggers retrieval of its last observed state.'),
('Retrieve current evidence',(.32,.52,.70,.99),'Identity, relations and observation time support an answer tied to the latest available evidence.')],
'13.3':[
('Proxemic context',(.01,.01,.32,.99),'The person, robot and shared environment determine comfortable interaction distances; context changes those preferences.'),
('Align spatial frames',(.34,.01,.67,.99),'Robot and human views are aligned through shared object identities and spatial relations before interaction-aware planning.'),
('Legible interaction',(.69,.01,.99,.99),'A readable path and offer or transfer gesture help the person anticipate the robot’s next action.')],
'13.4':[
('User goals and access needs',(.01,.01,.28,.91),'Observed goals and access needs include vision, memory, attention and mobility support.'),
('Shared spatial engine',(.33,.01,.65,.43),'The observed environment is represented through objects, locations and activity state.'),
('Personalize with consent',(.33,.45,.65,.90),'Support is personalized to an output channel, subject to consent, data limits and confidence. Uncertainty can trigger clarification or a pause.'),
('Direction and reminders',(.70,.01,.99,.58),'Audio and haptic direction cues and stepwise reminders provide alternative assistive outputs.'),
('Shared-control assistance',(.70,.63,.99,.99),'A user goal or joystick input is combined with spatial constraints to support assisted motion.')],
'14.1':[
('Scan to BIM',(.01,.01,.33,.53),'Observed building elements are registered to a building information model, including slabs, columns and walls.'),
('As-designed model',(.36,.34,.64,.80),'The BIM supplies planned geometry, schedule and element identifiers for comparison and execution.'),
('Progress monitoring',(.67,.01,.99,.53),'An observed scan is compared with planned state; a planned element may not yet be observed.'),
('Structural inspection',(.01,.58,.33,.99),'Detected damage is localized and linked to a model element to guide inspection and site updates.'),
('Construction robotics',(.67,.58,.99,.99),'Registered model geometry supports model-guided placement; subsequent capture updates the site state.')],
'14.2':[
('Player tracking and registration',(.01,.01,.32,.99),'Player identities and ball observations are registered across frames and into pitch coordinates.'),
('Pose and biomechanics',(.34,.01,.66,.99),'Calibrated views triangulate three-dimensional joints; pose sequences support joint angles, motion measures and estimated loads.'),
('Tactical analysis',(.68,.01,.99,.99),'Registered trajectories support space-control regions, predicted motion and candidate passing lanes.')],
'14.3':[
('Digitize heritage',(.01,.01,.32,.99),'Multi-view observations are registered and reconstructed into a textured three-dimensional surface or mesh.'),
('Restore fragments',(.34,.01,.66,.99),'Fragment geometry and appearance constrain matching, alignment and virtual reassembly of the mural.'),
('Discover structures',(.68,.01,.99,.99),'Airborne LiDAR separates canopy and ground returns, yielding bare-earth relief and candidate structures.')],
'14.4':[
('Underwater perception',(.01,.01,.43,.39),'Image enhancement improves visibility before visual observations are used downstream.'),
('Localization',(.69,.01,.99,.53),'Acoustic or sonar measurements, pressure and inertial observations support pose and aligned observations.'),
('Underwater robot',(.39,.41,.65,.65),'The underwater platform links sensing, mapping and inspection actions in a closed loop.'),
('Inspection',(.01,.57,.42,.99),'Inspection localizes defects on a hull or pipeline and selects a subsequent view.'),
('Terrain and structure mapping',(.68,.61,.99,.99),'A spatial map of terrain, habitat or structures supports coverage and standoff planning.')],
'14.5':[
('Calibrated observations',(.25,.01,.77,.46),'Calibrated cameras associate observations across the store in a common spatial frame.'),
('Cashierless checkout',(.01,.10,.23,.61),'A person-product interaction updates a virtual basket linked to the shopper identity.'),
('Shelf monitoring',(.79,.10,.99,.61),'Observed shelf slots are compared with the expected planogram to detect empty or misplaced stock.'),
('Person-product-location binding',(.28,.49,.75,.63),'Person identity, product identity, shelf location and time bind observations into a consistent event.'),
('Shopper-flow analytics',(.24,.66,.77,.99),'Aggregated ground locations provide flow direction and visit-density estimates.')],
}

class Figure(PreviousFigure):
 def add(self,svg,bounds,z=0):
  super().add(svg,bounds,z)
  order,markup,box=self.parts[-1]
  # Normalize mathematical alphanumeric glyphs to Cambria's corresponding
  # ordinary character, retaining the source font run's explicit italics.
  def normalize(match):
   content=match.group(2)
   content=''.join(unicodedata.normalize('NFKC',chr(ord(ch)+0x10000) if 0xd400<=ord(ch)<=0xd7ff else ch) if 0xd400<=ord(ch)<=0xd7ff or 0x1d400<=ord(ch)<=0x1d7ff else ch for ch in content)
   return match.group(1)+content+match.group(3)
  markup=re.sub(r'(<text\b[^>]*>)(.*?)(</text>)',normalize,markup).replace('f1011-flow','f1214-flow')
  # The source's txexs tilde is encoded as "e". Cambria renders that literal
  # letter at p's baseline; retain the original standalone accent outline.
  if self.id=='122' and re.search(r'<text x="399\.952"[^>]*>e</text>',markup):
   tilde='M.6359863 .7250366H.60598757C.59799197 .7000427 .56900027 .67803958 .46998597 .67803958 .375 .6779785 .34298707 .72198489 .25099183 .72198489 .09899902 .72198489 .055999757 .6769867 .02999878 .62098696H.05999756C.067993167 .64598086 .10398865 .6669922 .20298767 .6669922 .29699708 .66703799 .32998658 .6230469 .42199708 .6230469 .57398989 .6230469 .6100006 .66903689 .6359863 .7250366Z'
   markup=re.sub(r'<text x="399\.952"[^>]*>e</text>',f'<path class="formula-accent" aria-label="tilde" d="{tilde}" transform="translate(399.952 629.318) scale(18.263 -18.263)" fill="#29363f"/>',markup)
  self.parts[-1]=(order,markup,box)
 def motion_routes(self,drawings):
  # Coordinates and legend samples describe the diagram; they do not transmit
  # a signal. Exclude their shafts before recovering complete process routes.
  static={
   '124':[(20,465,80,520)],
   '125':[(185,45,380,145),(145,478,985,489)],
   '127':[(390,280,615,399)],
   '142':[(510,270,660,345),(398,490,467,556),(710,587,775,602)],
   '144':[(895,55,970,125)],
   '145':[(785,588,960,602)],
  }.get(self.id,[])
  scale=1000/self.doc[0].rect.width
  def eligible(d):
   b=tuple(v*scale for v in d['rect'])
   return not any(r[0]<=b[0] and r[1]<=b[1] and b[2]<=r[2] and b[3]<=r[3] for r in static)
  routes=native.arrow_routes([d for d in drawings if eligible(d)],strict_dashes=True)
  if self.id=='134':
   # The source draws one vertical bus between three arrowheads. Each output
   # starts at the consent gate, rather than at another output's arrowhead.
   routes=[route for route in routes if int(route[2]) not in (60,66,69)]
   for seqno,y in [(60,130.325),(66,354.344),(69,692.045)]:
    shaft=next(d for d in drawings if d['seqno']==seqno)
    a=fitz.Point(583.416/scale,528.210/scale);b=fitz.Point(655.303/scale,528.210/scale);c=fitz.Point(655.303/scale,y/scale)
    items=[('l',a,b),('l',b,c)]+shaft['items']
    routes.append((items,fitz.Rect(min(a.x,c.x),min(a.y,c.y),shaft['rect'].x1,max(a.y,c.y)),seqno+.1))
  return routes
 def pdf(self,path):
  return native.Figure.pdf(self,path,route_builder=self.motion_routes)
 def image_clips(self,page):
  # Image clips are absent from get_drawings' seqno map. Recover the exact
  # SVG polygon/curve clips for image placements as well as vector primitives.
  root=etree.fromstring(page.get_svg_image(text_as_path=False).encode())
  images=[im for im in root.xpath('//*[local-name()="image"]') if not any(etree.QName(a).localname=='defs' for a in im.iterancestors())]
  clips={};known={};scale=1000/page.rect.width
  for index,image in enumerate(images):
   ids=[]
   for ancestor in reversed(list(image.iterancestors())):
    value=ancestor.get('clip-path')
    if not value:continue
    old=value[5:-1]
    if old not in known:
     cid=f'f{self.id}-image-clip-{len(known)}';known[old]=cid
     source=root.xpath('//*[@id=$old]',old=old)[0]
     children=''.join(etree.tostring(child,encoding='unicode') for child in source)
     self.clip_defs.append(f'<clipPath id="{cid}" transform="scale({scale})">{children}</clipPath>')
    ids.append(known[old])
   clips[index]=ids
  return clips,len(images)
 def render(self):
  path=SITE.parent/f'Spatial_Intelligence_Book_2025_v14/figures/part4/section{self.entry["chapter"]}'/(Path(self.entry['sources'][0]).stem+'.pdf')
  doc=fitz.open(path);page=doc[0];reg=native.registration(self.n,page,self.man,figure_id=self.id,min_scale=.80)
  a=reg['scale'];dx=reg['x'];dy=reg['y'];source_h=self.h;pdf_h=page.rect.height/page.rect.width*1000
  self.regions=[(title,(b[0]*1000*a+dx,b[1]*pdf_h*a+dy,b[2]*1000*a+dx,b[3]*pdf_h*a+dy)) for title,b,_ in PANELS[self.key]]
  self.prepare_clips(page);image_clips,image_count=self.image_clips(page)
  self.pdf(path);self.h=source_h
  image_order=[i for i,(kind,_) in enumerate(page.get_bboxlog()) if kind=='fill-image']
  assert len(image_order)==image_count==len(self.man['assets']),(self.key,len(image_order),image_count)
  for asset in self.man['assets']:
   index=asset['pdf_image_index'];x,y,x1,y1=asset['pdf_box']
   markup=f'<image href="/assets/img/figs/f{self.id}/{asset["file"]}" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}" preserveAspectRatio="none"/>'
   for cid in reversed(image_clips[index]):markup=f'<g clip-path="url(#{cid})">{markup}</g>'
   # Assets are in normalized PDF coordinates until the same whole-figure
   # registration as the vectors is applied below.
   self.add(markup,(x,y,x1,y1),image_order[index])
  self.parts=[(z,f'<g transform="translate({dx} {dy}) scale({a})">{svg}</g>',(b[0]*a+dx,b[1]*a+dy,b[2]*a+dx,b[3]*a+dy)) for z,svg,b in self.parts]
  return self.finish()
 def finish(self):
  zones=[[] for _ in self.regions];scaffold=[]
  for z,svg,b in sorted(self.parts,key=lambda v:v[0]):
   cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
   covers=[i for i,(_,r) in enumerate(self.regions) if b[0]<=(r[0]+r[2])/2<=b[2] and b[1]<=(r[1]+r[3])/2<=b[3]]
   candidates=[] if len(covers)>1 else [i for i,(_,r) in enumerate(self.regions) if r[0]<=cx<=r[2] and r[1]<=cy<=r[3]]
   if candidates:
    i=min(candidates,key=lambda i:(self.regions[i][1][2]-self.regions[i][1][0])*(self.regions[i][1][3]-self.regions[i][1][1]));zones[i].append(svg)
   else:scaffold.append(svg)
  out=[];info={}
  for i,((title,b),body) in enumerate(zip(self.regions,zones)):
   assert body,(self.key,title)
   key=f'panel-{i}';info[key]={'t':title,'b':PANELS[self.key][i][2]};x,y,x1,y1=b
   out.append(f'<g class="rl-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(title)}">'+''.join(body)+f'<rect class="rl-hit" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/></g>')
  return f'<div class="nf nf-rl nf-f1214 nf-{self.id}" data-nf="f1214" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {native.fmt(self.h)}" role="group" aria-label="Figure {self.key}: interactive reconstruction"><rect width="1000" height="{native.fmt(self.h)}" fill="white"/><defs>{"".join(self.clip_defs)}</defs><g class="f1214-scaffold">'+''.join(scaffold)+'</g>'+''.join(out)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(info)+'</script></div>'

CSS=native.CSS.replace('nf-f9','nf-f1214').replace('f9-scaffold','f1214-scaffold')
def head(title):
 return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="/assets/css/site.css?v=f1214-1"><link rel="stylesheet" href="/assets/css/figures121-145.css?v=1"><style>{native.STYLE}</style><main>'
def foot():return '</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=f1214-1";mountNative();</script></html>'
def main():
 for base in ['source/src/css','assets/css']:(SITE/base/'figures121-145.css').write_text(CSS)
 overview=[head('Figures 12.1–14.5 · Interactive reconstruction'),'<h1>Figures 12.1–14.5 · Interactive reconstruction</h1><nav>']
 overview += [f'<a href="#f{e["chapter"]}{e["number"]}">{e["chapter"]}.{e["number"]}</a>' for e in INV];overview+=['</nav>'];stats={}
 for e in INV:
  figure=Figure(e);markup=figure.render();ident=figure.id;key=figure.key
  originals=''.join(f'<img class="original" src="/{s}" alt="Original Figure {key}">' for s in e['sources'])
  page=head(f'Figure {key} comparison')+'<nav><a href="/example/figures121-145.html">All figures</a><a href="#redraw">Reconstruction</a></nav>'+f'<h1>Figure {key} · Original and reconstruction</h1><div class="compare"><div><h2>Original</h2>'+originals+'</div><div><h2 id="redraw">Interactive reconstruction</h2>'+markup+'</div></div>'+foot()
  (SITE/f'source/pipeline/native/figure{ident}.html').write_text(markup)
  (SITE/f'example/figure{ident}.html').write_text(page);(SITE/f'example/figure{ident}-reconstruction.html').write_text(markup)
  overview += [f'<section id="f{ident}"><h2><a href="/example/figure{ident}.html">Figure {key} · Compare with original</a></h2>'+markup+'</section>']
  stats[ident]=dict(images=markup.count('<image'),paths=markup.count('<path'),texts=markup.count('<text'),zones=markup.count('role="button"'),motion_tracks=markup.count('class="f1214-flow rl-route"'))
  print(key,stats[ident],flush=True)
 (SITE/'example/figures121-145.html').write_text(''.join(overview)+foot());(SITE/'example/figures121-145-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':main()
