"""Read numbering and pagination from the supplied PDF, without recompiling the print book.

Run after stage.py + LaTeXML. Named destinations provide the exact citation order
and page numbers. LaTeXML supplies the source-label to element mapping.
"""
import json
import re
from pathlib import Path
from lxml import etree
from pypdf import PdfReader
from book_source import HERE, PDF, METADATA

NS = {'l': 'http://dlmf.nist.gov/LaTeXML'}
XID = '{http://www.w3.org/XML/1998/namespace}id'

def generate():
    METADATA.mkdir(parents=True, exist_ok=True)
    data = HERE / 'data'
    data.mkdir(exist_ok=True)
    reader = PdfReader(PDF)
    destinations = {}
    for key, dest in reader.named_destinations.items():
        index = reader.get_destination_page_number(dest)
        destinations[key] = dict(physical_page=index + 1, page=reader.page_labels[index],
                                 top=float(dest.top or 0), left=float(dest.left or 0))
    def ordered(prefix):
        return sorted(((k,v) for k,v in destinations.items() if k.startswith(prefix)),
                      key=lambda kv: (kv[1]['physical_page'], -kv[1]['top'], kv[1]['left']))
    def citation_key(key):
        key=key[5:]
        # hyperref stores UTF-8 citation keys in PDF names; some PDF readers
        # expose those bytes as Latin-1 (for example rÃ¶mer -> römer).
        try:return key.encode('latin1').decode('utf8')
        except (UnicodeEncodeError,UnicodeDecodeError):return key
    cites = {citation_key(key): i for i,(key,_) in enumerate(ordered('cite.'),1)}
    toc = []
    for kind in ['part','chapter','section','subsection','subsubsection']:
        for key, v in ordered(kind + '.'):
            num = key[len(kind)+1:]
            if num.isdigit() and kind == 'part':num = ['','I','II','III','IV','V'][int(num)]
            toc.append('\\contentsline {' + kind + '}{\\numberline {' + num + '}}{' + v['page'] + '}{' + key + '}')
    (METADATA / 'main.toc').write_text('\n'.join(toc))
    xml = etree.parse(str(HERE / 'build' / 'book.xml'))
    # Figures and tables retain source order within each float type. Unnumbered
    # front-matter tables and the Roman-numbered part openers are included.
    def get_num(el):
        if el is None:return ''
        if el.get('refnum'):return el.get('refnum')
        tag=el.find('l:tags/l:tag[@role="refnum"]',NS)
        return ''.join(tag.itertext()).strip() if tag is not None else ''
    float_pages = {}
    float_numbers = {}
    for kind in ['figure','table']:
        els=xml.xpath('//l:'+kind, namespaces=NS)
        dests=ordered(kind + '.')
        if len(els) != len(dests):
            raise ValueError(f'{kind}: XML {len(els)} != supplied PDF {len(dests)}')
        chapter_counters = {}
        opener = 0
        for el,(anchor,dest) in zip(els,dests):
            float_pages[el.get(XID)] = (anchor,dest)
            if kind == 'figure':
                labs=el.get('labels','')
                is_opener=any(s in labs for s in ['fig:part1-illustration','fig:p2_main','fig:p3_main','fig:p4_main','fig:p5_main'])
                if is_opener:
                    opener += 1
                    float_numbers[el.get(XID)] = ['','I','II','III','IV','V'][opener]
                else:
                    ch=next((p for p in el.iterancestors() if etree.QName(p).localname=='chapter'),None)
                    if ch is not None:
                        n=get_num(ch); chapter_counters[n]=chapter_counters.get(n,0)+1
                        float_numbers[el.get(XID)]=n+'.'+str(chapter_counters[n])
    labels = {}
    for el in xml.iter():
        if not el.get('labels'):continue
        kind=etree.QName(el).localname
        num=float_numbers.get(el.get(XID),get_num(el))
        if not num:
            tag=el.find('l:tags/l:tag[@role="refnum"]',NS)
            if tag is not None:num=''.join(tag.itertext()).strip()
        anchor=kind+'.'+num
        dest=destinations.get(anchor)
        if el.get(XID) in float_pages:
            anchor,dest=float_pages[el.get(XID)]
        elif kind in ['equation','equationgroup']:
            ch=num.split('.')[0]
            matches=[(k,v) for k,v in destinations.items() if k.startswith('equation.'+ch+'.') and k.rsplit('.',1)[-1]==num.rsplit('.',1)[-1]]
            if len(matches)==1:anchor,dest=matches[0]
        title=' '.join(''.join(el.find('l:title',NS).itertext()).split()) if el.find('l:title',NS) is not None else ''
        page=dest['page'] if dest else ''
        for lab in el.get('labels').split():
            labels[lab.removeprefix('LABEL:')]=dict(num=num,page=int(page) if page.isdigit() else None,anchor=anchor,title=title[:200])
    aux=['\\bibcite{'+k+'}{{'+str(n)+'}{}{{}}{{}}}' for k,n in cites.items()]
    aux += ['\\newlabel{'+k+'}{{'+v['num']+'}{'+str(v['page'] or '')+'}{'+v['title'].replace('{','').replace('}','')+'}{'+v['anchor']+'}{}}' for k,v in labels.items()]
    (METADATA/'main.aux').write_text('\n'.join(aux))
    (data/'pdfinfo.txt').write_text(f'Pages: {len(reader.pages)}\n')
    (data/'pdf_destinations.json').write_text(json.dumps(destinations,ensure_ascii=False))
    (data/'pdf_citations.json').write_text(json.dumps(cites,ensure_ascii=False))
    (data/'pdf_source.json').write_text(json.dumps(dict(path=str(PDF),pages=len(reader.pages),metadata={str(k):str(v) for k,v in reader.metadata.items()}),ensure_ascii=False,indent=2))
    print(f'PDF ground truth: {len(reader.pages)} pages, {len(cites)} references, {len(labels)} labels')

if __name__ == '__main__':generate()
