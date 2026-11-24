"""Extract the two VLA scenes and their separate photographic object cutouts."""
from pathlib import Path
from html import escape
import json
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = 'assets/figures/figures/part3/section7/VLA_spatial_reasoning.webp'
ASSETS = [
    ('i-inputs/initial-scene.png', 'Initial scene', (42,265,488,689), 'scene'),
    ('iii-execution/result-scene.png', 'Resulting scene', (1562,452,1900,777), 'scene'),
    ('i-inputs/robot-arm.png', 'Initial robot arm', (64,265,378,554), 'arm-initial'),
    ('i-inputs/red-block.png', 'Initial red block', (280,515,357,588), 'red'),
    ('i-inputs/blue-block.png', 'Initial blue block', (380,514,458,588), 'blue'),
    ('iii-execution/robot-arm.png', 'Resulting robot arm', (1562,452,1819,675), 'arm-result'),
    ('iii-execution/red-block.png', 'Stacked red block', (1774,614,1836,666), 'red'),
    ('iii-execution/blue-block.png', 'Stacked blue block', (1774,654,1836,706), 'blue'),
]


def cutout(original, bounds, kind):
    crop = original.crop(bounds)
    pixels = np.asarray(crop).astype(float)
    red, green, blue = pixels[:,:,0], pixels[:,:,1], pixels[:,:,2]
    if kind in ('red', 'blue'):
        if kind == 'red':
            mask = (red>green*1.4) & (red>blue*1.4) & (red>65)
        else:
            mask = (blue>red*1.4) & (blue>green*1.15) & (blue>55)
        # Retain the source RGB, including the different shading on each face.
        alpha = Image.fromarray((mask*255).astype('uint8'))
    else:
        # Remove only exterior white, preserving white robot surfaces and metal highlights.
        white = np.min(pixels,axis=2)>247
        labels, _ = ndimage.label(white)
        outside = np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]))
        outside = outside[outside!=0]
        alpha = Image.fromarray((~np.isin(labels,outside)*255).astype('uint8'))
        if kind.startswith('arm'):
            if kind == 'arm-initial':
                polygon = [(64,265),(378,265),(378,507),(177,507),(177,522),
                           (190,529),(190,540),(177,545),(153,550),(125,553),
                           (93,551),(71,547),(64,542)]
            else:
                polygon = [(1562,452),(1819,452),(1819,608),(1644,608),
                           (1644,648),(1658,654),(1658,663),(1647,668),
                           (1628,672),(1606,674),(1580,672),(1562,668)]
            shape = Image.new('L',crop.size)
            ImageDraw.Draw(shape).polygon([(x-bounds[0],y-bounds[1]) for x,y in polygon],fill=255)
            alpha = Image.fromarray(np.minimum(np.asarray(alpha),np.asarray(shape)))
    rgba = crop.convert('RGBA')
    rgba.putalpha(alpha)
    return rgba


def main():
    original = Image.open(ROOT/SOURCE).convert('RGB')
    entries = []
    overview = Image.new('RGB',(1400,1100),'#f3f5f7')
    d = ImageDraw.Draw(overview)
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    for i,(file,title,bounds,kind) in enumerate(ASSETS):
        rgba = cutout(original,bounds,kind)
        for base in [OUT,ROOT/'source/src/img/figs/f722',ROOT/'assets/img/figs/f722']:
            destination = base/file
            destination.parent.mkdir(parents=True,exist_ok=True)
            rgba.save(destination)
        entries.append(dict(file=file,title=title,source_box=bounds,size=list(rgba.size),kind=kind))
        if i<2:
            x,y,w,h=i*700,0,700,450
        else:
            x,y,w,h=((i-2)%3)*466,450+((i-2)//3)*325,466,325
        d.text((x+20,y+15),title,fill='#29353b',font=font)
        for yy in range(y+55,y+h-10,16):
            for xx in range(x+20,x+w-20,16):
                d.rectangle((xx,yy,xx+15,yy+15),fill='#e4e9ed' if (xx//16+yy//16)%2 else 'white')
        scale=min((w-70)/rgba.width,(h-80)/rgba.height)
        enlarged=rgba.resize((round(rgba.width*scale),round(rgba.height*scale)),Image.Resampling.LANCZOS)
        overview.paste(enlarged,(x+(w-enlarged.width)//2,y+60+(h-80-enlarged.height)//2),enlarged)
    overview.save(OUT/'overview.png')
    notes = [
        'Embodied inputs: draw the instruction, robot-state box, state formula, optional depth / 3D / keypoint text, and input arrows independently.',
        'VLA policy: draw fusion, autoregressive action boxes, diffusion circles and formulas, hybrid decoder, RL refinement, and every arrow independently.',
        'Action and execution: draw the action representation and formula, controller, planner, and environment-feedback loop independently.',
        'Complete scene plates preserve the original tabletop, object contact, and photographic shadows. Individual robot and block cutouts are also provided for finer interaction.',
    ]
    (OUT/'manifest.json').write_text(json.dumps(dict(figure='7.22',source=SOURCE,source_size=list(original.size),assets=entries,frontend=notes),indent=2)+'\n')
    def cards(items):
        return ''.join(f'<article><h3>{escape(e["title"])}</h3><div class="checker"><img src="/assets/figures/elements/figure722/{e["file"]}" alt="{escape(e["title"])}"></div><p>{e["size"][0]} × {e["size"][1]} · transparent PNG</p></article>' for e in items)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.22 · Asset review</title><style>body{margin:24px;background:#f3f5f7;color:#29353b;font:16px/1.6 Arial}main{max-width:1600px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{display:block;width:100%;height:auto}h1{font-size:25px}h2{font-size:20px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.scenes{grid-template-columns:repeat(2,minmax(0,1fr))}.checker{height:280px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e4e9ed 0 25%,white 0 50%) 0/32px 32px}.scenes .checker{height:380px}.checker img{max-width:94%;max-height:95%;object-fit:contain;width:auto;height:auto}li{margin:12px 0}@media(max-width:600px){body{margin:12px}section{padding:12px}.grid{grid-template-columns:1fr}.scenes .checker{height:310px}}</style><main><h1>Figure 7.22 · Extracted assets</h1><section><h2>Original</h2><img class="original" src="/'''+SOURCE+'''" width="2000" height="1047" alt="Original Figure 7.22"></section><section><h2>Initial and resulting scenes</h2><p>Photographic scene plates retain the source appearance and shadows; diagram annotations are excluded.</p><div class="grid scenes">'''+cards(entries[:2])+'''</div></section><section><h2>Separate robots and blocks</h2><div class="grid">'''+cards(entries[2:])+'''</div></section><section><h2>Independent frontend elements — next step</h2><ul>'''+''.join('<li>'+escape(v)+'</li>' for v in notes)+'''</ul></section></main></html>'''
    (ROOT/'example/figure722-assets.html').write_text(page)
    print('Created eight transparent PNGs, source/served mirrors, manifest and asset review.')


if __name__=='__main__':
    main()
