"""Reproducible pictorial extraction for Figure 7.9; annotations stay in the frontend."""
from pathlib import Path
from html import escape
from collections import deque
import json
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
SITE=OUT.parents[3]
SOURCE='assets/figures/figures/part3/section7/explicit_structured_neural_reasoning_task.webp'
ORIGINAL=Image.open(SITE/SOURCE).convert('RGB')

def polygon_crop(box,points):
    scale=3
    mask=Image.new('L',(ORIGINAL.width*scale,ORIGINAL.height*scale))
    ImageDraw.Draw(mask).polygon([(x*scale,y*scale) for x,y in points],fill=255)
    mask=mask.resize(ORIGINAL.size,Image.Resampling.LANCZOS)
    result=ORIGINAL.crop(box).convert('RGBA');result.putalpha(mask.crop(box));return result

def paper_crop(box):
    # Remove exterior white paper, preserving enclosed white regions of the drawing.
    src=ORIGINAL.crop(box);w,h=src.size;pixels=src.load()
    exterior=set();queue=deque()
    def push(x,y):
        if 0<=x<w and 0<=y<h and (x,y) not in exterior and min(pixels[x,y])>=218:
            exterior.add((x,y));queue.append((x,y))
    for x in range(w):push(x,0);push(x,h-1)
    for y in range(h):push(0,y);push(w-1,y)
    while queue:
        x,y=queue.popleft()
        for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):push(x+dx,y+dy)
    out=src.convert('RGBA');alpha=Image.new('L',src.size,255);a=alpha.load()
    for x,y in exterior:a[x,y]=0
    # A short soft edge avoids leaving a white fringe on the silhouette.
    for y in range(h):
        for x in range(w):
            if (x,y) in exterior:continue
            if any((x+dx,y+dy) in exterior for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))):
                a[x,y]=max(0,255-min(pixels[x,y]))
    out.putalpha(alpha);return out

def main():
    specs=[
      ('a-program-vqa/scene','Compositional tabletop scene',(34,163,588,324),[(37,165),(585,165),(585,321),(37,321)]),
      ('a-program-vqa/red-cube-left','Left red cube',(66,217,148,294),[(70,230),(103,220),(141,226),(144,280),(110,290),(73,284)]),
      ('a-program-vqa/red-cube-right','Right red cube',(161,223,240,299),[(165,235),(198,226),(233,236),(234,286),(199,295),(169,284)]),
      ('a-program-vqa/green-sphere','Green sphere',(266,215,353,306),[(271,255),(275,240),(286,226),(301,221),(319,220),(335,228),(345,242),(349,257),(345,276),(333,293),(318,301),(299,300),(283,291),(274,275)]),
      ('a-program-vqa/gray-cylinder','Gray cylinder',(372,173,447,284),[(377,184),(387,179),(407,177),(429,179),(441,184),(441,194),(438,273),(426,278),(408,280),(390,277),(376,271)]),
      ('a-program-vqa/gray-cube','Gray cube',(470,207,556,292),[(476,223),(507,212),(551,220),(548,277),(518,288),(474,279)]),
      ('b-scene-graph/table-scene','Table, chair, cup and book scene',(636,207,923,484),None),
      ('b-scene-graph/cup','Cup',(745,209,802,266),[(749,218),(755,214),(770,213),(784,216),(786,224),(793,223),(799,227),(798,240),(792,246),(785,245),(783,260),(776,263),(757,261),(753,257)]),
      ('b-scene-graph/book','Book',(813,263,893,307),[(819,286),(851,267),(887,272),(887,278),(858,302),(818,295)]),
      ('c-visual-program/zebra','Zebra',(1323,87,1587,278),None),
    ]
    entries=[]
    for name,title,box,points in specs:
        image=polygon_crop(box,points) if points else paper_crop(box)
        entry=dict(file=name+'.png',title=title,source_box=box,size=image.size);entries.append(entry)
        for base in (OUT,SITE/'source/src/img/figs/f79',SITE/'assets/img/figs/f79'):
            target=base/entry['file'];target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
    frontend={
      'a-program-vqa':'Panel border, heading, query, program box, nested program text and answer.',
      'b-scene-graph':'Panel border, heading, query, dashed divider, graph nodes, relation arrows, probabilities and answer.',
      'c-visual-program':'Panel border, heading, code box, code, tool boxes, arrows and final answer.'
    }
    (OUT/'manifest.json').write_text(json.dumps(dict(source=SOURCE,source_size=ORIGINAL.size,assets=entries,frontend=frontend),indent=2)+'\n')
    overview=Image.new('RGBA',(1200,750),'#f3f5f7')
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
    cards=[]
    for i,e in enumerate(entries):
        card=Image.new('RGBA',(285,234),'white');d=ImageDraw.Draw(card);d.text((12,12),e['title'],font=font,fill='#27343a')
        for y in range(42,220,12):
            for x in range(12,273,12):
                d.rectangle((x,y,min(x+11,272),min(y+11,219)),fill='#e6ebef' if (x//12+y//12)%2 else 'white')
        im=Image.open(OUT/e['file']);scale=min(245/im.width,165/im.height)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
        card.alpha_composite(im,((285-im.width)//2,42+(178-im.height)//2))
        overview.alpha_composite(card,((i%4)*300+7,(i//4)*250+8))
        url='/assets/figures/elements/figure79/'+e['file']
        cards.append(f'<article><h3>{escape(e["title"])}</h3><div class="checker"><img src="{url}" alt="{escape(e["title"])}"></div><p><a href="{url}">Open transparent PNG</a></p></article>')
    overview.convert('RGB').save(OUT/'overview.jpg',quality=94)
    notes=''.join(f'<li><strong>{key}</strong>: {value}</li>' for key,value in frontend.items())
    (SITE/'example/figure79-assets.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.9 extracted assets</title><style>
body{{margin:24px;font:16px Arial;background:#f3f5f7;color:#27343a}}main{{max-width:1400px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px}}h3{{font-size:15px}}
.original,.overview{{display:block;width:100%;height:auto;background:white}}.overview{{max-width:1200px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}article{{background:white;padding:12px;border-radius:8px}}
.checker{{height:150px;display:grid;place-items:center;background:repeating-conic-gradient(#e6ebef 0% 25%,white 0% 50%) 0/20px 20px}}.checker img{{max-width:95%;height:130px;object-fit:contain}}li,p{{line-height:1.5}}@media(max-width:600px){{body{{margin:12px}}}}
</style><main><h1>Figure 7.9 · Extracted pictorial assets</h1><h2>Original</h2>
<img class="original" src="/{SOURCE}" width="2000" height="606" alt="Original Figure 7.9">
<h2>Transparent PNG overview</h2><img class="overview" src="/assets/figures/elements/figure79/overview.jpg" alt="Extracted objects, table scene, cup, book and zebra">
<details><summary>Inspect 10 individual PNGs</summary><div class="grid">{''.join(cards)}</div></details>
<h2>Frontend reconstruction</h2><ul>{notes}</ul></main></html>''')

if __name__=='__main__':main()
