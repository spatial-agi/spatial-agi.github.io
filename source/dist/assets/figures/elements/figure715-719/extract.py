"""Reproducible pictogram extraction and batch element review for Figures 7.15–7.19."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
FIGS={
715:('policy-based-rl.webp',579,'Policy-based RL',['State and policy boxes','Environment and trajectory buffer','Policy-gradient equation, update note and every feedback arrow']),
716:('AC-based-rl.webp',542,'Actor–critic RL',['State, actor, critic and environment boxes','Advantage equation','Action, state, reward and actor-update arrows']),
717:('ppo-based-rl.webp',825,'PPO',['Old and new policies','Rollout buffer with individually drawn transition rows','Probability ratio and clipped surrogate objective','Sampling, policy update and old-policy synchronization arrows']),
718:('dpo-based-rl.webp',649,'DPO',['Prompt and reference-policy boxes','Two response cards and their text lines','Human preference panel with extracted thumb icons','Reward log-ratio fractions and Bradley–Terry loss','Sampling and offline update arrows']),
719:('grpo-based-rl.webp',618,'GRPO',['Prompt and old-policy group of outputs','Reward model with individual response/reward cards','Group-relative advantage fraction','Clipped surrogate and KL-penalized objective','New policy and every connecting arrow'])}
ASSETS=[
(718,'prompt/document.png','DPO · prompt document',(84,104,151,186)),
(718,'human-preference/thumb-up.png','DPO · preferred response',(1153,316,1230,380)),
(718,'human-preference/thumb-down.png','DPO · rejected response',(1371,323,1447,391)),
(719,'prompt/document.png','GRPO · prompt document',(92,155,160,240))]
def main():
 entries={k:[] for k in FIGS};crops=[]
 for number,file,title,box in ASSETS:
  source=ROOT/'assets/figures/figures/part3/section7'/FIGS[number][0]
  original=Image.open(source).convert('RGB');crop=original.crop(box)
  # Black source artwork: white becomes fully transparent, dark edge pixels retain antialiasing.
  alpha=crop.convert('L').point(lambda v:255-v if v<248 else 0)
  if 'thumb-up' in file:
   # At the top, the thumb touches the response-card border; keep only the thumb's narrow tip.
   d=ImageDraw.Draw(alpha)
   d.rectangle((0,0,1194-box[0],3),fill=0)
   d.rectangle((1204-box[0],0,crop.width,3),fill=0)
  rgba=Image.new('RGBA',crop.size,(0,0,0,0));rgba.putalpha(alpha)
  # Remove tiny compression speckles while keeping all parts of the icon, including the cuff.
  pixels=alpha.load();seen=set()
  for y in range(alpha.height):
   for x in range(alpha.width):
    if pixels[x,y]<10 or (x,y) in seen:continue
    todo=[(x,y)];seen.add((x,y));component=[]
    while todo:
     cx,cy=todo.pop();component.append((cx,cy))
     for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
      nx,ny=cx+dx,cy+dy
      if 0<=nx<alpha.width and 0<=ny<alpha.height and pixels[nx,ny]>=10 and (nx,ny) not in seen:
       seen.add((nx,ny));todo.append((nx,ny))
    if len(component)<8:
     for cx,cy in component:pixels[cx,cy]=0
  rgba.putalpha(alpha)
  for base in [ROOT/f'assets/figures/elements/figure{number}',ROOT/f'source/src/img/figs/f{number}',ROOT/f'assets/img/figs/f{number}']:
   p=base/file;p.parent.mkdir(parents=True,exist_ok=True);rgba.save(p)
  entries[number].append({'file':file,'title':title,'source_box':box,'size':rgba.size})
  crops.append((title,rgba))
 manifests=[]
 for number,(file,height,title,frontend) in FIGS.items():
  manifest={'figure':f'7.{number-700}','source':f'assets/figures/figures/part3/section7/{file}','source_size':[2000,height],'assets':entries[number],'frontend':frontend,'animation':'White light cores with soft blue luminous halos; hover/focus/pin uses the established white-mask effect.'}
  p=ROOT/f'assets/figures/elements/figure{number}';p.mkdir(parents=True,exist_ok=True);(p/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');manifests.append(manifest)
 (OUT/'manifest.json').write_text(json.dumps(manifests,ensure_ascii=False,indent=2)+'\n')
 overview=Image.new('RGB',(1200,360),'#f3f5f7');d=ImageDraw.Draw(overview)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
 for i,(title,rgba) in enumerate(crops):
  x=i*300;d.text((x+12,16),title,fill='#29343a',font=font)
  for yy in range(53,335,12):
   for xx in range(x+12,x+288,12):d.rectangle((xx,yy,xx+11,yy+11),fill='#e6ebef' if ((xx-x)//12+yy//12)%2 else 'white')
  size=rgba.resize((rgba.width*3,rgba.height*3),Image.Resampling.LANCZOS)
  overview.paste(size,(x+(300-size.width)//2,62+(260-size.height)//2),size)
 overview.save(OUT/'overview.png')
 sections=[]
 for m in manifests:
  number=700+int(m['figure'].split('.')[1]);title=FIGS[number][2]
  cards=''.join(f'<a class="asset" href="/assets/figures/elements/figure{number}/{e["file"]}"><h3>{e["title"]}</h3><div class="checker"><img src="/assets/figures/elements/figure{number}/{e["file"]}" alt="{e["title"]}"></div><p>{e["size"][0]} × {e["size"][1]} · transparent PNG</p></a>' for e in m['assets'])
  if not cards:cards='<p>No pictorial PNG assets: all elements are diagram primitives for frontend reconstruction.</p>'
  notes=''.join('<li>'+v+'</li>' for v in m['frontend'])
  sections.append(f'<section id="figure{number}"><h2>Figure {m["figure"]} · {title}</h2><img class="original" src="/{m["source"]}" width="2000" height="{m["source_size"][1]}" alt="Original Figure {m["figure"]}"><div class="grid">{cards}</div><h3>Draw independently in the frontend</h3><ul>{notes}</ul></section>')
 html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures 7.15–7.19 · Asset review</title><style>body{margin:24px;background:#f3f5f7;color:#29343a;font:16px/1.6 Arial}main{max-width:1600px;margin:auto}h1{font-size:24px}h2{font-size:21px}h3{font-size:17px}nav a{margin-right:20px}section{margin:32px 0;padding:20px;background:white}.original{display:block;width:100%;height:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:20px}.asset{padding:12px;color:inherit;text-decoration:none;border:1px solid #dbe1e6}.checker{height:270px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e6ebef 0 25%,white 0 50%) 0/24px 24px}.checker img{max-width:90%;max-height:240px;image-rendering:auto;width:auto;height:auto;transform:scale(2.6)}li{line-height:1.6}@media(max-width:600px){body{margin:12px}section{padding:12px}.grid{grid-template-columns:1fr}}</style><main><h1>Figures 7.15–7.19 · Original figures and extracted assets</h1><p>Four transparent PNG pictograms are isolated for DPO and GRPO. All text, formulas, card frames, response lines and arrows will be reconstructed as independent frontend elements.</p><nav>'''+''.join(f'<a href="#figure{k}">Figure 7.{k-700}</a>' for k in FIGS)+'''</nav><h2>Extracted pictograms</h2><img class="original" src="/assets/figures/elements/figure715-719/overview.png" width="1200" height="360" alt="Four isolated pictograms">'''+''.join(sections)+'''</main></html>'''
 (ROOT/'example/figure715-719-assets.html').write_text(html)
 print('Created five manifests, four transparent PNG assets, source/served mirrors, extraction overview and batch review page.')
if __name__=='__main__':main()
