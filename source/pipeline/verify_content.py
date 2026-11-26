"""Validate a content build against PDF metadata and approved visual inputs."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import html
from book_source import DIST, HERE, SITE_ROOT


def verify():
    errors=[]
    toc=json.loads((DIST/'data/toc.json').read_text())
    chapters=[c for p in toc['parts'] for c in p['chapters']]
    sections=[s for c in chapters for s in c['sections']]
    pdf=json.loads((HERE/'data/pdf_destinations.json').read_text())
    for s in sections:
        target=pdf.get('section.'+s['num'])
        if not target or int(target['page'])!=s['page']:errors.append(('section pagination',s))
    expected_sections={k[len('section.'):] for k in pdf if re.fullmatch(r'section\.\d+\.\d+', k)}
    if {s['num'] for s in sections}!=expected_sections:errors.append(('section inventory',len(sections),len(expected_sections)))
    refs=json.loads((DIST/'data/refs.json').read_text());pdfcites=json.loads((HERE/'data/pdf_citations.json').read_text())
    if {k:v['n'] for k,v in refs.items()}!=pdfcites:errors.append(('bibliography numbering mismatch',))
    documents={}
    for p in DIST.rglob('*.html'):
        documents['/'+str(p.relative_to(DIST))]=html.parse(str(p))
    ids={p:set(d.xpath('//@id')) for p,d in documents.items()}
    for path,doc in documents.items():
        for a in doc.xpath('//a[@href]|//link[@href]|//script[@src]|//img[@src]'):
            raw=a.get('href') or a.get('src')
            u=urlsplit(raw)
            if u.scheme or u.netloc or not u.path.startswith('/'):continue
            dest=unquote(u.path)
            file=DIST/dest.lstrip('/')
            if dest.endswith('/'):file=file/'index.html'
            if not file.is_file():errors.append(('missing file',path,raw));continue
            key='/'+str(file.relative_to(DIST))
            if u.fragment and key in ids and unquote(u.fragment) not in ids[key]:
                # Interactive SVGs and the home book map create targets in JS.
                if a.get('class')=='xref':errors.append(('missing cross-reference anchor',path,raw))
        for a in doc.xpath('//a[@class="cite"]'):
            k=a.get('data-k')
            if k not in refs:errors.append(('missing citation',path,k))
            elif ''.join(a.itertext()).strip().isdigit() and int(''.join(a.itertext()).strip())!=refs[k]['n']:errors.append(('wrong citation number',path,k))
    approved=json.loads((HERE/'data/approved_figure_bodies.json').read_text());actual={}
    for p in (DIST/'read').glob('*/index.html'):
        for m in re.finditer(r'(<figure\b[^>]*\bid="([^"]+)"[^>]*>)(.*?)(?=<figcaption\b)',p.read_text(),re.S):
            if 'ltx_figure' in m[1]:actual[m[2]]=m[1]+m[3]
    if approved!=actual:errors.append(('approved figure bodies changed',))
    for folder in ['css','js','fonts','img']:
        for p in (DIST/'assets'/folder).rglob('*'):
            if p.is_file():
                source=SITE_ROOT/'assets'/folder/p.relative_to(DIST/'assets'/folder)
                if source.exists() and hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(source.read_bytes()).digest():errors.append(('visual asset changed',str(source)))
    result=dict(parts=len(toc['parts']),chapters=len(chapters),sections=len(sections),references=len(refs),preserved_figures=len(actual),html_pages=len(documents),errors=errors)
    (HERE/'build/content_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2)[:14000])
    if errors:raise SystemExit(1)
    return result

if __name__=='__main__':verify()
