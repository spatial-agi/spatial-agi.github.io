"""Publish generated content while refusing changes to the site's visual assets."""
import json
import re
import shutil
from pathlib import Path
from book_source import DIST, SITE_ROOT, HERE


def publish():
    for folder in ['css','js','fonts','img']:
        for source in (DIST/'assets'/folder).rglob('*'):
            if not source.is_file():continue
            target=SITE_ROOT/'assets'/folder/source.relative_to(DIST/'assets'/folder)
            if target.exists() and source.read_bytes()!=target.read_bytes():
                raise ValueError(f'Content-only publication would change a visual asset: {target}')
    approved=json.loads((HERE/'data/approved_figure_bodies.json').read_text())
    figures={}
    for source in (DIST/'read').glob('*/index.html'):
        for m in re.finditer(r'(<figure\b[^>]*\bid="([^"]+)"[^>]*>)(.*?)(?=<figcaption\b)',source.read_text(),re.S):
            if 'ltx_figure' in m[1]:figures[m[2]]=m[1]+m[3]
    if approved!=figures:
        raise ValueError('Approved figure renderings differ from the content build')
    files=list(DIST.rglob('*.html'))+list((DIST/'data').glob('*.json'))
    # Only generated site HTML is selected; the build contains no preview or source HTML.
    for source in files:
        target=SITE_ROOT/source.relative_to(DIST)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    for name in ['pagefind']:
        if (DIST/name).exists():shutil.copytree(DIST/name,SITE_ROOT/name,dirs_exist_ok=True)
    pdf=DIST/'assets/spatial-intelligence-handbook.pdf'
    if pdf.exists():shutil.copy2(pdf,SITE_ROOT/'assets/spatial-intelligence-handbook.pdf')
    print(f'Published {len(files)} HTML/data files, PDF and search index; {len(figures)} approved figures preserved')

if __name__=='__main__':publish()
