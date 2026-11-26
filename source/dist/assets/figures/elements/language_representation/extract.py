"""Extract Figure 4.5 artwork; diagram labels and connectors remain frontend elements."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SRC=SITE/'assets/figures/figures/part2/language_representation.webp'
im=Image.open(SRC).convert('RGB')
records=[]
def save(name,crop,box,matte=True,note=''):
    if matte:
        rgb=np.asarray(crop).astype(float); alpha=255-rgb.min(axis=2); alpha[alpha<5]=0
        color=np.clip(255-(255-rgb)*255/np.maximum(alpha[:,:,None],1),0,255).astype('uint8')
        crop=Image.fromarray(np.dstack((color,alpha.astype('uint8'))),'RGBA')
    else: crop=crop.convert('RGBA')
    p=ROOT/(name+'.png'); p.parent.mkdir(parents=True,exist_ok=True); crop.save(p)
    records.append(dict(file=name+'.png',source_box=box,size=list(crop.size),note=note))
chair=(316,255,408,370)
save('left/chair',im.crop(chair),chair)
lamp=(474,280,545,352)
save('left/lamp',im.crop(lamp),lamp)
table=(416,212,602,419)
crop=im.crop(table); d=ImageDraw.Draw(crop)
d.rectangle((12,12,173,194),fill='white')
# Restore only the short bottom edge hidden by the original blue arrow.
d.rectangle((84,194,104,206),fill='white')
d.line((84,201,104,201),fill=(40,40,40),width=3)
save('left/table',crop,table,note='Lamp and blue arrow removed from the tabletop; the short obscured bottom edge is locally restored.')
board=(1608,201,1986,590)
save('right/board-state',im.crop(board),board,False,'Reference board artwork with grid; coordinate labels excluded. Grid and discs will be independent frontend shapes in the redraw.')
for name,cx,cy in [('white-disc',1727,276),('black-disc',1774,324)]:
    box=(cx-21,cy-21,cx+22,cy+22); tile=im.crop(box).convert('RGBA')
    scale=4; mask=Image.new('L',(43*scale,43*scale)); md=ImageDraw.Draw(mask)
    md.ellipse((2.5*scale,2.5*scale,40*scale,40*scale),fill=255)
    tile.putalpha(mask.resize((43,43),Image.Resampling.LANCZOS))
    save('right/'+name,tile,box,False,'Circular crop of the original piece; edge pixels may retain a slight green board matte.')
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SRC.relative_to(SITE)),assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
sheet=Image.new('RGB',(1050,650),'#e6e9ec'); d=ImageDraw.Draw(sheet)
for i,item in enumerate(records):
    x=(i%3)*350; y=(i//3)*325
    d.rounded_rectangle((x+8,y+8,x+342,y+317),12,fill='#f7f7f7',outline='#b3bcc5')
    a=Image.open(ROOT/item['file']); a.thumbnail((290,260),Image.Resampling.LANCZOS)
    if 'disc' in item['file']: a=a.resize((100,100),Image.Resampling.LANCZOS)
    sheet.paste(a,(x+(350-a.width)//2,y+18+(260-a.height)//2),a)
    d.text((x+18,y+286),item['file'],font=font,fill='#2a343d')
sheet.save(ROOT/'overview.png')
for item in records:
    a=Image.open(ROOT/item['file']); assert a.mode=='RGBA'; assert a.getbbox()
print('Extracted and checked',len(records),'PNG assets')
