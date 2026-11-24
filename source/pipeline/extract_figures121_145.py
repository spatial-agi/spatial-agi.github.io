"""Extract reviewable, panel-grouped raster plates for Figures 12.1–14.5.

This is the asset-review step only. All labels, formulas, frames, arrows and
vector diagrams remain for the frontend reconstruction after review.
"""
from pathlib import Path
from html import escape
import json, math, re
import numpy as np
from lxml import etree
import fitz
from PIL import Image, ImageDraw, ImageFont
from extract_figures101_1116 import artwork, STYLE
from extract_figures91_924 import transparent_white

ROOT=Path(__file__).resolve().parents[2]
INV=json.loads((ROOT/'source/pipeline/figures121_145_sources.json').read_text())
BOOK=ROOT.parent/'Spatial_Intelligence_Book_2025_v14/figures/part4'
PLATES={
"12.1": [["perception","brain-anatomy"],["model-and-plan","brain-treatment"],["intervention","tracked-intervention"]],
"12.2": [["segmentation","input-ct"],["detection","input-ct"],["segmentation","segmented-ct"],["segmentation","organ-anatomy"],["detection","roi-ct"],["registration","moving-ct"],["registration","reference-mri"]],
"12.3": [["reconstruction","input-ct"],["reconstruction","volume-ct-layer-1"],["reconstruction","volume-ct-layer-2"],["reconstruction","heart-mesh"],["patient-model","heart-anatomy"],["patient-model","scar-mri"],["patient-model","heart-digital-twin"],["planning","simulated-heart"],["planning","catheter-heart"],["planning","radiotherapy-ct"]],
"12.4": [["anatomical-registration","preoperative-brain"],["anatomical-registration","patient-reference"],["anatomical-registration","registered-brain"],["tracking-guidance","tracked-patient"],["tracking-guidance","ar-intervention"],["endoscopic-geometry","endoscopic-surface"]],
"12.5": [["life-science","protein-structure"],["life-science","tissue-structure"],["life-science","cell"],["life-science","tissue-culture"]],
"12.6": [],"12.7": [],
"12.8": [["reconstruct","protein-structure"],["reconstruct","cryo-em-projection-1"],["reconstruct","cryo-em-projection-2"],["reconstruct","cryo-em-projection-3"],["reconstruct","protein-density"],["interact","binding-surface"],["design","protein-backbone"]],
"13.1": [["inputs","robot-in-living-room"],["outputs","manage-bookshelf"],["outputs","collaborate-with-person"],["outputs","empower-person"]],
"13.2": [["ground-and-act","robot-in-living-room"]],
"13.3": [["proxemic-context","person-and-robot"],["legible-interaction","person-and-robot"]],
"13.4": [["user-needs","vision-support"],["user-needs","mobility-support"]],
"14.1": [["construction-robotics","crane-and-concrete"],["structural-inspection","concrete-pillar"]],
"14.2": [["tracking","soccer-match"],["biomechanics","soccer-player"]],
"14.3": [["digitize","statue"],["digitize","statue-mesh"],["restore","fragment-1"],["restore","fragment-2"],["restore","fragment-3"],["restore","fragment-4"],["restore","fragment-5"],["restore","fragment-6"],["restore","fragment-7"],["restore","fragment-8"],["restore","fragment-9"],["restore","reassembled-mural"],["discover","forest-canopy"]],
"14.4": [["perceive","degraded-coral"],["perceive","enhanced-coral"],["localize","underwater-robot"],["inspect","underwater-inspection"]],
"14.5": [["observations","store-interior"],["checkout","shopper-picks-product"],["shelf-monitoring","product-shelf"]]
}

PHOTOS={('12.1',2),('12.2',0),('12.2',1),('12.2',2),('12.2',4),('12.2',5),('12.2',6),('12.3',0),('12.3',1),('12.3',2),('12.3',5),('12.3',9),('12.4',1),('12.4',3),('12.4',4),('12.4',5),('12.8',1),('12.8',2),('12.8',3),('12.8',5),('13.1',0),('13.2',0),('13.3',0),('13.3',1),('13.4',0),('13.4',1),('14.1',1),('14.2',0),('14.4',0),('14.4',1),('14.4',3),('14.5',1)}


def clip_plate(image, info, svg_image, svg_root):
    """Rasterize the source's polygon clips into the plate's alpha channel."""
    clips=[a.get('clip-path')[5:-1] for a in svg_image.iterancestors() if a.get('clip-path')]
    if not clips:return image
    x0,y0,x1,y1=info['bbox'];ss=2;w,h=image.size
    alpha=np.asarray(image.getchannel('A')).copy()
    for cid in clips:
        mask=Image.new('L',(w*ss,h*ss),0);draw=ImageDraw.Draw(mask)
        for path in svg_root.xpath('//*[@id=$cid]/*',cid=cid):
            data=path.get('d','');tokens=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',data)
            assert set(re.findall(r'[A-Za-z]',data))<=set('MLHVZ'),(cid,data)
            numbers=re.findall(r'[-+]?(?:\d*\.\d+|\d+)',path.get('transform','matrix(1,0,0,1,0,0)'))
            a,b,c,d,e,f=map(float,numbers);points=[];i=0;cmd=None;xx=yy=0
            while i<len(tokens):
                if tokens[i].isalpha():
                    cmd=tokens[i];i+=1
                    if cmd=='Z':break
                if cmd in ('M','L'):
                    xx,yy=float(tokens[i]),float(tokens[i+1]);i+=2
                    if cmd=='M':cmd='L'
                elif cmd=='H':xx=float(tokens[i]);i+=1
                elif cmd=='V':yy=float(tokens[i]);i+=1
                else:raise ValueError((cid,cmd))
                px=a*xx+c*yy+e;py=b*xx+d*yy+f
                points.append(((px-x0)/(x1-x0)*w*ss,(py-y0)/(y1-y0)*h*ss))
            if points:draw.polygon(points,fill=255)
        alpha=np.minimum(alpha,np.asarray(mask.resize((w,h),Image.Resampling.LANCZOS)))
    result=np.asarray(image).copy();result[:,:,3]=alpha
    return Image.fromarray(result,'RGBA')

def make_figure(entry):
    ch,n=entry['chapter'],entry['number'];key=f'{ch}.{n}';fid=f'{ch}{n}'
    pdf=BOOK/f'section{ch}'/(Path(entry['sources'][0]).stem+'.pdf')
    doc=fitz.open(pdf);page=doc[0];infos=page.get_image_info(xrefs=True)
    out=ROOT/f'assets/figures/elements/figure{fid}';out.mkdir(parents=True,exist_ok=True)
    assert len(infos)==len(PLATES[key]),(key,len(infos))
    svg_root=etree.fromstring(page.get_svg_image(text_as_path=False).encode()) if key=='14.3' else None
    svg_images=[im for im in svg_root.xpath('//*[local-name()="image"]') if not any(etree.QName(a).localname=='defs' for a in im.iterancestors())] if svg_root is not None else []
    if svg_root is not None:assert len(svg_images)==len(infos)
    entries=[];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    for i,info in enumerate(infos):
        # PDF image placements often include tiny clipping masks/texture tiles;
        # retain only meaningful plates that can be reviewed as visual elements.
        box=info['bbox'];w,h=box[2]-box[0],box[3]-box[1]
        if w<8 or h<8 or w*h<120:continue
        im=artwork(doc,info).convert('RGBA')
        panel,name=PLATES[key][i]
        kind='photo' if (key,i) in PHOTOS else 'cutout'
        if kind=='cutout':im=transparent_white(im)
        if svg_root is not None:im=clip_plate(im,info,svg_images[i],svg_root)
        filename=f'{panel}/{name}.png'
        for base in (out,ROOT/f'source/src/img/figs/f{fid}',ROOT/f'assets/img/figs/f{fid}'):
            dest=base/filename;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
        entries.append(dict(file=filename,title=name.replace('-',' '),panel=panel,size=list(im.size),
            source_index=0,pdf_image_index=i,pdf_box=[round(v*1000/page.rect.width,3) for v in box],pdf_source_box=[round(v,3) for v in box],kind=kind))
        print(f'{key} {filename}: {im.size}',flush=True)
    notes=['Extracted raster artwork is saved as individual PNG plates, grouped by the source figure’s semantic panels. Photo interiors are retained; cutouts have transparent exterior backgrounds.',
      'All text, formulas, labels, symbols, arrows, borders and vector diagram elements are reserved for independent frontend drawing.',
      'Only directional arrows will receive the approved white light core and soft blue halo animation. Separators, borders and checkmarks remain static.',
      'After asset review, rebuild the source figure in the frontend with region-level keyboard and pointer interaction, white-mask focus and English popovers.']
    if not entries:notes.insert(0,'This source figure is entirely vector artwork; no raster plates are embedded. Every diagram element should be rebuilt independently in the frontend.')
    manifest=dict(figure=key,sources=entry['sources'],source_sizes=[list(Image.open(ROOT/entry['sources'][0]).size)],source_pdf=str(pdf.relative_to(ROOT.parent)),assets=entries,frontend=notes)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Transparent checkerboard asset review cards.
    cols=4;cw,chh=300,280;rows=max(1,math.ceil(len(entries)/cols))
    sheet=Image.new('RGB',(cols*cw,rows*chh),'#eef2f6');draw=ImageDraw.Draw(sheet)
    cards=[]
    for k,a in enumerate(entries):
        x=k%cols*cw;y=k//cols*chh;draw.text((x+8,y+7),a['panel']+' · '+a['title'],font=font,fill='#273640')
        for yy in range(y+42,y+268,12):
            for xx in range(x+8,x+292,12):draw.rectangle((xx,yy,xx+11,yy+11),fill='#e3e9ef' if (xx//12+yy//12)%2 else 'white')
        pic=Image.open(out/a['file']).convert('RGBA');pic.thumbnail((274,214));sheet.paste(pic,(x+(cw-pic.width)//2,y+45+(214-pic.height)//2),pic)
        cards.append(f'<article><h3>{escape(a["file"])}</h3><div class="checker"><img src="/assets/figures/elements/figure{fid}/{a["file"]}" alt="{escape(a["title"])}"></div><p>{a["size"][0]} × {a["size"][1]} · PNG</p></article>')
    if not entries:
        draw.text((20,12),f'Figure {key}: vector artwork (no embedded raster assets)',font=font,fill='#273640')
        original_plate=Image.open(ROOT/entry['sources'][0]).convert('RGB');original_plate.thumbnail((1130,215))
        sheet.paste(original_plate,((1200-original_plate.width)//2,48))
    sheet.save(out/'overview.png')
    original=''.join(f'<img class="original" src="/{s}" alt="Original Figure {key}">' for s in entry['sources'])
    (ROOT/f'example/figure{fid}-assets.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure '+key+' asset review</title><style>'+STYLE+'</style><main><nav><a href="/example/figures121-145-assets.html">All target figures</a></nav><h1>Figure '+key+' · Asset review</h1><section><h2>Original</h2>'+original+'</section><section><h2>'+str(len(entries))+' independent PNG assets</h2><div class="grid">'+''.join(cards)+'</div></section><section><h2>Frontend reconstruction</h2><ul>'+''.join('<li>'+escape(note)+'</li>' for note in notes)+'</ul></section></main></html>')
    return manifest

def main():
    manifests=[make_figure(e) for e in INV];total=sum(len(m['assets']) for m in manifests)
    sections=[];nav=[]
    for m in manifests:
        key=m['figure'];fid=key.replace('.','');count=len(m['assets']);nav.append(f'<a href="#f{fid}">{key}</a>')
        desc=f'{count} raster assets extracted' if count else 'Vector-only figure · no raster assets'
        sections.append(f'<section id="f{fid}"><h2><a href="/example/figure{fid}-assets.html">Figure {key} · '+desc+f'</a></h2><a href="/example/figure{fid}-assets.html"><img class="overview" loading="lazy" src="/assets/figures/elements/figure{fid}/overview.png" alt="Extracted assets for Figure {key}"></a></section>')
    (ROOT/'example/figures121-145-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 12.1–14.5 · Asset review</title><style>{STYLE}</style><main><h1>Figures 12.1–14.5 · Asset review</h1><p class="note">{total} individual PNG assets across 17 figures. Review these pictorial plates before frontend reconstruction. Text, formulas, labels, arrows, borders and vector diagram elements remain independent frontend elements.</p><nav>{"".join(nav)}</nav>{"".join(sections)}</main></html>')
    print('TOTAL',total,flush=True)
if __name__=='__main__':main()
