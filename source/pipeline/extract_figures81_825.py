"""Reproducible source-pixel asset preparation for Figures 8.1–8.25.

Coordinates below are in a 1000-unit-wide source space. Diagrams, typography,
frames and connector paths are deliberately left for independent frontend drawing.
"""
from pathlib import Path
from html import escape
import json, shutil, sys
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
INVENTORY=json.loads((ROOT/'source/pipeline/figures81_825_sources.json').read_text())
SPECS={i:[] for i in range(1,26)}
def add(n,panel,name,box,kind='photo',source=0,polygon=None,reuse=None):
 SPECS[n].append(dict(file=f'{panel}/{name}.png',title=name.replace('-',' '),box=box,kind=kind,source_index=source,polygon=polygon,reuse=reuse))
def row(n,panel,names,xs,y,w,h,kind='photo',source=0):
 for name,x in zip(names,xs):add(n,panel,name,(x,y,x+w,y+h),kind,source)
add(1,'shared','input-corgi',(28,145,120,240),'cutout');add(1,'shared','output-corgi',(882,141,983,241),'cutout')
add(2,'example','corgi-skateboard',(843,467,977,598),'cutout')
for panel,name,box in [('task','blue-mug',(49,54,160,165)),('task','red-mug',(471,54,582,165)),('a','source',(21,260,92,331)),('b','source',(351,262,417,328)),('c','before',(688,254,752,318)),('c','after',(912,254,976,318)),('d','reference',(101,621,162,682))]:add(3,panel,name,box)
# The handle/target overlay is removed by reusing the identical clean source photograph.
add(3,'e','drag-source',(604,624,706,726),reuse=(3,0))
for name,box in [('trellis',(44,9,234,257)),('printing-press',(257,11,488,257)),('camera',(533,10,738,255)),('house',(771,12,983,255)),('ship',(5,286,122,405)),('food-truck',(135,285,245,404)),('dragon',(251,285,370,404)),('mech',(383,284,487,406)),('lamp',(522,284,618,405)),('clock',(623,284,749,405)),('owl',(761,284,858,405)),('turntable',(870,283,987,405))]:add(4,'objects',name,box,'tinted-cutout')
add(4,'references','trellis',(89,219,151,280));add(4,'references','press',(331,218,393,281))
for panel,name,box in [('task','chair',(641,13,724,111)),('p1','generated-chair',(420,218,475,294)),('p2','optimized-chair',(534,204,591,282)),('p3','view-1',(225,514,275,577)),('p3','view-2',(302,514,350,577)),('p3','view-3',(376,514,426,577)),('p3','lifted-chair',(70,577,126,650)),('p4','reconstructed-chair',(862,470,922,548))]:add(5,panel,name,box,'cutout')
# Dataset objects are separate cutouts; source-visible occlusions are retained.
objects=[('space-station',(51,36,219,168)),('pagoda',(256,43,335,196)),('balloon',(342,44,397,134)),('castle',(387,19,552,198)),('biplane',(538,48,597,136)),('lighthouse',(551,55,657,194)),('dinosaur',(623,91,811,265)),('space-shuttle',(806,56,956,161)),('dragon-statue',(172,128,269,220)),('banana',(98,194,181,228)),('classical-bust',(332,155,396,242)),('fish-skeleton',(380,184,579,277)),('yellow-car',(578,198,632,219)),('armchair',(765,172,915,306)),('mask',(905,220,977,302)),('sneaker',(45,223,113,283)),('owl-clock',(128,214,186,315)),('vending-machine',(193,223,249,310)),('buddha',(258,204,318,303)),('grand-piano',(300,252,409,354)),('radio',(409,274,499,329)),('lion-bust',(505,253,568,343)),('ornate-chair',(560,229,612,306)),('blue-vase',(617,295,656,344)),('ring-sculpture',(651,245,744,343)),('orange',(744,283,787,318)),('skull',(878,295,956,355)),('blue-jar',(81,279,115,335)),('small-bird',(107,295,132,332)),('shell',(117,327,146,359)),('stone-sculpture',(138,316,245,403)),('saxophone',(237,307,288,353)),('radio-device',(248,350,310,386)),('black-pebble',(329,344,357,378)),('clay-vase',(390,328,452,402)),('bulldozer',(428,329,531,444)),('tortoise',(549,316,652,390)),('small-stone',(657,341,691,369)),('white-speaker',(728,326,763,368)),('camera',(761,301,826,391)),('book',(826,313,868,347)),('telephone',(645,366,738,435)),('wooden-box',(737,378,786,417)),('church',(24,315,219,536)),('church-spire',(207,421,270,535)),('calculator',(213,394,273,434)),('green-stool',(250,432,298,490)),('well',(293,380,372,466)),('disc',(372,408,415,451)),('penguin',(532,370,559,417)),('conch',(542,390,631,456)),('house',(746,350,982,550)),('red-car',(287,465,361,546)),('toy-engine',(363,468,432,554)),('round-dial',(436,447,489,486)),('motorbike',(438,485,494,554)),('woodwind',(505,447,559,555)),('blue-car',(532,494,584,531)),('electric-guitar',(577,465,655,554)),('black-cube',(599,477,653,517)),('yellow-plane',(609,447,765,544)),('blue-cube',(678,427,745,471))]
for name,box in objects:add(6,'objects',name,box,'cutout')
add(7,'task','room',(467,31,580,144))
row(7,'b',['view-1','view-2','view-3'],[526,626,726],221,71,71)
row(7,'c',['observed-1','observed-2'],[23,112],523,64,65)
add(7,'c','novel-view',(289,635,366,712))
row(7,'d',['frame-1','frame-2','frame-3'],[580,695,811],661,74,74)
# Figure 8.8: each photograph/render tile is independent, not a labelled cell screenshot.
row(8,'two-view',['input-1','input-2','input-3'],[24]*3,12,44,31) if False else None
for r in range(3):row(8,'two-view',[f'row-{r+1}-rgb',f'row-{r+1}-depth',f'row-{r+1}-heat'],[24,69,113],12+34*r,42,31)
for r in range(3):add(8,'multi-view',f'view-{r+1}',(169,12+34*r,227,44+34*r))
add(8,'multi-view','reconstruction-1',(229,12,375,73),'cutout');add(8,'multi-view','reconstruction-2',(229,75,375,109),'cutout')
add(8,'continuous','forest-strip',(389,14,500,31));add(8,'continuous','people-strip',(505,14,621,31))
add(8,'continuous','forest-scene',(388,37,501,111),'cutout');add(8,'continuous','people-scene',(507,36,637,107),'cutout')
add(8,'large-scale','reconstruction',(644,10,820,111),'cutout');add(8,'matching','correspondences',(831,12,985,112))
for k,box in enumerate([(24,162,74,210),(24,214,74,262),(189,162,239,210),(189,214,239,262),(77,160,188,263)]):add(8,'static-3dgs',f'view-{k+1}',box,'cutout' if k==4 else 'photo')
add(8,'dynamic-3dgs','view-strip',(248,162,278,211));add(8,'dynamic-3dgs','scene-top',(294,162,418,210),'cutout')
row(8,'dynamic-3dgs',['scene-1','scene-2'],[248,335],214,83,48)
for k,box in enumerate([(433,163,477,212),(482,163,525,212),(433,214,477,261),(482,214,525,261),(532,174,599,262)]):add(8,'nvs-no-3d',f'render-{k+1}',box,'cutout')
for k,box in enumerate([(611,162,690,208),(709,162,787,208),(611,216,690,262),(709,216,787,262)]):add(8,'video-nvs',f'view-{k+1}',box)
add(8,'image-nvs','source',(800,163,897,261));row(8,'image-nvs',['novel-1','novel-2'],[903,948],162,39,49,'cutout');row(8,'image-nvs',['novel-3','novel-4'],[903,948],214,39,48,'cutout')
add(8,'3dgs-generation','ocean',(24,312,125,411));row(8,'3dgs-generation',['frame-1'],[129],312,32,30)
for k in range(1,3):add(8,'3dgs-generation',f'frame-{k+1}',(129,312+34*k,161,342+34*k))
add(8,'nerf-generation','source',(181,334,238,393))
for k,x in enumerate([241,291,342]):add(8,'nerf-generation',f'rgb-{k+1}',(x,312,x+49,359));add(8,'nerf-generation',f'normal-{k+1}',(x,362,x+49,410))
for name,box in [('axe',(412,311,474,366)),('lamp',(412,365,480,411)),('jacket',(478,312,595,411))]:add(8,'mesh-generation',name,box,'cutout')
add(8,'slam','mapped-room',(610,311,801,413),'cutout')
for r in range(2):row(8,'robotics',[f'row-{r+1}-rgb',f'row-{r+1}-mask',f'row-{r+1}-feature'],[821,876,932],312+51*r,52,48)
for panel,name,box in [('task','observed-1',(19,25,126,132)),('task','observed-2',(138,25,245,132)),('task','recovered',(723,25,830,132)),('p1','input',(31,354,111,435)),('p1','rendered',(194,354,275,435)),('p2','new-1',(371,237,438,305)),('p2','new-2',(452,237,519,305)),('p2','new-3',(533,237,600,305)),('p3','visible-part',(697,230,743,320))]:add(9,panel,name,box)
for panel,name,box in [('task','panorama',(307,6,639,117)),('task','room',(742,4,937,118)),('c','observed-1',(22,533,166,580)),('c','observed-2',(22,604,166,651)),('d','panorama',(528,519,713,581))]:add(10,panel,name,box,'cutout' if name=='room' else 'photo')
# Use the source's unannotated corresponding plates; retain placement separately.
add(10,'a','panorama',(195,310,465,400),reuse=(10,0))
for k,x in enumerate([528,682,836]):add(10,'b',f'frame-{k+1}',(x,351,x+129,394),reuse=(10,0))
add(10,'d','room',(720,604,918,717),'cutout',reuse=(10,1))
# Literature montage, boundaries excluded and every distinct example separated.
for name,box in [('photo-before-1',(14,36,100,101)),('photo-after-1',(106,36,193,101)),('photo-before-2',(14,114,100,180)),('photo-after-2',(106,114,193,180)),('style-before-1',(14,214,100,279)),('style-after-1',(106,214,193,279)),('style-before-2',(14,286,100,352)),('style-after-2',(106,286,193,352))]:add(11,'a',name,box)
for name,box in [('flower-source',(214,66,298,128)),('flower-extracted',(305,20,390,82)),('flower-removed',(305,104,390,166)),('move-before',(213,192,300,256)),('move-after',(304,192,390,256)),('duplicate-before',(213,279,300,342)),('duplicate-after',(304,279,390,342))]:add(11,'b',name,box)
row(11,'c',['bulldozer-1','bulldozer-2','bulldozer-3'],[411,473,533],35,59,47,'tinted-cutout')
row(11,'c',['bear-1','bear-2','bear-3'],[407,469,532],113,59,44)
add(11,'c','deformed-surface-before',(434,193,566,261));add(11,'c','deformed-surface-after',(434,265,566,341))
for name,box in [('original-statue',(614,24,695,85)),('removed-statue',(702,61,783,122)),('removal-mask',(614,102,695,163)),('insertion-before',(606,181,695,235)),('insertion-after',(699,181,787,235)),('original-sculpture',(619,263,671,320)),('masked-sculpture',(676,267,735,321)),('completed-sculpture',(740,268,788,321))]:add(11,'d',name,box)
row(11,'e',['bear-before','bear-after'],[810,901],38,86,49)
row(11,'e',['giraffe-1','giraffe-2','giraffe-3'],[815,872,927],134,51,54)
row(11,'e',['stump','butterfly-1','butterfly-2'],[821,870,923],214,46,44,'tinted-cutout')
row(11,'e',['man-before','man-after'],[835,901],298,61,50)
for panel,name,box in [('task','blue-chair-room',(20,30,152,162)),('task','red-chair-room',(843,30,975,162)),('a','rendered',(186,263,263,339)),('a','edited',(186,470,233,517)),('d','edited-scene',(30,756,107,832))]:add(12,panel,name,box)
row(12,'b',['view-1','view-2','view-3'],[360,456,553],275,65,65)
row(12,'b',['target-1','target-2','target-3'],[365,461,557],463,53,53)
row(13,'task',[f'ball-{k}' for k in range(1,5)],[415,559,703,847],12,117,117)
row(13,'a',[f'frame-{k}' for k in range(1,5)],[47,102,157,212],396,48,49)
row(13,'b',[f'frame-{k}' for k in range(1,5)],[404,453,501,550],589,43,42)
row(13,'c',[f'frame-{k}' for k in range(1,5)],[733,782,831,880],584,42,43)
row(14,'task',[f'frame-{k}' for k in range(1,4)],[569,712,855],11,116,115)
add(14,'a','anchor',(40,263,118,342))
row(14,'c',[f'depth-{k}' for k in range(1,4)],[35,127,220],446,76,77)
row(14,'output',[f'frame-{k}' for k in range(1,4)],[701,788,874],718,71,71)
row(15,'task',[f'frame-{k}' for k in range(1,5)],[423,567,710,853],12,115,115)
row(15,'d',[f'reference-{k}' for k in range(1,4)],[349,437,525],506,66,66)
row(15,'output',[f'frame-{k}' for k in range(1,4)],[689,783,878],633,76,77)
row(16,'task',[f'frame-{k}' for k in range(1,4)],[563,706,850],30,117,117)
add(16,'a','style-reference',(208,227,283,302))
row(16,'output',[f'frame-{k}' for k in range(1,4)],[595,706,817],691,86,86)
row(17,'task',[f'source-{k}' for k in range(1,4)],[23,106,190],51,75,75)
row(17,'task',[f'edited-{k}' for k in range(1,4)],[737,820,904],51,75,75)
for panel,y in [('a',249),('b',422)]:
 row(17,panel,[f'source-{k}' for k in range(1,4)],[27,67,107],y,35,35)
 row(17,panel,[f'edited-{k}' for k in range(1,4)],[857,897,937],y,35,35)
row(17,'c',['training-source','training-target'],[27,107],591,38,38)
row(17,'c',[f'edited-{k}' for k in range(1,4)],[857,897,937],594,35,35)
row(17,'d',[f'edited-{k}' for k in range(1,4)],[857,897,937],767,35,35)
add(17,'e','source',(30,926,83,978));row(17,'e',[f'edited-{k}' for k in range(1,4)],[857,897,937],938,35,35)
for name,box in [('joint-positions',(84,29,176,246)),('kinematic-chains',(283,29,447,247)),('surface-markers',(500,29,697,267)),('joint-rotations',(775,29,962,267))]:add(18,'top',name,box,'cutout')
for name,box in [('skinning',(20,5,267,256)),('shape',(267,5,500,256)),('pose',(499,5,751,256)),('articulated',(752,0,1000,256))]:add(18,'smpl',name,box,'cutout',source=1)
add(19,'task','woman',(20,25,126,132));add(19,'scene','room',(134,570,253,643),'cutout')
row(20,'dog',[f'pose-{k}' for k in range(1,4)],[648,762,878],126,106,65,'cutout')
row(20,'bird',[f'pose-{k}' for k in range(1,4)],[653,770,885],298,84,56,'cutout')
row(20,'horse',[f'pose-{k}' for k in range(1,4)],[642,758,874],445,111,85,'cutout')
for panel,offset in [('observed',0),('candidate',654)]:
 for name,box in [('north-car',(133,108,166,176)),('east-car',(236,190,298,221)),('west-car',(57,242,119,272)),('ego-car',(176,279,212,350))]:add(21,panel,name,tuple(v+offset if k%2==0 else v for k,v in enumerate(box)),'road-cutout')
row(23,'task',['chair-1','chair-2','chair-3'],[416,552,686],34,77,98,'cutout')
add(23,'b','input-chair',(265,226,325,307),'cutout')
row(23,'c',['frame-1','frame-2','frame-3'],[416,469,522],253,38,50,'cutout')
add(23,'d','static-chair',(657,247,699,301),'cutout')
row(23,'ii',['target-1','target-2','target-3'],[751,819,885],558,53,65,'cutout')
add(25,'p2','program-icon',(339,135,393,189),'icon');add(25,'p3','prompt-icon',(306,258,363,310),'icon')
add(25,'output','raster-art',(906,77,983,115),'icon');add(25,'output','vector-ui',(906,158,983,198),'icon');add(25,'output','3d-scene',(907,252,983,299),'icon')

# A source module overlaps the lifted chair's top. Reuse its clean matching view.
SPECS[5][6]['reuse']=(5,5)
for spec in SPECS[6]:
 if spec['title']=='small bird':spec['box']=(107,260,130,299)
 if spec['title']=='blue vase':spec['box']=(619,296,646,358)
 if spec['title']=='blue car':spec['box']=(532,471,584,521)
# Silhouette constraints remove labels, inset frames and neighbouring objects.
for candidate in SPECS[21][4:]:
 candidate['reuse']=(21,SPECS[21][:4].index(next(a for a in SPECS[21][:4] if a['title']==candidate['title'])))
POLYGONS={
 (4,'trellis'):[(44,10),(93,10),(108,31),(138,37),(153,55),(176,55),(195,86),(184,121),(225,147),(229,243),(206,256),(153,216),(86,198),(45,174)],
 (4,'printing-press'):[(307,13),(368,13),(405,50),(437,49),(450,75),(441,124),(475,135),(488,205),(432,251),(359,217),(307,198),(258,174),(279,129),(275,104),(296,70)],
 (4,'camera'):[(551,21),(589,10),(695,51),(700,98),(726,117),(738,179),(717,253),(654,241),(610,242),(552,185),(536,110),(533,86),(550,79)],
 (4,'house'):[(815,67),(836,53),(905,13),(918,24),(940,102),(979,160),(982,215),(935,252),(894,240),(776,185),(772,152),(804,132)],
 (6,'tortoise'):[(553,351),(562,336),(588,323),(608,322),(633,335),(646,354),(664,359),(665,370),(646,376),(635,389),(621,385),(603,387),(581,379),(570,384),(561,374),(552,370)],
 (6,'conch'):[(547,437),(565,419),(575,406),(592,396),(607,399),(623,416),(629,437),(616,451),(580,455),(546,449)],
 (6,'blue-car'):[(552,472),(570,475),(578,485),(583,506),(575,517),(550,519),(540,510),(534,491)],
 (6,'yellow-plane'):[(649,448),(658,450),(663,469),(688,480),(706,490),(719,492),(731,505),(758,532),(741,532),(715,516),(687,507),(671,518),(652,524),(643,519),(630,516),(620,511),(642,497),(650,489)],
 (6,'space-station'):[(53,113),(129,36),(171,45),(217,96),(185,125),(166,134),(149,166),(106,154)],
 (6,'castle'):[(469,19),(495,20),(522,41),(530,80),(548,117),(535,171),(542,191),(406,197),(388,168),(409,122),(421,76)],
 (6,'lighthouse'):[(617,54),(635,55),(647,82),(652,177),(632,190),(555,181),(550,174),(601,170),(600,81)],
 (6,'dinosaur'):[(643,240),(643,211),(669,157),(710,120),(751,97),(785,95),(808,107),(805,126),(773,140),(770,168),(784,173),(777,184),(753,176),(745,207),(766,241),(766,254),(741,256),(721,224),(713,203),(697,226),(687,242),(699,251),(687,264),(652,257),(629,252)],
 (6,'dragon-statue'):[(180,129),(208,131),(223,152),(246,150),(267,143),(261,181),(244,210),(198,222),(175,214)],
 (6,'banana'):[(98,208),(105,197),(142,194),(169,203),(180,204),(180,211),(142,215),(121,229),(103,223)],
 (6,'fish-skeleton'):[(382,184),(463,186),(485,173),(499,186),(503,209),(579,229),(574,240),(539,241),(509,256),(473,272),(438,259),(403,247),(380,245)],
 (6,'armchair'):[(783,174),(828,174),(909,188),(912,207),(887,265),(877,296),(844,305),(774,284),(764,269),(772,212)],
 (6,'owl-clock'):[(139,214),(155,216),(164,236),(182,249),(178,266),(170,279),(176,300),(166,310),(133,310),(130,295),(140,276),(134,259),(127,247)],
 (6,'buddha'):[(265,217),(281,204),(294,212),(295,231),(306,249),(319,290),(297,300),(265,296),(259,268)],
 (6,'grand-piano'):[(341,252),(365,253),(407,269),(396,291),(397,334),(378,349),(324,350),(302,337),(302,318),(323,302),(328,274)],
 (6,'ring-sculpture'):[(683,247),(704,247),(724,263),(738,290),(740,325),(722,339),(686,341),(653,328),(652,314),(672,303),(666,280)],
 (6,'stone-sculpture'):[(150,339),(163,330),(180,319),(201,317),(229,327),(239,342),(229,366),(245,374),(239,390),(205,403),(141,383),(140,368)],
 (6,'bulldozer'):[(473,330),(506,330),(506,355),(526,368),(520,406),(520,439),(481,440),(430,426),(430,409),(447,405),(450,374),(465,362)],
 (6,'church'):[(53,314),(64,323),(72,352),(93,382),(100,406),(140,400),(160,411),(181,407),(191,420),(186,446),(207,465),(217,507),(197,522),(167,533),(130,522),(108,532),(76,522),(60,514),(35,514),(24,490),(49,464),(48,443),(39,435),(67,412),(71,386)],
 (6,'house'):[(815,376),(853,350),(888,354),(910,376),(931,399),(969,413),(981,436),(949,482),(949,512),(891,549),(850,528),(820,516),(785,499),(747,469),(759,444),(769,416),(799,410)],
 (6,'woodwind'):[(507,448),(518,450),(531,489),(556,535),(547,552),(526,554),(519,541),(519,508)],
 (6,'electric-guitar'):[(578,466),(586,468),(604,500),(620,511),(628,508),(644,516),(654,540),(639,553),(614,553),(600,542),(595,528),(598,518)],
 (6,'black-cube'):[(622,478),(635,478),(652,493),(646,515),(622,517),(608,507),(605,493)],
 (6,'blue-cube'):[(679,430),(713,428),(743,441),(733,463),(711,472),(692,464)],
}
for (figure,name),points in POLYGONS.items():
 for spec in SPECS[figure]:
  if spec['title']==name.replace('-',' '):spec['polygon']=points
# Preserve all three distinct panorama frames; restore only the circular overlay.
for spec,cx in zip([a for a in SPECS[10] if a['file'].startswith('b/')],[559,741,923]):
 spec['reuse']=None;spec['repair_circle']=(cx,371,9)
# Trim two literature captions and skeletal panel labels.
for spec in SPECS[11]:
 if spec['file'].startswith('e/giraffe'):spec['box']=(spec['box'][0],134,spec['box'][2],180)

STYLE='''body{margin:24px;background:#f1f4f8;color:#263445;font:16px/1.6 Arial}main{max-width:1500px;margin:auto}section{background:white;padding:20px;margin:24px 0;border-radius:8px}h1{font-size:27px}h2{font-size:22px}h3{font-size:16px}.original{display:block;max-width:100%;height:auto;margin:auto}nav{display:flex;gap:14px;flex-wrap:wrap}a{color:#344cc1}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}.checker{height:210px;background:repeating-conic-gradient(#e4e9ed 0 25%,white 0 50%) 0/24px 24px;display:flex;align-items:center;justify-content:center}.checker img{max-width:95%;max-height:95%;object-fit:contain}article{min-width:0}p{overflow-wrap:anywhere}.overview{max-height:500px;object-fit:contain;width:100%}@media(max-width:800px){body{margin:10px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:480px){.grid{grid-template-columns:1fr}}'''

def extract(n,spec,sources):
 im=sources[spec['source_index']];scale=im.width/1000
 box=tuple(round(v*scale) for v in spec['box']);crop=im.crop(box).convert('RGBA')
 if spec.get('reuse'):
  f,k=spec['reuse'];other=SPECS[f][k];original=sources[other['source_index']]
  crop=original.crop(tuple(round(v*original.width/1000) for v in other['box'])).convert('RGBA').resize(crop.size,Image.Resampling.LANCZOS)
 if spec.get('repair_circle'):
  cx,cy,radius=spec['repair_circle'];a=np.array(crop).astype(float)
  yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]]
  mask=(xx/scale-cx)**2+(yy/scale-cy)**2<radius**2
  indices=ndimage.distance_transform_edt(mask,return_distances=False,return_indices=True)
  a[mask]=a[tuple(indices)][mask]
  for _ in range(350):
   mean=ndimage.convolve(a,np.array([[0,1,0],[1,0,1],[0,1,0]])[:,:,None]/4,mode='nearest');a[mask]=mean[mask]
  crop=Image.fromarray(a.astype('uint8'))
 p=np.array(crop).astype(float);rgb=p[:,:,:3];kind=spec['kind']
 if kind=='icon':
  alpha=255-rgb.min(2);alpha[alpha<10]=0
  crop=Image.new('RGBA',crop.size);crop.putalpha(Image.fromarray(alpha.astype('uint8')))
 elif kind!='photo':
  if kind=='road-cutout':
   bg=np.array([244,245,246]);dist=np.max(np.abs(rgb-bg),2);mask=dist<26
  elif kind=='tinted-cutout':
   edges=np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]]);bg=np.median(edges,axis=0);mask=np.max(np.abs(rgb-bg),2)<14
  else:mask=rgb.min(2)>246
  labels,_=ndimage.label(mask);boundary=np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]));boundary=boundary[boundary!=0]
  exterior=np.isin(labels,boundary)
  alpha=np.where(exterior,0,255).astype('uint8')
  # Suppress only tiny isolated compression remnants, preserving fine visible limbs.
  components,count=ndimage.label(alpha>0);sizes=np.bincount(components.ravel());small=sizes<max(2,scale*scale*2);small[0]=False;alpha[small[components]]=0
  # Restrict every dataset cutout to its main connected object. Thin detached
  # source pieces are retained when a manual silhouette is supplied.
  if n in (4,6,18):
   if spec.get('polygon'):
    poly=Image.new('L',crop.size);ImageDraw.Draw(poly).polygon([(round(x*scale)-box[0],round(y*scale)-box[1]) for x,y in spec['polygon']],fill=255)
    alpha=np.minimum(alpha,np.array(poly))
   components,count=ndimage.label(alpha>0);sizes=np.bincount(components.ravel());sizes[0]=0
   if count:alpha[components!=sizes.argmax()]=0
  if n==4 and spec['file'].startswith('objects/'):
   # Reference insets occlude the original object; they are independent assets.
   yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]];xx=xx/scale;yy=yy/scale
   if spec['title']=='trellis':alpha[(xx<155)&(yy>215)]=0
   if spec['title']=='printing press':alpha[(xx>327)&(xx<396)&(yy>215)]=0
  crop.putalpha(Image.fromarray(alpha))
 return crop,box

def make_figure(n):
 key=f'8{n}';data=INVENTORY[n-1];out=ROOT/f'assets/figures/elements/figure{key}';out.mkdir(parents=True,exist_ok=True)
 if n==22:return 0
 sources=[Image.open(ROOT/p).convert('RGB') for p in data['sources']]
 entries=[];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
 overview=Image.new('RGB',(1200,max(1,(len(SPECS[n])+3)//4)*245),'#f3f5f7');d=ImageDraw.Draw(overview)
 cards=''
 for i,spec in enumerate(SPECS[n]):
  asset,box=extract(n,spec,sources)
  for base in [out,ROOT/f'source/src/img/figs/f{key}',ROOT/f'assets/img/figs/f{key}']:
   dest=base/spec['file'];dest.parent.mkdir(parents=True,exist_ok=True);asset.save(dest)
  e={k:v for k,v in spec.items() if v is not None};e['source_box']=box;e['size']=asset.size;entries.append(e)
  x=i%4*300;y=i//4*245
  d.text((x+10,y+8),spec['file'].replace('.png',''),font=font,fill='#263445')
  for yy in range(y+35,y+235,12):
   for xx in range(x+8,x+292,12):d.rectangle((xx,yy,xx+11,yy+11),fill='#e4e9ed' if (xx//12+yy//12)%2 else 'white')
  thumb=asset.copy();thumb.thumbnail((272,190));overview.paste(thumb,(x+(300-thumb.width)//2,y+40+(190-thumb.height)//2),thumb)
  cards+=f'<article><h3>{escape(spec["file"])}</h3><div class="checker"><img loading="lazy" src="/assets/figures/elements/figure{key}/{spec["file"]}" alt="{escape(spec["title"])}"></div><p>{asset.width} × {asset.height} · RGBA PNG</p></article>'
 notes=['Text, formulas (Cambria Math with source-matched italics), frames, arrows and diagram primitives will be independent frontend elements.','Cutouts retain source shading and visible occlusions; photographs retain their rectangular image content.']
 if n==24:notes.append('This figure has no raster pictorial elements: the full diagram will be rebuilt in the frontend.')
 if n in [3,10]:notes.append('Clean corresponding source plates replace annotated plates; their original placement is recorded in the manifest.')
 overview.save(out/'overview.png')
 manifest=dict(figure=f'8.{n}',sources=data['sources'],source_sizes=[im.size for im in sources],assets=entries,frontend=notes)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (out/'extract.py').write_text('from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[4]\nsys.path.insert(0,str(ROOT/"source/pipeline"))\nfrom extract_figures81_825 import make_figure\nif __name__=="__main__": make_figure('+str(n)+')\n')
 originals=''.join(f'<img class="original" src="/{p}" alt="Original Figure 8.{n}">' for p in data['sources'])
 page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 8.{n} asset review</title><style>{STYLE}</style><main><nav><a href="/example/figures81-825-assets.html">All 25 figures</a></nav><h1>Figure 8.{n} · Asset review</h1><section><h2>Original</h2>{originals}</section><section><h2>{len(entries)} extracted PNG assets</h2><div class="grid">{cards}</div></section><section><h2>Frontend reconstruction · next step</h2><ul>'+''.join(f'<li>{escape(v)}</li>' for v in notes)+'</ul></section></main></html>'
 (ROOT/f'example/figure{key}-assets.html').write_text(page)
 print(f'8.{n}: {len(entries)} assets')
 return len(entries)

def main():
 for n in [int(a) for a in sys.argv[1:]] or range(1,26):make_figure(n)
 cards='';total=0
 for n in range(1,26):
  key=f'8{n}'
  if n==22:cards+='<section id="f822"><h2>Figure 8.22 · Existing approved reconstruction</h2><p>Preserved existing assets and integrated figure.</p><a href="/example/figure822.html">Open original-versus-redraw preview</a></section>';continue
  total+=len(SPECS[n])
  cards+=f'<section id="f{key}"><h2>Figure 8.{n} · {len(SPECS[n])} PNG assets</h2><a href="/example/figure{key}-assets.html">Open original and individual assets →</a><a href="/example/figure{key}-assets.html"><img loading="lazy" class="overview" src="/assets/figures/elements/figure{key}/overview.png" alt="Figure 8.{n} assets"></a></section>'
 nav=''.join(f'<a href="#f8{n}">8.{n}</a>' for n in range(1,26))
 (ROOT/'example/figures81-825-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 8.1–8.25 · Asset review</title><style>{STYLE}</style><main><h1>Figures 8.1–8.25 · Asset review</h1><p>{total} separately saved PNG assets. Figure 8.22 retains its approved reconstruction. Figure 8.24 is entirely frontend-drawn. Open each figure for its original and individual assets.</p><nav>{nav}</nav>{cards}</main></html>')
 print('Total:',total)
if __name__=='__main__':main()
