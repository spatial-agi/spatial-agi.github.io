"""Figure 7.21: LLM/VLM spatial reasoning, reconstructed from separate elements."""
from pathlib import Path
from html import escape
import json

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/LLM_VLM-centric_spatial_reasoning.webp'
INFO = {
    'text': ('Text-only description', 'Relations can be supplied directly in language: the book is left of the lamp, and the cup is right of it. The model reasons from these stated relations.'),
    'scene': ('Visual scene and query', 'The query asks which object is left of the lamp. The highlighted book is the relevant object. This shading marks the queried region; it is not a measured attention map.'),
    'graph': ('Graph evidence', 'An optional scene graph supplies object identities and spatial relations as structured evidence.'),
    'roi': ('Regions and boxes', 'Optional regions of interest or bounding boxes help ground language in specific objects and image locations.'),
    'depth': ('Depth and 3D evidence', 'Optional depth or 3D cues support reasoning about geometry beyond image-plane relations.'),
    'core': ('Pretrained LLM / VLM', 'A pretrained language or vision–language model combines language context with visual features to locate objects, relate them, and produce an answer.'),
    'prompt': ('Prompt strategies', 'Reasoning steps and visual markers can guide a pretrained model at inference time. Prompt, training, data, and model strategies are complementary options, not sequential stages.'),
    'training': ('Training strategies', 'Spatial objectives, auxiliary losses, or reinforcement learning can improve spatial reasoning through training. This is one of four complementary intervention strategies.'),
    'data': ('Data strategies', 'Spatial labels and simulated scenes can supply targeted examples for learning relations and geometry. This strategy can be combined with the other interventions.'),
    'model': ('Model strategies', 'Visual experts and geometry tokens provide architectural ways to incorporate spatial information. The converging arrows illustrate the combination of complementary sources.'),
    'answer': ('Grounded relational answer', 'For this query, the answer is the book: left-of(book, lamp). The relation binds the identified object to the reference object.'),
    'tasks': ('Other task outputs', 'Spatial reasoning can also produce distance or orientation estimates, navigation instructions, and mental-rotation answers. Metric answers require scale cues.'),
    'intrinsic': ('Intrinsic attributes', 'Evaluation can test whether a model understands spatial properties intrinsic to an object.'),
    'relations': ('Spatial relations', 'Evaluation can test relations between objects, including the left-of relation illustrated above.'),
    'logic': ('Deep spatial logic', 'Evaluation can test multi-step spatial inferences and the consistency of composed relations.'),
    'tests': ('Comprehensive tests', 'Broader evaluation combines different categories to assess spatial competence across tasks.'),
}


def fig721():
    out = []
    a = out.append

    def text(x, y, value, size=32, cls='', width=None):
        heading_widths = {
            '(i) Inputs': 153, '(ii) Reasoning core': 322, '(iii) Outputs': 204,
            'Text-only description': 371, 'Visual scene + query': 363,
            'Optional spatial evidence': 398, 'Pretrained LLM / VLM': 366,
            'Prompt': 129, 'Training': 143, 'Data': 82, 'Model': 109,
            'Answer: the book': 305, 'Other task outputs': 292,
        }
        if cls == 'f721-heading':
            width = heading_widths.get(value, width)
            size = 34 if size == 36 else size
        fit = f' textLength="{width}" lengthAdjust="spacingAndGlyphs"' if width else ''
        return f'<text x="{x}" y="{y}" text-anchor="middle" class="{cls}" style="font-size:{size}px"{fit}>{escape(value)}</text>'

    def path(d, cls='f721-ink'):
        return f'<path d="{d}" class="{cls}"/>'

    def route(d):
        return f'<path d="{d}" class="rl-route" marker-end="url(#f721-arrow)"/>'

    def box(x, y, w, h, blue=False):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="f721-box'+(' f721-selected' if blue else '')+'"/>'

    def zone(key, body, bounds):
        x, y, w, h = bounds
        a(f'<g class="rl-zone" data-k="{key}" role="button" tabindex="0" aria-pressed="false" aria-label="{escape(INFO[key][0])}">{body}<rect class="rl-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></g>')

    a('<div class="nf nf-rl nf-721" data-nf="721" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1000" role="group" aria-label="Figure 7.21: LLM/VLM-centric spatial reasoning"><defs><marker id="f721-arrow" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M3 4L14 9L3 14Z" fill="#4145e9" stroke="#4145e9" stroke-width="2.3" stroke-linejoin="round"/></marker></defs><rect width="2000" height="1000" fill="white"/>')
    a('<g class="f721-scaffold">'+path('M575 27V958M1437 27V958M627 652H1376M1497 680H1967', 'f721-divider')
      +text(280,58,'(i) Inputs',36,'f721-heading')+text(1000,58,'(ii) Reasoning core',36,'f721-heading')
      +text(1733,58,'(iii) Outputs',36,'f721-heading')
      +text(280,832,'Optional spatial evidence',32,'f721-heading')
      +text(1733,737,'Evaluate spatial competence',32,'f721-heading',453)+'</g>')

    body = text(280,135,'Text-only description',36,'f721-heading')+box(28,181,504,130)
    body += text(280,238,'The book is left of the lamp.',32,width=407)+text(280,269,'The cup is right of the lamp.',32,width=407)
    body += text(280,354,'Relations supplied in language',30,width=410)+route('M546 235L623 191')
    zone('text',body,(18,93,522,273))

    body = text(280,430,'Visual scene + query',36,'f721-heading')
    body += '<ellipse cx="163" cy="578" rx="103" ry="65" fill="#ebecfd"/>'
    body += path('M38 643H516M70 643V688M487 643V688')
    for name,x,y,w,h in [('book',72,563,168,84),('lamp',271,471,93,168),('cup',414,551,89,83)]:
        body += f'<image href="/assets/img/figs/f721/scene/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>'
    body += text(280,743,'Which object is left of the lamp?',32,'f721-blue',475)+route('M541 539L630 252')
    zone('scene',body,(25,393,510,365))
    for key,label,x,w in [('graph','Graph',34,160),('roi','RoI / boxes',200,160),('depth','Depth / 3D',369,160)]:
        zone(key,box(x,868,w,77,True)+text(x+w/2,914,label,30,width={'graph':84,'roi':145,'depth':142}[key]),(x,863,w,86))

    body = box(634,107,732,155,True)+text(1000,163,'Pretrained LLM / VLM',36,'f721-heading')
    body += text(1000,223,'Language context ↔ visual features',32,'f721-blue',521)
    body += text(1000,331,'Locate objects → relate → answer',32,'f721-blue',480)
    zone('core',body,(630,98,742,250))

    body = text(815,409,'Prompt',36,'f721-heading')
    for x,blue in [(680,False),(791,True),(902,False)]:
        body += box(x,471,65,52,blue)
    body += route('M753 497H778')+route('M864 497H889')+text(815,602,'Steps / visual markers',32,width=305)
    zone('prompt',body,(645,375,346,251))

    body = text(1191,409,'Training',36,'f721-heading')+box(1068,458,246,78,True)
    body += text(1191,505,'Spatial objective',32,width=232)
    body += route('M1085 548L1133 568')+route('M1248 569L1296 549')
    body += text(1191,611,'Auxiliary loss / RL',30,width=239)
    zone('training',body,(1048,375,289,251))

    body = text(815,713,'Data',36,'f721-heading')
    for x,y in [(695,785),(726,768),(757,751)]:
        body += box(x,y,154,68).replace('f721-box"','f721-box f721-blue-outline"') if x==757 else box(x,y,154,68)
    body += text(815,922,'Spatial labels / simulation',30,width=350)
    zone('data',body,(632,678,365,259))

    body = text(1191,713,'Model',36,'f721-heading')+box(1083,769,74,56,True)+box(1246,769,74,56,True)
    body += route('M1131 832L1182 862')+route('M1274 832L1205 863')+'<circle cx="1194" cy="877" r="9.5" fill="#4145e9"/>'
    body += text(1191,945,'Visual experts / geometry tokens',28,width=425)
    zone('model',body,(974,681,433,275))

    body = route('M1378 185H1477')+box(1501,107,465,176,True)
    body += text(1733,169,'Answer: the book',36,'f721-heading')+text(1733,242,'left-of (book, lamp)',36,'f721-math f721-blue',275)
    zone('answer',body,(1493,99,482,195))
    body = text(1733,356,'Other task outputs',32,'f721-heading')
    for y,label,width in [(423,'Distance / orientation',318),(491,'Navigation instructions',339),(559,'Mental-rotation answers',343)]:
        body += text(1733,y,label,32,width=width)
    body += text(1733,637,'Metric answers need scale cues',30,'f721-blue',425)
    zone('tasks',body,(1497,321,478,333))
    for key,x,y,labels in [('intrinsic',1498,785,['Intrinsic','attributes']),('relations',1742,785,['Spatial','relations']),('logic',1498,892,['Deep spatial','logic']),('tests',1742,892,['Comprehensive','tests'])]:
        body=box(x,y,228,86)
        for offset,label in zip([36,62],labels):body+=text(x+114,y+offset,label,30,width=214 if label=='Comprehensive' else None)
        zone(key,body,(x,y,228,86))
    a('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps({k:dict(t=v[0],b=v[1]) for k,v in INFO.items()})+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure 7.21 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure721-1"><style>body{margin:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;height:auto;background:#fff}@media(max-width:600px){body{margin:12px}}</style><main><h1>Figure 7.21 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/'''+ORIGINAL+'''" width="2000" height="1000" alt="Original Figure 7.21"><h2>Interactive reconstruction</h2>'''+fig721()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure721-1';mountNative();</script></html>'''
    (SITE/'example/figure721.html').write_text(page)
    print('Generated Figure 7.21 comparison.')
