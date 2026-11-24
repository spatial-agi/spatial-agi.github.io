"""Prepare panel-level pictorial PNGs for Figures 10.1–11.16, before redraw.

Use clean source artwork; annotations and vector diagrams stay independent.
The approved Chapter 9 extractor supplies affine image recovery, exterior-white
removal and placement matching against the website's actual original images.
"""
from pathlib import Path
from html import escape
import json, math
import fitz
from PIL import Image, ImageDraw, ImageFont
from extract_figures91_924 import artwork, transparent_white, match_box, STYLE

ROOT=Path(__file__).resolve().parents[2]
INV=json.loads((ROOT/'source/pipeline/figures101_1116_sources.json').read_text())
PLATES={
'10.1':[('registration','table-with-plant-and-mug'),('user','headset-and-pinch')],
'10.2':[('tracking','headset-user'),('mapping','living-room'),('registration','living-room')],
'10.3':[('hand-tracking','hand-observation'),('gaze-and-pinch','pinch-gesture')],
'10.4':[('foveated-rendering','living-room'),('reprojection','earlier-pose-room'),('reprojection','latest-pose-room')],
'10.5':[('experience','dragon-city-scene'),('response','headset-user')],
'10.6':[('geometric-fusion','room-view-1'),('geometric-fusion','room-view-2'),('geometric-fusion','room-view-3'),('appearance-models','novel-view-room'),('visual-positioning','dragon-city-scene')],
'10.7':[('parametric-surface','body-mesh'),('volumetric-capture','point-cloud-person'),('captured-motion','performer'),('avatar-playback','performer')],
'10.8':[('engine-primitives','living-room'),('virtual-production','camera-and-led-wall'),('camera-planning','castle-scene')],
'11.1':[('physical-asset','machine-tool'),('construct','machine-mesh')],
'11.2':[('metric-geometry','closed-cabinet'),('materials','closed-cabinet'),('articulation','open-drawer-cabinet')],
'11.3':[('constructed-model','robot-and-bin'),('observations','robot-and-bin')],
'11.4':[('physical-asset','machine-tool'),('synchronized-twin','machine-mesh')],
'11.5':[],
'11.6':[('crop-mapping','farmland')],
'11.7':[('urban-context','city-model')],
'11.8':[],
'11.9':[('surface-hydrology','river-valley'),('water-quality','lake-and-buoy')],
'11.10':[], '11.11':[],
'11.12':[('sensing','monocular-satellite'),('sensing','multiview-satellite-1'),('sensing','multiview-satellite-2'),('outputs','pose-satellite'),('outputs','semantic-satellite'),('outputs','planetary-rover')],
'11.13':[('monocular-input','satellite'),('pose-estimate','satellite'),('reprojection','satellite')],
'11.14':[('detection','satellite'),('parts-recognition','satellite')],
'11.15':[('coordination','satellite-a'),('coordination','satellite-b'),('coordination','satellite-c'),('coordination','satellite-d'),('coordination','satellite-e'),('coordination','satellite-f')],
'11.16':[('perception','planetary-rover'),('manipulation','planetary-rover')],
}
PHOTOS={('10.3',0),('10.5',0),('10.6',4),('10.8',1),('10.8',2),('11.3',0),('11.3',1),('11.6',0),('11.9',0),('11.9',1)}
VECTOR_NOTES={
'11.5':'Sensor icons, model-family diagrams, output symbols and the globe are vector geometry; reconstruct them as independent frontend elements.',
'11.8':'Heatmaps, contours, land-cover patches, chemistry symbols and ecological gauges are vector artwork, reserved for faithful frontend reconstruction.',
'11.10':'Hazard maps, deformations, flood and fire regions, building footprints and legends are vector artwork, reserved for independent frontend reconstruction.',
'11.11':'Forecast bands, map layers, graph nodes and population symbols are vector artwork, reserved for independent frontend reconstruction.',
}

def make_figure(chapter,number):
    key=f'{chapter}.{number}';fid=f'{chapter}{number}'
    entry=next(e for e in INV if e['chapter']==chapter and e['number']==number)
    original=Image.open(ROOT/entry['sources'][0]).convert('RGB')
    pdf=ROOT.parent/f'Spatial_Intelligence_Book_2025_v14/figures/part4/section{chapter}'/(Path(entry['sources'][0]).stem+'.pdf')
    doc=fitz.open(pdf);page=doc[0];images=page.get_image_info(xrefs=True)
    assert len(images)==len(PLATES[key]),(key,len(images),len(PLATES[key]))
    out=ROOT/f'assets/figures/elements/figure{fid}';out.mkdir(parents=True,exist_ok=True)
    entries=[];scale=1000/page.rect.width
    for i,(info,(panel,name)) in enumerate(zip(images,PLATES[key])):
        im=artwork(doc,info);kind='photo' if (key,i) in PHOTOS else 'cutout'
        if kind=='cutout':im=transparent_white(im)
        expected=[v*scale for v in info['bbox']];box,confidence=match_box(original,im,expected)
        filename=f'{panel}/{name}.png'
        for base in (out,ROOT/f'source/src/img/figs/f{fid}',ROOT/f'assets/img/figs/f{fid}'):
            dest=base/filename;dest.parent.mkdir(parents=True,exist_ok=True);im.convert('RGBA').save(dest)
        entries.append(dict(file=filename,title=name.replace('-',' '),panel=panel,size=list(im.size),source_index=0,
            source_box=[round(v*original.width/1000,2) for v in box],box=box,kind=kind,
            pdf_image_index=i,pdf_box=[round(v,3) for v in expected],placement_confidence=confidence))
        print(f'{key} {filename}: {im.size}, placement {confidence}',flush=True)
    notes=['Clean pictorial artwork is extracted without overlaid labels, formulas, arrows, frames or diagram lines.',
        'All text, formulas, borders, arrows, symbols and vector diagrams remain independent frontend elements. Formulas will use Cambria Math with the original italics.',
        'Cutouts have transparent backgrounds. Photographs retain their original scene content.',
        'Only directional arrows will receive white light cores and soft blue halos. Dividers, borders and checkmarks remain static.']
    if key in VECTOR_NOTES:notes.insert(0,VECTOR_NOTES[key])
    manifest=dict(figure=key,sources=entry['sources'],source_sizes=[list(original.size)],source_pdf=str(pdf.relative_to(ROOT.parent)),assets=entries,frontend=notes)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'extract.py').write_text(f'from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[4]\nsys.path.insert(0,str(ROOT/"source/pipeline"))\nfrom extract_figures101_1116 import make_figure\nif __name__=="__main__":make_figure({chapter},{number})\n')
    sheet=Image.new('RGB',(1200,max(1,math.ceil(len(entries)/4))*280),'#eef2f6');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16);cards=''
    for i,a in enumerate(entries):
        x=i%4*300;y=i//4*280
        draw.text((x+9,y+7),a['panel'],font=font,fill='#273640');draw.text((x+9,y+27),Path(a['file']).stem,font=font,fill='#273640')
        for yy in range(y+52,y+270,12):
            for xx in range(x+8,x+292,12):draw.rectangle((xx,yy,xx+11,yy+11),fill='#e3e9ef' if (xx//12+yy//12)%2 else 'white')
        im=Image.open(out/a['file']).convert('RGBA');im.thumbnail((274,206));sheet.paste(im,(x+(300-im.width)//2,y+56+(206-im.height)//2),im)
        cards+=f'<article><h3>{escape(a["file"])}</h3><div class="checker"><img src="/assets/figures/elements/figure{fid}/{a["file"]}" alt="{escape(a["title"])}" loading="lazy"></div><p>{a["size"][0]} × {a["size"][1]} · RGBA PNG</p></article>'
    if not entries:
        draw.text((24,40),f'Figure {key}: vector artwork',font=font,fill='#273640')
        draw.text((24,80),'No embedded raster plates. Reconstruct maps, charts and symbols independently in the frontend.',font=font,fill='#273640')
    sheet.save(out/'overview.png')
    original_html=''.join(f'<img class="original" src="/{src}" alt="Original Figure {key}">' for src in entry['sources'])
    (ROOT/f'example/figure{fid}-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure {key} asset review</title><style>{STYLE}</style><main><nav><a href="/example/figures101-1116-assets.html">All 24 figures</a></nav><h1>Figure {key} · Asset review</h1><section><h2>Original</h2>{original_html}</section><section><h2>{len(entries)} independent PNG assets</h2><div class="grid">{cards}</div></section><section><h2>Frontend drawing · next step</h2><ul>'+''.join(f'<li>{escape(note)}</li>' for note in notes)+'</ul></section></main></html>')
    return manifest

def main():
    manifests=[make_figure(e['chapter'],e['number']) for e in INV];total=sum(len(m['assets']) for m in manifests)
    nav='';sections=''
    for e,m in zip(INV,manifests):
        key=m['figure'];fid=key.replace('.','');count=len(m['assets']);nav+=f'<a href="#f{fid}">{key}</a>'
        note=f'{count} independent PNG assets' if count else VECTOR_NOTES[key]
        sections+=f'<section id="f{fid}"><h2><a href="/example/figure{fid}-assets.html">Figure {key} · Original and individual assets</a></h2><p>{note}</p><a href="/example/figure{fid}-assets.html"><img class="overview" loading="lazy" src="/assets/figures/elements/figure{fid}/overview.png" alt="Extracted asset overview for Figure {key}"></a></section>'
    (ROOT/'example/figures101-1116-assets.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 10.1–11.16 · Asset review</title><style>{STYLE}</style><main><h1>Figures 10.1–11.16 · Asset review</h1><p class="note">{total} independent PNG assets across 24 figures. Select a figure to compare its original and clean pictorial plates. Labels, formulas, frames, arrows and vector diagrams will be reconstructed after asset review.</p><nav>{nav}</nav>{sections}</main></html>')
    print('TOTAL',total,flush=True)
if __name__=='__main__':main()
