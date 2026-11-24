"""Figure 6.6: separate RGB/depth artwork; all diagram primitives stay native."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/depth_estimation_v3.webp'
src=Image.open(SOURCE).convert('RGB')
SPECS=[
    ('inputs/monocular-rgb',(1412,134,1610,233)),
    ('inputs/monocular-depth',(1784,134,1982,233)),
    ('methods/supervised-rgb',(436,663,530,710)),
    ('methods/supervised-depth',(680,663,774,710)),
    ('methods/self-supervised-frame-t',(836,640,970,707)),
    ('methods/self-supervised-frame-next',(1033,640,1167,707)),
    ('methods/foundation-depth',(1870,686,1962,732)),
]
records=[]
for name,box in SPECS:
    im=src.crop(box).convert('RGBA')
    path=ROOT/(name+'.png');path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    records.append(dict(file=name+'.png',source_box=box,size=list(im.size)))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
sheet=Image.new('RGB',(1260,830),'#e2e7ec');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    x,y=12+i%3*416,12+i//3*273
    d.rounded_rectangle((x,y,x+400,y+255),8,fill='#fff',outline='#bac4ce')
    im=Image.open(ROOT/r['file']);im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
    im.thumbnail((374,208),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(400-im.width)//2,y+12+(208-im.height)//2),im)
    # Wrap long filenames across two lines without altering the saved asset name.
    group,name=r['file'].removesuffix('.png').split('/')
    d.text((x+12,y+222),group+' / '+name,font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
print(f'Saved {len(records)} independent PNG assets.')
