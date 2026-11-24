"""Figure 7.23 photographic plates and separate object cutouts, in source pixels."""
from pathlib import Path
import json
from html import escape
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = 'assets/figures/figures/part3/section7/chain-of-thought_spatial_reasoning.webp'
ASSETS = [
    ('b-visual/scene.png','Visual reasoning scene',(744,95,1249,340),'scene'),
    ('c-embodied/kitchen.png','Kitchen scene',(1380,120,1656,398),'scene'),
    ('b-visual/white-cube.png','White cube',(769,150,875,269),'white-cube'),
    ('b-visual/red-cube.png','Red cube',(893,155,990,268),'red-cube'),
    ('b-visual/green-sphere.png','Green sphere',(1007,151,1120,265),'green'),
    ('b-visual/white-cylinder.png','White cylinder',(1131,139,1228,267),'cylinder'),
    ('c-embodied/blue-mug.png','Blue mug',(1587,237,1631,275),'mug'),
]


def restore_scene(original):
    """Remove the blue annotation; interpolate only its narrow occluded strip."""
    a=np.asarray(original).astype(float).copy()
    roi=a[149:274,887:997]
    r,g,b=roi[:,:,0],roi[:,:,1],roi[:,:,2]
    mask=(b>135)&(b>r*1.2)&(b>g*1.12)
    mask=ndimage.binary_dilation(mask,iterations=1)
    nearest=ndimage.distance_transform_edt(mask,return_distances=False,return_indices=True)
    roi[mask]=roi[tuple(nearest)][mask]
    # Harmonic interpolation avoids retaining a blue edge in the repaired plate.
    for _ in range(350):
        mean=ndimage.convolve(roi,np.array([[0,1,0],[1,0,1],[0,1,0]])[:,:,None]/4,mode='nearest')
        roi[mask]=mean[mask]
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))


def extract(im,bounds,kind):
    crop=im.crop(bounds).convert('RGBA')
    if kind=='scene': return crop
    w,h=crop.size
    scale=4
    alpha=Image.new('L',(w*scale,h*scale))
    d=ImageDraw.Draw(alpha)
    def polygon(points):
        d.polygon([((x-bounds[0])*scale,(y-bounds[1])*scale) for x,y in points],fill=255)
    if kind=='white-cube':
        polygon([(771,175),(789,152),(872,153),(872,241),(863,265),(773,266)])
    elif kind=='red-cube':
        polygon([(894,174),(904,156),(988,157),(986,265),(895,265)])
    elif kind=='cylinder':
        polygon([(1133,150),(1224,150),(1225,251),(1219,260),(1197,265),(1166,264),(1141,259),(1133,251)])
        d.ellipse(((1133-bounds[0])*scale,(141-bounds[1])*scale,(1225-bounds[0])*scale,(162-bounds[1])*scale),fill=255)
    elif kind=='green':
        # Trace the silhouette, retaining the dark brown-green shadow on the left.
        polygon([(1062,153),(1077,155),(1091,160),(1103,170),(1111,183),
                 (1116,198),(1117,214),(1113,230),(1106,244),(1093,255),
                 (1077,261),(1061,263),(1045,260),(1031,253),(1019,241),
                 (1012,226),(1009,210),(1011,194),(1017,179),(1027,166),
                 (1043,157)])
    elif kind=='mug':
        p=np.asarray(crop).astype(float)
        r,g,b=p[:,:,0],p[:,:,1],p[:,:,2]
        mask=(b>r*1.25)&(b>g*1.08)
        labels,n=ndimage.label(mask)
        sizes=np.bincount(labels.ravel());sizes[0]=0
        mask=labels==sizes.argmax()
        alpha=Image.fromarray((mask*255).astype('uint8'))
        crop.putalpha(alpha)
        return crop
    crop.putalpha(alpha.resize((w,h),Image.Resampling.LANCZOS))
    return crop


def main():
    original=Image.open(ROOT/SOURCE).convert('RGB')
    repaired=restore_scene(original)
    entries=[]
    overview=Image.new('RGB',(1400,1000),'#f3f5f7')
    d=ImageDraw.Draw(overview)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    for i,(file,title,bounds,kind) in enumerate(ASSETS):
        asset=extract(repaired,bounds,kind)
        for base in [OUT,ROOT/'source/src/img/figs/f723',ROOT/'assets/img/figs/f723']:
            dest=base/file;dest.parent.mkdir(parents=True,exist_ok=True);asset.save(dest)
        entries.append(dict(file=file,title=title,source_box=bounds,size=list(asset.size),kind=kind))
        if i<2: x,y,w,h=i*700,0,700,460
        else: x,y,w,h=((i-2)%3)*466,460+((i-2)//3)*270,466,270
        d.text((x+20,y+12),title,font=font,fill='#29353b')
        for yy in range(y+50,y+h-10,16):
            for xx in range(x+15,x+w-15,16):
                d.rectangle((xx,yy,xx+15,yy+15),fill='#e4e9ed' if (xx//16+yy//16)%2 else 'white')
        ratio=min((w-65)/asset.width,(h-80)/asset.height)
        thumb=asset.resize((round(asset.width*ratio),round(asset.height*ratio)),Image.Resampling.LANCZOS)
        overview.paste(thumb,(x+(w-thumb.width)//2,y+55+(h-80-thumb.height)//2),thumb)
    overview.save(OUT/'overview.png')
    notes=[
        '(a): all labels, A/B/C circles, directional arrows, compass and answer will be drawn independently in the frontend.',
        '(b): the blue selection rectangle has been removed from the photographic plate; its narrow occluded strips are locally interpolated. The rectangle will be drawn independently.',
        '(c): preserve the kitchen photograph and provide the blue mug as a separate transparent cutout.',
        'CoT, ToT, GoT, PoT and CoA: all nodes, boxes, arrows, text and formulas will be independent frontend elements.',
        'Scene plates preserve source backgrounds and shadows. Separate object cutouts have transparent backgrounds and retain source shading.',
    ]
    (OUT/'manifest.json').write_text(json.dumps(dict(figure='7.23',source=SOURCE,source_size=list(original.size),assets=entries,frontend=notes),indent=2)+'\n')
    def cards(items):
        return ''.join(f'<article><h3>{escape(e["title"])}</h3><div class="checker"><img src="/assets/figures/elements/figure723/{e["file"]}" alt="{escape(e["title"])}"></div><p>{e["size"][0]} × {e["size"][1]} · RGBA PNG</p></article>' for e in items)
    template=(ROOT/'example/figure722-assets.html').read_text()
    style=template.split('<style>')[1].split('</style>')[0]
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.23 · Asset review</title><style>'+style+'</style><main><h1>Figure 7.23 · Extracted assets</h1><section><h2>Original</h2><img class="original" src="/'+SOURCE+'" width="2000" height="1124" alt="Original Figure 7.23"></section><section><h2>Scene plates</h2><p>The blue annotation is removed for independent frontend drawing.</p><div class="grid scenes">'+cards(entries[:2])+'</div></section><section><h2>Separate objects</h2><div class="grid">'+cards(entries[2:])+'</div></section><section><h2>Independent frontend elements — next step</h2><ul>'+''.join('<li>'+escape(v)+'</li>' for v in notes)+'</ul></section></main></html>'
    (ROOT/'example/figure723-assets.html').write_text(page)
    print('Created seven PNG assets, source/served mirrors, manifest and review page.')


if __name__=='__main__': main()
