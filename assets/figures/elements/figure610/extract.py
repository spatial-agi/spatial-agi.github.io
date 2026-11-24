"""Extract Figure 6.10 photographs without their native diagram annotations."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE/'assets/figures/figures/part3/section6/height_estimation_2.webp'
src = Image.open(SOURCE).convert('RGB')


def restore(box, areas):
    """Remove blue annotations only inside known annotation areas.

    Solve the discrete Laplace equation over each marked pixel, preserving
    surrounding photo pixels. No photographic element is regenerated.
    """
    rgb = np.array(src.crop(box)).astype(float)
    blue = (rgb[:,:,2]-rgb[:,:,0]>35)&(rgb[:,:,2]-rgb[:,:,1]>22)&(rgb[:,:,2]>125)
    allowed = Image.new('L',(rgb.shape[1],rgb.shape[0]))
    d=ImageDraw.Draw(allowed)
    for x0,y0,x1,y1 in areas:
        d.rectangle((x0-box[0],y0-box[1],x1-box[0],y1-box[1]),fill=255)
    mask = binary_dilation(blue&(np.array(allowed)>0),iterations=3)
    ys,xs=np.where(mask)
    indices={(y,x):i for i,(y,x) in enumerate(zip(ys,xs))}
    mat=lil_matrix((len(ys),len(ys)))
    rhs=np.zeros((len(ys),3))
    for i,(y,x) in enumerate(zip(ys,xs)):
        neighbors=[(yy,xx) for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<rgb.shape[0] and 0<=xx<rgb.shape[1]]
        mat[i,i]=len(neighbors)
        for yy,xx in neighbors:
            j=indices.get((yy,xx))
            if j is None: rhs[i]+=rgb[yy,xx]
            else: mat[i,j]=-1
    if len(ys): rgb[ys,xs]=spsolve(mat.tocsr(),rhs)
    return Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA'),mask


records=[]
def save(name,im,box,note):
    p=ROOT/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    for folder in ['source/src/img/figs/f610','assets/img/figs/f610']:
        target=SITE/folder/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    records.append(dict(file=name+'.png',source_box=list(box),size=list(im.size),notes=note))

bbox=(692,189,1308,601)
b,bmask=restore(bbox,[(692,407,1307,421),(815,302,834,551),(1136,338,1154,494),(743,347,803,384),(1177,334,1227,374)])
save('b/street-people-clean',b,bbox,'Full street photograph; height arrows, labels and dashed horizon removed. Small covered photo regions are interpolated locally.')
cbox=(1353,189,1970,601)
c,cmask=restore(cbox,[(1353,189,1970,601)])
# Below the objects, nearby unmarked wood supplies actual grain rather than
# a smoothed interpolation over the former dimension labels.
original=np.array(src.crop(cbox))
arr=np.array(c)
for labelbox in [(1460,525,1540,580),(1735,525,1810,580)]:
    x0,y0,x1,y1=labelbox
    x0-=cbox[0];x1-=cbox[0];y0-=cbox[1];y1-=cbox[1]
    patch=arr[y0:y1,x0:x1]
    donor=original[y0:y1,x0+100:x1+100]
    yy,xx=np.mgrid[:y1-y0,:x1-x0]
    feather=np.clip(np.minimum.reduce([xx,yy,x1-x0-1-xx,y1-y0-1-yy])/7,0,1)[:,:,None]
    patch[:,:,:3]=np.uint8(donor*feather+patch[:,:,:3]*(1-feather))
c=Image.fromarray(arr)
save('c/tabletop-clean',c,cbox,'Full tabletop photograph; blue outlines, corner dots, dimension arrows and labels removed.')

def cutout(name,box,points,note):
    im=c.crop((box[0]-cbox[0],box[1]-cbox[1],box[2]-cbox[0],box[3]-cbox[1]))
    # Supersampled polygon edges preserve smooth transparency around the objects.
    mask=Image.new('L',(im.width*4,im.height*4))
    ImageDraw.Draw(mask).polygon([((x-box[0])*4,(y-box[1])*4) for x,y in points],fill=255)
    im.putalpha(mask.resize(im.size,Image.Resampling.LANCZOS))
    save(name,im,box,note)

cutout('c/reference-card',(1396,396,1576,469),[(1423,399),(1573,399),(1567,464),(1398,464)],'Reference card with chip, isolated on transparency; measurement marks remain native frontend elements.')
cutout('c/target-rectangle',(1599,351,1935,478),[(1612,353),(1888,354),(1931,468),(1912,475),(1602,474),(1601,468)],'Dark target rectangle isolated on transparency; blue border and corner markers removed.')

(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),notes='Panel a is entirely frontend geometry. Scene photographs remain rectangular RGBA assets; two tabletop objects have transparent cutout backgrounds. Rebuild all headings, text, equations, camera icons, triangulation, guide lines, arrows, borders and corner markers independently.',assets=records),indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
sheet=Image.new('RGB',(1240,820),'#e7ecf1');d=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
    x,y=16+(i%2)*612,16+(i//2)*396
    d.rounded_rectangle((x,y,x+596,y+380),10,fill='white',outline='#bac5d0')
    im=Image.open(ROOT/r['file']);im.thumbnail((572,328),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(596-im.width)//2,y+12+(328-im.height)//2),im)
    d.text((x+12,y+349),r['file'],fill='#29343a',font=font)
sheet.save(ROOT/'overview.png')
items=''.join('<article><img src="/assets/figures/elements/figure610/'+r['file']+'"><p>'+r['file']+'</p></article>' for r in records)
(SITE/'example/figure610-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.10 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#263238;margin:24px}main{max-width:1300px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:10px;padding:14px;text-align:center}article img{max-height:360px}p{overflow-wrap:anywhere}@media(max-width:600px){section{grid-template-columns:1fr}}</style><main><h1>Figure 6.10 · extracted pictorial assets</h1><h2>Original</h2><img src="/assets/figures/figures/part3/section6/height_estimation_2.webp"><h2 id="assets">Separated assets</h2><section>'''+items+'''</section></main></html>''')
print('Saved',len(records),'Figure 6.10 PNG assets.')
