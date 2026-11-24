"""Figure 7.1: geometric and algebraic reasoning, independently annotated SVG."""
import json
from html import escape
from pathlib import Path
SITE=Path(__file__).resolve().parents[2]
INFO={
'camera':('Camera and image points','Image measurements provide 2D pixel coordinates. Calibration and geometric models connect these observations to spatial quantities.'),
'depth':('Depth and LiDAR','Depth sensors and LiDAR provide 3D measurements in a local sensor frame. They must be registered into a shared frame.'),
'joints':('Joint states','Joint measurements describe the configuration of a kinematic chain. Forward kinematics maps them to the end-effector pose.'),
'imu':('IMU and odometry','Inertial and odometry measurements describe pose increments. Composing these increments updates position and orientation.'),
'environment':('Environment geometry','Explicit obstacle and scene geometry supplies the constraints needed to test visibility, reachability and collision avoidance.'),
'pose':('Transforms and pose','A rigid transformation in SE(3) relates coordinate frames A and B, combining rotation and translation.'),
'multiview':('Multi-view geometry','Corresponding image points constrain a common 3D point. The epipolar equation links the two views through the fundamental matrix.'),
'kinematics':('Kinematics and Jacobian','Forward kinematics maps joint configuration to spatial pose. The Jacobian maps joint velocities to end-effector velocity.'),
'constraints':('Spatial constraints','Geometry tests whether a target is visible, reachable or in valid contact. These tests turn candidate configurations into feasibility decisions.'),
'world':('World-frame coordinates and poses','Transform local measurements into a common world frame so positions and orientations can be compared and composed.'),
'mesh':('Reconstructed geometry and structure','Multi-view observations can recover explicit geometric structure, represented here as a triangulated surface.'),
'regions':('Visible and reachable regions','A view cone describes observable space. A reach boundary describes the region accessible to the mechanism.'),
'path':('Feasible paths','A collision-free path passes around an obstacle. The dashed direct route intersects it and fails the geometric feasibility test.'),
'grasp':('Grasp and contact decisions','Contact geometry and mechanism configuration determine whether a proposed grasp is feasible.'),
}
def fig71():
 out=[]; add=out.append
 def text(x,y,t,size=32,cls='text',raw=False):add(f'<text class="f71-{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{t if raw else escape(t)}</text>')
 def lines(x,y,ts,size=32,cls='text',dy=39):
  for i,t in enumerate(ts):text(x,y+i*dy,t,size,cls)
 def path(d,cls='ink'):add(f'<path class="f71-{cls}" d="{d}"/>')
 def rect(x,y,w,h,cls='panel',rx=7):add(f'<rect class="f71-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
 def image(n,x,y,w,h):add(f'<image href="/assets/img/figs/f71/{n}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')
 def arrow(d,blue=False):add(f'<path class="f71-route {"f71-blue" if blue else ""}" d="{d}" marker-end="url(#f71-{"blue" if blue else "ink"}-arrow)"/>')
 def axes(x,y,s=1):
  for dx,dy in [(0,-52),(52,0),(-28,26)]:arrow(f'M{x} {y}l{dx*s} {dy*s}')
 def zone(k,box,draw):
  add(f'<g class="f71-zone" data-k="{k}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[k][0])}">');draw();rect(*box,'hit');add('</g>')
 def cube(x,y,w=46,h=46,d=16):
  path(f'M{x} {y}l{d} {-d}h{w}v{h}l{-d} {d}H{x}Z','cube')
  path(f'M{x} {y}h{w}v{h}M{x+w} {y}l{d} {-d}')
 def cone(x,y,w=73,h=114):
  rect(x-25,y-19,51,38,'sensor',7);path(f'M{x} {y}L{x+w} {y-h/2}V{y+h/2}Z','cone')
  add(f'<circle class="f71-lens" cx="{x}" cy="{y}" r="11"/>')
 def reach(x,y,rx,ry):add(f'<ellipse class="f71-reach" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>')
 add('<div class="nf nf-71" data-nf="71" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 892" role="group" aria-label="Figure 7.1: geometric and algebraic reasoning"><defs>')
 for name,color in [('ink','#2c373d'),('blue','#4146eb')]:add(f'<marker id="f71-{name}-arrow" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto"><path d="M2 2L11 7L2 12" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></marker>')
 add('</defs><rect width="2000" height="892" fill="white"/><g class="f71-scaffold">')
 path('M530 24V798M1431 24V798','divider')
 arrow('M540 442H598');arrow('M1356 442H1418')
 for x,t in [(254,'(i) Inputs'),(982,'(ii) Reasoning core'),(1720,'(iii) Outputs')]:text(x,862,t,36,'blue-text')
 add('</g>')
 def camera():
  image('i-inputs/camera',30,85,59,49);image('i-inputs/image-points',95,54,79,98);lines(351,98,['Camera / image points','2D pixels'])
 zone('camera',(15,48,509,111),camera)
 def depth():
  image('i-inputs/depth-sensor',8,198,97,136);image('i-inputs/lidar-points',101,198,79,92);lines(351,239,['Depth / LiDAR','3D measurements'])
 zone('depth',(6,193,518,143),depth)
 def joints():
  image('i-inputs/joint-states-arm',14,339,152,122);lines(351,387,['Joint states','Kinematic chain'])
 zone('joints',(12,339,512,124),joints)
 def imu():
  cube(59,537,44,44,16);axes(81,555,1.12);lines(351,541,['IMU / odometry','Pose increments'])
 zone('imu',(30,489,494,113),imu)
 def environment():
  image('i-inputs/environment-obstacles',23,653,167,85);lines(351,698,['Environment','geometry / obstacles'])
 zone('environment',(15,645,509,108),environment)
 def pose():
  rect(615,59,361,358);text(795,122,'Transforms & pose',38,'heading');text(684,196,'A');text(898,183,'B');axes(691,275);axes(895,257,.88);arrow('M754 235H834',True);text(794,196,'T',32,'blue-text');text(795,366,'<tspan font-weight="bold">T</tspan> ∈ <tspan font-style="italic">SE</tspan>(3)',38,'math',True)
 zone('pose',(615,59,361,358),pose)
 def multiview():
  rect(992,59,361,358);lines(1173,106,['Multi-view','geometry'],38,'heading',43)
  image('i-inputs/camera',1029,292,59,49);image('i-inputs/camera',1258,292,59,49)
  for x,y,r in [(1171,203,8),(1095,279,7),(1249,279,7)]:add(f'<circle class="f71-point" cx="{x}" cy="{y}" r="{r}"/>')
  path('M1058 317L1171 203L1287 317','epipolar');text(1221,205,'X',32,'blue-text');text(1074,255,'x',30,'blue-text');text(1271,255,"x′",30,'blue-text');text(1172,379,'<tspan font-weight="bold">x′</tspan><tspan baseline-shift="super" font-size="24">T</tspan><tspan font-weight="bold">Fx</tspan> = 0',38,'math',True)
 zone('multiview',(992,59,361,358),multiview)
 def kinematics():
  rect(615,426,361,359);lines(795,480,['Kinematics /','Jacobian'],38,'heading',43);image('ii-reasoning/kinematics-arm',642,548,135,116);arrow('M848 608L931 558',True);text(899,661,'Velocity');text(795,693,'<tspan font-weight="bold">x</tspan> = <tspan font-style="italic">f</tspan>(<tspan font-weight="bold">q</tspan>)',36,'math',True);text(795,754,'<tspan font-weight="bold">ẋ</tspan> = <tspan font-weight="bold">J</tspan>(<tspan font-weight="bold">q</tspan>)<tspan font-weight="bold">q̇</tspan>',36,'math',True)
 zone('kinematics',(615,426,361,359),kinematics)
 def constraints():
  rect(992,426,361,359);lines(1173,477,['Spatial','constraints'],38,'heading',43);cone(1036,618,69,122);reach(1202,612,54,63);image('ii-reasoning/reach-arm-clean',1132,581,111,93);image('ii-reasoning/contact-gripper',1260,588,91,87);text(1066,725,'View',29);text(1198,725,'Reach',29);text(1297,725,'Contact',29)
 zone('constraints',(992,426,361,359),constraints)
 def world():
  axes(1519,131,1.2);lines(1804,101,['World-frame','coordinates / poses'])
 zone('world',(1450,58,530,120),world)
 def mesh():
  path('M1478 282L1497 225L1548 200L1606 225L1615 284L1545 307Z','mesh');path('M1478 282L1606 225M1497 225L1615 284M1548 200L1545 307');lines(1804,245,['Reconstructed','geometry / structure'])
 zone('mesh',(1452,191,528,128),mesh)
 def regions():
  cone(1469,426);reach(1614,433,51,60);image('iii-outputs/reachable-arm-clean',1558,401,96,82);lines(1835,412,['Visible / reachable','regions'])
 zone('regions',(1438,361,548,144),regions)
 def feasible():
  cube(1541,625,45,44,16);path('M1475 672L1638 631','rejected');arrow('M1475 672L1482 583H1602L1636 627',True);path('M1567 630L1579 642M1579 630L1567 642','cross');text(1830,613,'Feasible paths')
 zone('path',(1460,571,524,113),feasible)
 def grasp():
  image('iii-outputs/grasp-gripper',1495,696,95,85);path('M1616 748L1624 758L1638 739','check');lines(1830,732,['Grasp / contact','decisions'])
 zone('grasp',(1480,691,504,96),grasp)
 add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:{'t':v[0],'b':v[1]} for k,v in INFO.items()})+'</script></div>')
 return ''.join(out)
if __name__=='__main__':
 (SITE/'example/figure71.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure71-2"><title>Figure 7.1 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 7.1 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/711_geo.webp" alt="Original Figure 7.1"><h2>Interactive reconstruction</h2>'''+fig71()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure71-2';mountNative();</script></html>''')
