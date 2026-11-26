"""Extract Figure 6.2's four panel images as separate transparent PNGs."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SRC=SITE/'assets/figures/figures/part3/section6/segmentation.webp'
src=Image.open(SRC).convert('RGB')
# Four matching card images, excluding their caption lines.
boxes={
 'raw':(22,308,459,590),
 'semantic':(525,308,962,590),
 'instance':(1042,308,1479,590),
 'panoptic':(1545,308,1982,590),
}
records=[]
for name,box in boxes.items():
 arr=np.asarray(src.crop(box));lo=arr.min(2)
 # Remove only the near-white page outside the rounded panel; preserve white masks inside it.
 alpha=np.clip((250-lo)*42,0,255).astype('uint8')
 alpha[lo<242]=255
 rgba=np.dstack((arr,alpha));out=Image.fromarray(rgba,'RGBA')
 p=ROOT/(name+'.png');out.save(p)
 records.append(dict(file=p.name,source_box=box,size=list(out.size)))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SRC.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
sheet=Image.new('RGB',(1200,380),'#e2e7ec');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 x=10+i*297;d.rounded_rectangle((x,10,x+285,370),8,fill='#fafafa',outline='#b8c2cb')
 im=Image.open(ROOT/r['file']);im.thumbnail((265,300),Image.Resampling.LANCZOS);sheet.paste(im,(x+10,18),im)
 d.text((x+12,333),r['file'].replace('.png',''),font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
for r in records:
 im=Image.open(ROOT/r['file']);assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
print('Verified',len(records),'transparent panel assets')
