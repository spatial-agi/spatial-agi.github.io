"""PDF parity check: for every reader page, compare the numbers it shows (equations, figures, tables, citations,
cross-references) with the numbers printed in the PDF on the page range of that section."""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import lxml.html as LH

HERE = Path(__file__).resolve().parent
DIST = HERE.parent / "dist"
PDF = HERE.parents[1] / "Spt-Intell-share-paper" / "main.pdf"
toc = json.loads((DIST / "data" / "toc.json").read_text())
secs = [(s["slug"], s["page"]) for p in toc["parts"] for c in p["chapters"] for s in c["sections"] if s.get("page")]
secs.sort(key=lambda x: x[1])
report, totals = [], Counter()
for i, (slug, start) in enumerate(secs):
    end = secs[i + 1][1] if i + 1 < len(secs) else start + 12
    pdf = subprocess.run(["pdftotext", "-f", str(start), "-l", str(end), "-layout", str(PDF), "-"], capture_output=True, text=True).stdout
    page = LH.parse(str(DIST / "read" / slug / "index.html")).getroot()
    art = page.xpath('//article[contains(@class,"prose")]')[0]
    web_eq = {x.text_content().strip("() ") for x in art.xpath('.//td[contains(@class,"ltx_eqn_eqno")]')}
    web_fig = {re.sub(r"^(Figure|Table) ", "", x.text_content()) for x in art.xpath('.//*[@class="cap-tag"]')}
    web_cite = {a.text_content() for a in art.xpath('.//a[@class="cite"]')}
    pdf_eq = set(re.findall(r"\((\d+\.\d+)\)\s*$", pdf, re.M))
    pdf_fig = set(re.findall(r"^\s*(?:Figure|Table) (\d+\.\d+):", pdf, re.M))
    pdf_cite = set(re.findall(r"\[(\d+)(?:, (\d+))*\]", pdf))
    pdf_cite_all = set(n for grp in re.findall(r"\[([\d,\s–-]+)\]", pdf) for n in re.findall(r"\d+", grp))
    miss_eq = sorted(web_eq - pdf_eq)
    miss_fig = sorted(web_fig - pdf_fig)
    miss_cite = sorted(web_cite - pdf_cite_all, key=int)
    totals.update(eq=len(web_eq), fig=len(web_fig), cite=len(web_cite), miss_eq=len(miss_eq), miss_fig=len(miss_fig), miss_cite=len(miss_cite))
    if miss_eq or miss_fig or miss_cite:
        report.append(dict(slug=slug, pages=f"{start}-{end}", eq=miss_eq[:8], fig=miss_fig[:8], cite=miss_cite[:12]))
print(json.dumps(dict(totals), indent=0))
for r in report:
    print(r)
