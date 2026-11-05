#!/usr/bin/env python3
"""Import the LaTeX book into the static Contents reader (no server required).

Install dependencies: python3 -m pip install -r scripts/requirements-book.txt
Run: python3 scripts/import_book.py [--source ../Spatial_Intelligence_Book_2025_v12]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]


def strip_comments(text):
    return '\n'.join(
        re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in text.splitlines())


def group(text, pos):
    """Read a balanced TeX group, preserving nested and escaped braces."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != '{':
        raise ValueError(f'Expected TeX group near {text[pos:pos+100]!r}')
    start, depth = pos + 1, 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        depth += (text[pos] == '{') - (text[pos] == '}')
        if depth == 0:
            return text[start:pos], pos + 1
        pos += 1
    raise ValueError(f'Unclosed TeX group near {text[start:start+100]!r}')


def transform_command(text, name, count, callback):
    pattern = re.compile(r'\\' + re.escape(name) + r'(?![A-Za-z])')
    out, pos = [], 0
    while match := pattern.search(text, pos):
        out.append(text[pos:match.start()])
        end, args = match.end(), []
        try:
            for _ in range(count):
                arg, end = group(text, end)
                args.append(arg)
        except ValueError:
            out.append(match.group())
            pos = match.end()
            continue
        out.append(callback(*args))
        pos = end
    return ''.join(out) + text[pos:]


class Importer:
    def __init__(self, source, output):
        self.source, self.output = source, output
        self.files = []
        self.assets = {}
        self.references = {}
        self.citation_count = 0
        self.warnings = []
        self.raw = Counter()

    def expand(self, path, stack=()):
        path = path.resolve()
        if not path.is_relative_to(self.source):
            raise ValueError(f'Input escapes source directory: {path}')
        if path in stack:
            raise ValueError(f'Cyclic input: {path}')
        if not path.is_file():
            raise FileNotFoundError(f'Missing LaTeX input: {path}')
        self.files.append(str(path.relative_to(self.source)))
        text = strip_comments(path.read_text(encoding='utf-8'))
        # Ignore the print-only preamble; retain all actual document content.
        if path == self.source / 'main.tex':
            text = text.split(r'\begin{document}', 1)[1].split(r'\end{document}', 1)[0]
        pattern = r'\\(?:input|include)\b\s*(?:\{([^}]+)\}|([^\s{}]+))'
        def replace(m):
            name = (m[1] or m[2]).strip()
            if not Path(name).suffix:
                name += '.tex'
            target = self.source / name
            if not target.is_file():
                target = path.parent / name
            return '\n' + self.expand(target, (*stack, path)) + '\n'
        return re.sub(pattern, replace, text)

    def prepare(self, text):
        # These commands carry manuscript/layout metadata, not reader content.
        for name in ('RespondAuthor', 'scott', 'zy', 'wsq', 'jp'):
            text = transform_command(text, name, 1, lambda _: '')
        text = transform_command(text, 'FramedInitial', 2, lambda a, b: a + b)
        text = transform_command(text, 'resizebox', 3, lambda a, b, body: body)
        text = transform_command(text, 'scalebox', 2, lambda scale, body: body)
        text = transform_command(text, 'tablestyle', 2, lambda a, b: '')
        # Make custom paragraph and table macros readable to Pandoc.
        for name in ('blue', 'red', 'green', 'orange', 'tokenblue', 'bang'):
            text = transform_command(text, name, 1, lambda body: r'\textbf{' + body + '}')
        for name in ('better', 'betterinv', 'worse', 'worseinv'):
            arrow = r'$\uparrow$ ' if name in ('better', 'worseinv') else r'$\downarrow$ '
            text = transform_command(text, name, 1, lambda body, a=arrow: a + body)
        for name, value in {'eg': 'e.g.', 'ie': 'i.e.', 'etc': 'etc.', 'etal': 'et al.',
                            'vs': 'vs.', 'wrt': 'w.r.t.', 'dof': 'd.o.f.', 'iid': 'i.i.d.',
                            'checkmark': '✓', 'cmark': '✓', 'crossmark': '✗', 'xmark': '✗',
                            'ours': 'VL-Cogito'}.items():
            text = re.sub(r'\\' + name + r'\b\s*(?:\{\})?', lambda m: value + ' ', text)
        text = re.sub(r'\\(?:bibliographystyle|bibliography)\{[^}]*\}', '', text)
        text = re.sub(r'\\(?:maketitle|tableofcontents)\b', '', text)
        text = re.sub(r'\\setcounter\{tocdepth\}\{[^}]*\}', '', text)
        text = re.sub(r'\\phantomsection\{[^}]*\}|\\(?:clearpage|newpage|noindent)\b', '', text)
        # TeX custom L/R/C/x/y/z columns have the same alignment semantics as p{}.
        text = re.sub(r'([LRCxyz])\{([^{}]*)\}', r'p{\2}', text)
        text = re.sub(r'\\(?:rowcolor|cellcolor)(?:\[[^\]]*\])?\{[^}]*\}', '', text)
        text = re.sub(r'\\(?:cdashline|cmidrule)(?:\([^)]*\))?\{[^}]*\}', r'\\hline', text)
        text = re.sub(r'\\(?:shline|hshline)\b', r'\\hline', text)
        # A named opening page makes the abstract and title-page illustration navigable.
        text = r'\chapter*{Overview}' + '\n' + text
        return text

    def copy_asset(self, value):
        import pymupdf
        value = unquote(value)
        if value in self.assets:
            return self.assets[value]
        source = (self.source / value).resolve()
        if not source.suffix:
            source = next((source.with_suffix(s) for s in ('.pdf', '.png', '.jpg', '.jpeg', '.svg')
                           if source.with_suffix(s).exists()), source)
        if not source.is_relative_to(self.source) or not source.is_file():
            raise FileNotFoundError(f'Missing/invalid figure: {value}')
        relative = source.relative_to(self.source)
        if source.suffix.lower() == '.pdf':
            target = self.output / 'book-assets' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            preview = target.with_suffix('.png')
            if not preview.exists() or preview.stat().st_mtime < source.stat().st_mtime:
                with pymupdf.open(source) as doc:
                    page = doc[0]
                    scale = min(3, 2400 / max(page.rect.width, page.rect.height))
                    page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).save(preview)
            result = preview.relative_to(self.output).as_posix()
        else:
            target = self.output / 'book-assets' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or source.stat().st_mtime_ns != target.stat().st_mtime_ns:
                shutil.copy2(source, target)
            result = target.relative_to(self.output).as_posix()
        self.assets[value] = result
        return result

    def parse_bibliography(self):
        text = (self.source / 'main.bib').read_text(encoding='utf-8')
        entry_start = re.compile(r'@([A-Za-z]+)\s*([({])\s*([^,\s]+)\s*,')
        pos = 0
        while match := entry_start.search(text, pos):
            key = match.group(3)
            open_char = match.group(2)
            close_char = '}' if open_char == '{' else ')'
            depth, quote_mode, i = 1, False, match.end()
            while i < len(text) and depth:
                char = text[i]
                if char == '"' and (i == 0 or text[i - 1] != '\\'):
                    quote_mode = not quote_mode
                elif not quote_mode:
                    if char == open_char:
                        depth += 1
                    elif char == close_char:
                        depth -= 1
                i += 1
            body = text[match.end():i - 1]
            fields = {}
            field_pattern = re.compile(r'(?im)(?:^|,)\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*')
            for field in field_pattern.finditer(body):
                start = field.end()
                while start < len(body) and body[start].isspace():
                    start += 1
                if start >= len(body):
                    continue
                if body[start] == '{':
                    value, _ = group(body, start)
                elif body[start] == '"':
                    end = start + 1
                    while end < len(body) and (body[end] != '"' or body[end - 1] == '\\'):
                        end += 1
                    value = body[start + 1:end]
                else:
                    end = re.search(r'\s*,\s*[A-Za-z][A-Za-z0-9_-]*\s*=|\s*$', body[start:])
                    value = body[start:start + end.start() if end else len(body)]
                fields[field.group(1).lower()] = re.sub(r'\\[a-zA-Z]+\s*', ' ', value).replace('{', '').replace('}', '').strip()
            author = fields.get('author', 'Unknown author').replace(' and others', ' et al.')
            surnames = [name.strip().split(',')[0].split()[-1] for name in author.split(' and ') if name.strip()]
            short_author = (surnames[0] + ' et al.' if len(surnames) > 2 else
                            ' & '.join(surnames) if surnames else 'Unknown author')
            item = {
                'key': key, 'type': match.group(1).lower(), 'title': fields.get('title', key),
                'author': author, 'short_author': short_author, 'year': fields.get('year', 'n.d.'),
                'venue': fields.get('journal') or fields.get('booktitle') or fields.get('publisher', ''),
                'doi': fields.get('doi', ''), 'url': fields.get('url', ''),
            }
            self.references[key] = item
            pos = max(i, match.end())

    def citation_html(self, citations):
        items = []
        for citation in citations:
            key = citation.get('citationId', '')
            item = self.references.get(key)
            if not item:
                item = {'key': key, 'title': key, 'author': 'Reference not found in main.bib',
                        'short_author': key, 'year': 'n.d.', 'venue': '', 'doi': '', 'url': ''}
                self.warnings.append(f'Citation key not found in main.bib: {key}')
            items.append(item)
        self.citation_count += len(items)
        label = '; '.join(f'{item["short_author"]}, {item["year"]}' for item in items)
        payload = html.escape(json.dumps(items, ensure_ascii=False, separators=(',', ':')), quote=True)
        return {'t': 'RawInline', 'c': ['html', f'<button type="button" class="citation-bubble" data-citation="{payload}" aria-haspopup="dialog">({html.escape(label)})</button>']}

    def ast_filter(self, value):
        if isinstance(value, list):
            return [self.ast_filter(v) for v in value]
        if not isinstance(value, dict):
            return value
        kind, content = value.get('t'), value.get('c')
        if kind == 'Cite':
            return self.citation_html(content[0])
        if kind == 'Image':
            content[2][0] = self.copy_asset(content[2][0])
        if kind in ('RawBlock', 'RawInline') and content[0] == 'latex':
            raw = content[1]
            # Never silently discard unsupported source content.
            self.raw[raw[:100]] += 1
            if kind == 'RawBlock':
                return {'t': 'RawBlock', 'c': ['html', '<details class="latex-fallback"><summary>Original LaTeX</summary><pre>' + html.escape(raw) + '</pre></details>']}
            return {'t': 'RawInline', 'c': ['html', '<code class="latex-inline">' + html.escape(raw) + '</code>']}
        return {k: self.ast_filter(v) for k, v in value.items()}

    def build_reader(self, converted):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(converted, 'html.parser')
        # Pandoc outputs PDF figures as embeds; all figures are converted to native images.
        for embed in soup.select('embed'):
            img = soup.new_tag('img', src=self.copy_asset(embed['src']))
            embed.replace_with(img)
        for img in soup.select('img'):
            img['loading'] = 'lazy'
            img['decoding'] = 'async'
            if not img.get('alt'):
                figure = img.find_parent('figure')
                caption = figure.find('figcaption') if figure else None
                img['alt'] = caption.get_text(' ', strip=True) if caption else Path(img['src']).stem
        for table in list(soup.select('table')):
            wrapper = soup.new_tag('div', attrs={'class': 'book-table-scroll', 'tabindex': '0'})
            table.wrap(wrapper)
        for heading in soup.select('h1,h2,h3,h4,h5,h6'):
            if not heading.get('id'):
                heading['id'] = 'heading-' + hashlib.sha256(str(heading).encode()).hexdigest()[:12]
        # Each part introduction and each chapter is an independent reader page.
        pages, page, chapter_no, part_no = [], None, 0, 0
        for node in list(soup.contents):
            if node.name in ('h1', 'h2'):
                is_part = node.name == 'h1' and node.get_text(strip=True) not in ('Overview', 'Preface')
                if is_part:
                    part_no += 1
                is_chapter = node.name == 'h2' and node.get_text(strip=True) not in ('Overview', 'Preface')
                if is_chapter:
                    chapter_no += 1
                    node.insert(0, f'Chapter {chapter_no}: ')
                page = {'id': node['id'], 'title': node.get_text(' ', strip=True),
                        'part': part_no, 'is_part': is_part, 'nodes': []}
                pages.append(page)
                node.name = 'h1'
                del node['id']  # The outer section owns the same unique anchor.
            if page:
                page['nodes'].append(node)
        # Citeproc appends the entire bibliography in one div, give it its own reader page.
        for p in pages:
            for node in list(p['nodes']):
                if getattr(node, 'get', lambda *_: None)('id') == 'refs':
                    p['nodes'].remove(node)
                    pages.append({'id': 'references', 'title': 'References', 'part': 0,
                                  'is_part': False, 'nodes': ['<h1>References</h1>', node]})
        parts, front = {}, []
        for p in pages:
            if p['part']:
                parts.setdefault(p['part'], []).append(p)
            else:
                front.append(p)
        def link(p):
            return f'<a class="toc-link" href="#{html.escape(p["id"], quote=True)}">{html.escape(p["title"])}</a>'
        toc = ''.join(link(p) for p in front)
        for group_pages in parts.values():
            title = group_pages[0]['title']
            toc += f'<details class="toc-book-part"><summary>{html.escape(title)}</summary>'
            for p in group_pages:
                headings = [n for n in p['nodes'] if getattr(n, 'name', '') in ('h3', 'h4')]
                toc += f'<details class="toc-book-chapter"><summary>{html.escape(p["title"])}</summary>' if headings else ''
                toc += link(p)
                for heading in headings:
                    toc += f'<a class="toc-link toc-subheading" href="#{html.escape(heading["id"], quote=True)}">{html.escape(heading.get_text(" ", strip=True))}</a>'
                toc += '</details>' if headings else ''
            toc += '</details>'
        sections = []
        for i, p in enumerate(pages):
            body = ''.join(str(n) for n in p['nodes'])
            nav = '<nav class="section-pagination" aria-label="Chapter navigation">'
            for j, cls, label in ((i-1, 'nav-prev', '← Previous'), (i+1, 'nav-next', 'Next →')):
                if 0 <= j < len(pages):
                    nav += f'<a class="{cls}" href="#{html.escape(pages[j]["id"], quote=True)}">{label}: {html.escape(pages[j]["title"])}</a>'
            nav += '</nav>'
            sections.append(f'<section id="{html.escape(p["id"], quote=True)}" class="content-section imported-chapter{" active" if i == 0 else ""}">{body}{nav}</section>')
        template = (self.output / 'contents.html').read_text()
        template = re.sub(r'\s*<script src="https://polyfill.io/[^\"]+"></script>', '', template)
        template = re.sub(r'<nav class="toc-nav">.*?</nav>', '<nav class="toc-nav" aria-label="Book contents">' + toc + '</nav>', template, count=1, flags=re.S)
        template = re.sub(r'(<main class="content-area" id="contentArea">).*?(</main>)', lambda m: m[1] + '\n' + '\n'.join(sections) + '\n' + m[2], template, count=1, flags=re.S)
        template = template.replace('<div class="sidebar-header">', '<div class="sidebar-header">', 1)
        # Mobile contents control must live outside the off-screen sidebar.
        if 'id="readerMenuToggle"' not in template:
            template = template.replace('<div class="reader-container">', '<button id="readerMenuToggle" class="reader-menu-toggle" aria-controls="sidebar" aria-expanded="false">☰ Contents</button>\n    <div class="reader-container">')
        return template, pages

    def run(self, pandoc):
        from bs4 import BeautifulSoup
        raw = self.expand(self.source / 'main.tex')
        prepared = self.prepare(raw)
        def convert(args, data):
            result = subprocess.run([pandoc, *args], input=data, text=True, capture_output=True, cwd=self.source)
            if result.returncode:
                raise RuntimeError(result.stderr)
            if result.stderr:
                self.warnings.extend(result.stderr.splitlines())
            return result.stdout
        with tempfile.TemporaryDirectory(prefix='spatial-book-') as tmp:
            # Keep bibliography conversion separate: citeproc is prohibitively slow on
            # this large BibTeX file. The reader still receives a complete references page.
            self.parse_bibliography()
            ast = json.loads(convert(['-f', 'latex', '-t', 'json'], prepared))
            ast = self.ast_filter(ast)
            converted = convert(['-f', 'json', '-t', 'html5', '--mathjax'], json.dumps(ast))
            bib_entries = []
            cited_keys = {key for match in re.finditer(r'data-citation="([^"]+)"', converted)
                          for item in json.loads(html.unescape(match.group(1))) for key in [item['key']]}
            for key, item in self.references.items():
                if key not in cited_keys:
                    continue
                details = f'<strong>{html.escape(item["title"])}</strong>. {html.escape(item["author"])} ({html.escape(item["year"])}).'
                if item['venue']:
                    details += f' <em>{html.escape(item["venue"])}</em>.'
                if item['doi']:
                    doi_url = 'https://doi.org/' + quote(item['doi'], safe='/')
                    details += f' <a href="{html.escape(doi_url, quote=True)}">doi:{html.escape(item["doi"])}</a>.'
                elif item['url']:
                    details += f' <a href="{html.escape(item["url"], quote=True)}">Link</a>.'
                bib_entries.append(f'<li id="ref-{html.escape(key, quote=True)}">{details}</li>')
            converted += '<section id="references"><h1>References</h1><ol class="references-list">' + ''.join(bib_entries) + '</ol></section>'
        rendered, pages = self.build_reader(converted)
        soup = BeautifulSoup(rendered, 'html.parser')
        ids = [tag['id'] for tag in soup.select('[id]')]
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        if duplicates:
            raise ValueError(f'Duplicate HTML IDs: {duplicates[:20]}')
        broken = sorted({unquote(a['href'][1:]) for a in soup.select('a[href^="#"]')
                         if a['href'][1:] and unquote(a['href'][1:]) not in ids})
        # Source labels may be unresolved in the manuscript; keep a precise report.
        for target in broken:
            self.warnings.append(f'Unresolved source reference: {target}')
            # Pandoc does not always preserve labels attached to display equations.
            # Add a stable invisible anchor so every source cross-reference remains navigable.
            link = next((a for a in soup.find_all('a') if a.get('href') == '#' + target), None)
            section = link.find_parent('section') if link else None
            if section:
                anchor = soup.new_tag('a', id=target, attrs={'class': 'reference-anchor', 'aria-hidden': 'true'})
                section.insert(0, anchor)
        for img in soup.select('img[src]'):
            if not (self.output / unquote(img['src'])).is_file():
                raise FileNotFoundError(img['src'])
        rendered = str(soup)
        self.output.joinpath('contents.html').write_text(rendered)
        report = {
            'source': self.source.name, 'input_files': list(dict.fromkeys(self.files)),
            'reader_pages': [{'id': p['id'], 'title': p['title']} for p in pages],
            'assets': self.assets, 'figures': len(soup.select('figure')), 'tables': len(soup.select('table')),
            'equations': len(soup.select('.math')), 'references': len(soup.select('.references-list li')),
            'citation_instances': len(soup.select('.citation-bubble')),
            'citation_keys': len(self.references),
            'unsupported_latex': dict(self.raw), 'warnings': self.warnings,
        }
        (self.output / 'book-import-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(f'Imported {len(report["input_files"])} LaTeX files into {len(pages)} reader pages; '
              f'{report["figures"]} figures, {report["tables"]} tables, '
              f'{report["equations"]} math expressions, {report["references"]} references.')
        print(f'Warnings: {len(self.warnings)}; LaTeX fallbacks: {sum(self.raw.values())}. See book-import-report.json.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent / 'Spatial_Intelligence_Book_2025_v12')
    parser.add_argument('--output', type=Path, default=ROOT)
    parser.add_argument('--pandoc', help='Optional path to a Pandoc executable')
    args = parser.parse_args()
    try:
        import bs4, pymupdf
        pandoc = args.pandoc or shutil.which('pandoc')
        if not pandoc:
            import pypandoc
            pandoc = pypandoc.get_pandoc_path()
        Importer(args.source.resolve(), args.output.resolve()).run(pandoc)
    except ImportError as exc:
        sys.exit(f'Missing dependency ({exc}). Run: python3 -m pip install -r scripts/requirements-book.txt')
    except (OSError, ValueError, RuntimeError) as exc:
        sys.exit(f'Book import failed: {exc}')


if __name__ == '__main__':
    main()
