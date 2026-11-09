"""Compare every labelled number in the LaTeXML XML with the print build (main.aux)."""
import json
import re
from collections import Counter
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
NS = {"ltx": "http://dlmf.nist.gov/LaTeXML"}
aux = json.loads((HERE / "data" / "labels.json").read_text())
doc = etree.parse(str(HERE / "build" / "book.xml"))
xmlnum = {}
for el in doc.iter():
    labs = el.get("labels")
    if not labs:
        continue
    tag = etree.QName(el).localname
    num = el.get("refnum") or ""
    if not num:
        t = el.find("ltx:tags/ltx:tag[@role='refnum']", NS)
        if t is None:
            t = el.find("ltx:tags/ltx:tag", NS)
        num = "".join(t.itertext()).strip() if t is not None else ""
    for lab in labs.split():
        lab = lab.replace("LABEL:", "")
        xmlnum[lab] = (tag, num, el.get("{http://www.w3.org/XML/1998/namespace}id"))
ok, diff, only_aux, only_xml = 0, [], [], []
for lab, v in aux.items():
    lab_x = lab.replace(" ", "_")
    if lab_x in xmlnum and lab not in xmlnum:
        xmlnum[lab] = xmlnum[lab_x]
    if lab not in xmlnum:
        only_aux.append(lab)
        continue
    a = v["num"]
    x = xmlnum[lab][1]
    if a == x:
        ok += 1
    else:
        diff.append((lab, a, x, xmlnum[lab][0]))
only_xml = [l for l in xmlnum if l not in aux]
print(f"aux labels {len(aux)}  xml labels {len(xmlnum)}  match {ok}  differ {len(diff)}  aux-only {len(only_aux)}  xml-only {len(only_xml)}")
print("differ by element:", Counter(d[3] for d in diff).most_common())
for d in diff[:25]:
    print("  ", d)
print("aux-only sample:", only_aux[:10])
print("xml-only sample:", only_xml[:10])
json.dump({"diff": diff, "only_aux": only_aux, "only_xml": only_xml}, open(HERE / "build" / "numbering_report.json", "w"), indent=1)
