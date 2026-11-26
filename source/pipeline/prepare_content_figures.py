"""Reuse approved web assets during content-only builds, preserving their pixels."""
import json
from pathlib import Path
from lxml import etree
from PIL import Image
from book_source import HERE, SITE_ROOT

root=etree.parse(str(HERE/'build/book.xml'))
ns={'l':'http://dlmf.nist.gov/LaTeXML'}
figmap={}
missing=[]
for el in root.xpath('//l:graphics',namespaces=ns):
    graphic=el.get('graphic')
    if not graphic:continue
    path=Path(graphic)
    if path.suffix.lower() in ['.pdf','.png','.jpg','.jpeg','.webp']:path=path.with_suffix('')
    # Keep dots within source basenames; only the image extension is stripped.
    asset=SITE_ROOT/'assets/figures'/(str(path)+'.webp')
    if not asset.is_file():missing.append((graphic,str(asset)));continue
    with Image.open(asset) as im:width,height=im.size
    figmap[graphic]={'src':'figures/'+str(asset.relative_to(SITE_ROOT/'assets/figures')),'w':width,'h':height}
if missing:raise FileNotFoundError(missing)
(HERE/'data/figures.json').write_text(json.dumps(figmap,ensure_ascii=False,indent=2))
cache=HERE/'build/figures'
if not cache.exists():cache.symlink_to(SITE_ROOT/'assets/figures',target_is_directory=True)
print('Reused',len(figmap),'unchanged figure assets')
