"""Figure 7.10 pictorial asset; all diagram annotations remain frontend elements."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent
SITE=OUT.parents[3]
SOURCE='assets/figures/figures/part3/section7/explicit_structured_neural_reasoning_method.webp'
def main():
    original=Image.open(SITE/SOURCE).convert('RGBA')
    box=(985,288,1080,353)
    crop=original.crop(box)
    entry={'file':'c-module-network/room.png','title':'Indoor scene photograph','source_box':box,'size':crop.size}
    for base in (OUT,SITE/'source/src/img/figs/f710',SITE/'assets/img/figs/f710'):
        p=base/entry['file'];p.parent.mkdir(parents=True,exist_ok=True);crop.save(p)
    notes={
      'a-mac':'Panel border, three MAC cells, Control/Read/Write boxes, Q and A labels, recurrence arrows.',
      'b-state-machine':'Concept detector, probabilistic scene graph, graph nodes and edges, reading head, finite-automaton transitions and state symbols.',
      'c-module-network':'Question, parser, layout, LSTM and CNN blocks, colored module tiles, answer node and all connecting arrows.',
      'd-program-generator':'LLM, generated Python code, vision-tool API, tool boxes, final answer and all connecting arrows.'}
    (OUT/'manifest.json').write_text(json.dumps({'source':SOURCE,'source_size':original.size,'assets':[entry],'frontend':notes},indent=2)+'\n')
    overview=Image.new('RGB',(700,300),'#f3f5f7');d=ImageDraw.Draw(overview)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    d.text((20,18),'Panel C · Indoor scene photograph',fill='#27343a',font=font)
    for y in range(60,280,12):
      for x in range(20,680,12):d.rectangle((x,y,x+11,y+11),fill='#e6ebef' if (x//12+y//12)%2 else 'white')
    enlarged=crop.resize((285,195),Image.Resampling.LANCZOS)
    overview.paste(enlarged,(207,72),enlarged);overview.save(OUT/'overview.jpg',quality=95)
    items=''.join(f'<li><strong>{k}</strong>: {v}</li>' for k,v in notes.items())
    (SITE/'example/figure710-assets.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.10 extracted assets</title><style>body{{margin:24px;font:16px Arial;background:#f3f5f7;color:#27343a}}main{{max-width:1600px;margin:auto}}h1{{font-size:24px}}h2{{font-size:19px}}.original{{width:100%;height:auto;background:white}}.overview{{max-width:700px;width:100%}}li{{line-height:1.6}}@media(max-width:600px){{body{{margin:12px}}}}</style><main><h1>Figure 7.10 · Extracted pictorial asset</h1><h2>Original</h2><img class="original" src="/{SOURCE}" width="2000" height="437" alt="Original Figure 7.10"><h2>Panel C · Indoor scene</h2><img class="overview" src="/assets/figures/elements/figure710/overview.jpg" alt="Isolated indoor photograph"><p><a href="/assets/figures/elements/figure710/c-module-network/room.png">Open isolated PNG at original resolution</a></p><h2>Frontend reconstruction</h2><ul>{items}</ul></main></html>''')
if __name__=='__main__':main()
