"""Figure 7.7 in the original 2000 × 608 coordinate system."""
from html import escape
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/implicit_neural_spatial_reasoning_task.webp'
INFO = {
    'question': ('Compositional spatial question', 'The question combines color, shape and a left-of relation. The model must identify the green sphere, find the red cubes to its left, and count them.'),
    'scene': ('Visual evidence', 'Two red cubes lie to the left of the green sphere. The gray cylinder and gray cube are distractors: their shapes or colors do not match the question.'),
    'answer': ('Grounded answer', 'The answer is 2. Counting the objects that meet all three conditions connects the visual scene to the language query.'),
    'attention': ('Spatial attention for captioning', 'The blue attention map emphasizes the car and the street. These visual regions support the subject and spatial context in the generated caption.'),
    'caption': ('Spatially grounded caption', '“A car is parked on the street.” The caption describes both the object and its relation to the surrounding scene.'),
    'relations': ('Visual relational reasoning', 'The model must infer relations from the arrangement of visual objects. Dashed links illustrate pairwise relationships among the circle, triangle and square.'),
    'predicate': ('Relational output', 'Left-of(object A, object B) expresses a directional relationship. Its arguments identify the two objects whose positions are being compared.'),
}


def fig77():
    parts = []
    add = parts.append
    manifest = json.loads((SITE/'assets/figures/elements/figure77/manifest.json').read_text())
    assets = {a['file'].removesuffix('.png'): a for a in manifest['assets']}

    def text(x, y, value, size=31, cls='', raw=False):
        add(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" class="f77-{cls}">{value if raw else escape(value)}</text>')

    def path(d, cls='ink', arrow=False):
        classes = ' '.join('f77-'+c for c in cls.split())
        marker = ' marker-end="url(#f77-arrow)"' if arrow else ''
        add(f'<path d="{d}" class="{classes}"{marker}/>')

    def asset(name):
        x,y,r,b = assets[name]['source_box']
        add(f'<image href="/assets/img/figs/f77/{name}.png" x="{x}" y="{y}" width="{r-x}" height="{b-y}"/>')

    def zone(key, box, draw):
        add(f'<g class="f77-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        x,y,w,h = box
        add(f'<rect class="f77-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="5"/>')
        add('</g>')

    add('<div class="nf nf-77" data-nf="77" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 608" role="group" aria-label="Figure 7.7: implicit neural spatial reasoning tasks"><defs>')
    add('<marker id="f77-arrow" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto"><path d="M1 0.5L7 3.5L1 6.5Z" fill="#111"/></marker>')
    add('<radialGradient id="f77-node" cx="35%" cy="30%" r="80%"><stop stop-color="#f8f8f8"/><stop offset="1" stop-color="#e8e8e8"/></radialGradient>')
    add('</defs><rect width="2000" height="608" fill="#fff"/><g class="f77-scaffold">')
    for x,w in ((13,661),(697,616),(1340,647)):
        add(f'<rect x="{x}" y="25" width="{w}" height="570" rx="11" class="f77-panel"/>')
    text(329,107,'1. Visual Question Answering',31,'heading')
    text(1001,87,'2. Image captioning with',31,'heading')
    text(1001,127,'spatial attention',31,'heading')
    text(1653,107,'3. Visual relational reasoning',31,'heading')
    add('</g>')

    def scene():
        asset('i-vqa/scene')
        path('M99 478L161 427','ink route',True)
        text(107,512,'Image')
    add('<g class="f77-zone" data-k="scene" tabindex="0" role="button" aria-pressed="false" aria-label="Visual evidence">')
    scene()
    add('<path class="f77-hit" d="M83 243H625V421H180V525H54V477H83Z"/>')
    add('</g>')

    def question():
        text(350,188,'How many red cubes are to the')
        text(350,228,'left of the green sphere?')
        path('M297 477L298.5 243','ink route',True)
        text(298,506,'Question')
    # Two hit surfaces let the crossing arrow remain independent of the image.
    add('<g class="f77-zone" data-k="question" tabindex="0" role="button" aria-pressed="false" aria-label="Compositional spatial question">')
    question()
    add('<path class="f77-hit" d="M100 149H609V237H308V478H376V519H224V478H286V237H100Z"/>')
    add('</g>')

    def answer():
        path('M400 500L492 498','ink route',True)
        text(568,501,'Answer')
        text(568,560,'2',31,'answer')
    zone('answer',(394,477,238,96),answer)

    def attention():
        asset('ii-caption/street-background')
        asset('ii-caption/attended-car')
        asset('ii-caption/road-attention')
        add('<rect x="729" y="156" width="540" height="311" rx="0" class="f77-image-frame"/>')
    zone('attention',(727,154,544,315),attention)
    zone('caption',(750,483,499,63),lambda: text(1000,525,'A car is parked on the street.'))

    def relations():
        for d in ('M1503 358L1616 241','M1680 243L1775 335','M1524 384H1778'):
            path(d,'link route dashed')
        add('<circle cx="1648" cy="220" r="38" class="f77-node"/>')
        path('M1488 332L1446 409H1530Z','node')
        add('<rect x="1780" y="343" width="76" height="77" class="f77-node"/>')
    zone('relations',(1432,172,442,260),relations)
    zone('predicate',(1446,468,485,57),lambda: text(1652,506,'Left-of(object <tspan font-style="italic">A</tspan>, object <tspan font-style="italic">B</tspan>)',31,raw=True))
    info = json.dumps({k:{'t':t,'b':b} for k,(t,b) in INFO.items()})
    add(f'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">{info}</script></div>')
    return ''.join(parts)


if __name__ == '__main__':
    (SITE/'example/figure77.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.7 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure77-1">
<style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style>
<main><h1>Figure 7.7 · Original and interactive reconstruction</h1>
<h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="608" alt="Original Figure 7.7">
<h2>Interactive reconstruction</h2>{fig77()}</main>
<script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure77-1';mountNative();</script>
</html>''')
