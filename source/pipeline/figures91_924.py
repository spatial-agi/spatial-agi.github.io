"""Reviewed PNG plates and independent SVG reconstruction of Figures 9.1–9.24.

Website originals are the coordinate authority. A whole-figure registration
maps source PDF primitives to the served image, keeping revision whitespace.
Generate comparison previews only; reader integration follows visual approval.
"""
from pathlib import Path
from html import escape
import json, re, math
import fitz
import numpy as np
from PIL import Image
from scipy import signal

SITE=Path(__file__).resolve().parents[2]
BOOK=SITE.parent/'Spatial_Intelligence_Book_2025_v14/figures/part4/section9'
INV=json.loads((SITE/'source/pipeline/figures91_924_sources.json').read_text())
BLUE='#3646f0'

def fmt(value):
 return f'{value:.3f}'.rstrip('0').rstrip('.')
def color(value):
 if value is None:return 'none'
 if len(value)==1:value=value*3
 return '#'+''.join(f'{round(c*255):02x}' for c in value[:3])

# Bounds use website-original coordinates at width 1000.
REGIONS={
1:[('Task and feedback',(0,0,1000,165)),('Multimodal inputs',(0,165,230,795)),('Spatial anchors',(235,210,695,338)),('Functional affordances',(235,340,695,477)),('General VLA reasoning',(235,479,695,621)),('Geometric and logical constraints',(235,623,695,770)),('Policy and trajectory',(750,205,995,420)),('Robot execution',(750,432,995,609)),('Evaluation',(750,640,995,770))],
2:[('Produce spatial anchors',(0,0,330,651)),('Anchor-conditioned policy',(333,0,661,651)),('Evaluate generalization',(665,0,1000,651))],
3:[('Affordance representation',(0,0,315,746)),('Grasp and lift',(330,70,990,302)),('Stable placement',(330,305,990,502)),('Tool use: hook and pull',(330,505,990,717))],
4:[('Manipulation task',(0,0,1000,110)),('Explicit 3D representation',(0,115,1000,303)),('Canonical observations',(0,315,490,545)),('Spatial action discretization',(495,315,1000,545)),('Grounded reasoning traces',(0,560,1000,760)),('Cross-robot transfer',(0,765,1000,860))],
5:[('Symbolic and geometric planning',(0,0,333,540)),('Contact and trajectory optimization',(334,0,665,540)),('Constraint-aware generative planning',(667,0,1000,540)),('Teacher supervision',(0,560,333,730)),('Safety shield',(334,560,665,730)),('Structural prior',(667,560,1000,730))],
6:[('Level 0: no automation',(12,260,177,463)),('Level 1: driver assistance',(177,220,340,463)),('Level 2: partial automation',(340,188,502,463)),('Level 3: conditional automation',(502,150,666,463)),('Level 4: high automation',(666,111,830,463)),('Level 5: full automation',(830,72,992,463))],
7:[('Multi-view cameras',(10,0,300,230)),('LiDAR sensing',(302,0,510,230)),('Radar sensing',(512,0,720,230)),('GNSS and inertial sensing',(722,0,1000,230)),('Perception and detection',(0,265,325,582)),('Localization and mapping',(335,265,655,582)),('Decision and planning',(665,265,1000,582)),('Planned trajectory',(0,660,325,830)),('Tracking controller',(330,660,655,830)),('Vehicle commands',(660,660,1000,830)),('Evaluation',(0,858,330,970)),('Vehicle feedback',(660,858,1000,970))],
8:[('Object detection',(5,75,485,393)),('Semantics and occupancy',(505,75,995,393)),('Lane geometry',(5,411,485,724)),('Pedestrian reasoning',(505,411,995,724)),('Shared scene model',(247,778,748,845))],
9:[('Camera sensing',(0,0,249,185)),('LiDAR sensing',(251,0,498,185)),('Radar sensing',(501,0,747,185)),('GNSS and IMU',(750,0,1000,185)),('Joint state estimation',(10,245,355,690)),('Pose on HD map',(408,260,685,456)),('Incremental 3D map',(695,260,995,456)),('SLAM loop closure',(460,498,995,707))],
10:[('Raw sensor inputs',(0,215,175,590)),('Modular learned planning',(220,65,990,265)),('End-to-end sensor control',(220,300,990,455)),('Hybrid planning with checks',(220,505,990,700))],
11:[('On-body sensing',(0,30,260,810)),('Pose and biomechanics',(295,30,615,380)),('Activity and intent',(660,30,995,380)),('Personalized assistance',(295,407,995,525)),('Haptic cues',(295,555,510,765)),('Exoskeleton assistance',(530,555,745,765)),('Safety alerts',(765,555,995,765))],
12:[('Segment sensing',(0,20,255,785)),('Kinematic state estimation',(285,20,720,295)),('Parametric body model',(285,325,720,502)),('Visual-inertial fusion',(285,540,720,790)),('Full-body pose',(755,20,995,426)),('Global trajectory',(755,466,995,790))],
13:[('Multimodal time series',(20,35,300,440)),('Kinematic body graph',(20,455,300,745)),('Temporal encoder',(337,55,575,225)),('Graph encoder',(337,310,575,495)),('Attention fusion',(598,225,660,322)),('Recognized activity',(705,55,990,425)),('Intent forecast',(705,480,990,775)),('Neuromuscular pre-activation',(20,780,575,950))],
14:[('Wearable interfaces',(10,25,242,350)),('Interaction sensing',(279,25,587,350)),('Motion context',(648,25,903,350)),('Multimodal fusion',(10,400,275,600)),('Motion prediction',(320,400,585,600)),('Risk and response',(630,400,900,600)),('Haptic feedback',(10,645,275,855)),('Assistive torque',(320,645,585,855)),('Robot motion control',(630,645,900,855))],
15:[('Aerial sensing inputs',(0,0,278,463)),('Cross-view perception',(320,40,703,185)),('Detection and environment',(320,188,703,328)),('Navigation and decisions',(320,333,703,463)),('Flight execution',(755,0,1000,463))],
16:[('Ground view',(0,0,300,160)),('Drone view',(0,164,300,322)),('Satellite view',(0,325,300,500)),('Shared visual encoder',(355,140,555,450)),('Viewpoint-invariant metric space',(610,0,1000,500))],
17:[('Oriented detection input',(0,0,450,177)),('Arbitrary orientation',(455,0,626,177)),('Scale variation',(633,0,802,177)),('Dense small objects',(809,0,1000,177)),('Oriented-object detection',(0,200,490,405)),('Multi-scale features',(510,200,1000,405)),('Person re-identification',(0,475,330,632)),('Action recognition',(335,475,665,632)),('Multi-target tracking',(670,475,1000,632))],
18:[('Instruction and observations',(0,0,230,423)),('Semantic-topometric representation',(240,35,455,423)),('Language-guided planner',(480,125,650,330)),('Flight plan',(680,30,845,423)),('Evaluation',(850,30,1000,203)),('Multi-drone coordination',(850,215,1000,423))],
19:[('Multi-sensor inputs',(0,20,245,805)),('Perception',(300,82,710,185)),('Localization and mapping',(300,196,710,297)),('Reasoning and planning',(300,310,710,411)),('Manipulation and control',(300,422,710,523)),('Human–robot collaboration',(300,535,710,645)),('Picking and handling',(755,20,1000,420)),('Pallet transport',(755,435,1000,767)),('Middleware and feedback',(300,697,710,767))],
20:[('Multimodal sensing',(10,40,990,150)),('Detection and segmentation',(10,190,475,566)),('6D object pose',(535,190,990,566)),('Structured scene graph',(10,620,990,895))],
21:[('Sensor streams',(10,65,190,632)),('Pose-graph optimization',(245,65,580,632)),('Warehouse map and poses',(625,65,990,632)),('Loop validation',(700,630,995,735))],
22:[('Task list',(10,20,310,200)),('Fleet state',(347,20,647,200)),('Warehouse map',(685,20,985,200)),('Combinatorial optimization',(40,252,485,586)),('Learned coordination',(515,252,955,586)),('Hybrid hierarchical design',(210,630,790,755)),('Task allocation',(10,845,310,1065)),('Motion paths',(347,845,647,1065)),('Temporal schedule',(685,845,985,1065))],
23:[('Grasp synthesis',(10,62,430,420)),('Sampling-based planning',(495,62,995,420)),('Camera observation',(20,500,235,748)),('Learned policy and action',(270,500,685,748)),('Robot execution',(735,500,995,748))],
24:[('Multimodal human sensing',(10,50,305,708)),('Intent recognition',(360,50,640,295)),('Proxemics-aware planning',(360,345,640,708)),('Adaptive robot behavior',(705,50,990,708))]
}

# Explanations follow the region order above and remain independent of labels.
EXPLANATIONS={
1:[
'Observe the drawer and mug, reason about the task, act, and obtain new observations for replanning.',
'RGB-D, point clouds, robot state and the instruction provide complementary observations of the manipulation task.',
'Keypoints and correspondences ground object-relative spatial locations that can be tracked during manipulation.',
'Actionable parts connect grasp contact, placement, handles and receptacles to the intended physical effect.',
'The vision-language-action model combines 3D evidence with language and predicts action tokens.',
'Collision limits and logical preconditions constrain which pick-and-place actions are feasible.',
'The policy selects a 6-DoF action or trajectory from the grounded task representation.',
'Fixed-arm and mobile manipulators execute the action; the changed scene supplies new observations.',
'Schematic success and transfer measurements compare task performance across execution settings.'
],
2:[
'Corresponding visual points establish anchors across views. Vision priors produce object-relative keypoints and optional temporal tracks.',
'The policy conditions on spatial anchors, the goal and robot state to select a gripper action.',
'Matched seen and unseen trials estimate a generalization gap. The displayed bars are illustrative rather than measured scores.'
],
3:[
'Dense descriptors and functional keypoints identify where and how the robot can act, conditioned on the task and scene.',
'A 6-DoF gripper pose establishes contact with the mug; the intended effect is lifting and holding it.',
'The support and contact configuration guide placement so that the mug remains stable after release.',
'A hook-and-pull interaction uses the handle to open the drawer, connecting tool motion to the desired effect.'
],
4:[
'The instruction requires spatial grounding of the mug, drawer and robot before predicting actions.',
'Explicit 3D features enter token fusion and attention before the model decodes an action.',
'Canonicalized RGB-D and orthographic views reduce viewpoint variation before the VLA policy.',
'An adaptive spatial grid discretizes actions into tokens while retaining spatial structure.',
'Predicted traces, trajectories or depth cues ground reasoning before conditioned action prediction.',
'Fixed and mobile robot platforms test viewpoint robustness and cross-robot transfer.'
],
5:[
'Symbolic action preconditions are refined against collision and reachability checks in scene geometry.',
'Non-penetration, friction and force limits constrain the contact and trajectory optimizer.',
'Joint denoising or constrained optimization guides candidate trajectories toward a feasible goal.',
'A planner provides feasible trajectories as supervision for a learned policy.',
'A filter or quadratic program projects proposed actions onto a modeled safe set.',
'Geometry and dynamics can prune infeasible candidates before action selection.'
],
6:[
'The human performs the driving task. Warnings or brief interventions do not constitute sustained automation.',
'The system assists with steering or speed, while the human continuously supervises the driving task.',
'The system assists with both steering and speed. The human continues to supervise and provides fallback.',
'The system performs the driving task in defined conditions; the human must be ready to resume when requested.',
'The system performs the task and fallback within its defined operating conditions, without human fallback in those conditions.',
'The system performs the task across all human-drivable conditions without requiring human driving.'
],
7:[
'Surround camera views supply appearance, object and lane observations from complementary viewpoints.',
'LiDAR returns supply range and 3D geometry for objects, free space and mapping.',
'Radar supplies range and relative velocity measurements that complement the other sensors.',
'GNSS and inertial measurements provide global pose cues and short-term motion estimates.',
'Object and pedestrian detections, lanes and drivable areas describe the local scene.',
'Mapping estimates ego pose and updates the map; revisited places can provide loop-closure constraints.',
'The model combines the scene, map and route to predict agent motion and select a plan.',
'The planned vehicle trajectory specifies the path that the tracking controller should follow.',
'Trajectory and ego-state feedback are converted into commands that track the selected path.',
'Steering, acceleration and braking commands are applied to the physical vehicle.',
'Execution logs support score and collision evaluation; the plots are schematic.',
'The vehicle changes the environment and receives fresh observations, closing the sensing and control loop.'
],
8:[
'Image detections and 3D cuboids identify vehicles and vulnerable road users; BEV boxes express their spatial locations.',
'Semantic labels and 3D occupancy describe road, vegetation, buildings, vehicles and other occupied regions.',
'Lane boundaries and centerlines encode solid and dashed road structure using sampled 3D geometry.',
'Pedestrian position and motion support a short-horizon hypothesis, shown as an illustrative dashed path.',
'The complementary perception outputs contribute to a shared scene model for localization and planning.'
],
9:[
'Camera observations contribute appearance and visual geometry; reliability depends on the operating conditions.',
'LiDAR returns contribute geometric range measurements for localization and mapping.',
'Radar contributes range and motion evidence that complements visual and geometric sensing.',
'GNSS and IMU supply global reference and inertial motion cues with condition-dependent reliability.',
'Fusion updates the vehicle-state distribution from synchronized and calibrated sensor observations.',
'The estimated vehicle pose is aligned with the HD map; trajectory accuracy can be evaluated with ATE and RPE.',
'Registering new points incrementally updates the geometric 3D map.',
'A revisited place is recognized and verified before adding a loop constraint to reduce accumulated error.'
],
10:[
'Camera and LiDAR observations supply the raw measurements for all three control architectures.',
'Perception and localization create an explicit BEV scene before a planning policy selects control.',
'A sensor encoder feeds a learned control policy directly; internal features depend on the architecture.',
'Learned perception retains an inspectable scene or trajectory before explicit planning and constraint checks.'
],
11:[
'Egocentric cameras, muscle signals, gloves and inertial sensors measure body and scene information.',
'Sensor fusion estimates pose, state and biomechanics from the multimodal observations.',
'Temporal observations support activity recognition, intent, motion forecasting and risk assessment.',
'Personalized assistance turns the estimated wearer state into adaptive control or a safety intervention.',
'Glove vibration or force cues provide haptic guidance to the wearer.',
'An exoskeleton supplies torque and support according to the assistance policy.',
'Visual, auditory or haptic channels communicate safety alerts to the wearer.'
],
12:[
'Segment-mounted IMUs provide time series from wrists, chest and shins for articulated-motion estimation.',
'Filtering, optimization or learned inference combines observations with joint limits, temporal priors and a noise model.',
'Pose, body shape and a global transform parameterize an articulated body model such as SMPL.',
'Visual tracks and IMU integration combine with loop and contact constraints in a factor graph.',
'Joint configuration reconstructs full-body pose in a root-relative frame.',
'Visual or inertial anchoring and additional constraints estimate world-frame motion and reduce global drift.'
],
13:[
'IMU motion and EMG muscle signals provide complementary multimodal time series.',
'Joints and bones form a kinematic graph that encodes body structure and relationships.',
'A temporal convolutional network or transformer encodes successive time steps into temporal features.',
'A graph neural network aggregates information over joints and their structural connections.',
'Attention combines the temporal and graph representations before activity and intent inference.',
'The fused representation classifies current activities such as walking, running, lifting or climbing.',
'The model predicts an uncertain short-horizon motion continuation rather than a guaranteed future.',
'Muscle activation can precede visible motion and provide an early cue for anticipating movement.'
],
14:[
'A glove and exoskeleton provide wearable sensing and assistance interfaces.',
'Contact, force, effort and proximity signals describe the physical interaction.',
'Predicted human intent and the planned robot motion provide context for interaction risk.',
'Temporal alignment combines multimodal features together with their uncertainty.',
'Human and robot trajectory estimates include an uncertainty envelope for downstream risk reasoning.',
'A risk estimate and threshold determine which response channels should be selected.',
'Glove vibration or force cues deliver haptic feedback to the wearer.',
'Exoskeleton torque supplies support or guidance based on the interaction estimate.',
'The robot slows, stops or reroutes, producing a changed physical state that is sensed again.'
],
15:[
'Satellite, airship and UAV observations combine with positioning and onboard sensors across aerial tiers.',
'Cross-view perception matches observations across viewpoints and supports visual geolocalization.',
'Environmental perception extracts land use, water, assets and other scene structure.',
'Navigation combines spatial connectivity, safety constraints and the mission goal.',
'The flight controller follows the planned 6-DoF route; execution produces new observations for the next cycle.'
],
16:[
'The ground-level image provides a street-scale appearance of the location.',
'The oblique aerial image links facade and roof information from an intermediate viewpoint.',
'The overhead satellite image provides top-down layout and geographic context.',
'A shared encoder extracts features that preserve location identity across viewpoint and orientation changes.',
'Views of the same place are pulled together in feature space, while different locations are pushed apart.'
],
17:[
'Oriented detections localize parked vehicles whose boxes are not aligned with the image axes.',
'An object rotation angle motivates orientation-aware spatial representations.',
'Large variation in apparent object size requires features at multiple spatial scales.',
'Dense small objects require sufficient resolution and spatial separation during detection.',
'Rotated boxes, keypoints or Gaussian representations capture object orientation.',
'A feature pyramid and multi-scale attention combine fine and coarse image evidence.',
'Person re-identification matches the same individual across different observations.',
'Temporal body structure supports action recognition across poses such as walking, running and carrying.',
'Tracking maintains object identities across successive frames.'
],
18:[
'The language instruction identifies a destination, while the aerial image supplies the observed scene.',
'Named landmarks and local connectivity form a semantic-topometric graph for navigation.',
'The planner grounds the instruction in the graph and reasons about the route to the goal.',
'Waypoints specify position, attitude and velocity along the planned aerial route.',
'Success, path efficiency and navigation error summarize the navigation result.',
'Multiple drones coordinate their flight at different altitude levels.'
],
19:[
'RGB-D, LiDAR and RFID provide observations of the warehouse and its changing state.',
'Perception extracts entities and spatial relationships from warehouse observations.',
'Localization and mapping estimate robot pose relative to warehouse structure.',
'Reasoning and planning translate task requirements into feasible action sequences.',
'Manipulation and control turn the plan into physical robot motion.',
'Human–robot collaboration accounts for people in shared tasks and spaces.',
'A robot arm grasps and handles parcels at a work surface.',
'A mobile platform transports palletized goods through the warehouse.',
'Middleware connects observations, maps and plans; execution outcomes update the next planning cycle.'
],
20:[
'RGB-D, LiDAR and RFID combine with calibration and prior map information.',
'Image boxes and illustrative instance masks locate and segment the shelf objects.',
'Each object receives a 6D pose with rotation and translation in SE(3).',
'The graph records object relations and attributes including identity, pose and uncertainty for downstream tasks.'
],
21:[
'IMU, LiDAR, cameras, wheel encoders and UWB provide complementary sensor streams.',
'Pose states are connected by sensor factors and optional map or beacon anchors for joint estimation.',
'The estimated trajectory is expressed relative to warehouse storage and restricted regions.',
'A loop candidate is verified before its validated constraint is added back to the estimator.'
],
22:[
'Pick and replenishment tasks specify the work that the warehouse fleet must perform.',
'Robot availability, battery charge and current activity constrain the fleet assignment.',
'The warehouse layout specifies storage structure and the navigation environment.',
'Assignment matrices and routing optimization jointly address tasks and vehicle paths under constraints.',
'Coordination policies map robot and fleet observations to actions or waiting decisions.',
'A hierarchical system can combine symbolic allocation with learned coordination and graph models.',
'The assignment matrix identifies which robot handles each task, including unavailable robots.',
'Task-visit paths connect each robot to the destinations assigned to it.',
'The schedule places tasks, busy intervals and charging periods on a shared time axis.'
],
23:[
'Analytic metrics and learned grasp quality rank candidate object grasps.',
'A sampling-based planner searches around obstacles and selects a feasible path from start to goal.',
'The camera supplies the current scene observation for learned visuomotor control.',
'The learned policy maps visual evidence to a task-space or low-level command.',
'The robot applies the command; the next camera observation closes the visuomotor loop.'
],
24:[
'Vision, audio, inertial, UWB and RFID signals describe human pose, gesture, gaze and motion history.',
'A sequence model estimates human intent from successive observations.',
'Predicted human occupancy and clearance constraints guide motion planning near people.',
'The robot adapts by slowing, rerouting or stopping, then senses the resulting shared workspace again.'
]
}

def registration(n,page,manifest,*,figure_id=None,min_scale=.94):
    cache=SITE/f'assets/figures/elements/figure{figure_id or str(9)+str(n)}/registration.json'
    if cache.exists():return json.loads(cache.read_text())
    # Crop the full native rendering to its ink, then match scale and translation.
    # This also handles the four entirely vector figures, without raster assets.
    original=Image.open(SITE/manifest['sources'][0]).convert('RGB');original.thumbnail((1000,1800))
    target=np.asarray(original.convert('L'),dtype=float)/255
    pix=page.get_pixmap(matrix=fitz.Matrix(1000/page.rect.width,1000/page.rect.width),alpha=False)
    clean=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    a=np.asarray(clean);yy,xx=np.where(a.min(2)<220)
    crop=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));plate=clean.crop(crop).convert('L')
    sums=np.pad(target,((1,0),(1,0))).cumsum(0).cumsum(1);squares=np.pad(target*target,((1,0),(1,0))).cumsum(0).cumsum(1)
    best=None
    for scale in np.arange(min_scale,1.021,.002):
        w=round(plate.width*scale);h=round(plate.height*scale)
        if h>=target.shape[0] or w>=target.shape[1]:continue
        t=np.asarray(plate.resize((w,h),Image.Resampling.BILINEAR),dtype=float)/255;t-=t.mean()
        corr=signal.fftconvolve(target,t[::-1,::-1],mode='valid')
        sm=sums[h:,w:]-sums[:-h,w:]-sums[h:,:-w]+sums[:-h,:-w]
        ss=squares[h:,w:]-squares[:-h,w:]-squares[h:,:-w]+squares[:-h,:-w]
        score=corr/(np.sqrt(np.maximum(ss-sm*sm/(w*h),0))*np.linalg.norm(t)+1e-8)
        y,x=np.unravel_index(score.argmax(),score.shape);v=float(score[y,x])
        if best is None or v>best[0]:best=(v,float(scale),float(x-crop[0]*scale),float(y-crop[1]*scale))
    assert best and best[0]>.75,(n,best)
    result=dict(confidence=round(best[0],5),scale=round(best[1],5),x=round(best[2],3),y=round(best[3],3))
    cache.write_text(json.dumps(result,indent=2)+'\n');return result

def arrow_routes(drawings, *, strict_dashes=False):
 """Recover motion independently of paint order, including open and two-way heads.

 Some PDFs paint a complete elbow first and overprint only its last leg with
 the arrow command. Follow that leg back onto the underlying stem, trimming
 at the shared point. Never change the visible PDF paths to join motion.
 """
 def reverse(items):
  return [('l',it[2],it[1]) if it[0]=='l' else ('c',it[4],it[3],it[2],it[1]) for it in reversed(items)]
 def end(items):return items[-1][-1]
 def unit(v):return v/abs(v) if abs(v)>1e-6 else fitz.Point(0,0)
 def dot(a,b):return a.x*b.x+a.y*b.y
 def tangent(items,last=False):
  it=items[-1] if last else items[0]
  return unit(it[-1]-it[-2] if last else it[2]-it[1])
 def same_color(a,b):return a is not None and b is not None and max(abs(x-y) for x,y in zip(a,b))<.01
 def dash_key(d):
  values=re.search(r'\[([^]]*)\]',d.get('dashes') or '')
  return tuple(round(float(v)/max(d.get('width') or 1,1e-6),2) for v in values.group(1).split()) if values else ()
 heads=[];head_ids=set()
 for i,d in enumerate(drawings):
  its=d['items'];r=d['rect']
  if r.width>=12 or r.height>=12 or not all(it[0]=='l' for it in its):continue
  if d.get('fill') is not None and len(its)==3:
   heads.append((i,d,None,None));head_ids.add(i)
  elif d['type']=='s' and len(its)==2 and not d.get('closePath') and abs(its[0][2]-its[1][1])<.02:
   a,tip,b=its[0][1],its[0][2],its[1][2];u=a-tip;v=b-tip
   # A small symmetric chevron, rather than a checkmark or an elbow.
   if .4<abs(u)<5 and abs(abs(u)-abs(v))<.05 and .15<dot(unit(u),unit(v))<.9:
    heads.append((i,d,tip,unit(tip-(a+b)/2)));head_ids.add(i)
 shafts=[]
 for i,d in enumerate(drawings):
  its=d['items']
  if (i in head_ids or d['type']!='s' or d.get('closePath') or not its
      or not all(it[0] in ('l','c') for it in its)):continue
  if any(abs(a[-1]-b[1])>.03 for a,b in zip(its,its[1:])):continue
  if abs(its[0][1]-end(its))<.03:continue
  shafts.append((i,d))
 routes=[];seen=set()
 for si,shaft in shafts:
  for backward in (False,True):
   items=reverse(shaft['items']) if backward else list(shaft['items'])
   terminal=end(items);direction=tangent(items,True);matched=[]
   for hi,head,tip,axis in heads:
    if not same_color(shaft.get('color'),head.get('fill') if tip is None else head.get('color')):continue
    if tip is not None:
     if abs(terminal-tip)>.06 or dot(direction,axis)<.8:continue
    else:
     # Filled triangle: its apex must face the terminal shaft tangent.
     vertices=[it[1] for it in head['items']]
     choices=[]
     for j,v in enumerate(vertices):
      base=(vertices[(j+1)%3]+vertices[(j+2)%3])/2
      if dot(unit(v-base),direction)>.85 and abs(v-terminal)<=2.05:choices.append(v)
     if not choices:continue
     tip=min(choices,key=lambda v:abs(v-terminal))
    matched.append((hi,tip))
   if not matched:continue
   # Only the nearest attached head, regardless of intervening PDF drawings.
   hi,tip=min(matched,key=lambda h:abs(h[1]-terminal))
   used={si};bounds=fitz.Rect(shaft['rect'])
   while True:
    start=items[0][1];incoming=tangent(items);candidates=[]
    for pi,prev in shafts:
     if pi in used or not same_color(prev.get('color'),shaft.get('color')):continue
     if strict_dashes and dash_key(prev)!=dash_key(shaft):continue
     if abs((prev.get('width') or 0)-(shaft.get('width') or 0))>.261:continue
     for oriented in (prev['items'],reverse(prev['items'])):
      pe=end(oriented);gap=abs(pe-start)
      if gap<=2.05:
       bridge=start-pe
       if gap>.06 and max(dot(unit(bridge),tangent(oriented,True)),dot(unit(bridge),incoming))<.98:continue
       candidates.append((gap,pi,list(oriented),prev))
      # A terminal arrow leg may overprint an interior point of the stem.
      for j,it in enumerate(oriented):
       if it[0]!='l':continue
       delta=it[2]-it[1];length=abs(delta)
       if length<.1 or dot(unit(delta),incoming)<.995:continue
       t=dot(start-it[1],delta)/(length*length)
       if not .001<t<.999:continue
       projected=it[1]+delta*t;gap=abs(projected-start)
       if gap>.03:continue
       prefix=list(oriented[:j])+[('l',it[1],start)]
       candidates.append((gap,pi,prefix,prev))
    if not candidates:break
    candidates.sort(key=lambda c:c[0]);gap,pi,prefix,prev=candidates[0]
    # Ambiguous forks are not joined across unrelated diagram lines.
    if any(c[1]!=pi and abs(c[0]-gap)<.03 for c in candidates[1:]):break
    bridge=[('l',end(prefix),start)] if gap>.02 else []
    items=prefix+bridge+items;used.add(pi);bounds|=prev['rect']
   if abs(end(items)-tip)>.02:items.append(('l',end(items),tip))
   key=tuple((it[0],*(round(v,3) for pt in it[1:] for v in pt)) for it in items)
   if key in seen:continue
   seen.add(key);routes.append((items,bounds,shaft['seqno']+.1))
 return routes

class Figure:
 def __init__(self,n):
  self.n=n;self.id=f'9{n}';self.entry=INV[n-1]
  self.man=json.loads((SITE/f'assets/figures/elements/figure{self.id}/manifest.json').read_text())
  self.w=1000;self.h=self.man['source_sizes'][0][1]/self.man['source_sizes'][0][0]*1000
  self.regions=REGIONS[n];self.parts=[];self.routes=[];self.fonts=set()
 def add(self,svg,bounds,z=0):self.parts.append((z,svg,bounds))
 def assets(self):pass
 def pdf(self,path,route_builder=None):
  self.doc=fitz.open(path);pg=self.doc[0];scale=1000/pg.rect.width
  self.h=pg.rect.height*scale
  drawings=pg.get_drawings()
  clipmap={};stack=[]
  for item in pg.get_drawings(extended=True):
   level=item.get('level',0)
   stack=[v for v in stack if v[0]<level]
   if item['type']=='clip':stack.append((level,item['scissor']))
   elif 'seqno' in item:
    clip=fitz.Rect(pg.rect)
    for _,r in stack:clip &= r
    clipmap[item['seqno']]=clip

  def is_chainable(d):
   return (d['type']=='s' and d.get('fill') is None and not d.get('closePath')
           and bool(d['items']) and all(it[0] in ('l','c') for it in d['items']))
  def endpoints(d):
   items=d['items'];return items[0][1], items[-1][2] if items[-1][0]=='l' else items[-1][-1]
  def attached_arrowhead(shaft, following):
   # Drawing order alone does not imply a connection: ticks, separators and
   # borders may immediately precede an unrelated arrow. Animate only shafts
   # whose endpoint actually meets an arrowhead of the same color.
   _,end=endpoints(shaft)
   for head in following:
    if (head['fill'] is None or len(head['items'])!=3
        or not all(it[0]=='l' for it in head['items'])
        or head['rect'].width>=12 or head['rect'].height>=12):continue
    if shaft.get('color') is None or max(abs(a-b) for a,b in zip(shaft['color'],head['fill']))>.01:continue
    r=head['rect']
    gap=(max(r.x0-end.x,0,end.x-r.x1)**2+max(r.y0-end.y,0,end.y-r.y1)**2)**.5
    if gap<=2.05:return head
   return None
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
   head=attached_arrowhead(d,drawings[end_i+1:end_i+3])
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
   style+=f';fill-opacity:{d.get("fill_opacity",1)};stroke-opacity:{d.get("stroke_opacity",1)}'
   if da:style+=';stroke-dasharray:'+','.join(fmt(float(v)*scale) for v in da.split())
   shape=f'<path d="{" ".join(p)}" style="{style}"/>'
   clip=clipmap.get(d['seqno'],pg.rect)
   if not clip.contains(d['rect']):
    visible=d['rect'] & clip
    if visible.is_empty:continue
    bounds=tuple(v*scale for v in visible)
    x,y,x1,y1=[v*scale for v in clip];cid=f'f{self.id}-clip-{gi}'
    shape=f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/></clipPath></defs><g clip-path="url(#{cid})">{shape}</g>'
   self.add(shape,bounds,d['seqno'])
  # Motion follows recovered complete shafts; the visible drawing stays unchanged.
  for items,rect,z in (route_builder or arrow_routes)(drawings):
   route=[];last=None
   for item in items:
    if last is None or abs(item[1]-last)>.02:route.append('M'+pt(item[1]))
    if item[0]=='l':route.append('L'+pt(item[2]))
    else:route.append('C'+' '.join(pt(v) for v in item[2:]))
    last=item[-1]
   if max(rect.width,rect.height)>1:
    track=f'<path d="{" ".join(route)}" class="f9-flow rl-route" fill="none" stroke="#3646f0" opacity="0" style="stroke-width:1px" data-duration="{max(1500,min(4200,max(rect.width,rect.height)*60)):.0f}"/>'
    self.add(track,tuple(v*scale for v in rect),z)
  # Use PyMuPDF's Unicode-correct text spans. The trace API exposes glyph IDs
  # for some embedded Type-1 math fonts and would map several Greek symbols wrong.
  for block in pg.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     value=span['text'].translate(str.maketrans({'휙':'φ','퐸':'E','퐷':'D','퐺':'G','휃':'θ','휓':'ψ','푝':'p','푛':'n','푧':'z','푇':'T','푡':'t','훼':'α','휎':'σ','휖':'ε','푣':'v','퐼':'I','휄':'ι','푖':'i','푥':'x','푦':'y','푤':'w','푟':'r','푎':'a','푏':'b','푘':'k','푚':'m','푠':'s','푢':'u','푐':'c','푑':'d','푒':'e','휂':'η','푢':'u','푀':'M','휅':'κ','푐':'c','휋':'π','푉':'V','푃':'P','푠':'s','ℎ':'h','ℓ':'l','푅':'R','퐾':'K','Í':'I','푘':'k','푆':'S','푓':'f','훾':'γ','훽':'β','Î':'∏','푁':'N','푔':'g','푞':'q','휇':'μ'}))
     if not value.strip():continue
     value=value.translate(str.maketrans({'푃':'P','푁':'N','푔':'g','푞':'q','푡':'t','푖':'i','푗':'j','푓':'f','푛':'n','휇':'μ','푇':'T','푝':'p','푧':'z','휋':'π','휃':'θ','훽':'β','푢':'u','푥':'x','푘':'k','푀':'M','ℓ':'l','푎':'a','푅':'R','푆':'S'}))
     value=value.replace('¤','˙').replace('Ð','θ')
     x0,y0=span['origin']
     font=span['font'];is_math=not font.startswith('Aptos');size=span['size']*scale
     b=tuple(v*scale for v in span['bbox'])
     family="'Cambria Math'" if is_math else 'Figure711Sans'
     italic=('NewTXMI' in font or 'txmiaX' in font or 'Italic' in font)
     style=f'font-family:{family};font-size:{fmt(size)}px;font-style:{"italic" if italic else "normal"};font-weight:{700 if "Bold" in font else 400};fill:{color(((span["color"]>>16&255)/255,(span["color"]>>8&255)/255,(span["color"]&255)/255))}'
     # The source PDF stores math as many font runs. Keep each run at its exact
     # PDF baseline and constrain Cambria Math to the source run's measured width.
     direction=line.get('dir',(1,0));angle=math.degrees(math.atan2(direction[1],direction[0]))
     width=((span['bbox'][2]-span['bbox'][0])*abs(direction[0])+(span['bbox'][3]-span['bbox'][1])*abs(direction[1]))*scale
     rotation=f' transform="rotate({fmt(angle)} {fmt(x0*scale)} {fmt(y0*scale)})"' if abs(angle)>.01 else ''
     self.add(f'<text x="{fmt(x0*scale)}" y="{fmt(y0*scale)}"{rotation} textLength="{fmt(width)}" lengthAdjust="spacingAndGlyphs" style="{style}">{escape(value)}</text>',b,span.get('seqno',50000))
  self.assets()

 def render(self):
  path=BOOK/(Path(self.entry['sources'][0]).stem+'.pdf');page=fitz.open(path)[0]
  reg=registration(self.n,page,self.man);a=reg['scale'];dx=reg['x'];dy=reg['y'];source_h=self.h
  if self.n==14:
   rects=[(17,62,263,363),(306,62,642,363),(712,62,983,363),(17,438,300,640),(358,438,642,640),(700,438,983,640),(17,715,300,937),(358,715,642,937),(700,715,983,937)]
   self.regions=[(title,tuple(v*a+(dx if i%2==0 else dy) for i,v in enumerate(box))) for (title,_),box in zip(self.regions,rects)]
  self.pdf(path);self.h=source_h
  self.parts=[(z,f'<g transform="translate({dx} {dy}) scale({a})">{svg}</g>',(b[0]*a+dx,b[1]*a+dy,b[2]*a+dx,b[3]*a+dy)) for z,svg,b in self.parts]
  image_order=[i for i,(kind,_) in enumerate(page.get_bboxlog()) if kind=='fill-image']
  for ai,asset in enumerate(self.man['assets']):
   x,y,x1,y1=[v*a+(dx if i%2==0 else dy) for i,v in enumerate(asset['pdf_box'])]
   self.add(f'<image href="/assets/img/figs/f{self.id}/{asset["file"]}" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}" preserveAspectRatio="none"/>',(x,y,x1,y1),image_order[ai])
  return self.finish()
 def finish(self):
  zones=[[] for _ in self.regions];scaffold=[]
  for z,svg,b in sorted(self.parts,key=lambda v:v[0]):
   cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
   # A shared frame must stay below all of its child interaction regions.
   covers=[i for i,(_,r) in enumerate(self.regions) if b[0]<=(r[0]+r[2])/2<=b[2] and b[1]<=(r[1]+r[3])/2<=b[3]]
   candidates=[] if len(covers)>1 else [i for i,(_,r) in enumerate(self.regions) if r[0]<=cx<=r[2] and r[1]<=cy<=r[3]]
   if candidates:
    i=min(candidates,key=lambda i:(self.regions[i][1][2]-self.regions[i][1][0])*(self.regions[i][1][3]-self.regions[i][1][1]));zones[i].append(svg)
   else:scaffold.append(svg)
  out=[];info={}
  for i,((title,b),body) in enumerate(zip(self.regions,zones)):
   key=f'panel-{i}';info[key]={'t':title,'b':EXPLANATIONS[self.n][i]}
   x,y,x1,y1=b
   out.append(f'<g class="rl-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(title)}">'+''.join(body)+f'<rect class="rl-hit" x="{x}" y="{y}" width="{x1-x}" height="{y1-y}"/></g>')
  return f'<div class="nf nf-rl nf-f9 nf-{self.id}" data-nf="f9" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {fmt(self.h)}" role="group" aria-label="Figure 9.{self.n}: interactive reconstruction"><rect width="1000" height="{fmt(self.h)}" fill="white"/><g class="f9-scaffold">'+''.join(scaffold)+'</g>'+''.join(out)+'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(info)+'</script></div>'

CSS="""
.nf-f9{position:relative}.nf-f9 .nf-svg{display:block;width:100%;height:auto}.nf-f9 text{letter-spacing:0}.nf-f9 .rl-hit{stroke-width:0}.nf-f9 .rl-zone{isolation:isolate}
.nf-f9 .rl-pulse{r:2;fill:white!important;stroke:#5baaff;stroke-width:.45;filter:drop-shadow(0 0 2px white) drop-shadow(0 0 4px #48a5ff)}
.nf-f9 .rl-glow{r:5;filter:blur(2.5px)}.nf-f9 .f9-scaffold{pointer-events:none;transition:opacity .22s}
.nf-f9.is-focus .f9-scaffold{opacity:.1}
@media(prefers-reduced-motion:reduce){.nf-f9 .f9-scaffold{transition:none}.nf-f9 .rl-pulse,.nf-f9 .rl-glow{display:none}}
"""
STYLE='body{margin:24px;background:#f4f6f8;color:#29353b;font:16px/1.5 Arial}main{max-width:1800px;margin:auto}h1{font-size:24px}h2{font-size:19px}.original{display:block;width:100%;height:auto;background:white}section{background:white;margin:28px 0;padding:18px}nav{display:flex;gap:16px;flex-wrap:wrap}a{color:#3046c9}.compare{display:grid;grid-template-columns:1fr 1fr;gap:20px}.compare>div{min-width:0}@media(max-width:900px){.compare{grid-template-columns:1fr}}@media(max-width:600px){body{margin:10px}section{padding:5px}}'
def head(title):return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="/assets/css/site.css?v=f9-1"><link rel="stylesheet" href="/assets/css/figures91-924.css?v=1"><style>{STYLE}</style><main>'
def foot():return '</main><script type="module">import {mountNative} from "/assets/js/nfig.js?v=f9-1";mountNative();</script></html>'
def main():
 for base in ['source/src/css','assets/css']:(SITE/base/'figures91-924.css').write_text(CSS)
 overview=[head('Figures 9.1–9.24 · Interactive reconstruction'),'<h1>Figures 9.1–9.24 · Interactive reconstruction</h1><nav>']
 overview += [f'<a href="#f9{n}">9.{n}</a>' for n in range(1,25)];overview+=['</nav>'];stats={}
 for n in range(1,25):
  markup=Figure(n).render();e=INV[n-1];ident=f'9{n}'
  originals=''.join(f'<img class="original" src="/{s}" alt="Original Figure 9.{n}">' for s in e['sources'])
  page=head(f'Figure 9.{n} comparison')+'<nav><a href="/example/figures91-924.html">All figures</a><a href="#redraw">Reconstruction</a></nav>'+f'<h1>Figure 9.{n} · Original and reconstruction</h1><div class="compare"><div><h2>Original</h2>'+originals+'</div><div><h2 id="redraw">Interactive reconstruction</h2>'+markup+'</div></div>'+foot()
  native_dir=SITE/'source/pipeline/native';native_dir.mkdir(parents=True,exist_ok=True);(native_dir/f'figure{ident}.html').write_text(markup)
  (SITE/f'example/figure{ident}.html').write_text(page);(SITE/f'example/figure{ident}-reconstruction.html').write_text(markup)
  overview += [f'<section id="f{ident}"><h2><a href="/example/figure{ident}.html">Figure 9.{n} · Compare with original</a></h2>'+markup+'</section>']
  stats[ident]=dict(images=markup.count('<image'),paths=markup.count('<path'),texts=markup.count('<text'),zones=markup.count('role="button"'),motion_tracks=markup.count('class="f9-flow rl-route"'))
  print(n,stats[ident],flush=True)
 (SITE/'example/figures91-924.html').write_text(''.join(overview)+foot());(SITE/'example/figures91-924-validation.json').write_text(json.dumps(stats,indent=2))
if __name__=='__main__':main()
