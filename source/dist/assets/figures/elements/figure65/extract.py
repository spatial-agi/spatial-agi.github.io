"""Extract Figure 6.5 photos; all text, frames, grids and graph lines stay native."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SOURCE=SITE/'assets/figures/figures/part3/section6/scene_classification.webp'
src=Image.open(SOURCE).convert('RGB')
SPECS=[
    ('tasks/single-label-kitchen',(12,23,415,324)),
    ('tasks/multi-label-kitchen',(478,23,880,324)),
    ('tasks/farmland',(946,24,1191,192)),
    ('tasks/highway',(1238,24,1482,192)),
    ('tasks/forest',(946,231,1191,400)),
    ('tasks/animal',(1238,231,1482,400)),
    ('tasks/caption-kitchen',(1549,23,1905,289)),
]
records=[]
for name,box in SPECS:
    out=src.crop(box).convert('RGBA')
    path=ROOT/(name+'.png');path.parent.mkdir(parents=True,exist_ok=True);out.save(path)
    records.append(dict(file=name+'.png',source_box=box,size=list(out.size)))
# Both thumbnails reuse the clean kitchen photograph. Recreate only its faded
# background; the original overlapping grids, graph labels and nodes are excluded.
kitchen=src.crop(SPECS[0][1])
for name,box in [('methods/handcrafted-background',(29,590,281,778)),('methods/scene-graph-background',(1251,591,1503,779))]:
    size=(box[2]-box[0],box[3]-box[1])
    photo=kitchen.resize(size,Image.Resampling.LANCZOS)
    out=Image.blend(photo,Image.new('RGB',size,'white'),.62).convert('RGBA')
    path=ROOT/(name+'.png');path.parent.mkdir(parents=True,exist_ok=True);out.save(path)
    records.append(dict(file=name+'.png',source_box=box,size=list(size),restoration='Clean source kitchen resized with a 62% white overlay; diagram annotations removed.'))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
sheet=Image.new('RGB',(1280,975),'#e2e7ec');d=ImageDraw.Draw(sheet)
for i,rec in enumerate(records):
    x,y=12+i%3*423,12+i//3*321
    d.rounded_rectangle((x,y,x+408,y+305),8,fill='#fff',outline='#bac4ce')
    im=Image.open(ROOT/rec['file']);im.thumbnail((380,255),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(408-im.width)//2,y+10+(255-im.height)//2),im)
    d.text((x+12,y+278),rec['file'].removesuffix('.png'),font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
print(f'Saved {len(records)} individual PNG assets')
