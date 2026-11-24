"""Extract Figure 7.1 pictograms as transparent, panel-grouped PNG assets."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'assets/figures/figures/part3/section7/711_geo.webp'
OUT = ROOT / 'assets/figures/elements/figure71'
GROUPS = {
    'i-inputs': {
        'camera': (30, 85, 89, 134),
        'image-points': (95, 54, 174, 152),
        'depth-sensor': (8, 198, 105, 334),
        'lidar-points': (101, 198, 180, 290),
        'joint-states-arm': (14, 339, 166, 461),
        'environment-obstacles': (23, 653, 190, 738),
    },
    'ii-reasoning': {
        'kinematics-arm': (642, 548, 777, 664),
        'contact-gripper': (1260, 588, 1351, 675),
    },
    'iii-outputs': {
        'reachable-arm': (1558, 401, 1654, 483),
        'grasp-gripper': (1495, 696, 1590, 781),
    },
}
POLYGONS = {
    'reachable-arm': [(1560,482),(1560,469),(1568,466),(1573,438),(1572,433),(1602,407),(1610,406),(1636,424),(1641,430),(1645,444),(1653,458),(1640,460),(1634,447),(1630,438),(1627,436),(1605,421),(1585,442),(1582,466),(1590,471),(1590,482)],
}

im = Image.open(SOURCE).convert('RGBA')
for group, items in GROUPS.items():
    for name, box in items.items():
        crop = im.crop(box)
        if name in POLYGONS:
            mask=Image.new('L',crop.size,0)
            ImageDraw.Draw(mask).polygon([(x-box[0],y-box[1]) for x,y in POLYGONS[name]],fill=255)
            crop.putalpha(mask)
        px = crop.load()
        for y in range(crop.height):
            for x in range(crop.width):
                r, g, b, a = px[x, y]
                if name in ('depth-sensor','reachable-arm') and b-r>8 and b-g>8:
                    px[x,y]=(r,g,b,0)
                    continue
                # Remove only near-white paper while retaining antialiased ink.
                whiteness = min(r, g, b)
                if whiteness > 246 and max(r, g, b) - whiteness < 8:
                    px[x, y] = (r, g, b, 0)
                elif whiteness > 232 and max(r, g, b) - whiteness < 12:
                    px[x, y] = (r, g, b, round(a * (246 - whiteness) / 14))
        target = OUT / group / f'{name}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        crop.save(target)
        for mirror in [ROOT/'source/src/img/figs/f71',ROOT/'assets/img/figs/f71']:
            dest=mirror/group/target.name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(target,dest)

manifest={'source':str(SOURCE.relative_to(ROOT)),'source_size':list(im.size),'assets':[{'file':f'{group}/{name}.png','source_box':list(box)} for group,items in GROUPS.items() for name,box in items.items()], 'frontend':'All text, formulas, axes, transformations, epipolar lines, view cones, reachable-region boundaries, paths, arrows, check/cross symbols, cube and mesh geometry, panel borders and dividers.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
files=[OUT/a['file'] for a in manifest['assets']]
overview=Image.new('RGB',(960,240*((len(files)+2)//3)),'#f2f4f6')
for i,p in enumerate(files):
    card=Image.new('RGBA',(320,240),'white')
    asset=Image.open(p);asset.thumbnail((280,175))
    card.alpha_composite(asset,((320-asset.width)//2,45+(175-asset.height)//2))
    ImageDraw.Draw(card).text((12,14),p.parent.name+' / '+p.stem,fill='#263238')
    overview.paste(card.convert('RGB'),((i%3)*320,(i//3)*240))
overview.save(OUT/'overview.jpg',quality=94)

articles=[]
for group,items in GROUPS.items():
    articles.append('<section><h2>'+group+'</h2><div class="grid">')
    for name in items:
        articles.append(f'<article><h3>{name}</h3><div class="checker"><img alt="{name}" src="/assets/figures/elements/figure71/{group}/{name}.png"></div></article>')
    articles.append('</div></section>')
page=ROOT/'example/figure71-assets.html'
old=page.read_text();start=old.index('<div class="groups">');end=old.index('</main>',start)
page.write_text(old[:start]+'<div class="groups">'+''.join(articles)+'</div><p>All text, formulas, axes, arrows, view cones, reach boundaries, paths, check/cross symbols, geometric cubes and meshes, panel borders and dividers will be drawn independently in the frontend.</p>'+old[end:])


