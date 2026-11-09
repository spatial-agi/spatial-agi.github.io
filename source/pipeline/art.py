"""Web versions of the handbook artwork (teaser world, era sketches, part-opener art)."""
from pathlib import Path

from PIL import Image

FG = Path(__file__).resolve().parents[2] / "figgen"
OUT = Path(__file__).resolve().parents[1] / "src" / "img"
OUT.mkdir(parents=True, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None


def save(im, name, w, q=82):
    im = im.convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(OUT / name, "WEBP", quality=q, method=6)
    print(name, im.size, round((OUT / name).stat().st_size / 1024), "KB")


world = Image.open(FG / "teaser/world/rings_r4_color.png")
save(world, "world.webp", 1500, 80)
save(world, "world-sm.webp", 760, 78)
eras = Image.open(FG / "teaser/vig/eras.png").convert("RGB")
sc = eras.width / 1500
for k, (l, r) in enumerate([(40, 300), (360, 610), (625, 870), (895, 1165), (1195, 1455)], 1):
    save(eras.crop((int(l * sc), int(60 * sc), int(r * sc), int(420 * sc))), f"era-{k}.webp", 520, 82)
for k, c in zip(range(1, 6), "abbaa"):
    im = Image.open(FG / f"out/opener_v1/part{k}_concept_S2_graphite_cobalt_gpt-image-2.5-sunburst_{c}.png")
    save(im, f"part-{k}.webp", 1200, 80)
