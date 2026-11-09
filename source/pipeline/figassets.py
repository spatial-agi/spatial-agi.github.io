"""Raster pieces for the natively drawn web figures (Fig. 1.1, Fig. 2.1, part openers).

Run with the figure environment (numpy + matplotlib), from this folder:
    ~/miniforge3/envs/figgen/bin/python figassets.py
Reads the print-figure sources in ../../figgen (same crops as fig1_1.py / fig2_1.py / opener.py) and writes
WebP/PNG files to ../src/img/figs plus figs/meta.json (aspect ratios, cube colours) for webfigs.py.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

FIGGEN = Path(__file__).resolve().parents[2] / "figgen"
sys.path.insert(0, str(FIGGEN))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from figlib import ASSETS, BLUE, draw_cloud, project_cloud, table_cup_cloud  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "src" / "img" / "figs"
OUT.mkdir(parents=True, exist_ok=True)
PX = 7            # exported pixels per point (the figures are ~2 px/pt on screen, so this covers 3x displays)
meta = {}


def load(name):
    return Image.open(ASSETS / f"{name}.png")


def trim(im):
    return im.crop(im.getchannel("A").getbbox()) if im.mode == "RGBA" else im


def save(im, name, width_pt=None, height_pt=None, q=86):
    if width_pt:
        w = round(width_pt * PX)
        h = round(w * im.height / im.width)
    else:
        h = round(height_pt * PX)
        w = round(h * im.width / im.height)
    if w < im.width:
        im = im.resize((w, h), Image.LANCZOS)
    im.save(OUT / f"{name}.webp", "WEBP", quality=q, method=6)
    meta[name] = dict(ar=round(im.width / im.height, 5))


def cloud_png(name, u, v, w_pt, h_pt, Z, s, color=None):
    """The point cloud drawn exactly as draw_cloud() does in the print figure, on a transparent box of w x h pt."""
    fig = plt.figure(figsize=(w_pt / 72, h_pt / 72), dpi=72)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_pt), ax.set_ylim(h_pt, 0), ax.axis("off")

    class C:
        pass
    cv = C()
    cv.ax = ax
    draw_cloud(cv, u, v, 0, 0, w_pt, h_pt, s=s, Zdepth=Z, **({"color": color} if color else {}))
    fig.savefig(OUT / f"{name}.png", dpi=72 * PX * 1.4, transparent=True)
    plt.close(fig)


# ---------------- Fig. 2.1
living = load("living").convert("RGB")
ldepth = load("living_depthmap").convert("RGB")
disp = np.load(ASSETS / "living_disp.npy")
for name, h in [("tablecup", 38), ("cutaway", 50), ("city", 46)]:
    save(trim(load(name)), f"f21-{name}", height_pt=h)
save(living.crop((60, 0, 1536, 984)), "f21-perception", width_pt=68)
save(trim(load("gripper")), "f21-gripper", height_pt=50)
for k, name in enumerate(["pred1", "pred2", "room_robot"]):
    save(load(name).convert("RGB").crop((300, 120, 1400, 1000)), f"f21-pred{k}", width_pt=21)
save(living.crop((300, 0, 1300, 1000)), "f21-obs-rgb", width_pt=10)
save(ldepth.crop((300, 0, 1300, 1000)), "f21-obs-depth", width_pt=10)
CW, CH = (110 - 12) / 2, 58
u, v, cols, Z = project_cloud(living, disp, step=6, yaw=28, pitch=18, near_cut=0.05)
cloud_png("f21-geometric", u, v, CW - 4, CH - 15, Z, s=0.05)
u2, v2, _, Z2 = project_cloud(living, disp, step=18, yaw=28, pitch=18, near_cut=0.05)
cloud_png("f21-obs-cloud", u2, v2, 8.4, 8.4, Z2, s=0.02)
# abstract cell: the same pseudo-random voxel shades as the print figure
rng = np.random.default_rng(3)
shades = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            shades.append(dict(i=i, j=j, k=k, t=round(float(rng.uniform(0.15, 0.85)), 4)))
meta["f21-voxels"] = shades

# ---------------- Fig. 1.1
room = load("room").convert("RGB")
pred1 = load("pred1").convert("RGB")
pred2 = load("pred2").convert("RGB")
save(living.crop((560, 120, 1536, 770)), "f11-world", height_pt=39)
save(pred1.crop((420, 220, 1300, 840)), "f11-experience", width_pt=38)
save(room, "f11-room", width_pt=17)
save(pred2.crop((380, 40, 1300, 1000)), "f11-hub", width_pt=119)
uc, vc, Zc = table_cup_cloud()
cloud_png("f11-cloud", uc, vc, 21, 21, Zc, s=0.05, color=BLUE)

# ---------------- part openers: the text-free artwork at full resolution
OPENERS = {1: "a", 2: "b", 3: "b", 4: "a", 5: "a"}
for k, c in OPENERS.items():
    im = Image.open(FIGGEN / f"out/opener_v1/part{k}_concept_S2_graphite_cobalt_gpt-image-2.5-sunburst_{c}.png").convert("RGB")
    im.save(OUT / f"opener-{k}.webp", "WEBP", quality=88, method=6)
    im.resize((1600, round(1600 * im.height / im.width)), Image.LANCZOS).save(OUT / f"opener-{k}-1600.webp", "WEBP", quality=86, method=6)
    meta[f"opener-{k}"] = dict(w=im.width, h=im.height)

(OUT / "meta.json").write_text(json.dumps(meta, indent=1))
print("wrote", len(list(OUT.iterdir())), "files to", OUT)
