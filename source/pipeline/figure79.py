"""Figure 7.9 reconstructed in the original 2000 x 606 coordinate system."""
from html import escape
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
ORIGINAL = 'assets/figures/figures/part3/section7/explicit_structured_neural_reasoning_task.webp'
INFO = {
    'vqa': ('Program-style VQA', 'The query is parsed into nested filters and a left-of relation, then executed over the object scene. Two red cubes satisfy the program.'),
    'graph': ('Scene-graph traversal', 'The query asks what is on top of the table. A state-machine reasoner follows the table-to-cup edge, whose predicted relation has confidence 0.92.'),
    'program': ('Visual program execution', 'Generated code locates the zebra and calls a captioning tool. The tool chain returns a grounded description of its black and white stripes.'),
}


def fig79():
    out = []; add = out.append

    def text(x, y, value, size=27, cls='', anchor='middle', raw=False):
        add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" class="f79-{cls}">{value if raw else escape(value)}</text>')

    def path(d, cls='ink', arrow=False):
        marker = ' marker-end="url(#f79-arrow)"' if arrow else ''
        add(f'<path d="{d}" class="f79-{cls}"{marker}/>')

    def rect(x, y, w, h, cls='box', rx=7):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="f79-{cls}"/>')

    def image(name, x, y, w, h):
        add(f'<image href="/assets/img/figs/f79/{name}.png" x="{x}" y="{y}" width="{w}" height="{h}"/>')

    def zone(key, bounds, draw):
        add(f'<g class="f79-zone" data-k="{key}" tabindex="0" role="button" aria-pressed="false" aria-label="{escape(INFO[key][0])}">')
        draw()
        x, y, w, h = bounds
        add(f'<rect class="f79-hit" x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/></g>')

    add('<div class="nf nf-79" data-nf="79" data-pagefind-ignore="all"><svg class="nf-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 606" role="group" aria-label="Figure 7.9: representative tasks for explicit structured neural reasoning"><defs>')
    add('<marker id="f79-arrow" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="9" refX="8.5" refY="4.5" orient="auto"><path d="M1 1L8.5 4.5L1 8" fill="none" stroke="#111" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')
    add('<rect width="2000" height="606" fill="#fff"/><g class="f79-scaffold">')
    for x, w in ((14, 598), (626, 644), (1284, 702)):
        add(f'<rect x="{x}" y="13" width="{w}" height="580" rx="11" class="f79-panel"/>')
    text(313, 62, '1. Program-style VQA compositional scenes', 27, 'heading')
    text(948, 62, '2. Scene-graph state-machine traversal', 27, 'heading')
    text(1635, 62, '3. LLM-generated visual program execution', 27, 'heading')
    add('</g>')

    def vqa():
        text(313, 112, 'Query: How many red cubes are to', 27)
        text(313, 148, 'the left of the green sphere?', 27)
        image('a-program-vqa/scene', 34, 163, 554, 161)
        rect(64, 347, 488, 193, 'program-box', 18)
        lines = [
            ('count(filter_color(red,', 77, 377),
            ('filter_shape(cube,', 99, 408),
            ('relate(left_of,', 122, 439),
            ('filter_color(green,', 144, 470),
            ('filter_shape(sphere,scene)))))', 166, 501),
        ]
        for value, x, y in lines:
            text(x, y, value, 25, anchor='start')
        text(268, 571, 'Answer:', 26, anchor='end')
        text(277, 571, '2', 27, 'answer', anchor='start')
    zone('vqa', (20, 78, 586, 501), vqa)

    def graph():
        text(948, 115, 'Query: What is on top of the table?', 27)
        image('b-scene-graph/table-scene', 636, 207, 287, 277)
        path('M934 163V501', 'divider')
        # Relation graph: nodes and directed predicates are all frontend geometry.
        path('M1100 333V230', 'edge', True)
        path('M1083 353L1018 454', 'edge', True)
        path('M1117 353L1180 454', 'edge', True)
        path('M1035 479H1167', 'edge', True)
        for x, y, label in ((1100, 190, 'cup'), (1100, 333, 'table'), (1000, 478, 'chair'), (1208, 478, 'book')):
            add(f'<circle cx="{x}" cy="{y}" r="40" class="f79-node"/>')
            text(x, y + 9, label, 26)
        text(1142, 252, 'on', 24)
        text(1142, 280, '0.92', 24)
        text(973, 388, 'beside', 24)
        text(990, 416, '0.76', 24)
        text(1180, 388, 'on', 24)
        text(1188, 416, '0.88', 24)
        text(1100, 459, 'beside', 24)
        text(1100, 508, '0.81', 24)
        text(824, 569, 'Answer:', 26, anchor='end')
        text(836, 569, 'Cup', 27, 'answer', anchor='start')
    zone('graph', (632, 78, 632, 501), graph)

    def program():
        image('c-visual-program/zebra', 1323, 87, 264, 191)
        rect(1321, 325, 584, 79, 'program-box', 8)
        text(1342, 357, 'obj = find(“zebra”)', 25, anchor='start')
        text(1342, 388, 'ans = obj.crop_to_caption(“animal_pattern”)', 25, anchor='start')
        rect(1314, 464, 126, 77, 'tool-box', 8)
        rect(1488, 464, 126, 77, 'tool-box', 8)
        rect(1664, 464, 136, 77, 'tool-box', 8)
        rect(1828, 428, 143, 150, 'quote-box', 14)
        text(1377, 493, 'Object', 24); text(1377, 522, 'detector', 24)
        text(1551, 493, 'Attribute', 24); text(1551, 522, 'classifier', 24)
        text(1732, 508, 'Captioner', 24)
        text(1899, 465, '“Zebra', 23); text(1899, 495, 'has black', 23)
        text(1899, 524, 'and white', 23); text(1899, 553, 'stripes”', 23)
        path('M1440 502H1480', 'flow', True)
        path('M1614 502H1656', 'flow', True)
        path('M1800 502H1820', 'flow', True)
    zone('program', (1290, 78, 682, 501), program)

    info = json.dumps({k: {'t': title, 'b': body} for k, (title, body) in INFO.items()})
    add(f'</svg><div class="nf-card" hidden role="status"></div><script class="nf-info" type="application/json">{info}</script></div>')
    return ''.join(out)


if __name__ == '__main__':
    preview = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Figure 7.9 comparison</title><link rel="stylesheet" href="/assets/css/site.css?v=figure79-3">
<style>body{{padding:24px;background:#f4f6f8}}main{{max-width:2000px;margin:auto}}h1{{font:600 22px Arial}}h2{{font:500 17px Arial;margin:24px 0 12px}}.original{{display:block;width:100%;height:auto;background:#fff}}.nf{{padding:0;border:0}}@media(max-width:600px){{body{{padding:12px}}}}</style>
<main><h1>Figure 7.9 · Original and interactive reconstruction</h1><h2>Original</h2><img class="original" src="/{ORIGINAL}" width="2000" height="606" alt="Original Figure 7.9"><h2>Interactive reconstruction</h2>{fig79()}</main>
<script type="module">import {{mountNative}} from '/assets/js/nfig.js?v=figure79-3';mountNative();</script></html>'''
    (SITE / 'example/figure79.html').write_text(preview)
