"""Extract pictorial coordinate-system icons from Figure 6.8."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/camera-1.webp'
src=Image.open(SOURCE).convert('RGB')
SPECS=[('icons/world-axes',(104,130,240,238)),('icons/camera-axes',(510,130,650,238)),('icons/image-plane-axes',(890,135,1065,238)),('icons/pixel-axes',(1300,135,1470,238))]
def ink(im):
    out=Image.new('RGBA',im.size)
    # Recover dark ink, excluding the original colored card background.
    out.putdata([(0,0,0,max(0,min(255,round((110-min(p))*255/110)))) for p in im.getdata()])
    return out
records=[]
for name,box in SPECS:
    im=ink(src.crop(box)); path=ROOT/(name+'.png'); path.parent.mkdir(parents=True,exist_ok=True); im.save(path)
    records.append({'file':name+'.png','source_box':box,'size':list(im.size)})
(ROOT/'manifest.json').write_text(json.dumps({'source':str(SOURCE.relative_to(SITE)),'notes':'Icons only; colored cards, labels, formulas and arrows are frontend primitives.','assets':records},indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
sheet=Image.new('RGB',(1000,300),'#e2e7ec'); d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    x=12+i*246; y=12; d.rounded_rectangle((x,y,x+230,y+270),8,fill='white',outline='#bac4ce')
    im=Image.open(ROOT/r['file']); im.thumbnail((204,190),Image.Resampling.LANCZOS); sheet.paste(im,(x+(230-im.width)//2,y+12),im); d.text((x+12,y+226),r['file'],font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
print('Saved',len(records),'Figure 6.8 icon assets.')
