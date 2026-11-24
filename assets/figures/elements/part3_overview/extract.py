"""Figure III: extract sketch artwork using a 2000 × 1250 reference coordinate grid."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation,distance_transform_edt
ROOT=Path(__file__).resolve().parent; SITE=ROOT.parents[3]
SRC=SITE/'assets/img/figs/opener-3.webp'; src=Image.open(SRC).convert('RGB'); scale=src.width/2000
records=[]
def extract(name,box,polygon=None,clean=False):
    b=tuple(round(v*scale) for v in box); arr=np.array(src.crop(b)); note=''
    if clean:
        yy,xx=np.indices(arr.shape[:2]);xx=xx/scale+box[0]; yy=yy/scale+box[1]
        r,g,bl=[arr[:,:,i].astype(int) for i in range(3)]
        region=((xx>780)&(xx<1220)&(yy>375)&(yy<665))
        preserve=((xx>915)&(xx<985)&(yy>500)&(yy<575))
        mask=region&~preserve&(bl-r>24)&(bl-g>14)
        mask=binary_dilation(mask,iterations=2)
        indices=distance_transform_edt(mask,return_distances=False,return_indices=True);arr[mask]=arr[tuple(indices[:,mask])]
        note='Blue route removed where practical; its intersections with sketch strokes are locally approximated. Cup and target outline retained.'
    rgb=arr.astype(float);a=255-rgb.min(axis=2);a[a<7]=0
    if polygon:
        mask=Image.new('L',(arr.shape[1],arr.shape[0]));d=ImageDraw.Draw(mask)
        d.polygon([(round((x-box[0])*scale),round((y-box[1])*scale)) for x,y in polygon],fill=255)
        a=np.minimum(a,np.array(mask))
    # Remove neighboring artwork and diagram connectors from the individual assets.
    yy,xx=np.indices(arr.shape[:2]);xx=xx/scale+box[0];yy=yy/scale+box[1]
    r,g,bl=[arr[:,:,i].astype(int) for i in range(3)]
    blue=(bl-r>20)&(bl-g>12)
    if name=='perceive/scene':
        a[blue&~((xx<155)&(yy>570)&(yy<685))]=0
        a[(xx>302)&(yy<856)&(yy>775)]=0
    if name=='perceive/objects':
        a[(xx<235)&(yy>550)]=0
    if name=='perceive/depth':
        a[(xx<337)&(yy>650)]=0
    if name.startswith('generate/motion-frame-'):
        # Inter-frame arrow heads sit clear of each figure's silhouette.
        ranges={1:[(1624,1634)],2:[(1643,1655),(1738,1744)],3:[(1757,1766),(1840,1851)],4:[(1860,1869)]}
        for x0,x1 in ranges[int(name[-1])]:
            a[(xx>=x0)&(xx<=x1)&(yy>757)&(yy<781)]=0
        if name.endswith('-2'):
            a[(xx>1714)&(yy>818)]=0
    if name=='generate/world':
        a[blue&(yy>1060)&(xx<1700)]=0
    color=np.clip(255-(255-rgb)*255/np.maximum(a[:,:,None],1),0,255).astype('uint8')
    im=Image.fromarray(np.dstack((color,a.astype('uint8'))),'RGBA');p=ROOT/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    records.append(dict(file=name+'.png',source_box=list(b),reference_box=box,size=list(im.size),note=note))
extract('perceive/scene',(0,210,475,1038),[(0,210),(188,210),(189,564),(332,644),(332,771),(472,989),(238,1038),(0,990)])
planes=[[(195,320),(302,250),(302,661),(195,590)],[(312,334),(410,268),(410,740),(312,661)],[(420,353),(521,284),(521,799),(420,722)],[(533,353),(631,287),(631,813),(533,741)]]
for name,poly in zip(['objects','depth','relations','motion'],planes):
    extract('perceive/'+name,(min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)),poly)
extract('perceive/motion-sequence',(299,776,595,929),[(300,776),(595,862),(595,929),(300,824)])
extract('reason/room-and-robot',(656,218,1349,1026),clean=True)
extract('generate/image',(1591,217,1929,370))
extract('generate/scene-3d',(1595,372,1921,578))
# Each film frame is saved independently; film perforations and borders will be drawn in SVG.
for i,(x0,x1) in enumerate([(1530,1634),(1640,1740),(1746,1849),(1855,1961)]):
    extract(f'generate/video-frame-{i+1}',(x0,600,x1,669))
for i,(x0,x1) in enumerate([(1530,1634),(1643,1744),(1757,1851),(1860,1968)]):
    extract(f'generate/motion-frame-{i+1}',(x0,699,x1,826))
extract('generate/world',(1542,828,1957,1128))
(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SRC.relative_to(SITE)),reference_size=[2000,1250],assets=records),indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
cw,ch=300,300; rows=(len(records)+4)//5
sheet=Image.new('RGB',(cw*5,ch*rows),'#e1e5e9');d=ImageDraw.Draw(sheet)
for i,item in enumerate(records):
    x=(i%5)*cw;y=(i//5)*ch;d.rounded_rectangle((x+6,y+6,x+294,y+294),10,fill='#f8f8f8',outline='#b6c0c9')
    im=Image.open(ROOT/item['file']);im.thumbnail((270,245),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(cw-im.width)//2,y+12+(245-im.height)//2),im)
    d.text((x+13,y+266),item['file'].replace('.png',''),font=font,fill='#223443')
sheet.save(ROOT/'overview.png')
for item in records:
    im=Image.open(ROOT/item['file']);assert im.mode=='RGBA' and im.getbbox();assert im.getchannel('A').getextrema()[0]==0
print('Saved and verified',len(records),'transparent PNG assets')
