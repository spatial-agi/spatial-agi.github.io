"""Extract Figure 6.25 scene assets; annotations stay in the frontend."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw
SITE = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent
SOURCE = 'assets/figures/figures/part3/section6/temporal_localization_task_settings.webp'
im = Image.open(SITE / SOURCE).convert('RGBA')
specs = [
 ('shared-video/frame-00.png', (55,189,232,367), ['a','b','c','d','f'], 'Approaching the counter'),
 ('shared-video/frame-01.png', (241,189,417,367), ['a','b','c','d','f'], 'Opening the microwave'),
 ('shared-video/frame-02.png', (425,189,602,367), ['a','c','d','f'], 'Reaching toward the microwave'),
 ('e-corpus/cooking.png', (721,739,810,828), ['e'], 'Cooking'),
 ('e-corpus/cycling.png', (819,739,907,828), ['e'], 'Cycling'),
 ('e-corpus/microwave.png', (919,742,1004,825), ['e'], 'Microwave video; blue selection border excluded'),
 ('e-corpus/reading.png', (721,837,810,926), ['e'], 'Reading'),
 ('e-corpus/washing.png', (819,837,907,926), ['e'], 'Washing dishes'),
 ('e-corpus/laundry.png', (918,837,1007,926), ['e'], 'Laundry'),
 ('e-retrieved/video-03.png', (1133,788,1261,917), ['e'], 'Retrieved microwave video'),
]
assets=[]
for file,box,panels,notes in specs:
 frame=im.crop(box);target=ROOT/file;target.parent.mkdir(parents=True,exist_ok=True);frame.save(target)
 for mirror in ['source/src/img/figs/f625','assets/img/figs/f625']:
  dest=SITE/mirror/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,dest)
 assets.append({'file':file,'source_box':box,'size':frame.size,'panels':panels,'notes':notes+'. Original scene retained in RGBA PNG; no diagram annotations.'})
canvas=Image.new('RGB',(1200,940),'#edf1f5');d=ImageDraw.Draw(canvas)
for i,a in enumerate(assets):
 x=20+(i%4)*300;y=15+(i//4)*310
 frame=Image.open(ROOT/a['file']);frame.thumbnail((265,245));frame=frame.resize((int(frame.width*min(265/frame.width,245/frame.height)),int(frame.height*min(265/frame.width,245/frame.height))),Image.Resampling.NEAREST)
 canvas.paste(frame.convert('RGB'),(x,y+35));d.text((x,y+10),a['file'],fill='#243342')
canvas.save(ROOT/'overview.png')
(ROOT/'manifest.json').write_text(json.dumps({'source':SOURCE,'source_size':im.size,'assets':assets,'frontend':'Panel headings, labels and formulas; selection border; time axes; solid and dashed intervals; unseen future box; now/onset/detected markers; latency arrow; retrieval arrows and saliency curve.'},indent=2)+'\n')
