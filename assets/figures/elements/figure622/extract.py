"""Recover the shared street frames; tracking annotations belong to frontend geometry."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import shift
from scipy.ndimage import binary_dilation
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = 'assets/figures/figures/part3/section6/object_tracking.webp'
FRAMES = [
    ((24,113,216,403), (690,719,882,1009), (1358,113,1550,403), (51,185,114,351), (73,157,93,187)),
    ((240,113,431,403), (906,719,1097,1009), (1573,113,1764,403), (270,186,333,351), (291,157,311,187)),
    ((455,113,647,403), (1122,719,1314,1009), (1789,113,1981,403), (490,186,553,351), (511,157,531,187)),
]


def align(reference, target):
    """Register repeated inset pixels using only their unannotated top background."""
    a, b = np.asarray(target, dtype=float), np.asarray(reference, dtype=float)
    candidates=[]
    for dy in range(-2,3):
        for dx in range(-2,3):
            error=np.mean((a[5:38,5:-7,:3]-b[5+dy:38+dy,5+dx:b.shape[1]-7+dx,:3])**2)
            candidates.append((error,dy,dx))
    _,dy,dx=min(candidates)
    return Image.fromarray(np.uint8(np.clip(shift(b,(-dy,-dx,0),order=1,mode='nearest'),0,255))), [dx,dy]


def remove_residue(asset, restored):
    """Interpolate tiny blue annotation remnants only within restored strips."""
    a=np.asarray(asset).astype(float)
    r,g,b=a[:,:,:3].transpose(2,0,1)
    mask=(b-g>19)&(b-r>17)&(r>g-24)&(b>110)&(np.asarray(restored)>0)
    mask=binary_dilation(mask,iterations=1)
    coords=list(zip(*np.nonzero(mask)))
    index={pos:i for i,pos in enumerate(coords)}
    if not coords: return asset
    matrix=lil_matrix((len(coords),len(coords)));rhs=np.zeros((len(coords),3))
    h,w=mask.shape
    for i,(y,x) in enumerate(coords):
        neighbors=[(yy,xx) for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)) if 0<=yy<h and 0<=xx<w]
        matrix[i,i]=len(neighbors)
        for pos in neighbors:
            if pos in index:matrix[i,index[pos]]=-1
            else:rhs[i]+=a[pos][:3]
    colors=spsolve(matrix.tocsr(),rhs)
    for pos,c in zip(coords,colors):a[pos][:3]=c
    return Image.fromarray(np.uint8(np.clip(a,0,255)))


def main():
    original=Image.open(SITE/SOURCE).convert('RGBA')
    records=[]
    for i,(box,posebox,maskbox,outline,label) in enumerate(FRAMES):
        asset=original.crop(box)
        pose,pose_shift=align(original.crop(posebox),asset)
        segmentation,seg_shift=align(original.crop(maskbox),asset)
        # The pose panel shows the clean pixels underneath the tracking rectangle.
        # The segmentation panel has no label above the head, exposing that background.
        edge=Image.new('L',asset.size)
        d=ImageDraw.Draw(edge)
        l,t,r,b=outline; x,y=box[:2]
        d.rectangle((l-x-2,t-y-2,r-x+2,b-y+2),outline=255,width=8)
        edge=edge.filter(ImageFilter.GaussianBlur(.35))
        asset=Image.composite(pose,asset,edge)
        tag=Image.new('L',asset.size)
        l,t,r,b=label
        ImageDraw.Draw(tag).rectangle((l-x-2,t-y-2,r-x+2,b-y+2),fill=255)
        tag=tag.filter(ImageFilter.GaussianBlur(.4))
        asset=Image.composite(segmentation,asset,tag)
        restored=Image.fromarray(np.maximum(np.asarray(edge),np.asarray(tag)))
        asset=remove_residue(asset,restored)
        name=f'shared-street/frame-{i:02d}.png'
        dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);asset.save(dest)
        for mirror in ('source/src/img/figs/f622','assets/img/figs/f622'):
            target=SITE/mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,target)
        records.append(dict(file=name,source_box=box,size=asset.size,
            restoration=dict(pose_reference=posebox,segmentation_reference=maskbox,pose_shift=pose_shift,segmentation_shift=seg_shift),
            panels=['a-sot','b-mot','c-mots','e-pose','f-panoptic'],
            notes='RGBA scene photograph. External border, ID label and tracking rectangle removed using repeated source views. The photographic background is retained intentionally.'))
    (ROOT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,source_size=original.size,assets=records,
        frontend='Tracking boxes and IDs; instance and semantic masks; pose joints and skeletons; camera and LiDAR icons; oriented 3D boxes and trajectories; axes; time arrows; borders; all text.'),indent=2)+'\n')
    sheet=Image.new('RGB',(1180,700),'#eef2f6');d=ImageDraw.Draw(sheet)
    title=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',25)
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
    d.text((22,18),'Figure 6.22 - shared original scene assets',font=title,fill='#29343a')
    for i,r in enumerate(records):
        x=22+i*385
        d.rounded_rectangle((x,64,x+365,650),8,fill='white',outline='#ccd4dc')
        im=Image.open(ROOT/r['file']);im.thumbnail((328,500),Image.Resampling.LANCZOS)
        im=im.resize((round(im.width*1.65),round(im.height*1.65)),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+(365-im.width)//2,78),im)
        d.text((x+16,585),f't{i} - frame-{i:02d}.png',font=font,fill='#29343a')
        d.text((x+16,615),'Shared by panels (a), (b), (c), (e), (f)',font=font,fill='#29343a')
    sheet.save(ROOT/'overview.png')
    cards=''.join(f'<article><h3>t<sub>{i}</sub></h3><img src="/assets/figures/elements/figure622/{r["file"]}"><p>{r["file"]}</p></article>' for i,r in enumerate(records))
    (SITE/'example/figure622-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.22 assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1500px;margin:auto}h1{font-size:24px}h2{font-size:19px}.original{width:100%;height:auto;background:white}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:white;border:1px solid #ccd4dc;border-radius:8px;padding:14px;text-align:center}article img{max-width:100%;height:400px;object-fit:contain}p{overflow-wrap:anywhere;line-height:1.6}@media(max-width:650px){body{margin:12px}section{grid-template-columns:1fr}article img{height:340px}}</style><main><h1>Figure 6.22 · extracted original scene assets</h1><h2>Original</h2><img class="original" src="/'''+SOURCE+'''"><h2>Shared street frames · annotations removed</h2><section>'''+cards+'''</section><p>These three photographs are reused across panels (a), (b), (c), (e), and (f). Tracking rectangles and ID labels were restored from repeated views in the original figure. Photographic backgrounds remain intact.</p><p>Panel (d) camera/LiDAR symbols, oriented 3D boxes, trajectories and axes will be drawn independently in the frontend, along with all instance/semantic masks, pose skeletons, labels, arrows and borders.</p></main></html>''')
    print('Saved three shared scene PNG assets, review page, manifest and overview.')


if __name__=='__main__':
    main()
