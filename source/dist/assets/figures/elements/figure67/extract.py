"""Extract Figure 6.7 artwork; annotations and diagram geometry stay native."""
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / 'assets/figures/figures/part3/section6/surface_normal_estimation.webp'
src = Image.open(SOURCE).convert('RGB')
SPECS = [
    ('inputs/rgb-room', (217, 12, 435, 170)),
    ('video/frame-1', (124, 220, 234, 297)),
    ('video/frame-2', (243, 220, 353, 297)),
    ('video/frame-3', (363, 220, 469, 297)),
    ('multiview/table-plant', (265, 345, 362, 447)),
    ('multiview/camera-left', (177, 349, 222, 387)),
    ('multiview/camera-right', (398, 349, 446, 387)),
    ('multiview/camera-bottom', (291, 463, 336, 494)),
    ('output/normal-field', (1335, 112, 1689, 423)),
]


def transparent_ink(im):
    # Recover neutral ink over transparency, retaining antialiased edge coverage.
    # The original line illustrations are monochrome on a white background.
    ink = Image.new('RGBA', im.size)
    ink.putdata([(0, 0, 0, max(0, min(255, round((250-min(r,g,b))*255/250))))
                 for r, g, b in im.getdata()])
    return ink


records = []
for name, box in SPECS:
    im = src.crop(box)
    if name.startswith('output/'):
        im = im.convert('RGBA')
    else:
        im = transparent_ink(im)
    if name == 'multiview/table-plant':
        # Exclude the sight-line dashes below the two rear legs, while keeping
        # the lower central table leg. Coordinates remain in source space.
        mask = Image.new('L', im.size)
        p = [(265,345),(362,345),(362,432),(324,432),
             (324,447),(304,447),(304,432),(265,432)]
        ImageDraw.Draw(mask).polygon([(x-box[0], y-box[1]) for x,y in p], fill=255)
        im.putalpha(ImageChops.multiply(im.getchannel('A'), mask))
    if name == 'multiview/camera-right':
        # The adjacent dashed ray approaches the lower left crop corner.
        mask = Image.new('L', im.size, 255)
        ImageDraw.Draw(mask).polygon([(0,26),(7,38),(0,38)], fill=0)
        im.putalpha(ImageChops.multiply(im.getchannel('A'), mask))
    path = ROOT / (name + '.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    records.append(dict(file=name+'.png', source_box=box, size=list(im.size)))

(ROOT/'manifest.json').write_text(json.dumps(dict(
    source=str(SOURCE.relative_to(SITE)),
    notes='Artwork only. Rebuild film borders, sight lines, arrows, network, '
          'noise schedule, angular-error diagram, timelines and text in the frontend.',
    assets=records), indent=2)+'\n')

font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
sheet = Image.new('RGB', (1260, 900), '#e2e7ec')
d = ImageDraw.Draw(sheet)
for i, record in enumerate(records):
    x, y = 12 + i%3*416, 12 + i//3*296
    d.rounded_rectangle((x,y,x+400,y+280), 8, fill='#fff', outline='#bac4ce')
    im = Image.open(ROOT/record['file'])
    scale = min(3, 374/im.width, 235/im.height)
    im = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
    sheet.paste(im, (x+(400-im.width)//2,y+10+(235-im.height)//2), im)
    d.text((x+12,y+252), record['file'].removesuffix('.png'), font=font, fill='#223443')
sheet.save(ROOT/'overview.png')
print(f'Saved {len(records)} separate PNG assets to {ROOT}')
