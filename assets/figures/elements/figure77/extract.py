"""Extract the original pictorial layers and prepare the Figure 7.7 review."""
from html import escape
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

OUT = Path(__file__).resolve().parent
SITE = OUT.parents[3]
SOURCE = Path('assets/figures/figures/part3/section7/implicit_neural_spatial_reasoning_task.webp')
ORIGINAL = Image.open(SITE / SOURCE).convert('RGB')

# Coordinates in the original image. The object masks retain the visible faces,
# while the source scene retains the cast shadows and floor.
OBJECTS = [
    ('red-cube-left', 'Left red cube', [(118,325),(153,311),(195,319),(198,373),(165,386),(122,381)]),
    ('red-cube-right', 'Right red cube', [(213,331),(248,321),(285,332),(288,385),(245,396),(216,383)]),
    ('green-sphere', 'Green sphere', [(312,357),(316,341),(330,325),(345,320),(364,321),(380,332),
                                      (387,346),(389,360),(384,376),(373,391),(355,399),(338,397),
                                      (324,388),(315,374)]),
    ('gray-cylinder', 'Gray cylinder', [(399,265),(405,258),(425,253),(448,255),(466,262),(467,269),
                                        (464,353),(453,359),(431,362),(413,359),(398,354)]),
    ('gray-cube', 'Gray cube', [(502,319),(536,306),(588,316),(583,376),(553,392),(500,382)]),
]
CAR_OUTLINE = [
    (771,316),(777,306),(779,286),(788,280),(830,275),(854,264),(877,251),
    (899,244),(935,238),(978,238),(1009,243),(1034,253),(1058,268),(1082,279),
    (1110,283),(1148,290),(1178,299),(1190,309),(1199,323),(1201,342),
    (1194,350),(1150,356),(1147,364),(1135,373),(1118,376),(1105,374),
    (1093,365),(1087,355),(887,355),(881,366),(866,375),(850,375),
    (837,370),(826,356),(804,353),(779,348),(774,340),
]


def arrow_free_scene():
    scene = ORIGINAL.copy()
    pixels = scene.load()
    # The overlaid arrow is the only annotation that crosses the raster scene.
    for y in range(244, 421):
        center = 298.6 - (y - 244) * 0.007
        left, right = round(center) - 5, round(center) + 5
        start, end = pixels[left, y], pixels[right, y]
        for x in range(left + 1, right):
            f = (x - left) / (right - left)
            pixels[x, y] = tuple(round(a + (b - a) * f) for a, b in zip(start, end))
    return scene


def polygon_mask(points, antialias=True):
    scale = 3 if antialias else 1
    mask = Image.new('L', (ORIGINAL.width * scale, ORIGINAL.height * scale))
    ImageDraw.Draw(mask).polygon([(x * scale, y * scale) for x, y in points], fill=255)
    return mask.resize(ORIGINAL.size, Image.Resampling.LANCZOS) if antialias else mask


def alpha_crop(source, mask, box):
    image = source.crop(box).convert('RGBA')
    image.putalpha(mask.crop(box))
    return image


def extract():
    scene = arrow_free_scene()
    box = (84, 243, 625, 422)
    scene_mask = Image.new('L', ORIGINAL.size)
    ImageDraw.Draw(scene_mask).rectangle((86, 245, 622, 419), fill=255)
    yield 'i-vqa/scene', 'Tabletop scene with the question arrow removed', box, alpha_crop(scene, scene_mask, box)
    for name, title, points in OBJECTS:
        xs, ys = zip(*points)
        box = (min(xs)-3, min(ys)-3, max(xs)+4, max(ys)+4)
        yield 'i-vqa/' + name, title, box, alpha_crop(scene, polygon_mask(points), box)

    car_mask = polygon_mask(CAR_OUTLINE, antialias=False)
    box = (768, 235, 1204, 379)
    yield 'ii-caption/attended-car', 'Car with blue spatial attention', box, alpha_crop(ORIGINAL, car_mask, box)

    road_box = (745, 386, 1240, 463)
    road = ORIGINAL.crop(road_box)
    attention = Image.new('RGBA', road.size)
    # Convert the blue tint to a transparent layer over a neutral street.
    street = ORIGINAL.copy()
    street_pixels = street.load()
    attention_pixels = attention.load()
    for y in range(road.height):
        for x in range(road.width):
            red, green, blue = road.getpixel((x, y))
            excess = blue - red
            if excess < 5:
                continue
            base = min(254, blue + round(excess * 0.1))
            alpha = min(255, round(excess * 1.25))
            color = tuple(max(0, min(255, round(base + (channel - base) * 255 / alpha)))
                          for channel in (red, green, blue))
            attention_pixels[x, y] = (*color, alpha)
            street_pixels[x + road_box[0], y + road_box[1]] = (base,) * 3
    yield 'ii-caption/road-attention', 'Blue attention on the road', road_box, attention

    box = (728, 156, 1269, 467)
    frame_mask = Image.new('L', ORIGINAL.size)
    ImageDraw.Draw(frame_mask).rectangle((732, 158, 1266, 463), fill=255)
    background = alpha_crop(street, ImageChops.subtract(frame_mask, car_mask), box)
    yield 'ii-caption/street-background', 'Street backdrop with space for the car', box, background


def main():
    entries = []
    for name, title, box, image in extract():
        filename = name + '.png'
        entries.append(dict(file=filename, title=title, source_box=box, size=image.size))
        for base in (OUT, SITE / 'source/src/img/figs/f77', SITE / 'assets/img/figs/f77'):
            dest = base / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            image.save(dest)

    (OUT / 'manifest.json').write_text(json.dumps({
        'source': str(SOURCE), 'source_size': ORIGINAL.size, 'assets': entries,
        'frontend': [
            'Panel frames, headings, labels, arrows, and the captioning illustration border.',
            'Circle, triangle, square, dashed relations, and the Left-of expression.',
        ],
    }, indent=2) + '\n')

    groups = []
    for prefix, heading in [('i-vqa/', '1. Visual question answering'), ('ii-caption/', '2. Image captioning')]:
        cards = []
        for entry in entries:
            if not entry['file'].startswith(prefix):
                continue
            url = '/assets/figures/elements/figure77/' + entry['file']
            title = escape(entry['title'])
            width, height = entry['size']
            cards.append(f'<article><h3>{title}</h3><div class="checker"><img src="{url}" alt="{title}"></div>'
                         f'<p><a href="{url}">Open PNG</a> · {width} × {height}</p></article>')
        groups.append(f'<h2>{heading}</h2><div class="grid">{"".join(cards)}</div>')

    (SITE / 'example/figure77-assets.html').write_text(f'''<!doctype html>
<html lang="en">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.7 extracted assets</title>
<style>
body{{margin:24px;background:#f3f5f7;color:#27343a;font:16px Arial,sans-serif}}
main{{max-width:1280px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px;margin-top:24px}}h3{{font-size:15px}}
.original{{display:block;width:100%;height:auto;background:white}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,175px),1fr));gap:12px}}
article{{background:white;border-radius:8px;padding:12px}}
.checker{{height:106px;display:grid;place-items:center;background:repeating-conic-gradient(#e6ebef 0% 25%,#fff 0% 50%) 0/20px 20px}}
.checker img{{max-width:96%;max-height:100px;object-fit:contain}}p{{line-height:1.5}}
@media(max-width:600px){{body{{margin:12px}}}}
</style>
<main>
<h1>Figure 7.7 · Extracted pictorial assets</h1>
<h2>Original</h2><img class="original" src="/{SOURCE}" width="2000" height="608" alt="Original Figure 7.7">
{''.join(groups)}
<h2>3. Visual relational reasoning</h2>
<p>The circle, triangle, square, dashed links and relation expression will be drawn in the browser. Panel borders, all text and arrows will also be drawn in the browser.</p>
</main>
</html>
''')


if __name__ == '__main__':
    main()
