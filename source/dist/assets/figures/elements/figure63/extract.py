"""Extract pictorial assets from Figure 6.3, leaving labels and connectors for HTML."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SRC=SITE/'assets/figures/figures/part3/section6/segmentation-method.webp'
src=Image.open(SRC).convert('RGB')
specs={
 'classical-snake':(30,45,244,270),
 'graph-cuts':(270,75,387,240),
 # Keep the sampling diagrams; the rate labels belong in the front end.
 'dilated-context':(802,112,1122,247),
 # Query tokens and predicted masks are separate pictorial elements.
 'region-queries':(1175,78,1290,114),
 'region-predicted-masks':(1428,67,1490,267),
 # Prompt, input image and output mask are independent of arrows and model box.
 'foundation-prompt':(1560,97,1618,150),
 'foundation-input-image':(1558,194,1635,267),
 'foundation-output-mask':(1866,137,1959,222),
}
records=[]
for name,box in specs.items():
 arr=np.asarray(src.crop(box)).copy()
 lo=arr.min(axis=2)
 alpha=np.clip((250-lo)*42,0,255).astype('uint8');alpha[lo<242]=255
 if name=='region-predicted-masks':
  alpha[:,:18]=0
 out=Image.fromarray(np.dstack((arr,alpha)),'RGBA')
 p=ROOT/(name+'.png');out.save(p)
 records.append(dict(file=p.name,source_box=box,size=list(out.size)))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SRC.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
columns=3;rows=(len(records)+columns-1)//columns;cell_h=325
sheet=Image.new('RGB',(1280,20+rows*cell_h),'#e2e7ec');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 x=10+(i%columns)*423;y=10+(i//columns)*cell_h;d.rounded_rectangle((x,y,x+408,y+310),8,fill='#fafafa',outline='#bac4ce')
 im=Image.open(ROOT/r['file']);im.thumbnail((380,250),Image.Resampling.LANCZOS);sheet.paste(im,(x+14,y+10),im)
 d.text((x+12,y+274),r['file'].replace('.png',''),font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
for r in records:
 im=Image.open(ROOT/r['file']);assert im.mode=='RGBA' and im.getbbox() and im.getchannel('A').getextrema()[0]==0
print('Verified',len(records),'transparent illustrations')
