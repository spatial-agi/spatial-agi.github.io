from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_fill_holes, binary_dilation, label
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

src=Image.open('assets/figures/figures/part2/3D_representations_2.webp').convert('RGB')
root=Path('assets/figures/elements/3D_representations_2')
records=[]

def repair(im,lines):
    maskim=Image.new('L',im.size); d=ImageDraw.Draw(maskim)
    for coords,width in lines: d.line(coords,fill=255,width=width)
    mask=np.array(maskim)>0
    a=np.array(im,dtype=float); gray=a @ np.array([.299,.587,.114])
    yy,xx=np.where(mask); ids=np.full(mask.shape,-1,int); ids[yy,xx]=np.arange(len(yy))
    M=lil_matrix((len(yy),len(yy))); b=np.zeros(len(yy))
    for k,(y,x) in enumerate(zip(yy,xx)):
        neighbors=[(v,u) for v,u in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=v<mask.shape[0] and 0<=u<mask.shape[1]]
        M[k,k]=len(neighbors)
        for v,u in neighbors:
            if mask[v,u]: M[k,ids[v,u]]=-1
            else:b[k]+=gray[v,u]
    gray[yy,xx]=spsolve(M.tocsr(),b)
    a[mask]=gray[mask,None]
    return Image.fromarray(np.uint8(np.clip(a,0,255)))

def extract(section,name,box,polygon=None,lines=None,threshold=242):
    im=src.crop(box)
    if lines: im=repair(im,lines)
    arr=np.array(im); dark=arr.min(axis=2)<threshold
    if polygon:
        poly=Image.new('L',im.size);ImageDraw.Draw(poly).polygon([(x-box[0],y-box[1]) for x,y in polygon],fill=255)
        dark &= np.array(poly)>0
    labs,n=label(dark)
    sizes=np.bincount(labs.ravel()); keep=sizes>=4;keep[0]=False;dark=keep[labs]
    # Preserve enclosed whites and shaded interiors while clearing the outer paper.
    opaque=binary_fill_holes(dark)
    if name in ('raster-projected-splats','raster-depth-splats'):
        cc,n=label(opaque); counts=np.bincount(cc.ravel()); counts[0]=0; opaque=cc==counts.argmax()
    edge=binary_dilation(opaque,iterations=1)&~opaque
    alpha=opaque.astype(np.uint8)*255
    alpha[edge]=np.clip((255-arr.min(axis=2)[edge])*10,0,255).astype(np.uint8)
    if polygon: alpha[np.array(poly)==0]=0
    out=im.convert('RGBA'); out.putalpha(Image.fromarray(alpha))
    bb=out.getchannel('A').getbbox()
    if not bb:raise ValueError(name)
    out=out.crop(bb); canvas=Image.new('RGBA',(out.width+16,out.height+16));canvas.alpha_composite(out,(8,8))
    dest=root/section/(name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)
    records.append({'file':str(dest.relative_to(root)),'source_box':box,'size':canvas.size,'repaired':bool(lines)})
    return canvas

# (b) The bounding box and enlargement leaders cross the large teapot.
extract('b','gaussian-teapot',(674,56,1048,282),polygon=[(675,90),(750,80),(807,57),(849,57),(857,75),(914,87),(939,107),(950,148),(970,142),(995,95),(1017,82),(1044,82),(1045,92),(1027,103),(1008,151),(1000,185),(979,217),(956,237),(930,255),(906,273),(861,278),(810,279),(771,270),(738,252),(712,221),(698,195),(684,173),(676,138),(676,111)],lines=[([(214,102),(271,102),(271,149),(214,149),(214,102)],13), ([(214,149),(80,235)],13), ([(270,149),(303,242)],13)])
extract('b','gaussian-detail',(678,350,844,582))
extract('b','gaussian-detail-top',(695,350,831,453),polygon=[(697,433),(699,416),(710,398),(731,379),(756,363),(782,355),(807,353),(820,359),(827,371),(827,387),(819,406),(804,423),(783,438),(756,448),(731,450),(710,447)])
extract('b','gaussian-detail-small',(678,453,770,524),polygon=[(681,508),(684,498),(695,485),(712,473),(731,462),(749,456),(760,456),(765,461),(761,472),(750,486),(731,501),(711,513),(693,519),(684,518)])
extract('b','gaussian-detail-large',(740,434,845,580),polygon=[(745,552),(744,530),(750,506),(759,483),(774,460),(792,443),(809,437),(824,440),(835,453),(840,473),(839,495),(832,520),(820,543),(806,562),(789,574),(772,576),(756,570)])
extract('b','raster-gaussian-primitives',(1128,146,1205,241))
extract('b','raster-projected-splats',(1264,146,1315,232))
extract('b','raster-depth-splats',(1138,331,1187,401))
extract('b','raster-depth-stack',(1246,305,1298,409))
extract('b','raster-blend-stack',(1136,484,1199,573))
extract('b','raster-render-teapot',(1253,501,1323,556))
# (c) Keep the tetrahedral cage and the intrinsic surface triangulation.
extract('c','tetrahedral-grid-teapot',(1418,90,1653,277))
extract('c','triangle-mesh-teapot',(1436,363,1628,491))
extract('c','render-teapot',(1480,562,1548,614))
# The two pictured feature planes and their independent sampled feature vectors.
extract('c','triplane-xy',(1699,103,1776,252),polygon=[(1702,144),(1772,106),(1772,206),(1702,246)],lines=[([(39,67),(78,73)],7), ([(37,69),(36,149)],7)])
extract('c','triplane-xz',(1887,103,1966,252),polygon=[(1891,106),(1962,145),(1962,246),(1891,206)],lines=[([(0,73),(39,67)],7), ([(39,69),(39,149)],7)])
for name,box in [('feature-xy',(1727,278,1749,345)),('feature-yz',(1821,278,1842,345)),('feature-xz',(1917,278,1938,345))]:
    extract('c',name,box)
(root/'bc-assets.json').write_text(json.dumps(records,indent=2)+'\n')
# Contact sheet for review only; final assets stay separate.
thumbs=[]
for rec in records:
    im=Image.open(root/rec['file']); im.thumbnail((250,180))
    tile=Image.new('RGB',(280,220),'#e7ebef');tile.paste(im,((280-im.width)//2,8),im);ImageDraw.Draw(tile).text((8,195),rec['file'],fill='black');thumbs.append(tile)
sheet=Image.new('RGB',(280*4,220*((len(thumbs)+3)//4)),'white')
for i,t in enumerate(thumbs):sheet.paste(t,((i%4)*280,(i//4)*220))
sheet.save('/tmp/f43bc-contact.png')
print('Saved',len(records),'transparent PNG assets.')
