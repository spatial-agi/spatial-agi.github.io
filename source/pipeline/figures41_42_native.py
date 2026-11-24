"""Approved Chapter 4 diagrams used by the reader rebuild."""
from html import escape
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    '41': '/assets/figures/figures/part2/2D_representations.webp',
    '42': '/assets/figures/figures/part2/3d_representation.webp',
}


def render(number, image_id=None):
    fragment = (Path(__file__).parent / f'native/figure{number}.html').read_text().strip()
    attributes = 'data-pagefind-ignore="all"'
    if image_id:
        attributes += f' id="{escape(image_id, quote=True)}"'
    return fragment.replace('<div ', f'<div {attributes} ', 1)


def install_slots(root, native):
    for number, source in SOURCES.items():
        images = root.xpath('.//figure//img[@src=$source and contains(@class,"fig-img")]', source=source)
        for index, image in enumerate(images):
            figure = next(image.iterancestors('figure'))
            slot = f'web:fig{number}-{index}'
            native[slot] = render(number, image.get('id'))
            image.getparent().replace(image, etree.Element('div', {'class': 'nf-slot', 'data-slot': slot}))
            figure.set('class', f'{figure.get("class", "")} native'.strip())
