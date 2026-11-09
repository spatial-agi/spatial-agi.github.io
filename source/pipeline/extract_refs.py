"""Ground truth from the print build: citation numbers and label numbers (main.aux), bibliography (main.bib)."""
import json
import re
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

BOOK = Path(__file__).resolve().parents[2] / "Spt-Intell-share-paper"
OUT = Path(__file__).resolve().parent / "data"
aux = (BOOK / "main.aux").read_text(encoding="utf-8", errors="replace")

# \bibcite{key}{{n}{year}{{short}}{{long}}}
cites, short = {}, {}
for m in re.finditer(r"\\bibcite\{([^}]*)\}\{\{(\d+)\}\{[^}]*\}\{\{(.*?)\}\}", aux):
    cites[m.group(1)] = int(m.group(2))
    short[m.group(1)] = re.sub(r"~", " ", m.group(3))

# \newlabel{label}{{number}{page}{title}{anchor}{}}
labels = {}
for line in aux.splitlines():
    m = re.match(r"\\newlabel\{([^}]*)\}\{\{(.*?)\}\{(\d*)\}\{(.*)\}\{([^{}]*)\}\{.*\}\}\s*$", line)
    if not m or m.group(1).endswith("@cref"):
        continue
    lab, num, page, title, anchor = m.groups()
    labels[lab] = {"num": num, "page": int(page) if page else None, "anchor": anchor, "title": title[:200]}

parser = BibTexParser(common_strings=True)
parser.customization = convert_to_unicode
parser.ignore_nonstandard_types = False
bibtext = (BOOK / "main.bib").read_text(encoding="utf-8", errors="replace")
# bare-word field values (undefined @string macros such as csvt) become literal strings
bibtext = re.sub(r"(\b[a-zA-Z]+\s*=\s*)([A-Za-z][A-Za-z0-9_]*)(\s*[,}\n])",
                 lambda m: m.group(1) + "{" + m.group(2) + "}" + m.group(3), bibtext)
db = bibtexparser.loads(bibtext, parser=parser)


def clean(s):
    s = re.sub(r"[{}]", "", s or "")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return re.sub(r"\s+", " ", s).strip()


def authors(s):
    out = []
    for a in re.split(r"\s+and\s+", s or ""):
        a = clean(a)
        if not a:
            continue
        if a.lower() == "others":
            out.append("et al.")
            continue
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
            a = f"{first} {last}".strip()
        out.append(a)
    return out


refs = {}
for e in db.entries:
    key = e["ID"]
    venue = clean(e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("howpublished") or "")
    arxiv = None
    for f in ("journal", "eprint", "url", "note", "volume"):
        m = re.search(r"(\d{4}\.\d{4,5})", e.get(f, ""))
        if m and ("arxiv" in (e.get(f, "") + e.get("journal", "") + e.get("archiveprefix", "")).lower() or f == "eprint"):
            arxiv = m.group(1)
            break
    url = clean(e.get("url", "")) or None
    gh = re.search(r"github\.com/[\w.-]+/[\w.-]+", " ".join(e.get(f, "") for f in ("url", "note", "howpublished")))
    refs[key] = {
        "key": key, "num": cites.get(key), "short": short.get(key), "type": e.get("ENTRYTYPE"), "title": clean(e.get("title")),
        "authors": authors(e.get("author", "")), "year": clean(e.get("year")), "venue": venue,
        "arxiv": arxiv, "doi": clean(e.get("doi")) or None, "url": url, "github": gh.group(0) if gh else None,
    }

missing = [k for k in cites if k not in refs]
OUT.mkdir(exist_ok=True)
(OUT / "labels.json").write_text(json.dumps(labels, indent=0, ensure_ascii=False))
(OUT / "refs.json").write_text(json.dumps({k: v for k, v in refs.items() if v["num"]}, ensure_ascii=False))
(OUT / "refs_all.json").write_text(json.dumps(refs, ensure_ascii=False))
print(f"bibcite {len(cites)}  labels {len(labels)}  bib entries {len(refs)}  cited-but-missing {len(missing)} {missing[:5]}")
print("with arxiv", sum(1 for r in refs.values() if r['num'] and r['arxiv']), "with doi", sum(1 for r in refs.values() if r['num'] and r['doi']),
      "with url", sum(1 for r in refs.values() if r['num'] and r['url']))
