"""Extract annotation-free feature diagrams for Figure 7.8 asset review."""
from pathlib import Path
from html import escape
import json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
SITE = OUT.parents[3]
SOURCE = 'assets/figures/figures/part3/section7/implicit_neural_spatial_reasoning_method.webp'
ORIGINAL = Image.open(SITE/SOURCE).convert('RGB')
ASSETS = [
    ('b-attention/features', (544,215,656,332), 'Spatial attention · feature grid'),
    ('b-attention/weights', (693,215,806,332), 'Spatial attention · weights / weighted grid'),
    ('b-pyramid/coarse', (544,541,613,598), 'Feature pyramid · coarse feature map'),
    ('b-pyramid/middle', (525,634,631,691), 'Feature pyramid · middle feature map'),
    ('b-pyramid/fine', (507,733,650,790), 'Feature pyramid · fine feature map'),
    ('c-modulation/features', (1066,522,1203,669), 'FiLM · input feature stack'),
    ('c-modulation/modulated', (1309,522,1445,669), 'FiLM · modulated feature stack'),
    ('d-geometry/part-capsule', (1586,346,1647,407), 'Capsule routing · part pose'),
]

def cutout(box):
    src = ORIGINAL.crop(box)
    result=[]
    for rgb in src.getdata():
        # Unmatte against the white paper, preserving the original grey/blue edges.
        a=255-min(rgb)
        if a<=5:
            result.append((255,255,255,0))
        else:
            result.append((*[max(0,min(255,round(255-(255-c)*255/a))) for c in rgb],a))
    out=Image.new('RGBA',src.size);out.putdata(result);return out

def main():
    entries=[]
    for name,box,title in ASSETS:
        image=cutout(box)
        entry={'file':name+'.png','source_box':box,'title':title,'size':image.size}
        if name.endswith('/weights'):
            entry['placement_boxes']=[box,(846,215,959,332)]
        if name.endswith('/part-capsule'):
            entry['placement_boxes']=[box,(1717,346,1778,407),(1848,346,1909,407)]
        entries.append(entry)
        for folder in (OUT,SITE/'assets/img/figs/f78',SITE/'source/src/img/figs/f78'):
            target=folder/entry['file'];target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
    (OUT/'manifest.json').write_text(json.dumps({
        'source':SOURCE,'source_size':ORIGINAL.size,'assets':entries,
        'frontend':{
            'a-relations':'Object boxes, query, relation function, aggregation text, latent graph nodes and all edges.',
            'b-attention':'Operators, labels, pyramid blocks, lateral and top-down arrows.',
            'c-modulation':'Context and prediction boxes, formula, labels and all arrows.',
            'd-geometry':'Whole capsule box and pose arrow, part-to-whole arrows, equivariance diagram and formulas.',
            'common':'All headings, separators, text, borders and connectors are frontend elements.'
        }
    },indent=2)+'\n')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
    overview=Image.new('RGBA',(1200,620),'#f3f5f7')
    cards=[]
    for i,entry in enumerate(entries):
        card=Image.new('RGBA',(285,294),'white');d=ImageDraw.Draw(card)
        title=entry['title'].replace(' · ','\n')
        d.multiline_text((12,12),title,font=font,fill='#2c373d',spacing=6)
        for y in range(70,270,12):
            for x in range(12,273,12):
                d.rectangle((x,y,min(x+11,272),min(y+11,269)),fill='#e6ebef' if (x//12+y//12)%2 else 'white')
        image=Image.open(OUT/entry['file'])
        scale=min(240/image.width,180/image.height)
        image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
        card.alpha_composite(image,((285-image.width)//2,70+(200-image.height)//2))
        overview.alpha_composite(card,((i%4)*300+7,(i//4)*310+8))
        url='/assets/figures/elements/figure78/'+entry['file']
        cards.append(f'<article><h3>{escape(entry["title"])}</h3><div class="checker"><img src="{url}" alt="{escape(entry["title"])}"></div><p><a href="{url}">Open transparent PNG</a></p></article>')
    overview.convert('RGB').save(OUT/'overview.jpg',quality=94)
    (SITE/'example/figure78-assets.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.8 extracted assets</title>
<style>body{{margin:24px;font:16px Arial;background:#f3f5f7;color:#27343a}}main{{max-width:1400px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px}}h3{{font-size:15px}}.original,.overview{{display:block;width:100%;height:auto;background:white}}.overview{{max-width:1200px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}article{{background:white;padding:12px;border-radius:8px}}.checker{{height:150px;display:grid;place-items:center;background:repeating-conic-gradient(#e6ebef 0% 25%,white 0% 50%) 0/20px 20px}}.checker img{{max-width:95%;height:130px;object-fit:contain}}li,p{{line-height:1.5}}@media(max-width:600px){{body{{margin:12px}}}}</style>
<main><h1>Figure 7.8 · Extracted pictorial assets</h1><h2>Original</h2>
<img class="original" src="/{SOURCE}" width="2000" height="933" alt="Original Figure 7.8">
<h2>Transparent PNG overview</h2><img class="overview" src="/assets/figures/elements/figure78/overview.jpg" alt="Eight isolated feature maps and capsule pose assets">
<details><summary>Inspect 8 individual PNGs</summary><div class="grid">{''.join(cards)}</div></details>
<h2>Frontend reconstruction</h2><ul><li>(a) Relation Network and latent graph: boxes, symbols, graph nodes and edges.</li><li>(b) Operators, pyramid blocks and all lateral / top-down arrows.</li><li>(c) Context and prediction boxes, modulation formula and connectors.</li><li>(d) Whole capsule, routing arrows and equivariance diagram.</li><li>All headings, formulas, borders, dividers and text remain independent frontend elements.</li></ul>
</main></html>''')

if __name__=='__main__':main()
