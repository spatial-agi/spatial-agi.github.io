"""Install the approved diagrams in the checked-in reader pages."""
import re

from figures41_42_native import ROOT, SOURCES, render

STYLE = '<link rel="stylesheet" href="/assets/css/figures41-42.css?v=approved4142">'


def main():
    for number, source in SOURCES.items():
        section = number[-1]
        page = ROOT / f'read/4.{section}/index.html'
        html = page.read_text()
        opening = rf'(<figure id="Ch4\.F{section}" class="ltx_figure)(?: native)?(">)'
        image = rf'<img\b(?=[^>]*\bsrc="{re.escape(source)}")[^>]*>'
        start = re.search(opening, html)
        if not start:
            raise ValueError(f'Missing Figure 4.{section} in {page}')
        fragment = render(number, f'Ch4.F{section}.g1')
        caption = html.index('<figcaption', start.end())
        content = html[start.end():caption].strip()
        if not re.fullmatch(image, content) and 'data-nf="f4142"' not in content:
            raise ValueError(f'Unexpected Figure 4.{section} content in {page}')
        updated = html[:start.start()] + start[1] + ' native' + start[2] + fragment + '\n' + html[caption:]
        if STYLE not in updated:
            updated = updated.replace('</head>', f'{STYLE}\n</head>', 1)
        updated, count = re.subn(r'(src="/assets/js/reader\.js)(?:\?[^\"]*)?"', r'\1?v=approved4142"', updated)
        if count != 1:
            raise ValueError(f'Missing or duplicated reader script in {page}')
        if updated != html:
            page.write_text(updated)


if __name__ == '__main__':
    main()
