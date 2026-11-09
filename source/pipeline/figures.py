"""Rasterise every included book figure to WebP for the web (2000 px wide, plus a 900 px thumbnail)."""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1] / "Spt-Intell-share-paper"
OUT = HERE / "build" / "figures"
TMP = HERE / "build" / "tmp_png"
EXTRA = {"figures/web/si_milestones_tikz.pdf": HERE / "build" / "si_milestones_tikz.pdf",
         "figures/web/world_modeling_tikz.pdf": HERE / "build" / "world_modeling_tikz.pdf"}
Image.MAX_IMAGE_PIXELS = None


def resolve(g):
    if g in EXTRA:
        return EXTRA[g]
    f = BOOK / g
    if f.exists():
        return f
    for e in (".pdf", ".png", ".jpg"):
        if (BOOK / (g + e)).exists():
            return BOOK / (g + e)
    return None


def convert(g):
    src = resolve(g)
    if src is None or not src.exists():
        return g, None
    stem = g.rsplit(".", 1)[0] if g.lower().endswith((".pdf", ".png", ".jpg")) else g
    dst = OUT / (stem + ".webp")
    thumb = OUT / (stem + ".thumb.webp")
    if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime and "--force" not in sys.argv:
        im = Image.open(dst)
        return g, {"src": str(dst.relative_to(OUT.parent)), "w": im.width, "h": im.height}
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".pdf":
        TMP.mkdir(parents=True, exist_ok=True)
        base = TMP / stem.replace("/", "__")
        subprocess.run(["pdftoppm", "-png", "-singlefile", "-f", "1", "-l", "1", "-scale-to-x", "2000", "-scale-to-y", "-1",
                        str(src), str(base)], check=True)
        im = Image.open(str(base) + ".png").convert("RGB")
    else:
        im = Image.open(src)
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        if im.width > 2000:
            im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=84, method=6)
    t = im.copy()
    t.thumbnail((900, 900 * 4))
    t.save(thumb, "WEBP", quality=80, method=6)
    return g, {"src": str(dst.relative_to(OUT.parent)), "w": im.width, "h": im.height}


graphics = [l.strip() for l in (HERE / "data" / "graphics.txt").read_text().splitlines() if l.strip()]
with ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(convert, graphics))
(HERE / "data" / "figures.json").write_text(json.dumps(res, indent=1))
missing = [g for g, v in res.items() if v is None]
size = sum(p.stat().st_size for p in OUT.rglob("*.webp"))
print(f"figures {len(res) - len(missing)} ok, missing {missing}, total {size / 1e6:.1f} MB")
