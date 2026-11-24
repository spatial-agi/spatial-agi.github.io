"""Install approved fragments in the served reader without requiring LaTeXML data.

The full build also installs these fragments through figures121_145_native.
Only figure image markup and the batch stylesheet link change here.
"""
from pathlib import Path
from lxml import html
import re
from figures121_145_native import ROOT, SOURCES, render

def main():
    counts = dict.fromkeys((e['id'] for e in SOURCES), 0)
    for page in sorted((ROOT / 'read').glob('*/index.html')):
        source = page.read_text()
        for entry in SOURCES:
            pattern = re.compile(r'<figure\b[^>]*\bid="' + re.escape(entry['id']) + r'"[^>]*>.*?</figure>', re.S)
            def replace(match):
                original = match.group(); node = html.fromstring(original)
                image = node.xpath('.//img[contains(@class,"fig-img")]')
                if not image:
                    if node.xpath('.//*[@data-nf="f1214"]'): counts[entry['id']] += 1
                    return original
                assert len(image) == len(entry['images']), entry['id']
                opening = original[:original.index('>') + 1]
                if not re.search(r'\bnative\b', node.get('class', '')):
                    opening = re.sub(r'class="([^"]*)"', lambda m: 'class="' + m[1] + ' native"', opening)
                body = original[original.index('>') + 1:]
                imgs = list(re.finditer(r'<img\b[^>]*>', body))
                targets = [m for m in imgs if any(m.group().find(i['src']) >= 0 for i in entry['images'])]
                assert len(targets) == len(image), entry['id']
                for index, m in reversed(list(enumerate(targets))):
                    body = body[:m.start()] + (render(entry['chapter'], entry['number']) if index == 0 else '') + body[m.end():]
                changed = opening + body
                old_cap = re.search(r'<figcaption\b.*?</figcaption>', original, re.S).group()
                assert old_cap in changed
                counts[entry['id']] += 1
                return changed
            source = pattern.sub(replace, source)
        if 'data-nf="f1214"' in source and 'href="/assets/css/figures121-145.css' not in source:
            source = source.replace('</head>', '<link rel="stylesheet" href="/assets/css/figures121-145.css?v=approved1214">\n</head>')
        if source != page.read_text(): page.write_text(source)
    assert all(counts.values()), counts
    for k, count in counts.items(): print(k, count)
if __name__ == '__main__': main()
