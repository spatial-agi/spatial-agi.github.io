"""Social preview image (1200x630): title in Pagella on the left, the handbook world on the right."""
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

W = Path(__file__).resolve().parents[1]
FG = W.parent / "figgen"
font = lambda name, size: ImageFont.truetype(subprocess.run(["kpsewhich", name], capture_output=True, text=True).stdout.strip(), size)
img = Image.new("RGB", (1200, 630), "#ffffff")
world = Image.open(FG / "teaser/world/rings_r4_color.png").convert("RGB")
crop = world.crop((80, 120, 2080, 1780)).resize((560, 465), Image.LANCZOS)
img.paste(crop, (612, 82))
d = ImageDraw.Draw(img)
d.rectangle((0, 0, 1200, 8), fill="#3646F0")
d.text((64, 150), "SPATIAL", font=font("texgyrepagella-bold.otf", 62), fill="#1c2133")
d.text((64, 222), "INTELLIGENCE", font=font("texgyrepagella-bold.otf", 62), fill="#1c2133")
d.text((66, 340), "Foundations, Architectures, Methodologies,", font=font("texgyrepagella-italic.otf", 27), fill="#3b4258")
d.text((66, 376), "Applications and Challenges", font=font("texgyrepagella-italic.otf", 27), fill="#3b4258")
d.rounded_rectangle((64, 438, 250, 482), radius=22, fill="#eef0fe", outline="#cfd3fa")
d.text((84, 446), "Handbook", font=font("texgyrepagella-bold.otf", 25), fill="#3646F0")
d.text((66, 540), "spatial-agi.github.io", font=font("texgyrepagella-regular.otf", 24), fill="#6a7189")
img.save(W / "src" / "img" / "og.jpg", quality=88)
print("og.jpg written")
