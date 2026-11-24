"""Extract Figure 6.19's two photographic SLAM result panels."""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[3]
SOURCE = SITE / "assets/figures/figures/part3/section6/slam.webp"


def main():
    source = Image.open(SOURCE).convert("RGBA")
    panels = [
        ("visual-slam", (72, 56, 1179, 680), "Visual SLAM: tracked camera view and sparse map/trajectory composite."),
        ("lidar-slam", (1261, 56, 1881, 680), "LiDAR SLAM: dense point-cloud map with its embedded camera inset."),
    ]
    records = []
    for name, bounds, notes in panels:
        asset = source.crop(bounds)
        # The panel headings sit over near-uniform dark regions, so restore their background cleanly.
        title_boxes = {
            "visual-slam": (465, 10, 1065, 74),
            "lidar-slam": (300, 10, 610, 76),
        }
        fill = (43, 40, 42) if name == "visual-slam" else (45, 44, 45)
        ImageDraw.Draw(asset).rectangle(title_boxes[name], fill=fill)
        target = ROOT / f"{name}.png"
        asset.save(target)
        for folder in ("source/src/img/figs/f619", "assets/img/figs/f619"):
            dest = SITE / folder / target.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
        records.append({"file": target.name, "source_box": list(bounds), "size": list(asset.size), "notes": notes})

    (ROOT / "manifest.json").write_text(json.dumps({
        "source": str(SOURCE.relative_to(SITE)),
        "source_size": list(source.size),
        "notes": "The two raster assets preserve the source SLAM result imagery. Captions, layout borders, animation paths, labels and interaction regions will be drawn independently in the frontend.",
        "assets": records,
    }, indent=2) + "\n")

    sheet = Image.new("RGB", (1300, 520), "#eef2f6")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 25)
    draw.text((22, 16), "Figure 6.19 - separated SLAM panel assets", font=title, fill="#29343a")
    for (name, _, _), x in zip(panels, (20, 665)):
        im = Image.open(ROOT / f"{name}.png").convert("RGB")
        im.thumbnail((610, 385), Image.Resampling.LANCZOS)
        draw.rounded_rectangle((x, 60, x + 615, 480), 7, fill="white", outline="#c6cfd8")
        sheet.paste(im, (x + (615 - im.width) // 2, 74))
        draw.text((x + 12, 450), name, font=font, fill="#29343a")
    sheet.save(ROOT / "overview.png")

    sections = ""
    for name, _, notes in panels:
        sections += f'<article><h2>{name}</h2><img src="/assets/figures/elements/figure619/{name}.png"><p>{notes}</p></article>'
    (SITE / "example/figure619-assets.html").write_text(
        '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 6.19 extracted assets</title><style>body{font:16px Arial;background:#eef2f6;color:#29343a;margin:24px}main{max-width:1400px;margin:auto}h1{font-size:24px}h2{font-size:19px}img{max-width:100%;height:auto}.original{width:100%}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}article{background:#fff;border:1px solid #ccd4dc;border-radius:8px;padding:14px}article img{width:100%;height:340px;object-fit:contain}p{line-height:1.5}@media(max-width:700px){body{margin:12px}section{grid-template-columns:1fr}article img{height:240px}}</style><main><h1>Figure 6.19 · extracted SLAM panel assets</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/slam.webp"><section>'''
        + sections
        + "</section><p>Panel imagery is kept as raster source material. Labels, layout lines, animation and interactive regions will be reconstructed separately.</p></main></html>"
    )
    print(f"Saved {len(records)} panel assets and the asset review page.")


if __name__ == "__main__":
    main()
