"""Prepare separately saved pictorial PNGs for Figures 9.1–9.24.

Read clean embedded artwork directly from the source PDFs so source annotations
are not baked into the assets. Apply each PDF image transform (including upside
-down storage and rotated cars). Text, formulas, arrows, borders, plots, graphs,
skeleton diagrams and sensor symbols remain independent frontend primitives.
"""
from pathlib import Path
from html import escape
import json, math
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage, signal

ROOT=Path(__file__).resolve().parents[2]
BOOK=ROOT.parent/'Spatial_Intelligence_Book_2025_v14/figures/part4/section9'
INV=json.loads((ROOT/'source/pipeline/figures91_924_sources.json').read_text())
# Entries follow the source PDF image occurrence order; repeated plates remain
# independently named by their panel so each frontend placement is editable.
PLATES={
1:[('task','robot-and-open-drawer'),('task','mobile-manipulator'),('inputs','rgbd-view'),('inputs','drawer-inset'),('anchors','drawer-and-mug'),('affordances','drawer-and-mug'),('execution','fixed-arm'),('execution','mobile-arm')],
2:[('anchors','view-1'),('anchors','view-2'),('policy','grasp-execution'),('generalization','seen-objects'),('generalization','unseen-objects')],
3:[('representation','drawer-and-mug'),('grasp','before-lift'),('grasp','lifted-mug'),('placement','before-release'),('placement','released-mug'),('tool-use','closed-drawer'),('tool-use','opened-drawer')],
4:[('task','robot-and-drawer'),('canonicalization','rgbd-observation'),('reasoning','drawer-and-mug'),('evaluation','fixed-arm'),('evaluation','mobile-arm')],
5:[('symbolic-planning','collision-check'),('contact','gripper-and-mug')],
6:[],
7:[('sensors','front-camera'),('sensors','side-camera'),('perception','street-scene'),('feedback','vehicle-environment')],
8:[('detection','street-scene'),('pedestrian','crossing-scene')],
9:[('camera','street-observation')],
10:[('sensors','street-observation')],
11:[('sensing','wearable-user'),('haptics','sensor-glove'),('assistance','exoskeleton-user')],
12:[('sensing','imu-user'),('body-model','t-pose')],
13:[],
14:[('interfaces','glove-and-exoskeleton-user'),('feedback','haptic-glove'),('assistance','exoskeleton-user'),('control','mobile-robot')],
15:[('inputs','satellite'),('inputs','airship'),('inputs','quadcopter'),('cross-view','ground-view'),('cross-view','satellite-view'),('outputs','quadcopter')],
16:[('views','ground'),('views','drone-oblique'),('views','satellite-topdown')],
17:[('detection','parking-lot'),('orientation','rotated-car'),('scale','car-large'),('scale','car-medium'),('scale','car-small'),('scale','car-tiny'),('oriented-detection','rotated-car'),('reidentification','person-view-a'),('reidentification','person-view-b'),('tracking','frame-t'),('tracking','frame-t-plus-1')],
18:[('observations','uav-view'),('flight-plan','topdown-building')],
19:[('inputs','warehouse-aisle'),('picking','robot-arm-and-parcel'),('transport','pallet-robot')],
20:[('detection','shelf-scene'),('pose','shelf-scene')],
21:[],22:[],
23:[('grasp','object-candidates'),('grasp','gripper'),('visuomotor','camera-observation'),('visuomotor','execution')],
24:[('sensing','worker'),('behavior','shared-workspace')],
}
PHOTO={(2,0),(2,1),(2,3),(2,4),(7,0),(7,1),(7,2),(7,3),(8,0),(8,1),(9,0),(10,0),(15,3),(15,4),(16,0),(16,1),(16,2),(17,0),(17,7),(17,8),(17,9),(17,10),(18,0),(18,1),(19,0),(23,0)}
FRONTEND={
6:'The staircase, vehicle / steering symbols, labels and explanatory boxes are frontend geometry; no photographic assets are needed.',
13:'Waveforms, body skeletons, graph nodes, forecast poses, temporal tokens and every connector are independent frontend geometry; no raster plates are embedded in this original.',
21:'Sensor symbols, pose graph, warehouse map, trajectory and loop-closure connectors are independent frontend geometry; this source contains no raster plates.',
22:'Fleet / robot symbols, assignment matrices, coordination graphs, routes and schedule blocks are independent frontend geometry; this source contains no raster plates.',
}
STYLE='''body{margin:24px;background:#f3f6f8;color:#273640;font:16px/1.5 Arial}main{max-width:1600px;margin:auto}h1{font-size:25px}h2{font-size:21px}nav{display:flex;gap:12px;flex-wrap:wrap}a{color:#344bc3}section{margin:24px 0;padding:20px;background:white;border-radius:8px}.original{width:100%;height:auto;max-height:850px;object-fit:contain}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}.checker{height:245px;display:flex;align-items:center;justify-content:center;background-color:white;background-image:linear-gradient(45deg,#e3e9ef 25%,transparent 25%),linear-gradient(-45deg,#e3e9ef 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e3e9ef 75%),linear-gradient(-45deg,transparent 75%,#e3e9ef 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}.checker img{max-width:94%;max-height:94%;object-fit:contain}article h3{font-size:15px;overflow-wrap:anywhere}.overview{display:block;width:100%;max-width:1200px;height:auto}.note{padding:14px;background:#eef2ff;border-left:3px solid #5160ce}@media(max-width:600px){body{margin:10px}section{padding:12px}.grid{grid-template-columns:1fr}}'''

def artwork(doc,info):
    xref=info['xref'];pix=fitz.Pixmap(doc,xref)
    if pix.colorspace and pix.colorspace.n>3:pix=fitz.Pixmap(fitz.csRGB,pix)
    mask=next((im[1] for im in doc[0].get_images() if im[0]==xref),0)
    if mask:pix=fitz.Pixmap(pix,fitz.Pixmap(doc,mask))
    raw=Image.frombytes('RGBA' if pix.alpha else 'RGB',(pix.width,pix.height),pix.samples).convert('RGBA')
    a,b,c,d,e,f=info['transform'];box=info['bbox']
    # Preserve native source detail rather than upsampling the website's WebP.
    density=min(raw.width/max(math.hypot(a,b),.01),raw.height/max(math.hypot(c,d),.01))
    w=max(1,round((box[2]-box[0])*density));h=max(1,round((box[3]-box[1])*density))
    det=a*d-b*c;dx=box[0]-e;dy=box[1]-f
    affine=(raw.width*d/det/density,-raw.width*c/det/density,raw.width*(d*dx-c*dy)/det,
            -raw.height*b/det/density,raw.height*a/det/density,raw.height*(-b*dx+a*dy)/det)
    return raw.transform((w,h),Image.Transform.AFFINE,affine,Image.Resampling.BICUBIC)

def transparent_white(image):
    a=np.asarray(image).copy();rgb=a[:,:,:3].astype(float)
    whites=(rgb.min(2)>239)&(a[:,:,3]>0)
    components,_=ndimage.label(whites)
    exterior=np.unique(np.concatenate([components[0],components[-1],components[:,0],components[:,-1]]));exterior=exterior[exterior!=0]
    background=np.isin(components,exterior)
    # Keep internal whites and fine pale parts, and remove only border-connected white.
    alpha=np.clip((255-rgb.min(2))/16,0,1)*255
    a[:,:,3]=np.where(background,np.minimum(a[:,:,3],alpha),a[:,:,3]).astype('uint8')
    return Image.fromarray(a,'RGBA')

def match_box(source,asset,expected):
    """Find this clean plate in the website original, even across PDF revisions.

    The PDFs and served originals sometimes use different whitespace. Record the
    actual website placement using normalized correlation, never silently reuse
    PDF coordinates as website coordinates.
    """
    source=source.convert('RGB');source.thumbnail((800,2000));scale=source.width/1000
    src=np.asarray(source.convert('L'),dtype=float)/255
    # Composite transparency over white for image matching.
    clean=Image.new('RGBA',asset.size,'white');clean.alpha_composite(asset);clean=clean.convert('L')
    integral=np.pad(src,((1,0),(1,0))).cumsum(0).cumsum(1)
    sq=np.pad(src*src,((1,0),(1,0))).cumsum(0).cumsum(1)
    best=None
    target=(expected[2]-expected[0])*scale
    for factor in np.arange(.72,1.281,.02):
        w=max(7,round(target*factor));h=max(7,round(w*clean.height/clean.width))
        if h>=src.shape[0] or w>=src.shape[1]:continue
        template=np.asarray(clean.resize((w,h),Image.Resampling.BILINEAR),dtype=float)/255
        template-=template.mean();norm=np.sqrt((template*template).sum())
        if norm<.01:continue
        corr=signal.fftconvolve(src,template[::-1,::-1],mode='valid')
        sums=integral[h:,w:]-integral[:-h,w:]-integral[h:,:-w]+integral[:-h,:-w]
        sums2=sq[h:,w:]-sq[:-h,w:]-sq[h:,:-w]+sq[:-h,:-w]
        scores=corr/(np.sqrt(np.maximum(sums2-sums*sums/(w*h),0))*norm+1e-8)
        # Repeated source imagery is disambiguated using its intended panel.
        yy,xx=np.ogrid[:scores.shape[0],:scores.shape[1]]
        dist=np.hypot((xx+w/2)/scale-(expected[0]+expected[2])/2,(yy+h/2)/scale-(expected[1]+expected[3])/2)
        rank=scores-.00025*dist
        y,x=np.unravel_index(rank.argmax(),rank.shape);score=float(scores[y,x]);value=float(rank[y,x])
        if best is None or value>best[0]:best=(value,score,(x/scale,y/scale,(x+w)/scale,(y+h)/scale))
    return [round(v,3) for v in best[2]],round(best[1],4)

def make_figure(n):
    entry=INV[n-1];original=Image.open(ROOT/entry['sources'][0]).convert('RGB')
    pdf=BOOK/(Path(entry['sources'][0]).stem+'.pdf');doc=fitz.open(pdf);page=doc[0]
    images=page.get_image_info(xrefs=True);assert len(images)==len(PLATES[n]),(n,len(images),len(PLATES[n]))
    out=ROOT/f'assets/figures/elements/figure9{n}';out.mkdir(exist_ok=True,parents=True)
    entries=[];sc=1000/page.rect.width
    def save(im,panel,name,source_box,**extra):
        filename=f'{panel}/{name}.png'
        for base in [out,ROOT/f'source/src/img/figs/f9{n}',ROOT/f'assets/img/figs/f9{n}']:
            dest=base/filename;dest.parent.mkdir(parents=True,exist_ok=True);im.convert('RGBA').save(dest)
        rec=dict(file=filename,title=name.replace('-',' '),panel=panel,size=list(im.size),source_index=0,source_box=[round(v*original.width/1000,2) for v in source_box],box=source_box,**extra)
        entries.append(rec)
    for i,(info,(panel,name)) in enumerate(zip(images,PLATES[n])):
        im=artwork(doc,info);kind='photo' if (n,i) in PHOTO else 'cutout'
        if kind=='cutout':im=transparent_white(im)
        expected=[v*sc for v in info['bbox']];box,confidence=match_box(original,im,expected)
        save(im,panel,name,box,kind=kind,pdf_image_index=i,pdf_box=[round(v,3) for v in expected],placement_confidence=confidence)
        print(f'9.{n} {panel}/{name}: {im.size}, placement {confidence}',flush=True)
    notes=['Pictorial PNGs come from clean embedded source artwork, without the overlaid figure labels, formulas, frames, arrows or plotted annotations.','All text, formulas, borders, arrows, chart axes, sensor symbols and schematic lines will be separate frontend elements. Formulas use Cambria Math with source-matched italics.','Cutouts use transparent backgrounds; photographs preserve the rectangular scene content. Original placement is recorded in source pixels, separately from PDF placement.']
    if n in FRONTEND:notes.insert(0,FRONTEND[n])
    manifest=dict(figure=f'9.{n}',sources=entry['sources'],source_sizes=[list(original.size)],source_pdf=str(pdf.relative_to(ROOT.parent)),assets=entries,frontend=notes)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'extract.py').write_text('from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[4]\nsys.path.insert(0,str(ROOT/"source/pipeline"))\nfrom extract_figures91_924 import make_figure\nif __name__=="__main__":make_figure('+str(n)+')\n')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
    sheet=Image.new('RGB',(1200,max(1,math.ceil(len(entries)/4))*260),'#eef2f6');draw=ImageDraw.Draw(sheet)
    cards=''
    for i,a in enumerate(entries):
        x=i%4*300;y=i//4*260;draw.text((x+10,y+8),a['file'].replace('.png',''),font=font,fill='#273640')
        for yy in range(y+36,y+250,12):
            for xx in range(x+8,x+292,12):draw.rectangle((xx,yy,xx+11,yy+11),fill='#e3e9ef' if (xx//12+yy//12)%2 else 'white')
        thumb=Image.open(out/a['file']).convert('RGBA');thumb.thumbnail((274,204));sheet.paste(thumb,(x+(300-thumb.width)//2,y+40+(204-thumb.height)//2),thumb)
        cards+=f'<article><h3>{escape(a["file"])}</h3><div class="checker"><img src="/assets/figures/elements/figure9{n}/{a["file"]}" alt="{escape(a["title"])}" loading="lazy"></div><p>{a["size"][0]} × {a["size"][1]} · RGBA PNG</p></article>'
    if not entries:draw.text((24,40),'No raster plates: this diagram will be reconstructed from frontend primitives.',font=font,fill='#273640')
    sheet.save(out/'overview.png')
    original_html=''.join(f'<img class="original" src="/{src}" alt="Original Figure 9.{n}">' for src in entry['sources'])
    (ROOT/f'example/figure9{n}-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 9.{n} asset review</title><style>{STYLE}</style><main><nav><a href="/example/figures91-924-assets.html">All 24 figures</a></nav><h1>Figure 9.{n} · Asset review</h1><section><h2>Original</h2>{original_html}</section><section><h2>{len(entries)} independent PNG assets</h2><div class="grid">{cards}</div></section><section><h2>Frontend drawing · next step</h2><ul>'+''.join(f'<li>{escape(note)}</li>' for note in notes)+'</ul></section></main></html>')
    return manifest

def main():
    manifests=[make_figure(n) for n in range(1,25)]
    total=sum(len(m['assets']) for m in manifests)
    nav=''.join(f'<a href="#f9{n}">9.{n}</a>' for n in range(1,25))
    sections=''
    for n,m in enumerate(manifests,1):
        count=len(m['assets']);note=f'{count} independent PNG assets' if count else FRONTEND[n]
        sections+=f'<section id="f9{n}"><h2><a href="/example/figure9{n}-assets.html">Figure 9.{n} · Original and individual assets</a></h2><p>{note}</p><a href="/example/figure9{n}-assets.html"><img class="overview" loading="lazy" src="/assets/figures/elements/figure9{n}/overview.png" alt="Extracted asset overview for Figure 9.{n}"></a></section>'
    (ROOT/'example/figures91-924-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 9.1–9.24 · Asset review</title><style>{STYLE}</style><main><h1>Figures 9.1–9.24 · Asset review</h1><p class="note">{total} independent PNG assets. Select a figure to compare its original with each clean extracted plate. Text, formulas, frames, arrows and schematic geometry are reserved for frontend reconstruction after asset review.</p><nav>{nav}</nav>{sections}</main></html>')
    print('TOTAL',total,flush=True)
if __name__=='__main__':main()
