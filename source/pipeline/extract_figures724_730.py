"""Reproducible asset-only preparation for Figures 7.24–7.30.

Photographic plates retain original shadows and visible occlusions. Text, graph
nodes, frames, arrows and formulas are reserved for independent frontend drawing.
"""
from pathlib import Path
from html import escape
import json
import sys
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
SOURCE_DIR='assets/figures/figures/part3/section7/'


def item(file,title,box,kind='scene',polygon=None):
    return dict(file=file,title=title,source_box=box,kind=kind,polygon=polygon)


FIGURES={
    724: dict(source='code_DSL_spatial_reasoning.webp',title='Code / DSL spatial reasoning',assets=[
        item('i-understanding/scene.png','Understanding scene',(40,154,605,428)),
        item('i-planning/initial-scene.png','Planning: initial scene',(33,608,334,896),'exterior'),
        item('iii-result/result-scene.png','Planning: resulting scene',(1522,606,1816,888),'exterior'),
        item('i-understanding/white-cube.png','White cube',(69,217,187,348),'polygon',[(71,243),(94,219),(184,219),(184,323),(175,346),(72,345)]),
        item('i-understanding/red-cube.png','Red cube',(207,217,317,348),'polygon',[(208,243),(218,219),(313,219),(310,345),(209,345)]),
        item('i-understanding/green-sphere.png','Green sphere',(335,218,460,343),'polygon',[(397,219),(414,222),(430,229),(445,243),(454,260),(457,279),(455,298),(447,315),(433,330),(416,338),(397,341),(378,337),(361,329),(348,316),(340,300),(337,280),(340,261),(348,243),(361,229),(378,222)]),
        item('i-understanding/white-cylinder.png','White cylinder',(475,205,576,348),'cylinder'),
        item('i-planning/robot-arm.png','Initial robot arm',(49,608,263,808),'arm',[(49,608),(263,608),(263,772),(111,772),(111,787),(124,791),(124,799),(103,805),(72,805),(49,800)]),
        item('i-planning/red-block.png','Initial red block',(194,780,246,828),'red'),
        item('i-planning/blue-block.png','Initial blue block',(263,780,314,828),'blue'),
        item('iii-result/robot-arm.png','Resulting robot arm',(1535,606,1746,800),'arm',[(1535,606),(1746,606),(1746,747),(1595,747),(1595,779),(1610,784),(1610,792),(1590,798),(1556,798),(1535,793)]),
        item('iii-result/red-block.png','Stacked red block',(1708,747,1759,791),'red'),
        item('iii-result/blue-block.png','Stacked blue block',(1708,785,1759,825),'blue'),
    ],notes=[
        'Understanding: restore the blue selection rectangle independently; draw the request, code, perception API and result as frontend elements.',
        'Planning: draw code, instruction, result labels, arrows and the execution-feedback loop independently.',
        'Complete scene plates preserve contact shadows; cutouts preserve source shading and visible occlusion.'
    ]),
    725: dict(source='tool_augmented_spatial_reasoning.webp',title='Tool-augmented spatial reasoning',assets=[
        item('i-scene/workspace.png','Tool-use workspace',(29,305,553,771),'exterior'),
        item('i-scene/cabinet.png','Cabinet, visible portion',(32,369,384,554),'polygon',[(33,391),(331,370),(377,383),(366,409),(360,448),(350,463),(351,501),(371,510),(372,518),(83,551),(53,551),(35,538)]),
        item('i-scene/robot-arm.png','Robot arm, visible portion',(350,307,553,568),'arm',[(350,454),(365,427),(365,410),(378,394),(400,368),(421,345),(425,327),(438,312),(459,308),(482,312),(504,333),(522,360),(535,397),(550,425),(552,465),(543,490),(543,518),(551,531),(551,568),(469,548),(469,526),(478,512),(477,482),(471,458),(460,437),(450,419),(434,408),(413,425),(411,448),(420,464),(414,503),(401,509),(394,500),(394,480),(377,476),(371,500),(358,504),(353,493)]),
        item('i-scene/large-blue-cube.png','Larger blue cube',(288,529,382,630),'blue'),
        item('i-scene/small-blue-cube.png','Smaller blue cube',(424,561,476,616),'blue'),
    ],notes=[
        'Remove the solid cube box and dashed compartment box from the scene; draw both as independent frontend rectangles.',
        'The cabinet and robot retain their original visible occlusions. No hidden geometry has been invented.',
        'Rebuild all four tool-role diagrams, labels, formulas, boxes and return/STOP arrows in the frontend.'
    ]),
    726: dict(source='retrieval_memory_augmented_spatial_reasoning.webp',title='Retrieval and memory-augmented reasoning',assets=[
        item('i-inputs/kitchen-past.png','Kitchen: five minutes ago',(36,249,276,490)),
        item('i-inputs/hallway-now.png','Hallway: current observation',(314,249,554,490)),
        item('iii-evidence/kitchen-evidence.png','Retrieved kitchen evidence',(1400,753,1604,957)),
        item('i-inputs/kitchen-keys.png','Kitchen keys and blue fob',(79,376,237,450),'keys-kitchen'),
        item('i-inputs/hallway-keys.png','Hallway keys and blue fob',(423,383,522,435),'keys-hallway'),
    ],notes=[
        'Photographs are separate assets; keys and fobs are additionally available as transparent cutouts.',
        'Vector stores, spatial graphs, RAG branches, memory layers, timelines and every label/arrow/formula will be frontend elements.'
    ]),
    727: dict(source='agentic_spatial_reasoning.webp',title='Agentic spatial reasoning',assets=[
        item('i-inputs/hallway.png','Hallway and keys observation',(116,206,430,521)),
        item('i-inputs/keys.png','Keys and blue fob',(258,382,387,448),'keys-agent'),
    ],notes=[
        'The hallway observation and its keys are the photographic assets.',
        'Draw the perceive/reason/act/reflect loop, skill cards, state sequence and four supporting-mechanism panels independently.',
        'The closed / unlocked / open sequence consists of diagram boxes, not photographic frames.'
    ]),
    728: dict(source='world_model_based_spatial_reasoning.webp',title='World-model-based spatial reasoning',assets=[
        item('i-query/initial-scene.png','Initial observation',(18,138,312,418),'exterior'),
        item('a-observations/frame-t.png','Imagined frame at t',(26,775,217,956),'exterior'),
        item('a-observations/frame-t1.png','Imagined frame at t+1',(283,775,473,956),'exterior'),
        item('i-query/robot-arm.png','Initial robot arm',(35,138,240,331),'arm',[(35,138),(240,138),(240,295),(96,295),(96,309),(110,314),(110,321),(89,327),(57,327),(35,323)]),
        item('i-query/red-block.png','Initial red block',(175,304,226,351),'red'),
        item('i-query/blue-block.png','Initial blue block',(242,304,293,351),'blue'),
        item('a-observations/robot-t.png','Imagined robot at t',(37,775,173,901),'arm',[(37,775),(173,775),(173,876),(79,876),(79,888),(88,891),(88,896),(76,900),(54,900),(37,896)]),
        item('a-observations/red-t.png','Red block at t',(128,880,161,913),'red'),
        item('a-observations/blue-t.png','Blue block at t',(172,880,204,913),'blue'),
        item('a-observations/robot-t1.png','Imagined robot at t+1',(293,775,428,899),'arm',[(293,775),(428,775),(428,864),(333,864),(333,884),(344,887),(344,893),(330,897),(310,897),(293,894)]),
        item('a-observations/red-t1.png','Red block at t+1',(403,866,436,893),'red'),
        item('a-observations/blue-t1.png','Blue block at t+1',(403,890,436,917),'blue'),
    ],notes=[
        'Initial and imagined scenes preserve the source photographs; robots and blocks are also separate cutouts.',
        'Scene geometry, future-state blocks, trajectory branches, latent vectors, formulas and all prediction/feedback arrows will be frontend elements.'
    ]),
    729: dict(source='foundation_rl_hybrid.webp',title='Foundation model and RL hybrid',assets=[
        item('rl-controller/robot-icon.png','RL controller icon',(112,63,245,183),'icon'),
        item('hypothesis/brain-icon.png','Hypothesis generator icon',(917,54,1057,193),'icon'),
        item('verification/gears-icon.png','Verifier gears icon',(1724,54,1861,190),'icon'),
    ],notes=[
        'Keep the three source line-art icons as individual transparent PNGs.',
        'Draw all rounded boxes, mathematical module labels, bidirectional exchanges and dashed reward/verification links independently.'
    ]),
    730: dict(source='agentic_hybrid_orchestration.webp',title='Agentic hybrid orchestration',assets=[
        item('perception/eye-icon.png','Perception icon',(213,107,379,263),'icon'),
        item('hypothesis/brain-icon.png','Hypothesis generator icon',(909,202,1092,385),'icon'),
        item('world/cube-icon.png','World model icon',(1631,140,1800,309),'icon'),
        item('symbolic/hierarchy-icon.png','Symbolic solver icon',(219,675,372,817),'icon'),
        item('action/robot-arm-icon.png','Action executor icon',(943,780,1092,943),'icon'),
        item('memory/database-icon.png','Spatial memory icon',(1628,681,1797,850),'icon'),
    ],notes=[
        'Keep all six source pictograms as separate transparent PNGs.',
        'Draw the six module frames, all module labels/formulas, two-way connectors and outer perceive/reason/act/reflect loop independently.'
    ]),
}


def repair_rectangle(im,box,full_band=False):
    """Interpolate only blue annotation pixels in narrow rectangle-edge bands."""
    a=np.asarray(im).astype(float).copy()
    x0,y0,x1,y1=box
    left,top,right,bottom=x0-9,y0-9,x1+10,y1+10
    roi=a[top:bottom,left:right]
    yy,xx=np.mgrid[top:bottom,left:right]
    edges=((abs(xx-x0)<=4)|(abs(xx-x1)<=4)|(abs(yy-y0)<=4)|(abs(yy-y1)<=4))
    r,g,b=roi[:,:,0],roi[:,:,1],roi[:,:,2]
    mask=edges&(b>120)&(b>r*1.2)&(b>g*1.1)
    if full_band:
        mask=(abs(xx-x0)<=6)|(abs(xx-x1)<=6)|(abs(yy-y0)<=6)|(abs(yy-y1)<=6)
    mask=ndimage.binary_dilation(mask,iterations=1)
    indices=ndimage.distance_transform_edt(mask,return_distances=False,return_indices=True)
    roi[mask]=roi[tuple(indices)][mask]
    kernel=np.array([[0,1,0],[1,0,1],[0,1,0]])[:,:,None]/4
    for _ in range(450):
        mean=ndimage.convolve(roi,kernel,mode='nearest');roi[mask]=mean[mask]
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))


def polygon_alpha(size,points,origin):
    alpha=Image.new('L',(size[0]*4,size[1]*4))
    ImageDraw.Draw(alpha).polygon([((x-origin[0])*4,(y-origin[1])*4) for x,y in points],fill=255)
    return alpha.resize(size,Image.Resampling.LANCZOS)


def keys_alpha(im,kind,box):
    """Manual silhouettes preserve metal teeth; blue fobs use source chroma."""
    x0,y0,x1,y1=box
    # Outline coordinates are relative to the full source image.
    if kind=='keys-kitchen':
        points=[(81,434),(115,409),(116,401),(125,392),(141,388),(155,390),(165,395),(170,402),(164,411),(155,415),(143,440),(137,448),(131,446),(132,438),(137,428),(138,419),(129,419),(93,439),(82,441)]
        ring=(143,377,188,412)
    elif kind=='keys-hallway':
        points=[(424,423),(447,405),(448,399),(455,393),(466,391),(478,395),(482,403),(475,409),(468,410),(458,431),(453,434),(450,432),(451,426),(457,412),(450,411),(430,426),(424,427)]
        ring=(460,384,489,407)
    else:
        points=[(259,431),(287,410),(287,404),(297,395),(310,391),(324,394),(337,400),(338,411),(331,417),(322,418),(310,442),(304,447),(297,445),(298,438),(304,425),(306,419),(297,418),(269,435),(260,436)]
        ring=(309,383,345,413)
    alpha=polygon_alpha(im.size,points,(x0,y0))
    hi=alpha.resize((im.width*4,im.height*4),Image.Resampling.NEAREST)
    dr=ImageDraw.Draw(hi)
    r=[(ring[0]-x0)*4,(ring[1]-y0)*4,(ring[2]-x0)*4,(ring[3]-y0)*4]
    # Keep only the exposed upper ring arc; the lower arc is behind the heads.
    dr.arc(r,175,365,fill=255,width=3*4)
    alpha=np.asarray(hi.resize(im.size,Image.Resampling.LANCZOS)).copy()
    p=np.asarray(im).astype(float);r,g,b=p[:,:,0],p[:,:,1],p[:,:,2]
    blue=(b>r*1.15)&(b>g*1.03)&(b>40)
    blue=ndimage.binary_fill_holes(blue)
    alpha=np.maximum(alpha,(blue*255).astype('uint8'))
    return Image.fromarray(alpha)


def extract(im,spec):
    box=spec['source_box'];kind=spec['kind']
    crop=im.crop(box).convert('RGBA');p=np.asarray(crop)[:,:,:3].astype(float)
    if kind=='scene':return crop
    if kind=='icon':
        # The original pictograms are black: encode their antialiasing as alpha.
        alpha=255-np.min(p,axis=2)
        alpha[alpha<5]=0
        clean=Image.new('RGBA',crop.size,(0,0,0,0))
        clean.putalpha(Image.fromarray(alpha.astype('uint8')))
        return clean
    if kind.startswith('keys-'):
        crop.putalpha(keys_alpha(crop,kind,box));return crop
    if kind in ('red','blue','green'):
        r,g,b=p[:,:,0],p[:,:,1],p[:,:,2]
        if kind=='red':mask=(r>g*1.35)&(r>b*1.3)&(r>60)
        elif kind=='blue':mask=(b>r*1.35)&(b>g*1.13)&(b>50)
        else:mask=(g>r*1.01)&(g>b*1.01)&(g>30)
        labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0
        mask=ndimage.binary_fill_holes(labels==sizes.argmax())
        # Retain dark sphere shading by taking the convex hull of its silhouette.
        if kind=='green':
            from scipy.spatial import ConvexHull
            y,x=np.where(mask);hull=ConvexHull(np.column_stack([x,y]))
            alpha=Image.new('L',crop.size);ImageDraw.Draw(alpha).polygon([(int(x[i]),int(y[i])) for i in hull.vertices],fill=255)
        else:alpha=Image.fromarray((mask*255).astype('uint8'))
    elif kind=='polygon':alpha=polygon_alpha(crop.size,spec['polygon'],box)
    elif kind=='cylinder':
        alpha=Image.new('L',(crop.width*4,crop.height*4));d=ImageDraw.Draw(alpha)
        w,h=alpha.size
        d.rectangle((4,40,w-8,h-44),fill=255)
        d.ellipse((4,0,w-8,88),fill=255);d.ellipse((4,h-88,w-8,h-4),fill=255)
        alpha=alpha.resize(crop.size,Image.Resampling.LANCZOS)
    else:
        white=np.min(p,axis=2)>247
        labels,n=ndimage.label(white)
        outside=np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]));outside=outside[outside!=0]
        alpha=Image.fromarray((~np.isin(labels,outside)*255).astype('uint8'))
        if kind=='arm':
            alpha=Image.fromarray(np.minimum(np.asarray(alpha),np.asarray(polygon_alpha(crop.size,spec['polygon'],box))))
            if box==(350,307,553,568):
                r,g,b=p[:,:,0],p[:,:,1],p[:,:,2]
                wood=(r>b*1.25)&(g>b*1.1)
                yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]]
                outside=((xx<385)&(yy>420))|(yy>525)
                clean=np.asarray(alpha).copy();clean[wood&outside]=0;alpha=Image.fromarray(clean)
    crop.putalpha(alpha);return crop


STYLE='''body{margin:24px;background:#f3f5f7;color:#29353b;font:16px/1.6 Arial}main{max-width:1600px;margin:auto}section{background:white;padding:20px;margin:24px 0}h1{font-size:25px}h2{font-size:20px}h3{font-size:17px}.original{display:block;width:100%;height:auto}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.checker{height:260px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e4e9ed 0 25%,white 0 50%) 0/32px 32px}.checker img{max-width:94%;max-height:94%;object-fit:contain;width:auto;height:auto}nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#3046c9}li{margin:10px 0}.badge{color:#475867}article{min-width:0}p{overflow-wrap:anywhere}@media(max-width:700px){body{margin:12px}section{padding:12px}.grid{grid-template-columns:1fr}.checker{height:290px}}'''


def make_figure(num):
    data=FIGURES[num];source=SOURCE_DIR+data['source']
    im=Image.open(ROOT/source).convert('RGB')
    if num==724:im=repair_rectangle(im,(209,228,317,354))
    if num==725:
        im=repair_rectangle(im,(68,366,209,518),True);im=repair_rectangle(im,(289,526,382,628))
        # The dashed box crossed empty white above the cabinet. Restore that
        # known exterior directly rather than interpolating wood into it.
        p=np.asarray(im).copy();yy,xx=np.mgrid[0:im.height,0:im.width]
        exterior=(xx>=58)&(xx<=218)&(yy>=354)&(yy<391-(xx-33)*21/298)
        p[exterior]=255;im=Image.fromarray(p)
    out=ROOT/f'assets/figures/elements/figure{num}';out.mkdir(parents=True,exist_ok=True)
    entries=[];n=len(data['assets']);rows=(n+2)//3
    overview=Image.new('RGB',(1500,rows*350),'#f3f5f7');d=ImageDraw.Draw(overview)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    for i,spec in enumerate(data['assets']):
        asset=extract(im,spec)
        for base in [out,ROOT/f'source/src/img/figs/f{num}',ROOT/f'assets/img/figs/f{num}']:
            dest=base/spec['file'];dest.parent.mkdir(parents=True,exist_ok=True);asset.save(dest)
        entry={k:v for k,v in spec.items() if v is not None};entry['size']=list(asset.size);entries.append(entry)
        x=(i%3)*500;y=(i//3)*350
        d.text((x+16,y+12),spec['title'],font=font,fill='#29353b')
        for yy in range(y+50,y+336,16):
            for xx in range(x+14,x+486,16):d.rectangle((xx,yy,xx+15,yy+15),fill='#e4e9ed' if (xx//16+yy//16)%2 else 'white')
        ratio=min(440/asset.width,270/asset.height)
        thumb=asset.resize((round(asset.width*ratio),round(asset.height*ratio)),Image.Resampling.LANCZOS)
        overview.paste(thumb,(x+(500-thumb.width)//2,y+55+(270-thumb.height)//2),thumb)
    overview.save(out/'overview.png')
    (out/'manifest.json').write_text(json.dumps(dict(figure=f'7.{num-700}',source=source,source_size=list(im.size),assets=entries,frontend=data['notes']),indent=2)+'\n')
    (out/'extract.py').write_text('"""Run the shared, reproducible Figure 7.24–7.30 asset extractor."""\nfrom pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[4]\nsys.path.insert(0,str(ROOT/"source/pipeline"))\nfrom extract_figures724_730 import make_figure\nif __name__=="__main__": make_figure('+str(num)+')\n')
    cards=''.join(f'<article><h3>{escape(e["title"])}</h3><div class="checker"><img src="/assets/figures/elements/figure{num}/{e["file"]}" width="{e["size"][0]}" height="{e["size"][1]}" alt="{escape(e["title"])}"></div><p>{e["size"][0]} × {e["size"][1]} · RGBA PNG</p></article>' for e in entries)
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.{num-700} · Asset review</title><style>{STYLE}</style><main><nav><a href="/example/figures724-730-assets.html">All seven figures</a></nav><h1>Figure 7.{num-700} · {escape(data["title"])}</h1><section><h2>Original</h2><img class="original" src="/{source}" width="{im.width}" height="{im.height}" alt="Original Figure 7.{num-700}"></section><section><h2>Extracted assets · {len(entries)} PNGs</h2><div class="grid">{cards}</div></section><section><h2>Independent frontend elements — next step</h2><ul>'+''.join('<li>'+escape(v)+'</li>' for v in data['notes'])+'</ul></section></main></html>'
    (ROOT/f'example/figure{num}-assets.html').write_text(page)
    print(f'Figure 7.{num-700}: {len(entries)} assets')
    return overview


def main():
    requested=[int(a) for a in sys.argv[1:]] or list(FIGURES)
    for num in requested:make_figure(num)
    cards=''
    total=0
    summary=Image.new('RGB',(1600,2200),'#f3f5f7');d=ImageDraw.Draw(summary)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
    for i,(num,data) in enumerate(FIGURES.items()):
        overview=ROOT/f'assets/figures/elements/figure{num}/overview.png'
        if not overview.exists():continue
        n=len(data['assets']);total+=n
        cards+=f'<section id="f{num}"><h2><a href="/example/figure{num}-assets.html">Figure 7.{num-700} · {escape(data["title"])}</a></h2><p class="badge">{n} separate PNG assets · click the title for the original and individual assets</p><a href="/example/figure{num}-assets.html"><img class="original" src="/assets/figures/elements/figure{num}/overview.png" alt="Figure 7.{num-700} asset overview"></a></section>'
        x=(i%2)*800;y=(i//2)*550
        d.text((x+15,y+12),f'Figure 7.{num-700} · {n} assets',font=font,fill='#29353b')
        thumb=Image.open(overview);thumb.thumbnail((775,490));summary.paste(thumb,(x+(800-thumb.width)//2,y+50))
    summary.save(ROOT/'example/figures724-730-assets-overview.jpg',quality=92)
    nav=''.join(f'<a href="#f{num}">7.{num-700}</a>' for num in FIGURES)
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 7.24–7.30 · Asset review</title><style>{STYLE}</style><main><h1>Figures 7.24–7.30 · Asset review</h1><p>{total} separately saved PNG assets, grouped by figure and panel. Text, formulas, frames, graph schematics and arrows are reserved for frontend reconstruction.</p><nav>{nav}</nav>{cards}</main></html>'
    (ROOT/'example/figures724-730-assets.html').write_text(page)
    print(f'Total: {total} assets; batch overview and seven original/asset review pages.')


if __name__=='__main__':main()
