"""Figure 6.28: independently drawn vision-language grounding methods."""
import json
from html import escape
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
INFO = {
    'proposal': {'t': 'Proposal ranking', 'b': 'Candidate regions are generated first, then ranked by how well their visual features match the referring expression. The grid and score chart illustrate this selection process.'},
    'proposal-models': {'t': 'Proposal-based alignment', 'b': 'Deep Fragment aligns visual regions and language fragments. CRF alignment models their compatibility and dependencies when selecting a target.'},
    'composition': {'t': 'Compositional reasoning', 'b': 'A structured expression is decomposed into objects, attributes and relations. Attention and graph or module operations combine these cues to locate the target.'},
    'composition-models': {'t': 'Compositional grounding methods', 'b': 'MAttNet uses modular attention; Dynamic Graph models contextual relations; neural module networks compose reasoning operations.'},
    'end-to-end': {'t': 'End-to-end grounding', 'b': 'Visual features feed an MLP or Transformer that directly predicts the referred bounding box or segmentation mask.'},
    'end-to-end-models': {'t': 'Direct prediction methods', 'b': 'One-Stage and TransVG illustrate direct grounding pipelines that predict the output from visual and language representations.'},
    'pretraining': {'t': 'Grounded pre-training', 'b': 'Web-scale region–caption pairs train a language-conditioned Transformer detector. Its grounded representations support box or mask prediction.'},
    'pretraining-models': {'t': 'Grounded pre-training methods', 'b': 'MDETR, G-DINO, GLIP and RegionCLIP connect region-level visual representations with language through large-scale pre-training.'},
    'foundation': {'t': 'Foundation model grounding', 'b': 'An instruction-conditioned language or multimodal language model interprets the request and produces spatially grounded boxes or masks.'},
    'foundation-models': {'t': 'Grounding with foundation models', 'b': 'PixelLLM, OMG-LLAVA, LISA, Kosmos-2, Ferret-2 and Qwen-VL illustrate grounding capabilities built on language and multimodal foundation models.'},
    'agents': {'t': 'Tool-augmented agents', 'b': 'A language-model orchestrator selects tools such as cropping, zooming and SAM segmentation to inspect the image and ground the request.'},
    'agent-models': {'t': 'Agent-based grounding methods', 'b': 'SegAgent, SAM 3 Agent, DeepEyes and OpenThinkIMG illustrate grounding systems that coordinate visual tools through an agent.'},
}


def fig628():
    out = []
    add = out.append

    def text(x, y, value, size=20):
        add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle">{escape(value)}</text>')

    def lines(x, y, values, size=20, leading=25):
        for i, value in enumerate(values):
            text(x, y + i * leading, value, size)

    def rect(x, y, w, h, cls='module', rx=0):
        add(f'<rect class="f628-{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def path(d, cls='ink'):
        add(f'<path class="f628-{cls}" d="{d}"/>')

    def route(d):
        add(f'<path class="f628-route" d="{d}" marker-end="url(#f628-arrow)"/>')

    def start(key):
        add(f'<g class="f628-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key]["t"])}">')

    def end(x, y, w, h):
        rect(x, y, w, h, 'hit', 4)
        add('</g>')

    def models(key, boxes, hit):
        start(key)
        for x, y, w, h, label in boxes:
            rect(x, y, w, h, 'method', 2)
            text(x + w / 2, y + h / 2 + 7, label, 21)
        end(*hit)

    add('<div class="nf nf-628" data-nf="628" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 417" role="group" aria-label="Figure 6.28: vision-language grounding methodologies"><defs><marker id="f628-arrow" markerUnits="userSpaceOnUse" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 1L6 3.5L0 6Z" fill="#080808"/></marker></defs><rect width="2000" height="417" fill="white"/><g class="f628-scaffold">')
    for x, y, w, h in [(23,3,294,335),(339,3,272,333),(629,3,354,334),(1004,3,394,334),(1415,3,264,334),(1705,2,263,334)]:
        rect(x, y, w, h, 'panel', 18)
    lines(170, 378, ['(i) Proposal ranking'], 24)
    lines(475, 361, ['(ii) Compositional', 'Reasoning'], 24, 30)
    lines(806, 378, ['(iii) End-to-end'], 24)
    lines(1196, 361, ['(iv) Grounded Pre-', 'training'], 24, 30)
    lines(1547, 378, ['(v) Foundation Model'], 24)
    lines(1836, 361, ['(vi) Tool-augmented', 'agents'], 24, 30)
    add('</g>')

    start('proposal')
    add('<image href="/assets/img/figs/f628/i-proposal/steak.png" x="46" y="47" width="99" height="100" preserveAspectRatio="none"/>')
    rect(45,46,100,102,'grid')
    for x in [78,112]: path(f'M{x} 46V148','grid')
    for y in [80,114]: path(f'M45 {y}H145','grid')
    path('M181 49V145H303','axis')
    for x,y,h,cls in [(195,54,91,'bar-blue'),(223,69,76,'bar'),(252,120,25,'bar'),(281,99,46,'bar')]: rect(x,y,12,h,cls)
    text(96,172,'proposals grid',19)
    text(237,172,'ranking bar chart',19)
    end(28,35,283,145)
    models('proposal-models',[(57,197,226,48,'Deep Fragment'),(57,263,226,49,'CRF alignment')],(48,189,245,133))

    start('composition')
    path('M406 58L383 93L359 137M383 93L407 137M406 58L433 93L454 137','tree')
    for x,y,r in [(406,58,10.5),(383,93,10.5),(433,93,10.5),(359,137,10.5),(407,137,10.5),(454,137,10.5)]:
        add(f'<circle class="f628-node" cx="{x}" cy="{y}" r="{r}"/>')
    rect(493,10,103,154,'module',6)
    lines(545,25,['Attention','module'],20,25)
    add('<image href="/assets/img/figs/f628/ii-compositional/attention-heatmap.png" x="506" y="52" width="69" height="107" preserveAspectRatio="none"/>')
    end(346,7,255,164)
    models('composition-models',[(366,180,227,48,'MAttNet'),(366,230,227,47,'Dynamic Graph'),(366,280,227,48,'NMN')],(355,175,245,156))

    start('end-to-end')
    # Three staggered feature maps, with independent top and side faces.
    for x,y,w,h,depth in [(642,70,30,115,50),(682,70,19,91,32),(710,82,15,57,25)]:
        path(f'M{x} {y}l{depth} {-depth}h{w}l{-depth} {depth}Z','feature-top')
        path(f'M{x+w} {y}l{depth} {-depth}v{h}l{-depth} {depth}Z','feature-side')
        rect(x,y,w,h,'feature')
    route('M752 97H777')
    rect(777,20,120,154,'module',7)
    lines(837,72,['MLP','/','Transformer'],20,25)
    route('M898 100H922')
    lines(950,81,['Box','/','mask'],20,25)
    end(636,13,338,176)
    models('end-to-end-models',[(693,196,227,49,'One-Stage'),(693,257,227,49,'TransVG')],(683,190,247,124))

    start('pretraining')
    path('M1020 43V150C1020 174 1166 174 1166 150V43','module')
    add('<ellipse class="f628-module" cx="1093" cy="43" rx="73" ry="18"/>')
    lines(1093,93,['Web-scale','region-caption','pairs'],20,24)
    route('M1167 100H1191')
    rect(1194,18,121,154,'module',7)
    lines(1254,69,['Transformer','detector','(instruction','conditioned)'],20,25)
    route('M1316 100H1339')
    lines(1361,83,['Box','/','mask'],20,25)
    end(1012,13,375,167)
    models('pretraining-models',[(1027,201,151,48,'MDETR'),(1212,201,152,48,'G-DINO'),(1027,263,151,49,'GLIP'),(1212,265,152,48,'RegionCLIP')],(1016,192,361,131))

    start('foundation')
    rect(1440,23,120,122,'module',7)
    lines(1500,67,['LLM / MLLM','(instruction','conditioned)'],20,25)
    route('M1561 87H1585')
    lines(1615,67,['Box','/','mask'],20,25)
    end(1428,15,238,136)
    models('foundation-models',[(1422,158,118,48,'PixelLLM'),(1553,158,118,48,'OMG-LLAVA'),(1424,217,116,48,'LISA'),(1553,217,118,48,'Kosmos-2'),(1424,276,116,49,'Ferret-2'),(1553,276,118,49,'Qwen-VL')],(1419,153,255,176))

    start('agents')
    rect(1713,31,120,154,'module',7)
    lines(1774,88,['LLM','orchestrator','(agent)'],20,25)
    for x,y,w,h,label in [(1857,21,101,48,'Crop'),(1857,85,101,48,'Zoom-in'),(1857,149,101,48,'SAM')]:
        rect(x,y,w,h,'module',2)
        text(x+w/2,y+30,label,20)
    for d in ['M1834 67L1857 45','M1834 111H1857','M1834 151L1857 174']: route(d)
    end(1710,15,253,185)
    models('agent-models',[(1717,206,96,48,'SegAgent'),(1831,206,131,48,'SAM 3 Agent'),(1709,272,104,40,'DeepEyes'),(1816,272,148,40,'OpenThinkIMG')],(1708,203,257,117))

    add('</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">'+json.dumps(INFO)+'</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    (SITE/'example/figure628.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/assets/css/site.css?v=figure628-1"><title>Figure 6.28 comparison</title><style>body{padding:24px;background:#f4f6f8}main{max-width:2000px;margin:auto}h1{font:600 22px Arial}h2{font:500 17px Arial;margin:24px 0 12px}.original{display:block;width:100%;background:#fff}.nf{padding:0;border:0}@media(max-width:600px){body{padding:12px}}</style><main><h1>Figure 6.28 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/assets/figures/figures/part3/section6/visual_language_graounding_method.webp" alt="Original Figure 6.28"><h2>Interactive reconstruction</h2>'''+fig628()+'''</main><script type="module">import {mountNative} from '/assets/js/nfig.js?v=figure628-1';mountNative();</script></html>''')
