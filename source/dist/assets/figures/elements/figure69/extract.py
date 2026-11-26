"""Figure 6.9 pictorial assets; all annotations remain frontend primitives."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE/'assets/figures/figures/part3/section6/height_estimation_1.webp'
src = Image.open(SOURCE).convert('RGB')
records = []

def save(name, im, box, note):
    path = ROOT/(name+'.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    records.append(dict(file=name+'.png', source_box=box, size=list(im.size), notes=note))

# The same street appears twice. Recover the horizon stripe from the other
# instance wherever it is free of perspective rays; interpolate only the
# small common vanishing-point mark, rather than repainting the photograph.
a = np.array(src.crop((30,174,647,585))).astype(float)
c = np.array(src.crop((1353,174,1970,585))).astype(float)
def blue(v):
    return (v[:,:,2]>v[:,:,0]*1.3)&(v[:,:,2]>v[:,:,1]*1.2)&(v[:,:,2]>130)
stripe = np.zeros(c.shape[:2],bool)
stripe[190:215] = True
mask = blue(c)&stripe
from scipy.ndimage import binary_dilation
mask = binary_dilation(mask,iterations=2)
clean_a = ~binary_dilation(blue(a),iterations=2)
copy = mask&clean_a
c[copy] = a[copy]
missing = mask&~clean_a
grid_y,grid_x=np.ogrid[:c.shape[0],:c.shape[1]]
# Include the white interior of the original outlined vanishing-point marker.
missing |= (grid_x-299)**2+(grid_y-201)**2 < 15**2
ys,xs = np.where(missing)
lookup = {(y,x):i for i,(y,x) in enumerate(zip(ys,xs))}
mat = lil_matrix((len(ys),len(ys)))
rhs = np.zeros((len(ys),3))
for i,(y,x) in enumerate(zip(ys,xs)):
    neighbors=[(yy,xx) for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<c.shape[0] and 0<=xx<c.shape[1]]
    mat[i,i]=len(neighbors)
    for yy,xx in neighbors:
        j=lookup.get((yy,xx))
        if j is None: rhs[i]+=c[yy,xx]
        else: mat[i,j]=-1
if len(ys):
    c[ys,xs] = spsolve(mat.tocsr(),rhs)
street = Image.fromarray(np.uint8(np.clip(c,0,255))).convert('RGBA')
save('a/street-clean',street,[30,174,647,585],'Shared street photograph restored from both panels; blue rays, label and horizon removed. Reused in panel c.')
save('c/street-clean',street,[1353,174,1970,585],'Same clean street, separately grouped for the horizon panel.')

# Retain the photographed checker patterns; corner dots and outlines are
# separate frontend marks. Polygon masks remove the surrounding white canvas.
boards=[('left',(714,195,858,312),[(721,203),(830,204),(849,292),(740,303)]),
        ('center',(906,171,1076,303),[(914,179),(1067,179),(1067,295),(914,295)]),
        ('right',(1097,198,1271,310),[(1130,206),(1263,210),(1246,302),(1105,292)])]
for name,box,points in boards:
    im=src.crop(box).convert('RGBA')
    alpha=Image.new('L',im.size)
    ImageDraw.Draw(alpha).polygon([(x-box[0],y-box[1]) for x,y in points],fill=255)
    im.putalpha(alpha)
    # Corner marks intrude into the pattern; restore their pixels from the
    # adjacent checker cell while preserving the source's antialiasing.
    arr=np.array(im)
    ink=blue(arr[:,:,:3].astype(float))&(arr[:,:,3]>0)
    for y,x in zip(*np.where(ink)):
        candidates=[]
        for dy,dx in [(0,8),(0,-8),(8,0),(-8,0),(8,8),(-8,-8)]:
            yy,xx=y+dy,x+dx
            if 0<=yy<im.height and 0<=xx<im.width and arr[yy,xx,3]>0 and not ink[yy,xx]: candidates.append(arr[yy,xx,:3])
        if candidates: arr[y,x,:3]=candidates[0]
    save('b/checkerboard-'+name,Image.fromarray(arr),list(box),'Checkerboard only; blue corner dots are redrawn in the frontend.')

(ROOT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(SITE)),notes='Only pictorial assets. Rebuild headings, captions, formulas, dividers, corner dots, camera icons, borders, arrows and pitch geometry natively.',assets=records),indent=2)+'\n')
sheet=Image.new('RGB',(1200,790),'#e7ecf1')
d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
for i,r in enumerate(records):
    x,y=(16+i*592,16) if i<2 else (16+(i-2)*394,438)
    w,h=(576,406) if i<2 else (378,334)
    d.rounded_rectangle((x,y,x+w,y+h),10,fill='white',outline='#bcc6d0')
    im=Image.open(ROOT/r['file'])
    im.thumbnail((w-24,h-54),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(w-im.width)//2,y+12+(h-54-im.height)//2),im)
    d.text((x+12,y+h-32),r['file'],font=font,fill='#263238')
sheet.save(ROOT/'overview.png')
print('Saved',len(records),'Figure 6.9 PNG assets.')
