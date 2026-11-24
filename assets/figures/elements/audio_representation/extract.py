"""Extract Figure 4.6 artwork at source resolution; annotations are rebuilt later."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[3]
SRC=SITE/'assets/figures/figures/part2/audio_representation.webp'
src=Image.open(SRC).convert('RGB'); records=[]
def extract(name,box,clean=False):
    arr=np.array(src.crop(box))
    if clean:
        r,g,b=[arr[:,:,i].astype(int) for i in range(3)]
        yy,xx=np.indices(r.shape); xx=xx+box[0]; yy=yy+box[1]
        if name=='a/head-top':
            region=(abs(yy-(.522*xx+68))<14)|(abs(yy-(1.32*xx-36))<17)
        else:
            region=((abs(xx-722)<11)&(yy<291))|((xx>708)&(xx<766)&(yy>326)&(yy<355))
        mask=region&(b-r>6)&(b-g>2)
        mask=binary_dilation(mask,iterations=2)
        indices=distance_transform_edt(mask,return_distances=False,return_indices=True)
        arr[mask]=arr[tuple(indices[:,mask])]
        # Remove the pale compression halo left around blue annotation strokes.
        halo=region&(arr[:,:,2].astype(int)-arr[:,:,0].astype(int)>3)&(arr.min(axis=2)>185)
        arr[halo]=255
    if name=='a/sound-source':
        arr[65:,65:]=255
        arr[73:,60:]=255
        arr[:,76:]=255
    if name in ('a/head-top','b/head-profile'):
        restored=Image.fromarray(arr); dr=ImageDraw.Draw(restored)
        if name=='a/head-top':
            dr.line([(x-box[0],y-box[1]) for x,y in [(285,235),(291,230),(297,226),(303,223),(309,220)]],fill=(30,30,30),width=2)
        else:
            dr.line([(712-box[0],164-box[1]),(733-box[0],164-box[1])],fill=(30,30,30),width=2)
        arr=np.array(restored)
    rgb=arr.astype(float); alpha=255-rgb.min(axis=2); alpha[alpha<7]=0
    color=np.clip(255-(255-rgb)*255/np.maximum(alpha[:,:,None],1),0,255).astype('uint8')
    im=Image.fromarray(np.dstack((color,alpha.astype('uint8'))),'RGBA')
    p=ROOT/(name+'.png'); p.parent.mkdir(parents=True,exist_ok=True); im.save(p)
    records.append(dict(file=name+'.png',source_box=box,size=list(im.size),annotation_cleanup=clean))
extract('a/head-top',(239,185,486,481),True)
extract('a/sound-source',(70,80,148,156))
extract('b/head-profile',(608,160,910,516),True)
extract('b/sound-source',(678,42,765,116))
extract('c/speaker',(1422,131,1466,190))
extract('c/listener',(1725,151,1779,210))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
sheet=Image.new('RGB',(1080,800),'#e3e7eb'); d=ImageDraw.Draw(sheet)
for i,record in enumerate(records):
    x=(i%3)*360; y=(i//3)*400
    d.rounded_rectangle((x+8,y+8,x+352,y+392),12,fill='#f7f7f7',outline='#b4bdc7')
    im=Image.open(ROOT/record['file']); im.thumbnail((315,325),Image.Resampling.LANCZOS)
    if im.width<100 and im.height<100: im=im.resize((im.width*2,im.height*2),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(360-im.width)//2,y+20+(325-im.height)//2),im)
    d.text((x+18,y+361),record['file'],font=font,fill='#24333e')
sheet.save(ROOT/'overview.png')
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SRC.relative_to(SITE)),assets=records),indent=2))
for record in records:
    im=Image.open(ROOT/record['file']); assert im.mode=='RGBA' and im.getbbox(); assert im.getchannel('A').getextrema()[0]==0
print('Verified 6 nonempty transparent RGBA assets')
