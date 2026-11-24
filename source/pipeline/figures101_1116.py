"""Faithful editable reconstructions of Figures 10.1–11.16.

Reuse the reviewed PDF primitive recovery from Chapter 9: clipping, alpha,
continuous full-route arrow motion, source font baselines, and arrowhead tracking.
Panel geometry is registered against the original website WebP. This batch
produces comparison previews; integration follows visual approval.
"""
from pathlib import Path
from html import escape
import json
import fitz
from PIL import Image
import figures91_924 as native

SITE=Path(__file__).resolve().parents[2]
INV=json.loads((SITE/'source/pipeline/figures101_1116_sources.json').read_text())
# Rectangles are fractions of the source PDF page, transformed along with its
# content to the website original. Titles/legends are never standalone regions.
# Each record contains a meaningful diagram region and an English explanation.
PANELS={
'10.1':[
('Sense',(.01,.06,.33,.51),'Outward cameras and inertial measurements provide visual and motion observations for the XR tracking loop.'),
('Track and map',(.35,.06,.66,.51),'Visual–inertial SLAM estimates the six-degree-of-freedom device pose and builds a scene mesh.'),
('Register content',(.68,.06,.99,.51),'World-anchored virtual content is aligned with the scene, including occlusion and lighting.'),
('User in the loop',(.01,.58,.33,.96),'Head motion and hand actions change the observations and close the interaction loop.'),
('User-facing input',(.35,.58,.66,.96),'Gaze, pinch and body pose provide the interaction state used to select and manipulate content.'),
('Render and display',(.68,.58,.99,.96),'Foveation and stereo optics turn the registered scene into a displayed view, with fine detail near gaze.')],
'10.2':[
('Inside-out tracking',(.01,.01,.32,.99),'Camera and inertial samples are fused to estimate device pose from observed landmarks.'),
('Map and understand',(.35,.01,.66,.99),'Persistent scene geometry, planes, meshes and semantic labels support relocalization and stable anchors.'),
('Register content',(.69,.01,.99,.99),'Depth testing hides virtual pixels behind real surfaces while matched shading helps blend virtual and real content.')],
'10.3':[
('Hand tracking',(.01,.01,.32,.41),'The hand image is converted into an articulated 21-joint pose for gesture understanding.'),
('Eye and gaze tracking',(.01,.43,.32,.61),'An inward-facing eye camera estimates a three-dimensional gaze direction.'),
('Sparse body tracking',(.01,.64,.32,.99),'A few tracked body points constrain a larger pose; the remaining body joints are inferred.'),
('Spatial intent',(.38,.35,.61,.69),'Gaze and pose signals combine into spatial intent for selection, manipulation, avatar motion and locomotion.'),
('Gaze targets',(.66,.01,.99,.57),'Gaze identifies a target interface element; the highlighted Schedule row supplies the candidate target.'),
('Gaze and pinch activation',(.66,.58,.99,.99),'The selected target and a pinch event are combined before the Schedule action is activated.')],
'10.4':[
('Foveated rendering',(.01,.09,.29,.99),'Rendering allocates fine sampling near the tracked gaze point and coarser sampling in peripheral regions.'),
('Late reprojection',(.32,.09,.66,.99),'The latest pose warps an earlier rendered frame just before scanout, reducing visible motion latency.'),
('Video passthrough',(.69,.09,.83,.99),'A camera-mediated real-world view is combined with virtual content before reaching the eye.'),
('Optical see-through',(.84,.09,.99,.99),'Real-world light reaches the eye directly while optics add the virtual overlay.')],
'10.5':[
('Sensor inputs',(.01,.01,.23,.84),'RGB-D, film cameras and headset tracking provide scene, performer and viewer observations.'),
('World reconstruction',(.26,.08,.67,.31),'Geometry, semantics and lighting describe the world that will be rendered.'),
('Performance capture',(.26,.33,.67,.55),'Body, face and hand capture provide motion and expression for digital performances.'),
('Content authoring',(.26,.57,.67,.81),'Assets, layout, behavior and camera design turn spatial representations into an authored experience.'),
('Presented experience',(.73,.01,.99,.56),'Compositing and rendering present the digital scene to the user.'),
('User response',(.73,.59,.99,.87),'User response supplies new actions and observations for the live runtime loop.')],
'10.6':[
('Geometric fusion',(.01,.01,.32,.99),'RGB-D frames and camera poses fuse into a signed-distance field, then a surface mesh for collision and occlusion.'),
('Appearance models',(.35,.01,.66,.99),'Neural radiance fields and 3D Gaussian splatting offer alternative appearance representations for novel views.'),
('Visual positioning',(.69,.01,.99,.99),'A query image is matched to map landmarks to localize the viewer for persistent place-based AR.')],
'10.7':[
('Skeleton capture',(.01,.01,.30,.67),'Three-dimensional joint positions are retargeted to a rig for character motion.'),
('Parametric surface',(.35,.01,.65,.67),'A parametric body model fits shape and pose to drive a body mesh.'),
('Volumetric capture',(.69,.01,.99,.67),'Textured volumes or Gaussian representations reconstruct the performer for animation and playback.'),
('Avatar playback and timing',(.01,.70,.99,.99),'Captured motion is transferred to avatar playback; alignment, latency and temporal stability affect the result.')],
'10.8':[
('Engine primitives',(.01,.01,.32,.99),'Planes and world-locked anchors provide a persistent spatial reference for placing assets and behavior scripts.'),
('Virtual production',(.35,.01,.66,.99),'A tracked camera updates the LED-wall perspective to maintain the correct viewpoint and parallax.'),
('Camera planning',(.69,.01,.99,.99),'Narrative and scene constraints guide camera motion, shot planning and composition.')],
'11.1':[
('Physical asset',(.01,.01,.30,.57),'Images, LiDAR and telemetry observe the physical machine and its operating state.'),
('Construct the twin',(.36,.01,.63,.57),'Geometry, materials and articulated joints form a spatial model of the asset.'),
('Model and simulate',(.69,.01,.99,.49),'Dynamics and model parameters predict how the asset responds over time.'),
('Synchronize',(.36,.54,.64,.94),'Live observations correct the estimated state and uncertainty of the digital twin.'),
('Predict and decide',(.69,.54,.99,.94),'Forecasts inform operational decisions, control and maintenance actions on the physical asset.')],
'11.2':[
('Metric geometry',(.01,.01,.32,.90),'Multi-view images, LiDAR or RGB-D establish calibrated geometry, with scale and surface repair where needed.'),
('Relightable materials',(.35,.01,.66,.90),'Albedo, roughness and surface normals separate material properties from illumination.'),
('Physical articulation',(.69,.01,.99,.90),'Joint axes, part hierarchy, mass and friction describe how an articulated asset can move.')],
'11.3':[
('Constructed model',(.01,.01,.30,.53),'The reconstructed robot, objects and joints provide a spatial model for simulation.'),
('Physics engine',(.34,.01,.64,.53),'Rigid or deformable dynamics simulate contact, mass, friction and stiffness.'),
('Simulated behavior',(.69,.01,.99,.53),'The simulator predicts trajectories and responses to the applied actions.'),
('Real-asset observations',(.01,.60,.30,.99),'Observations of the real robot provide evidence for matching simulated and physical behavior.'),
('System identification',(.34,.60,.64,.99),'Model parameters are updated to reduce the discrepancy between predicted and observed behavior.'),
('Optional fast surrogate',(.69,.60,.99,.99),'Reduced or learned dynamics can approximate the next state for faster prediction.')],
'11.4':[
('Physical asset and telemetry',(.01,.01,.30,.45),'Vibration, temperature and pressure measurements describe the physical machine state.'),
('State assimilation',(.35,.01,.64,.45),'A prior prediction and observations combine into a posterior state estimate through a filtering update.'),
('Synchronized twin',(.69,.01,.99,.45),'The corrected state and uncertainty update the twin, which supplies the next prediction.'),
('Predictive operation',(.01,.49,.99,.83),'Forecasting, what-if analysis, anomaly detection and useful-life estimation support operation.'),
('Decision and control',(.28,.87,.70,.99),'The synchronized model informs control and maintenance actions on the physical asset.')],
'11.5':[
('Geospatial inputs',(.01,.01,.22,.76),'Satellite, UAV, LiDAR, GNSS and IoT observations provide complementary geospatial evidence.'),
('CNN spatial features',(.25,.11,.55,.33),'Convolutional models extract spatial features from geospatial observations.'),
('Transformer context',(.25,.35,.55,.56),'Attention models capture context and relationships among locations and observations.'),
('Ensemble uncertainty',(.25,.58,.55,.78),'Multiple models combine evidence and characterize prediction uncertainty.'),
('Application outputs',(.59,.01,.99,.79),'Geospatial predictions support agriculture, cities, environmental monitoring, water, disasters and public health.'),
('Maps and decisions',(.01,.84,.99,.99),'Maps and forecasts inform planning, policy and interventions; subsequent observations close the loop.')],
'11.6':[
('Crop mapping',(.01,.01,.32,.99),'SAR, optical and UAV time series distinguish crop types across fields.'),
('Yield and LAI estimation',(.35,.01,.66,.99),'Imagery, weather and field samples estimate yield and leaf area index, evaluated against observations.'),
('Precision irrigation',(.69,.01,.99,.99),'Moisture, weather and crop demand determine variable-rate irrigation and valve or pivot commands.')],
'11.7':[
('Shared urban context',(.01,.01,.34,.52),'A common city representation relates overhead and street-view observations in one spatial context.'),
('Structure extraction',(.37,.01,.67,.52),'Imagery, buildings and land use become footprints and semantic classes.'),
('Urban dynamics',(.70,.01,.99,.52),'Repeated observations on a shared map reveal built-up changes and temporal trends.'),
('Smart-city services',(.01,.55,.34,.99),'IoT, video, water, parking and energy systems update a live digital twin.'),
('Logistics and transport',(.37,.55,.67,.99),'Road connectivity and transport flows support routing, travel-time forecasting and infrastructure analysis.'),
('Green infrastructure',(.70,.55,.99,.99),'Trees, parks and green roofs provide spatial evidence for canopy and ecological monitoring.')],
'11.8':[
('Climate and vegetation',(.01,.01,.32,.87),'Satellite time series describe vegetation indices and their changes alongside environmental observations.'),
('Atmospheric chemistry',(.35,.01,.66,.87),'Radiance, weather and station observations estimate atmospheric concentrations and transport.'),
('Environmental impact',(.69,.01,.99,.87),'Land-cover change and ecological quality indicators describe environmental impacts.'),
('Policy and conservation',(.01,.90,.99,.99),'Parallel monitoring products inform conservation and environmental policy decisions.')],
'11.9':[
('Surface hydrology',(.01,.01,.49,.49),'Imagery, terrain and precipitation characterize runoff, river flow and drainage.'),
('Groundwater',(.51,.01,.99,.49),'Subsurface layers, wells and storage anomalies describe groundwater conditions.'),
('Water quality',(.01,.52,.49,.99),'Reflectance and in-situ samples estimate water-quality indicators such as chlorophyll and nutrients.'),
('Precipitation nowcasting',(.51,.52,.99,.99),'Recent radar observations and meteorological inputs predict near-term rainfall patterns.')],
'11.10':[
('Earthquake hazard',(.06,.14,.36,.38),'Terrain and sensing observations characterize seismic hazard and its spatial variation.'),
('Flood susceptibility',(.38,.14,.68,.38),'Terrain and radar observations reveal locations susceptible to flooding.'),
('Fire susceptibility',(.70,.14,.99,.38),'Multispectral and landscape evidence characterize forest-fire susceptibility.'),
('Earthquake deformation',(.06,.42,.36,.66),'Interferometric radar measures spatial ground displacement after an event.'),
('Flood extent',(.38,.42,.68,.66),'Radar observations distinguish inundated areas from non-water regions.'),
('Active fire hotspots',(.70,.42,.99,.66),'Event observations identify active hotspots and their relative intensity.'),
('Building damage',(.06,.70,.36,.94),'Building footprints and observations support post-earthquake damage assessment.'),
('Flood damage',(.38,.70,.68,.94),'Flood observations support damage assessment across affected buildings and infrastructure.'),
('Burn severity',(.70,.70,.99,.94),'Post-event spectral change characterizes burn severity across the affected landscape.')],
'11.11':[
('Disease surveillance',(.01,.01,.32,.99),'Clinical records, mobility, climate and environmental observations support incidence forecasts with uncertainty.'),
('Spread and clusters',(.35,.01,.66,.99),'Regional case counts, mobility and contact links describe transmission patterns and clusters.'),
('Exposure and public health',(.69,.01,.99,.99),'Pollution estimates and population data characterize exposure, risk and vulnerable groups.')],
'11.12':[
('Sensing',(.01,.01,.30,.94),'Monocular and multi-view cameras, LiDAR and telemetry provide observations for a space mission.'),
('Perception',(.36,.13,.56,.39),'Perception estimates pose and semantics from sensor observations.'),
('Reasoning',(.35,.59,.49,.91),'Reasoning relates spatial state and constraints to mission requirements.'),
('Decision',(.51,.59,.65,.91),'The decision process selects an action and can request further observations.'),
('Mission outputs',(.69,.01,.99,.94),'Estimated poses, structural semantics, high-level plans and surface actions guide mission execution.')],
'11.13':[
('Monocular observation',(.01,.01,.27,.99),'A monocular image of a non-cooperative target must support pose estimation under difficult illumination.'),
('Feature-based estimation',(.31,.06,.56,.28),'Keypoints and geometric correspondences constrain the target pose.'),
('Regression CNN',(.31,.35,.56,.58),'An image model directly regresses the target pose from visual evidence.'),
('Hybrid estimation',(.31,.65,.56,.88),'A hybrid approach combines learned estimates with geometric refinement.'),
('Six-degree-of-freedom pose',(.59,.06,.79,.99),'Rotation and translation describe the target relative to the camera.'),
('Pose error and reprojection',(.81,.01,.99,.99),'Translation, rotation and image reprojection compare the estimated pose with reference observations.')],
'11.14':[
('Object detection',(.01,.01,.25,.99),'A detection localizes the spacecraft in the input image.'),
('Semantic segmentation',(.28,.01,.68,.99),'A pixel-wise model predicts the spacecraft silhouette.'),
('Parts recognition',(.71,.01,.99,.99),'Functional parts such as the antenna, body, panels and thruster describe spacecraft structure.')],
'11.15':[
('Symbolic planning',(.01,.01,.29,.99),'Logical rules and a goal tree organize sensing and actions into a symbolic mission plan.'),
('Multi-agent coordination',(.32,.01,.65,.99),'Satellites exchange information and coordinate observations through peer and ground-station links.'),
('Foundation-model operator',(.68,.01,.99,.99),'Telemetry and retrieved knowledge inform an operator model that produces a natural-language plan.')],
'11.16':[
('Perception and mapping',(.01,.01,.33,.99),'Visual odometry and terrain mapping build the rover spatial state.'),
('Hierarchical decisions',(.35,.01,.66,.99),'Mission, path and locomotion decisions coordinate goals across planning scales.'),
('Vision-guided manipulation',(.68,.01,.99,.99),'The rover uses vision to interact with the terrain, collect samples and track task progress.')],
}

class Figure(native.Figure):
 def __init__(self,entry):
  self.entry=entry;self.n=entry['number'];self.key=f'{entry["chapter"]}.{self.n}';self.id=self.key.replace('.','')
  self.man=json.loads((SITE/f'assets/figures/elements/figure{self.id}/manifest.json').read_text())
  self.w=1000;self.h=self.man['source_sizes'][0][1]/self.man['source_sizes'][0][0]*1000
  self.parts=[];self.routes=[];self.fonts=set();self.clip_defs=[];self.clip_map={}
 def prepare_clips(self,page):
  # A bounding rectangle cannot reproduce a clipped geographic polygon.
  # Keep the full source clipping path as well as the shared renderer's scissor.
  stack=[];known={};scale=1000/page.rect.width
  def point(p):return native.fmt(p.x*scale)+' '+native.fmt(p.y*scale)
  for drawing in page.get_drawings(extended=True):
   level=drawing.get('level',0);stack=[v for v in stack if v[0]<level]
   if drawing['type']=='clip':
    cid=None
    if not (len(drawing['items'])==1 and drawing['items'][0][0]=='re'):
     parts=[];last=None
     for item in drawing['items']:
      if item[0]=='re':
       r=item[1];parts.append(f'M{native.fmt(r.x0*scale)} {native.fmt(r.y0*scale)}H{native.fmt(r.x1*scale)}V{native.fmt(r.y1*scale)}H{native.fmt(r.x0*scale)}Z');last=None
      elif item[0]=='qu':
       q=item[1];parts.append('M'+point(q.ul)+'L'+point(q.ur)+'L'+point(q.lr)+'L'+point(q.ll)+'Z');last=None
      else:
       if last is None or abs(item[1]-last)>.02:parts.append('M'+point(item[1]))
       if item[0]=='l':parts.append('L'+point(item[2]));last=item[2]
       elif item[0]=='c':parts.append('C'+' '.join(point(p) for p in item[2:]));last=item[-1]
     path=' '.join(parts);rule='evenodd' if drawing.get('even_odd') else 'nonzero';key=(path,rule)
     if key not in known:
      cid=f'f{self.id}-shape-clip-{len(known)}';known[key]=cid
      self.clip_defs.append(f'<clipPath id="{cid}"><path d="{path}" clip-rule="{rule}"/></clipPath>')
     cid=known[key]
    stack.append((level,cid))
   elif 'seqno' in drawing:self.clip_map[drawing['seqno']]=[cid for _,cid in stack if cid]
 def add(self,svg,bounds,z=0):
  svg=svg.translate(str.maketrans({'퐴':'A','퐵':'B','퐶':'C','퐹':'F'})).replace('f9-flow','f1011-flow').replace('fill-opacity:None','fill-opacity:1').replace('stroke-opacity:None','stroke-opacity:1')
  for cid in self.clip_map.get(z,[]):svg=f'<g clip-path="url(#{cid})">{svg}</g>'
  super().add(svg,bounds,z)
 def render(self):
  path=SITE.parent/f'Spatial_Intelligence_Book_2025_v14/figures/part4/section{self.entry["chapter"]}'/(Path(self.entry['sources'][0]).stem+'.pdf')
  page=fitz.open(path)[0];reg=native.registration(self.n,page,self.man,figure_id=self.id,min_scale=.80)
  a=reg['scale'];dx=reg['x'];dy=reg['y'];source_h=self.h;pdf_h=page.rect.height/page.rect.width*1000
  self.regions=[(title,(b[0]*1000*a+dx,b[1]*pdf_h*a+dy,b[2]*1000*a+dx,b[3]*pdf_h*a+dy)) for title,b,_ in PANELS[self.key]]
  self.prepare_clips(page);self.pdf(path);self.h=source_h
  self.parts=[(z,f'<g transform="translate({dx} {dy}) scale({a})">{svg}</g>',(b[0]*a+dx,b[1]*a+dy,b[2]*a+dx,b[3]*a+dy)) for z,svg,b in self.parts]
  image_order=[i for i,(kind,_) in enumerate(page.get_bboxlog()) if kind=='fill-image']
  assert len(image_order)==len(self.man['assets']),(self.key,len(image_order))
  for ai,asset in enumerate(self.man['assets']):
   x,y,x1,y1=[v*a+(dx if i%2==0 else dy) for i,v in enumerate(asset['pdf_box'])]
   self.add(f'<image href="/assets/img/figs/f{self.id}/{asset["file"]}" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}" preserveAspectRatio="none"/>',(x,y,x1,y1),image_order[ai])
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
  return f'<div class="nf nf-rl nf-f1011 nf-{self.id}" data-nf="f1011" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {native.fmt(self.h)}" role="group" aria-label="Figure {self.key}: interactive reconstruction"><rect width="1000" height="{native.fmt(self.h)}" fill="white"/><defs>{"".join(self.clip_defs)}</defs><g class="f1011-scaffold">'+''.join(scaffold)+'</g>'+''.join(out)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(info)+'</script></div>'

CSS=native.CSS.replace('nf-f9','nf-f1011').replace('f9-scaffold','f1011-scaffold')
def head(title):
 return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="/assets/css/site.css?v=f1011-1"><link rel="stylesheet" href="/assets/css/figures101-1116.css?v=1"><style>{native.STYLE}</style><main>'
def foot():return '</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=f1011-1";mountNative();</script></html>'
def main():
 for base in ['source/src/css','assets/css']:(SITE/base/'figures101-1116.css').write_text(CSS)
 overview=[head('Figures 10.1–11.16 · Interactive reconstruction'),'<h1>Figures 10.1–11.16 · Interactive reconstruction</h1><nav>']
 overview += [f'<a href="#f{e["chapter"]}{e["number"]}">{e["chapter"]}.{e["number"]}</a>' for e in INV];overview+=['</nav>'];stats={}
 for e in INV:
  figure=Figure(e);markup=figure.render();ident=figure.id;key=figure.key
  originals=''.join(f'<img class="original" src="/{s}" alt="Original Figure {key}">' for s in e['sources'])
  page=head(f'Figure {key} comparison')+'<nav><a href="/example/figures101-1116.html">All figures</a><a href="#redraw">Reconstruction</a></nav>'+f'<h1>Figure {key} · Original and reconstruction</h1><div class="compare"><div><h2>Original</h2>'+originals+'</div><div><h2 id="redraw">Interactive reconstruction</h2>'+markup+'</div></div>'+foot()
  (SITE/f'source/pipeline/native/figure{ident}.html').write_text(markup)
  (SITE/f'example/figure{ident}.html').write_text(page);(SITE/f'example/figure{ident}-reconstruction.html').write_text(markup)
  overview += [f'<section id="f{ident}"><h2><a href="/example/figure{ident}.html">Figure {key} · Compare with original</a></h2>'+markup+'</section>']
  stats[ident]=dict(images=markup.count('<image'),paths=markup.count('<path'),texts=markup.count('<text'),zones=markup.count('role="button"'),motion_tracks=markup.count('class="f1011-flow rl-route"'))
  print(key,stats[ident],flush=True)
 (SITE/'example/figures101-1116.html').write_text(''.join(overview)+foot());(SITE/'example/figures101-1116-validation.json').write_text(json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':main()
