"""Extract Figure 7.11 point clouds; annotations and geometry remain native SVG."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent
SITE=OUT.parents[3]
SOURCE='assets/figures/figures/part3/section7/geometry-aware_neural_spatial_reasoning.webp'
ASSETS=[('ii-grasping/point-cloud-original.png','Original point cloud',(756,165,882,266)),('ii-grasping/point-cloud-rotated.png','Rotated point cloud',(1065,180,1218,292))]
def main():
    original=Image.open(SITE/SOURCE).convert('RGB');entries=[];crops=[]
    for file,title,box in ASSETS:
        crop=original.crop(box).convert('RGBA')
        # Retain neutral gray dots; remove white background and blue annotations.
        pixels=[]
        for r,g,b,a in crop.getdata():
            if max(r,g,b)-min(r,g,b)>24 or min(r,g,b)>250:
                pixels.append((170,177,182,0))
            else:
                alpha=min(255,round((255-(r+g+b)/3)/(255-174)*255))
                pixels.append((169,176,181,alpha))
        crop.putdata(pixels);crops.append(crop)
        for base in (OUT,SITE/'source/src/img/figs/f711',SITE/'assets/img/figs/f711'):
            p=base/file;p.parent.mkdir(parents=True,exist_ok=True);crop.save(p)
        entries.append({'file':file,'title':title,'source_box':box,'size':crop.size})
    notes={
      'i-classification':'Digit glyphs, rotation labels, frames, prediction and invariant formula will be native text and SVG.',
      'ii-grasping':'The two point clouds are separate transparent PNGs. Grippers, pose axes, transformation arrow, g label and formula will be independent SVG elements.',
      'iii-molecule':'Atom circles, bonds, atom and index labels, transformation arrow and scalar-invariance formula will be native SVG.',
      'a-e-mechanisms':'All boxes, filters, basis kernels, point-set nodes, messages, arrows, text, formulas and separators will be rebuilt in the frontend.'}
    (OUT/'manifest.json').write_text(json.dumps({'source':SOURCE,'source_size':original.size,'assets':entries,'frontend':notes},indent=2)+'\n')
    overview=Image.new('RGB',(1000,370),'#f3f5f7');draw=ImageDraw.Draw(overview)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    for i,((file,title,box),crop) in enumerate(zip(ASSETS,crops)):
        x=15+i*500;draw.text((x+10,18),title,fill='#29343a',font=font)
        for yy in range(60,350,14):
            for xx in range(x+10,x+475,14):draw.rectangle((xx,yy,xx+13,yy+13),fill='#e7ebef' if ((xx-x)//14+yy//14)%2 else 'white')
        tile=crop.resize((crop.width*2,crop.height*2),Image.Resampling.LANCZOS)
        overview.paste(tile,(x+(485-tile.width)//2,75),tile)
    overview.save(OUT/'overview.png')
    notes_html=''.join(f'<li><strong>{k}</strong>: {v}</li>' for k,v in notes.items())
    links=''.join(f'<li><a href="/assets/figures/elements/figure711/{e["file"]}">{e["title"]} · PNG</a></li>' for e in entries)
    (SITE/'example/figure711-assets.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.11 extracted assets</title><style>body{{margin:24px;font:16px Arial;background:#f3f5f7;color:#29343a}}main{{max-width:1500px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px}}img{{width:100%;height:auto}}.overview{{max-width:1000px}}li{{line-height:1.6}}@media(max-width:600px){{body{{margin:12px}}}}</style><main><h1>Figure 7.11 · Extracted pictorial assets</h1><h2>Original</h2><img src="/{SOURCE}" width="2000" height="1031" alt="Original Figure 7.11"><h2>Panel ii · Independent transparent point clouds (2×)</h2><img class="overview" src="/assets/figures/elements/figure711/overview.png" alt="Original and rotated point clouds on checkerboard"><ul>{links}</ul><h2>Frontend reconstruction</h2><ul>{notes_html}</ul></main></html>''')
if __name__=='__main__':main()
