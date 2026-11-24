"""Figure 7.4 pictorial cutouts; annotations and geometry remain native."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT/'assets/figures/figures/part3/section7/714_constraint.webp'
original = Image.open(SOURCE).convert('RGBA')
ITEMS = [
    ('i-inputs/joint-arm', (20,77,127,156), 'Joint configuration arm'),
    ('i-inputs/pose-left-finger', (32,172,65,237), 'Pose gripper · left finger'),
    ('i-inputs/pose-right-finger', (76,172,105,237), 'Pose gripper · right finger'),
    ('i-constraints/collision-arm', (17,482,118,556), 'Collision avoidance arm'),
    ('i-constraints/reach-arm', (17,553,139,642), 'Reachability arm'),
    ('i-constraints/dynamics-arm', (17,652,128,728), 'Dynamics / limits arm'),
    ('ii-core/ik-reachable-arm', (561,658,674,743), 'IK solver · reachable arm'),
    ('ii-core/ik-infeasible-arm', (775,662,884,743), 'IK solver · infeasible arm'),
    ('ii-core/pick-left-finger', (1051,739,1079,791), 'Pick · left finger'),
    ('ii-core/pick-right-finger', (1081,739,1110,791), 'Pick · right finger'),
    ('ii-core/place-left-finger', (1333,733,1361,786), 'Place · left finger'),
    ('ii-core/place-right-finger', (1364,733,1393,786), 'Place · right finger'),
]

for name, box, title in ITEMS:
    asset = original.crop(box)
    if 'reach-arm' in name:
        # The row divider crosses the top joint: remove it and restore that joint.
        d=ImageDraw.Draw(asset)
        d.rectangle((0,0,asset.width,9),fill=(255,255,255,0))
        d.ellipse((45,3,61,19),fill='#b9d0ef',outline='#2c373d',width=3)
    if 'dynamics-arm' in name:
        # The same arm pose also appears cleanly in the joint-configuration row.
        # Use that source pose to restore the wrist hidden by the gauge.
        asset = original.crop((20,77,131,153))
    if ('pick-' in name or 'place-' in name):
        # Tight finger silhouettes exclude the downward arrow and held cube.
        w,h=asset.size
        polygon=[(10,0),(24,0),(24,18),(15,34),(27,44),(18,h-1),(0,36),(10,17)]
        if 'right' in name:
            polygon=[(w-1-x,y) for x,y in polygon]
        mask=Image.new('L',asset.size)
        ImageDraw.Draw(mask).polygon(polygon,fill=255)
        # Trim residual cube outlines just beyond the inward fingertips.
        d=ImageDraw.Draw(mask)
        if 'left' in name:
            d.rectangle((23,38,w,h),fill=0)
        else:
            d.rectangle((0,38,4,h),fill=0)
        if 'place-' in name:
            d.rectangle((0,0,w,4),fill=0)
        asset.putalpha(mask)
    pixels=asset.load()
    for y in range(asset.height):
        for x in range(asset.width):
            r,g,b,a=pixels[x,y]
            # Preserve neutral gray links, pale blue joints, and dark outlines.
            # Remove paper and green/red target annotations near the arms.
            colored=(g-r>24 and g-b>10) or (r-g>35 and r-b>20)
            blue_block=('finger' in name and b-r>35 and b-g>10)
            if min(r,g,b)>238 or colored or blue_block:
                pixels[x,y]=(255,255,255,0)
    target=OUT/(name+'.png')
    target.parent.mkdir(parents=True,exist_ok=True)
    asset.save(target)
    for base in [ROOT/'source/src/img/figs/f74', ROOT/'assets/img/figs/f74']:
        dest=base/(name+'.png')
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(target,dest)

frontend={
    'i-inputs':'Panel frames and dividers, state-transition nodes and arrows, coordinate axes, numbered cubes, collision box, target circles, dynamics gauge, task-logic graph, all labels.',
    'ii-core':'CSP search tree, SAT clauses and assignments, MILP regions, trajectory geometry, objective formulas, IK targets/checks/gauges, TAMP task boxes, arrows, held cubes and support line, central satisfy/optimize oval.',
    'iii-outputs':'Trajectory waypoints and obstacles, schedule bars and time arrow, assembly cubes and sequence arrows, certificate sheets, status symbols, gap gauge, all frames and labels.',
}
(OUT/'manifest.json').write_text(json.dumps({'source':str(SOURCE.relative_to(ROOT)),
    'source_size':list(original.size),'assets':[{'file':n+'.png','source_box':list(b),'title':t} for n,b,t in ITEMS],
    'frontend':frontend},indent=2))

overview=Image.new('RGB',(1200,960),'white')
for i,(name,box,title) in enumerate(ITEMS):
    card=Image.new('RGBA',(300,320),'white')
    d=ImageDraw.Draw(card)
    d.text((12,12),title,fill='#263238')
    for y in range(45,295,14):
        for x in range(12,288,14):
            d.rectangle((x,y,min(x+13,287),min(y+13,294)),fill='#edf0f3' if (x//14+y//14)%2 else 'white')
    asset=Image.open(OUT/(name+'.png'))
    asset=asset.resize((asset.width*2,asset.height*2),Image.Resampling.LANCZOS)
    card.alpha_composite(asset,((300-asset.width)//2,45+(250-asset.height)//2))
    overview.paste(card.convert('RGB'),((i%4)*300,(i//4)*320))
overview.save(OUT/'overview.jpg',quality=95)

cards=''.join(f'<article><h2>{title}</h2><div class="checker"><img src="/assets/figures/elements/figure74/{name}.png" alt="{title}"></div><p>{name}.png</p></article>' for name,box,title in ITEMS)
notes=''.join(f'<li><strong>{key}</strong>: {value}</li>' for key,value in frontend.items())
(ROOT/'example/figure74-assets.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.4 extracted assets</title><style>body{font:16px Arial;color:#27343a;background:#f3f5f7;margin:24px}main{max-width:1600px;margin:auto}h1{font-size:24px}h2{font-size:16px}.original{display:block;width:100%;background:white;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}article{padding:12px;background:white;border-radius:8px}.checker{height:200px;display:grid;place-items:center;background:repeating-conic-gradient(#edf0f3 0% 25%,white 0% 50%) 0/20px 20px}.checker img{width:90%;height:175px;object-fit:contain}p,li{line-height:1.5;font-size:13px;overflow-wrap:anywhere}li{margin-bottom:8px}@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:450px){.grid{grid-template-columns:1fr}}</style><main><h1>Figure 7.4 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section7/714_constraint.webp" alt="Original Figure 7.4"><h2>All extracted assets</h2><img class="original" src="/assets/figures/elements/figure74/overview.jpg" alt="All 12 extracted Figure 7.4 assets"><details><summary>Inspect individual transparent PNG files (12)</summary><div class="grid">'''+cards+'''</div></details><h2>Independent frontend geometry</h2><ul>'''+notes+'''</ul></main></html>''')
