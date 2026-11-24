"""Figure 7.12 isolated cart-pole and camera pictograms, without diagram annotations."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops
OUT=Path(__file__).resolve().parent
SITE=OUT.parents[3]
SOURCE='assets/figures/figures/part3/section7/differentiable_optimization_layers_for_spatial_reasoning.webp'
ASSETS=[
 ('ii-mpc/cart-pole-initial.png','MPC · initial cart-pole',(849,66,968,223),[(875,212),(944,212)]),
 ('ii-mpc/cart-pole-target.png','MPC · target cart-pole',(1159,54,1278,223),[(1185,212),(1254,212)]),
 ('iii-bundle-adjustment/input-camera-left.png','BA input · left camera',(1391,55,1452,113),None),
 ('iii-bundle-adjustment/input-camera-center.png','BA input · center camera',(1484,27,1520,84),None),
 ('iii-bundle-adjustment/input-camera-right.png','BA input · right camera',(1557,41,1597,101),None),
 ('iii-bundle-adjustment/output-camera-left.png','BA output · left camera',(1748,57,1811,113),None),
 ('iii-bundle-adjustment/output-camera-center.png','BA output · center camera',(1842,27,1879,84),None),
 ('iii-bundle-adjustment/output-camera-right.png','BA output · right camera',(1916,41,1957,101),None)]
def main():
 original=Image.open(SITE/SOURCE).convert('RGB');entries=[];crops=[]
 for file,title,box,wheels in ASSETS:
  crop=original.crop(box);alpha=crop.convert('L').point(lambda x:255-x)
  if wheels:
   mask=Image.new('L',crop.size,0);d=ImageDraw.Draw(mask);d.rectangle((0,179-box[1],crop.width,213-box[1]),fill=255)
   rod=[(850,66),(867,66),(920,179),(898,179)] if 'initial' in file else [(1209,54),(1228,54),(1228,179),(1209,179)]
   d.polygon([(x-box[0],y-box[1]) for x,y in rod],fill=255)
   if 'initial' in file:d.ellipse((850-box[0],67-box[1],867-box[0],84-box[1]),fill=255)
   for x,y in wheels:d.ellipse((x-10-box[0],y-10-box[1],x+10-box[0],y+10-box[1]),fill=255)
   alpha=ImageChops.multiply(alpha,mask)
  else:
   # Observation rays are pale gray; retain the dark pictogram and its edge pixels.
   alpha=alpha.point(lambda v:v if v>140 else 0)
   data=alpha.load();seen=set()
   for yy in range(alpha.height):
    for xx in range(alpha.width):
     if not data[xx,yy] or (xx,yy) in seen:continue
     stack=[(xx,yy)];seen.add((xx,yy));component=[]
     while stack:
      x,y=stack.pop();component.append((x,y))
      for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
       nx,ny=x+dx,y+dy
       if 0<=nx<alpha.width and 0<=ny<alpha.height and data[nx,ny] and (nx,ny) not in seen:seen.add((nx,ny));stack.append((nx,ny))
     if len(component)<14:
      for x,y in component:data[x,y]=0
  cut=Image.new('RGBA',crop.size,(0,0,0,0));cut.putalpha(alpha);crops.append(cut)
  for base in (OUT,SITE/'source/src/img/figs/f712',SITE/'assets/img/figs/f712'):
   p=base/file;p.parent.mkdir(parents=True,exist_ok=True);cut.save(p)
  entries.append({'file':file,'title':title,'source_box':box,'size':cut.size})
 notes={
  'i-assignment':'Sudoku grids, cell values, QP solver box, arrows and captions will be frontend elements.',
  'ii-mpc':'Two cart-pole PNGs are isolated. Ground hatching, state/control labels, MPC box and arrows will be reconstructed separately.',
  'iii-bundle-adjustment':'Six cameras are separate PNGs. Observation rays, 3D point nodes, solver box, arrows and text will be frontend elements.',
  'bottom-methods':'OptNet, CVXPY, Deep Declarative Networks and SATNet: all boxes, formulas, contour rings, optimization trajectory, feedback lines and arrows will be drawn in the frontend.'}
 (OUT/'manifest.json').write_text(json.dumps({'source':SOURCE,'source_size':original.size,'assets':entries,'frontend':notes},indent=2)+'\n')
 overview=Image.new('RGB',(1200,750),'#f3f5f7');d=ImageDraw.Draw(overview)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
 for i,((file,title,box,wheels),crop) in enumerate(zip(ASSETS,crops)):
  col=i%4;row=i//4;x=col*300;y=row*375
  d.text((x+12,y+15),title,fill='#29343a',font=font)
  for yy in range(y+52,y+354,12):
   for xx in range(x+12,x+288,12):d.rectangle((xx,yy,xx+11,yy+11),fill='#e6ebef' if ((xx-x)//12+(yy-y)//12)%2 else 'white')
  scale=min(2,250/crop.width,278/crop.height);large=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
  overview.paste(large,(x+(300-large.width)//2,y+62+(278-large.height)//2),large)
 overview.save(OUT/'overview.png')
 cards=''.join(f'<a class="asset" href="/assets/figures/elements/figure712/{e["file"]}"><strong>{e["title"]}</strong><div class="checker"><img src="/assets/figures/elements/figure712/{e["file"]}" alt="{e["title"]}"></div><span>{e["size"][0]} × {e["size"][1]} · transparent PNG</span></a>' for e in entries)
 notes_html=''.join(f'<li><strong>{k}</strong>: {v}</li>' for k,v in notes.items())
 (SITE/'example/figure712-assets.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.12 extracted assets</title><style>body{{margin:24px;font:16px Arial;background:#f3f5f7;color:#29343a}}main{{max-width:1600px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px}}.original{{width:100%;height:auto}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.asset{{display:block;background:white;padding:12px;color:inherit;text-decoration:none}}strong,span{{display:block;margin-bottom:10px}}span{{font-size:13px;margin-top:10px}}.checker{{height:230px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e6ebef 0 25%,white 0 50%) 0/24px 24px}}.checker img{{max-width:88%;max-height:210px;object-fit:contain;width:auto;height:auto;transform:scale(1.2)}}li{{line-height:1.6}}@media(max-width:800px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:480px){{body{{margin:12px}}.grid{{grid-template-columns:1fr}}}}</style><main><h1>Figure 7.12 · Extracted pictorial assets</h1><h2>Original</h2><img class="original" src="/{SOURCE}" width="2000" height="742" alt="Original Figure 7.12"><h2>Independent pictorial PNGs</h2><div class="grid">{cards}</div><h2>Frontend reconstruction</h2><ul>{notes_html}</ul></main></html>''')
if __name__=='__main__':main()
