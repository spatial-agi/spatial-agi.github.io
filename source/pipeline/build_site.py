"""Build the static site: split the LaTeXML HTML into reader pages, resolve figures, citations and
cross-references against the print build, render templates, copy assets. Output: website/dist."""
import copy
import html as H
import json
import re
import shutil
from collections import OrderedDict, defaultdict
from pathlib import Path

import lxml.html as LH
from jinja2 import Environment, FileSystemLoader
from lxml import etree

HERE = Path(__file__).resolve().parent
WEB = HERE.parent
BOOK = WEB.parent / "Spt-Intell-share-paper"
SRC, DIST, DATA = WEB / "src", WEB / "dist", HERE / "data"
NS = {"ltx": "http://dlmf.nist.gov/LaTeXML"}
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
ROMAN = ["", "I", "II", "III", "IV", "V"]
PART_COLORS = {1: "#A8722A", 2: "#3646F0", 3: "#7446D6", 4: "#11899A", 5: "#C0436E"}

aux = json.loads((DATA / "labels.json").read_text())
refs = json.loads((DATA / "refs.json").read_text())
figmap = json.loads((DATA / "figures.json").read_text())
num2key = {v["num"]: k for k, v in refs.items()}


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60]


def text(el):
    return " ".join((el.text_content() if el is not None else "").split())


# ------------------------------------------------------------------ XML side tables
xml = etree.parse(str(HERE / "build" / "book.xml"))
graphic_of, labels_of = {}, {}
for g in xml.iter("{%s}graphics" % NS["ltx"]):
    graphic_of[g.get(XMLID)] = g.get("graphic")
for el in xml.iter():
    if el.get("labels") and el.get(XMLID):
        labels_of[el.get(XMLID)] = [l.replace("LABEL:", "") for l in el.get("labels").split()]


def aux_num(xid):
    for lab in labels_of.get(xid, []):
        for cand in (lab, lab.replace("_", " ")):
            if cand in aux and aux[cand]["num"]:
                return aux[cand]["num"]
    return None


# PDF page numbers from the table of contents
toc_pages = {}
for m in re.finditer(r"\\contentsline \{(part|chapter|section|subsection|subsubsection)\}\{(.*?)\}\{(\d+)\}\{([^}]*)\}",
                     (BOOK / "main.toc").read_text(errors="replace")):
    kind, body, page, anchor = m.groups()
    nm = re.search(r"\\numberline \{([^}]*)\}", body)
    if nm:
        toc_pages[(kind, nm.group(1))] = int(page)
pdf_pages = int(re.search(r"Pages:\s+(\d+)", (HERE / "data" / "pdfinfo.txt").read_text()).group(1)) \
    if (HERE / "data" / "pdfinfo.txt").exists() else None

# ------------------------------------------------------------------ split the book into pages
doc = LH.parse(str(HERE / "build" / "html" / "book.html")).getroot()
article = doc.xpath('//article[contains(@class,"ltx_document")]')[0]
for junk in article.xpath('.//div[contains(@class,"ltx_pagination")]'):
    junk.getparent().remove(junk)


def kind_of(sec):
    for c in (sec.get("class") or "").split():
        if c.startswith("ltx_") and c[4:] in ("part", "chapter", "section", "subsection", "subsubsection", "paragraph",
                                               "appendix", "bibliography"):
            return c[4:]
    return None


def heading(sec):
    h = sec.xpath('./*[contains(@class,"ltx_title")]')
    return h[0] if h else None


def title_parts(sec):
    """(number, plain title) from the heading, without the tag."""
    h = heading(sec)
    if h is None:
        return None, ""
    h2 = copy.deepcopy(h)
    num = None
    for t in h2.xpath('.//*[contains(@class,"ltx_tag")]'):
        num = text(t)
        t.drop_tree()
    return num, text(h2)


pages = OrderedDict()   # slug -> dict(kind, title, num, el, part, chapter, ...)
id2page = {}


def add_page(slug_, kind, title, num, el, part=None, chapter=None, extra=None):
    pages[slug_] = dict(slug=slug_, kind=kind, title=title, num=num, el=el, part=part, chapter=chapter, **(extra or {}))
    for e in el.iter():
        if e.get("id"):
            id2page.setdefault(e.get("id"), slug_)
    return pages[slug_]


toc = []        # [{part, chapters:[{chapter, sections:[...]}]}]
front, back = [], []


def body_before_first(sec, kinds):
    """Clone of a sectioning element keeping only the content before its first child section of the given kinds."""
    c = copy.deepcopy(sec)
    for child in list(c):
        if child.tag == "section" and kind_of(child) in kinds:
            c.remove(child)
    return c


def subsections(sec):
    out = []
    for ss in sec.xpath('./section'):
        k = kind_of(ss)
        if k in ("subsection", "subsubsection"):
            n, t = title_parts(ss)
            out.append(dict(id=ss.get("id"), num=n, title=t, kind=k,
                            children=[dict(id=x.get("id"), num=title_parts(x)[0], title=title_parts(x)[1])
                                      for x in ss.xpath('./section') if kind_of(x) == "subsubsection"]))
    return out


for top in article:
    k = kind_of(top)
    if k == "chapter" and top.get("id", "").startswith("Chx"):
        n, t = title_parts(top)
        s = {"Preface": "preface", "Notation": "notation", "Glossary": "glossary"}.get(t, slug(t))
        add_page(s, "front", t, None, top)
        front.append(s)
    elif k == "part":
        pn = len(toc) + 1
        n, t = title_parts(top)
        pslug = f"part-{ROMAN[pn].lower()}"
        add_page(pslug, "part", t, ROMAN[pn], body_before_first(top, ("chapter",)), part=pn)
        pentry = dict(n=pn, roman=ROMAN[pn], title=t, slug=pslug, color=PART_COLORS[pn], chapters=[],
                      page=toc_pages.get(("part", ROMAN[pn])))
        toc.append(pentry)
        for ch in top.xpath('./section'):
            if kind_of(ch) != "chapter":
                continue
            cn, ct = title_parts(ch)
            cnum = re.sub(r"\D", "", cn or "")
            cslug = f"chapter-{cnum}"
            add_page(cslug, "chapter", ct, cnum, body_before_first(ch, ("section",)), part=pn, chapter=cnum)
            centry = dict(num=cnum, title=ct, slug=cslug, sections=[], page=toc_pages.get(("chapter", cnum)))
            pentry["chapters"].append(centry)
            for se in ch.xpath('./section'):
                if kind_of(se) != "section":
                    continue
                sn, st = title_parts(se)
                if sn:
                    sslug = sn
                    add_page(sslug, "section", st, sn, se, part=pn, chapter=cnum)
                    centry["sections"].append(dict(num=sn, title=st, slug=sslug, page=toc_pages.get(("section", sn)),
                                                   subs=subsections(se)))
                else:   # unnumbered back matter at the end of the last chapter
                    s = {"Acknowledge": "acknowledgements", "Acknowledgements": "acknowledgements",
                         "Acknowledgments": "acknowledgements", "Author Contributions": "contributions"}.get(st, slug(st))
                    add_page(s, "back", "Acknowledgements" if s == "acknowledgements" else st, None, se)
                    back.append(s)

# ------------------------------------------------------------------ transforms
cited_in = defaultdict(list)    # citation key -> [page slug]
xref = {}                        # element id -> preview data


def page_url(s):
    return f"/read/{s}/"


def fix_figures(root, page):
    for img in root.xpath('.//img[contains(@class,"ltx_graphics")]'):
        g = graphic_of.get(img.get("id"))
        info = figmap.get(g) if g else None
        if not info:
            continue
        src = "/assets/" + info["src"]
        img.set("src", src)
        img.set("width", str(info["w"]))
        img.set("height", str(info["h"]))
        img.set("loading", "lazy")
        img.set("decoding", "async")
        img.set("class", "fig-img")
        img.set("alt", "")
        img.attrib.pop("style", None)
    for fig in root.xpath('.//figure[contains(@class,"ltx_figure") or contains(@class,"ltx_table")]'):
        n = aux_num(fig.get("id"))
        tag = fig.xpath('.//*[contains(@class,"ltx_tag_figure") or contains(@class,"ltx_tag_table")]')
        if tag:
            is_tab = "ltx_tag_table" in tag[0].get("class")
            label = ("Table " if is_tab else "Figure ") + (n or re.sub(r"[^0-9IVX.]", "", text(tag[0]).split(":")[0]))
            for c in list(tag[0]):
                tag[0].remove(c)
            tag[0].text = label
            tag[0].set("class", "cap-tag")
        for sp in fig.xpath('.//figcaption//*[@style]'):
            if "font-size" in sp.get("style"):
                del sp.attrib["style"]
        cap = fig.xpath('./figcaption')
        img = fig.xpath('.//img[@src]')
        captext = ""
        if cap:
            c2 = copy.deepcopy(cap[0])
            for t_ in c2.xpath('.//*[@class="cap-tag"]'):
                t_.drop_tree()
            captext = text(c2).lstrip(":. ")
        xref[fig.get("id")] = dict(kind="table" if "ltx_table" in fig.get("class") else "figure",
                                   label=text(tag[0]) if tag else "", caption=captext[:320], full=captext,
                                   img=img[0].get("src").replace(".webp", ".thumb.webp") if img else None,
                                   url=page_url(page) + "#" + fig.get("id"))


WIDGETS = {}     # Fig. 1.3 is now drawn natively (fig13.py); the explore timeline keeps the dot-chart widget

# figures drawn natively for the web (pipeline/webfigs.py): the print image is replaced by live SVG / artwork + text.
# lxml's HTML parser mangles inline SVG, so a slot goes into the tree and the markup is swapped in after serialisation.
NATIVE = {}
OPENER_LABELS = {1: "fig:part1-illustration", 2: "fig:p2_main", 3: "fig:p3_main", 4: "fig:p4_main", 5: "fig:p5_main"}
OPENER_TARGETS = {
    1: [("/read/1.1/", "Section 1.1"), ("/read/1.2/", "Section 1.2"), ("/read/chapter-2/", "Chapter 2")],
    2: [("#part-intro", "The premise"), ("/read/chapter-4/", "Chapter 4"), ("/read/chapter-5/", "Chapter 5")],
    3: [("/read/chapter-6/", "Chapter 6"), ("/read/chapter-7/", "Chapter 7"), ("/read/chapter-8/", "Chapter 8")],
    4: [("#part-intro", "The premise"), ("#chapters", "Chapters 9–14"), ("#part-outro", "The common layer")],
    5: [("/read/chapter-15/", "Chapter 15"), ("/read/chapter-16/", "Chapter 16"), ("/read/16.4/", "Section 16.4")],
}


def native_figs(root):
    import site_data as SD_
    import webfigs as WF
    import fig13 as F13
    from figure61 import fig61 as WF61
    from figure62 import fig62 as WF62
    from figure63 import fig63 as WF63
    from figure64 import fig64 as WF64
    from figure65 import fig65 as WF65
    from figure66 import fig66 as WF66
    from figure67 import fig67 as WF67
    from figure68 import fig68 as WF68
    from figure69 import fig69 as WF69
    from figure610 import fig610 as WF610
    from figure611 import fig611 as WF611
    from figure612 import fig612 as WF612
    from figure613 import fig613 as WF613
    from figure614 import fig614 as WF614
    from figure615 import fig615 as WF615
    from figure616 import fig616 as WF616
    from figure617 import fig617 as WF617
    from figure618 import fig618 as WF618
    from figure619 import fig619 as WF619
    from figure620 import fig620 as WF620
    from figure621 import fig621 as WF621
    from figure622 import fig622 as WF622
    from figure623 import fig623 as WF623
    from figure624 import fig624 as WF624
    from figure625 import fig625 as WF625
    from figure626 import fig626 as WF626
    from figure627 import fig627 as WF627
    from figure628 import fig628 as WF628
    from figure71 import fig71 as WF71
    from figure72 import fig72 as WF72
    from figure73 import fig73 as WF73
    from figure74 import fig74 as WF74
    from figure75 import fig75 as WF75
    from figure76 import fig76 as WF76
    from figure77 import fig77 as WF77
    from figure78 import fig78 as WF78
    from figure79 import fig79 as WF79
    from figure710 import fig710 as WF710
    from figure711 import fig711 as WF711
    from figure712 import fig712 as WF712
    from figure713 import fig713 as WF713
    from figure714 import fig714 as WF714
    from figure720 import fig720 as WF720
    from figure721 import fig721 as WF721
    from figure722 import fig722 as WF722
    from figure723 import fig723 as WF723
    from figures724_730 import FIGURES as BATCH724_730
    from figure715_719 import GENERATORS as RL_WORKFLOWS, SOURCES as RL_SOURCES
    from figures81_825_native import SOURCES as BATCH8_SOURCES, render as render_batch8
    from figures91_924_native import SOURCES as BATCH9_SOURCES, render as render_batch9
    from figures101_1116_native import SOURCES as BATCH1011_SOURCES, render as render_batch1011
    from figures121_145_native import SOURCES as BATCH1214_SOURCES, render as render_batch1214
    from figures41_42_native import install_slots as install_figures41_42
    jobs = {"fig:p1_s1_1_si_covering_shifts": lambda cap: WF.fig11(), "fig:p1_s2_1_intro": lambda cap: WF.fig21(SD_.OPERATORS),
            "web:rl_overview": lambda cap: WF713(),
            "fig:p1_s1_2_si_evolution": lambda cap: WF.fig12(),
            "fig:p1_s1_2_milestones": lambda cap: F13.fig13(json.loads((DATA / "refs.json").read_text()), SD_.eras(),
                                                            "#" + next((x for x, labs in labels_of.items() if "tab:p1_s1_2_eras" in labs), ""))}
    for k, lab in OPENER_LABELS.items():
        jobs[lab] = (lambda k_: lambda cap: WF.fig3opener() if k_ == 3 else WF.opener(k_, OPENER_TARGETS[k_], alt=cap))(k)
    for lab, make in jobs.items():
        xid = next((x for x, labs in labels_of.items() if lab in labs), None)
        figs = root.xpath(f'.//figure[@id="{xid}"]') if xid else []
        # Match this example by asset path so book label changes do not break the redraw.
        if lab == "web:rl_overview":
            figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/rl_overview.webp")]]')
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]') if figs else []
        if not img:
            continue
        cap = figs[0].xpath('./figcaption')
        NATIVE[lab] = make(text(cap[0]).split(".", 1)[-1].strip() if cap else "")
        img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": lab}))
        figs[0].set("class", figs[0].get("class") + " native")
        if lab in OPENER_LABELS.values():       # anchors for the opener zones that point into the part's own text
            paras = [p for p in root.xpath('.//div[contains(@class,"ltx_para")]') if not p.xpath("ancestor::figure")]
            if paras:
                paras[0].set("id", "part-intro")
                paras[-1].set("id", "part-outro")

    # Figure 6.6: preserve the printed caption and its 2000 x 1126 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/depth_estimation_v3.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig66"}))
            NATIVE["web:fig66"] = WF66()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.7: preserve its caption and original 2000 x 877 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/surface_normal_estimation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig67"}))
            NATIVE["web:fig67"] = WF67()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.8: preserve its caption and original 1536 x 1024 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/camera-1.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig68"}))
            NATIVE["web:fig68"] = WF68()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.9: preserve its caption and original 2000 x 1031 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/height_estimation_1.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig69"}))
            NATIVE["web:fig69"] = WF69()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.17: preserve its caption and original 2000 x 1094 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/action_detection.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig617"}))
            NATIVE["web:fig617"] = WF617()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.19: preserve its caption and original 2000 x 1125 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/slam.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig619"}))
            NATIVE["web:fig619"] = WF619()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.20: preserve its caption and original 2000 x 847 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/slam_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig620"}))
            NATIVE["web:fig620"] = WF620()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.21: preserve its caption and original 2000 x 1077 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/scene_flow_estimation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig621"}))
            NATIVE["web:fig621"] = WF621()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.22: preserve its caption and original 2000 x 1219 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/object_tracking.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig622"}))
            NATIVE["web:fig622"] = WF622()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.23: preserve its caption and original 2000 x 454 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/object_tracking_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig623"}))
            NATIVE["web:fig623"] = WF623()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.24: preserve its caption and original 2000 x 1570 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/temporal_localization.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig624"}))
            NATIVE["web:fig624"] = WF624()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.25: preserve its caption and original 2000 x 1185 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/temporal_localization_task_settings.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig625"}))
            NATIVE["web:fig625"] = WF625()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.26: preserve its caption and original 2000 x 1031 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/audio_video_spatial_localization.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig626"}))
            NATIVE["web:fig626"] = WF626()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.27: preserve its caption and original 2000 x 475 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/visual_language_graounding_task.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig627"}))
            NATIVE["web:fig627"] = WF627()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.28: preserve its caption and original 2000 x 417 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/visual_language_graounding_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig628"}))
            NATIVE["web:fig628"] = WF628()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.1: preserve its caption and original 2000 x 892 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/711_geo.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig71"}))
            NATIVE["web:fig71"] = WF71()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.2: preserve its caption and original 2000 x 677 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/physical_reasoning.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig72"}))
            NATIVE["web:fig72"] = WF72()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.3: preserve its caption and original 2000 x 868 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/713_topo.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig73"}))
            NATIVE["web:fig73"] = WF73()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.4: preserve its caption and original 2000 x 923 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/714_constraint.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig74"}))
            NATIVE["web:fig74"] = WF74()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.5: preserve its caption and original 2000 x 894 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/715_program.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig75"}))
            NATIVE["web:fig75"] = WF75()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.6: preserve its caption and original 2000 x 930 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/716_causal.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig76"}))
            NATIVE["web:fig76"] = WF76()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.7: preserve its caption and original 2000 x 608 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/implicit_neural_spatial_reasoning_task.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig77"}))
            NATIVE["web:fig77"] = WF77()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.8: preserve its caption and original 2000 x 933 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/implicit_neural_spatial_reasoning_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig78"}))
            NATIVE["web:fig78"] = WF78()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.9: preserve its caption and original 2000 x 606 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/explicit_structured_neural_reasoning_task.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig79"}))
            NATIVE["web:fig79"] = WF79()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.10: preserve its caption and original 2000 x 437 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/explicit_structured_neural_reasoning_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig710"}))
            NATIVE["web:fig710"] = WF710()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.11: preserve its caption and original 2000 x 1031 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/geometry-aware_neural_spatial_reasoning.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig711"}))
            NATIVE["web:fig711"] = WF711()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.12: preserve its caption and original 2000 x 742 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/differentiable_optimization_layers_for_spatial_reasoning.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig712"}))
            NATIVE["web:fig712"] = WF712()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.14: preserve its caption and original 2000 x 571 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/value-based-rl.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig714"}))
            NATIVE["web:fig714"] = WF714()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figures 7.15–7.19: keep captions and source aspect ratios.
    for number, make in RL_WORKFLOWS.items():
        filename = RL_SOURCES[number][0]
        figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/' + filename + '")]]')
        if figs:
            images = figs[0].xpath('.//img[contains(@class,"fig-img")]')
            if images:
                slot = f"web:fig{number}"
                images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
                NATIVE[slot] = make()
                figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.20: keep the source proportions and surrounding caption.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/multi-agent_spatial_reasoning.webp")]]')
    if figs:
        images = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if images:
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig720"}))
            NATIVE["web:fig720"] = WF720()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.21: keep its source proportions and surrounding caption.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/LLM_VLM-centric_spatial_reasoning.webp")]]')
    if figs:
        images = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if images:
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig721"}))
            NATIVE["web:fig721"] = WF721()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.22: keep its source proportions and surrounding caption.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/VLA_spatial_reasoning.webp")]]')
    if figs:
        images = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if images:
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig722"}))
            NATIVE["web:fig722"] = WF722()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 7.23: keep the source proportions and surrounding caption.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section7/chain-of-thought_spatial_reasoning.webp")]]')
    if figs:
        images = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if images:
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig723"}))
            NATIVE["web:fig723"] = WF723()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Approved Figures 7.24–7.30: preserve image proportions and captions.
    for number, render in BATCH724_730.items():
        manifest = json.loads((Path(__file__).resolve().parents[2] / f"assets/figures/elements/figure{number}/manifest.json").read_text())
        source = "/" + manifest["source"]
        figs = root.xpath('.//figure[.//img[@src=$source]]', source=source)
        for figure in figs:
            images = figure.xpath('.//img[contains(@class,"fig-img")]')
            if images:
                slot = f"web:fig{number}"
                images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
                NATIVE[slot] = render()
                figure.set("class", (figure.get("class") or "") + " native")

    # Approved Figures 8.1–8.25: replace only image content, retaining captions.
    for number, entry in enumerate(BATCH8_SOURCES, 1):
        source = "/" + entry["sources"][0]
        figs = root.xpath('.//figure[.//img[@src=$source]]', source=source)
        for figure in figs:
            images = figure.xpath('.//img[contains(@class,"fig-img")]')
            if not images:
                continue
            slot = f"web:fig8{number}"
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
            for image in images[1:]:
                image.getparent().remove(image)
            NATIVE[slot] = render_batch8(number)
            figure.set("class", (figure.get("class") or "") + " native")

    # Approved Figures 9.1–9.24: replace only image content, retaining captions.
    for number, entry in enumerate(BATCH9_SOURCES, 1):
        source = "/" + entry["sources"][0]
        figs = root.xpath('.//figure[.//img[@src=$source]]', source=source)
        for figure in figs:
            images = figure.xpath('.//img[contains(@class,"fig-img")]')
            if not images:
                continue
            slot = f"web:fig9{number}"
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
            for image in images[1:]:
                image.getparent().remove(image)
            NATIVE[slot] = render_batch9(number)
            figure.set("class", (figure.get("class") or "") + " native")

    # Approved Figures 10.1–11.16: preserve the surrounding content and caption.
    for entry in BATCH1011_SOURCES:
        source = "/" + entry["sources"][0]
        for figure in root.xpath('.//figure[.//img[@src=$source]]', source=source):
            images = figure.xpath('.//img[contains(@class,"fig-img")]')
            if not images:
                continue
            slot = f'web:fig{entry["chapter"]}{entry["number"]}'
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
            for image in images[1:]:
                image.getparent().remove(image)
            NATIVE[slot] = render_batch1011(entry["chapter"], entry["number"])
            figure.set("class", (figure.get("class") or "") + " native")

    # Approved Figures 12.1–14.5: preserve the surrounding content and caption.
    for entry in BATCH1214_SOURCES:
        source = "/" + entry["sources"][0]
        for figure in root.xpath('.//figure[.//img[@src=$source]]', source=source):
            images = figure.xpath('.//img[contains(@class,"fig-img")]')
            if not images:
                continue
            slot = f'web:fig{entry["chapter"]}{entry["number"]}'
            images[0].getparent().replace(images[0], etree.Element("div", {"class": "nf-slot", "data-slot": slot}))
            for image in images[1:]:
                image.getparent().remove(image)
            NATIVE[slot] = render_batch1214(entry["chapter"], entry["number"])
            figure.set("class", (figure.get("class") or "") + " native")

    install_figures41_42(root, NATIVE)

    # Figure 6.18: preserve its caption and original 2000 x 1277 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/action_detection_method_1.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig618"}))
            NATIVE["web:fig618"] = WF618()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.16: preserve its caption and original 2000 x 1031 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/layout_parsing_method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig616"}))
            NATIVE["web:fig616"] = WF616()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.15: preserve its caption and original 2000 x 1003 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/layout_parsing.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig615"}))
            NATIVE["web:fig615"] = WF615()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.14: preserve its caption and original 2000 x 975 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/scene_graph.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig614"}))
            NATIVE["web:fig614"] = WF614()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.13: preserve its caption and original 2000 x 1493 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/spatial_relation_extraction.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig613"}))
            NATIVE["web:fig613"] = WF613()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.12: preserve its caption and original 2000 x 1100 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/pose_estimation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig612"}))
            NATIVE["web:fig612"] = WF612()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.11: preserve its caption and original 2000 x 1554 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/visual_odometry_and_camera_pose_estimation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig611"}))
            NATIVE["web:fig611"] = WF611()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.10: preserve its caption and original 2000 x 1124 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/height_estimation_2.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig610"}))
            NATIVE["web:fig610"] = WF610()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.5: preserve the caption and original 2000 x 976 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/scene_classification.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig65"}))
            NATIVE["web:fig65"] = WF65()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.4: preserve its caption and original 2000 x 1126 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/keypoint_detection_v2.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig64"}))
            NATIVE["web:fig64"] = WF64()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.3: preserve its caption and original 2000 x 522 proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/segmentation-method.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig63"}))
            NATIVE["web:fig63"] = WF63()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 6.2: retain its caption and replace the print panel image.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/segmentation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig62"}))
            NATIVE["web:fig62"] = WF62()
            figs[0].set("class", (figs[0].get("class") or "") + " native")


    # Figure 6.1: preserve the caption and replace only the source detector image.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part3/section6/object_detection.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig61"}))
            NATIVE["web:fig61"] = WF61()
            figs[0].set("class", (figs[0].get("class") or "") + " native")

    # Figure 4.3 uses the source image path as a stable key; the printed label may vary by edition.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part2/3D_representations_2.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig43"}))
            NATIVE["web:fig43"] = WF.fig43()
            figs[0].set("class", (figs[0].get("class") or "") + " native")
    # Figure 4.4 uses the source image path as a stable key.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part2/4D_representations.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig44"}))
            NATIVE["web:fig44"] = WF.fig44()
            figs[0].set("class", (figs[0].get("class") or "") + " native")
    # Preserve Figure 4.5's caption and replace only its printed image.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part2/language_representation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig45"}))
            NATIVE["web:fig45"] = WF.fig45()
            figs[0].set("class", (figs[0].get("class") or "") + " native")
    # Figure 4.6: keep the printed caption and original artwork proportions.
    figs = root.xpath('.//figure[.//img[contains(@src,"/part2/audio_representation.webp")]]')
    if figs:
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]')
        if img:
            img[0].getparent().replace(img[0], etree.Element("div", {"class": "nf-slot", "data-slot": "web:fig46"}))
            NATIVE["web:fig46"] = WF.fig46()
            figs[0].set("class", (figs[0].get("class") or "") + " native")


def add_widgets(root):
    """Figures with an interactive redraw get an 'As printed / Interactive version' toggle (the print figure stays the default)."""
    for lab, w in WIDGETS.items():
        xid = next((x for x, labs in labels_of.items() if lab in labs), None)
        figs = root.xpath(f'.//figure[@id="{xid}"]') if xid else []
        img = figs[0].xpath('.//img[contains(@class,"fig-img")]') if figs else []
        if not img:
            continue
        # the milestone chart opens in its interactive form (the print figure stays one click away and is the no-JS fallback)
        default = ' data-default="live"' if w == "timeline" else ""
        bar = LH.fragment_fromstring(f'<div class="figtoggle" role="tablist" aria-label="Figure view"{default}><button type="button" role="tab" aria-selected="true" data-fv="print">As printed</button><button type="button" role="tab" aria-selected="false" data-fv="live">Interactive version</button></div>')
        img[0].addnext(LH.fragment_fromstring(f'<div class="fig-live" data-widget="{w}" hidden></div>'))
        img[0].addprevious(bar)


def fix_citations(root, page):
    for cite in root.xpath('.//cite[contains(@class,"ltx_cite")]'):
        keys = [text(s) for s in cite.xpath('.//*[contains(@class,"ltx_missing_citation")]')]
        if not keys:
            continue
        macro = "citet" if "citemacro_citet" in cite.get("class") else "cite"
        new = etree.Element("cite", {"class": "cites"})
        parts = []
        for k in keys:
            r = refs.get(k)
            if not r:
                parts.append(("?", k, None))
                continue
            cited_in[k].append(page)
            parts.append((str(r["num"]), k, r))
        if macro == "citet":
            # natbib numbers + \citet: "Author et al. [n]"
            first = True
            for n, k, r in parts:
                if not first:
                    (new[-1] if len(new) else new).tail = ((new[-1].tail if len(new) else "") or "") + ", "
                a = etree.SubElement(new, "span", {"class": "citet-name"})
                a.text = (r or {}).get("short") or k
                b = etree.SubElement(new, "a", {"class": "cite", "href": f"/read/references/#ref-{n}", "data-k": k})
                b.text = n
                a.tail = " ["
                b.tail = "]"
                first = False
        else:
            new.text = "["
            for i, (n, k, r) in enumerate(parts):
                a = etree.SubElement(new, "a", {"class": "cite", "href": f"/read/references/#ref-{n}", "data-k": k})
                a.text = n
                a.tail = ", " if i < len(parts) - 1 else "]"
        new.tail = cite.tail
        cite.getparent().replace(cite, new)


def fix_refs(root):
    for a in root.xpath('.//a[contains(@class,"ltx_ref")]'):
        href = a.get("href") or ""
        if href.startswith("#"):
            tid = href[1:]
            pg = id2page.get(tid)
            if pg:
                a.set("href", page_url(pg) + ("" if pages[pg]["el"].get("id") == tid else "#" + tid))
            n = aux_num(tid)
            tag = a.xpath('.//*[contains(@class,"ltx_ref_tag")]')
            if n and tag:
                cur = text(tag[0])
                tag[0].text = f"({n})" if cur.startswith("(") else n
                for c in list(tag[0]):
                    tag[0].remove(c)
            a.set("class", "xref")
            a.set("data-x", tid)
            a.attrib.pop("title", None)
    for a in root.xpath('.//a[contains(@class,"ltx_href")]'):
        if (a.get("href") or "").startswith("http"):
            a.set("target", "_blank")
            a.set("rel", "noopener")


def fix_paragraph_titles(root):
    """LaTeX \\paragraph is run-in: merge the heading into the first paragraph."""
    for sec in root.xpath('.//section[contains(@class,"ltx_paragraph")]'):
        h = sec.xpath('./h6[contains(@class,"ltx_title_paragraph")]')
        p = sec.xpath('./div[contains(@class,"ltx_para")][1]/p[1]')
        if h and p:
            strong = etree.Element("strong", {"class": "runin"})
            strong.text = text(h[0])
            strong.tail = " " + (p[0].text or "")
            p[0].text = None
            p[0].insert(0, strong)
            sec.remove(h[0])


def fix_headings(root, top_level):
    """Re-level headings for a page whose top element is `top_level`; keep numbers in a span."""
    order = ["part", "chapter", "section", "subsection", "subsubsection"]
    base = order.index(top_level)
    for sec in [root] + root.xpath('.//section'):
        k = kind_of(sec)
        if k not in order:
            continue
        h = heading(sec)
        if h is None:
            continue
        if sec is root:          # the page header is rendered by the template
            if sec.get("id"):
                num, ttl = title_parts(sec)
                xref.setdefault(sec.get("id"), dict(kind=k, label=(num or ""), caption=ttl, url=None))
            h.getparent().remove(h)
            continue
        lvl = min(order.index(k) - base + 1, 4)
        num, ttl = title_parts(sec)
        new = etree.Element(f"h{lvl}", {"class": f"h-{k}", "id": sec.get("id") or ""})
        if num and k not in ("part", "chapter"):
            sn = etree.SubElement(new, "span", {"class": "secnum"})
            sn.text = num
            sn.tail = ttl
        else:
            new.text = ttl
        if sec.get("id") and k not in ("part", "chapter"):
            anchor = etree.SubElement(new, "a", {"class": "anchor", "href": "#" + sec.get("id"), "aria-label": "Link to this section",
                                                  "data-pagefind-ignore": "all"})
            anchor.text = "#"
        h.getparent().replace(h, new)
        if sec.get("id"):
            xref.setdefault(sec.get("id"), dict(kind=k, label=(num or ""), caption=ttl, url=None))
        sec.attrib.pop("id", None)


def fix_boxes(root):
    for q in root.xpath('.//blockquote[contains(@class,"web-box")]'):
        q.tag = "aside"
        q.set("class", "box")
    for q in root.xpath('.//blockquote[contains(@class,"web-raster")]'):
        q.tag = "div"
        q.set("class", "epigraphs")
    for d in root.xpath('.//*[contains(@class,"ltx_note")]'):
        pass


def fix_footnotes(root):
    notes = []
    for i, n in enumerate(root.xpath('.//*[contains(@class,"ltx_note") and contains(@class,"ltx_role_footnote")]'), 1):
        content = n.xpath('.//*[contains(@class,"ltx_note_content")]')
        body = copy.deepcopy(content[0]) if content else etree.Element("span")
        for m in body.xpath('.//*[contains(@class,"ltx_note_mark") or contains(@class,"ltx_tag_note")]'):
            m.drop_tree() if m.getparent() is not None else None
        fid = f"fn{i}"
        sup = etree.Element("sup", {"class": "fn", "id": f"fnref{i}"})
        a = etree.SubElement(sup, "a", {"href": f"#{fid}", "data-fn": fid})
        a.text = str(i)
        sup.tail = n.tail
        n.getparent().replace(n, sup)
        notes.append((fid, i, body))
    if notes:
        ol = etree.SubElement(root, "ol", {"class": "footnotes"})
        for fid, i, body in notes:
            li = etree.SubElement(ol, "li", {"id": fid})
            body.tag = "span"
            li.append(body)
            back_ = etree.SubElement(li, "a", {"href": f"#fnref{i}", "class": "fn-back", "aria-label": "Back to text"})
            back_.text = "↩"


def clean(root):
    for el in root.iter():
        cls = el.get("class")
        if cls and "ltx_" in cls:
            keep = [c for c in cls.split() if c in KEEP_CLASSES or not c.startswith("ltx_")]
            if keep:
                el.set("class", " ".join(keep))
            else:
                del el.attrib["class"]


KEEP_CLASSES = {"figtoggle", "fig-live", "figlink", "striped", "opener", "ltx_equation", "ltx_eqn_table", "ltx_eqn_row", "ltx_eqn_cell", "ltx_eqn_eqno", "ltx_align_center",
                "ltx_align_left", "ltx_align_right", "ltx_align_justify", "ltx_tabular", "ltx_td", "ltx_th", "ltx_tr",
                "ltx_border_t", "ltx_border_b", "ltx_border_tt", "ltx_border_bb", "ltx_border_l", "ltx_border_r",
                "ltx_border_ll", "ltx_border_rr", "ltx_figure", "ltx_table", "ltx_flex_figure", "ltx_flex_cell",
                "ltx_flex_size_2", "ltx_flex_size_3", "ltx_flex_size_4", "ltx_flex_break", "ltx_subfigure",
                "ltx_eqn_center_padleft", "ltx_eqn_center_padright", "ltx_equationgroup", "ltx_itemize",
                "ltx_enumerate", "ltx_item", "ltx_tag_item", "ltx_font_bold", "ltx_font_italic", "ltx_font_smallcaps",
                "ltx_font_typewriter", "ltx_centering", "ltx_inline-block", "ltx_p", "ltx_para", "ltx_quote",
                "ltx_eqn_lefteqn", "ltx_align_middle", "ltx_align_top", "ltx_align_bottom", "ltx_nopad_r",
                "ltx_nopad_l", "ltx_tag_equation", "ltx_tag", "ltx_description", "ltx_listingline", "ltx_figure_panel",
                "ltx_minipage", "ltx_font_sansserif", "ltx_framed", "ltx_lstlisting", "ltx_listing", "ltx_verbatim"}


def section_outline(el):
    out = []
    for ss in el.xpath('./section'):
        k = kind_of(ss)
        if k in ("subsection", "subsubsection"):
            n, t = title_parts(ss)
            out.append(dict(id=ss.get("id"), num=n, title=t))
    return out


# outline (before ids are moved to headings)
for p in pages.values():
    p["outline"] = section_outline(p["el"])
    p["words"] = len(text(p["el"]).split())

for slug_, p in pages.items():
    root = p["el"]
    top = {"part": "part", "chapter": "chapter", "section": "section"}.get(p["kind"], "chapter")
    fix_figures(root, slug_)
    native_figs(root)
    add_widgets(root)
    fix_citations(root, slug_)
    fix_refs(root)
    fix_paragraph_titles(root)
    fix_boxes(root)
    fix_footnotes(root)
    fix_headings(root, top)
    if slug_ in ("notation", "glossary"):
        for t in root.xpath('.//table[contains(@class,"ltx_tabular")]'):
            t.set("class", t.get("class") + " striped")
    if p["kind"] == "part":
        for f in root.xpath('.//figure[contains(@class,"ltx_figure")]')[:1]:
            f.set("class", f.get("class") + " opener")
    for t in root.xpath('.//*[contains(@class,"ltx_title_document")]'):
        t.drop_tree()

for k, v in xref.items():
    if v.get("url") is None and k in id2page:
        pg = id2page[k]
        v["url"] = page_url(pg) + ("" if pages[pg]["el"].get("id") == k else "#" + k)

# ------------------------------------------------------------------ navigation order
order = list(pages.keys())
order = [s for s in order if s in front] + [s for s in order if s not in front and s not in back] + back + ["references"]

# ------------------------------------------------------------------ render
env = Environment(loader=FileSystemLoader(str(SRC / "templates")), autoescape=False, trim_blocks=True, lstrip_blocks=True)
PDF_SRC = HERE / "build" / "handbook-web.pdf"
PDF_URL = "/assets/spatial-intelligence-handbook.pdf" if PDF_SRC.exists() else None
SITE = dict(pdf_url=PDF_URL, pdf_size=f"{PDF_SRC.stat().st_size / 1e6:.0f} MB" if PDF_SRC.exists() else None,
            title="Spatial Intelligence", subtitle="Foundations, Architectures, Methodologies, Applications and Challenges",
            url="https://spatial-agi.github.io", parts=toc, pdf_pages=pdf_pages, n_refs=len(refs),
            n_figures=sum(1 for v in xref.values() if v["kind"] == "figure"),
            n_tables=sum(1 for v in xref.values() if v["kind"] == "table"))


def out(path, html):
    f = DIST / path.strip("/") / "index.html" if not path.endswith(".html") else DIST / path.strip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8")


def serialize(el):
    clean(el)
    for m in el.iter("math"):            # keep MathML (and its TeX annotation) out of the search index
        m.set("data-pagefind-ignore", "all")
    for t in el.xpath('.//*[@class="figtoggle"]'):
        t.set("data-pagefind-ignore", "all")
    s = "".join(LH.tostring(c, encoding="unicode") for c in el)
    if el.text and el.text.strip():
        s = H.escape(el.text) + s
    return re.sub(r'<div class="nf-slot" data-slot="([^"]+)"></div>', lambda m: NATIVE[m.group(1)], s)


part_by_n = {p["n"]: p for p in toc}
chapter_by_num = {c["num"]: (p, c) for p in toc for c in p["chapters"]}

reader_tpl = env.get_template("reader.html")
READER_CTX = []
for i, s in enumerate(order[:-1]):
    p = pages[s]
    prev_ = pages[order[i - 1]] if i > 0 else None
    nxt = pages[order[i + 1]] if i + 1 < len(order) - 1 else None
    body = serialize(p["el"])
    crumbs = []
    if p["part"]:
        pe = part_by_n[p["part"]]
        crumbs.append(dict(label=f"Part {pe['roman']}", url=page_url(pe["slug"]), color=pe["color"]))
    if p["chapter"] and p["kind"] == "section":
        crumbs.append(dict(label=f"Chapter {p['chapter']}", url=page_url(f"chapter-{p['chapter']}")))
    pdf_page = None
    if p["kind"] == "section":
        pdf_page = toc_pages.get(("section", p["num"]))
    elif p["kind"] == "chapter":
        pdf_page = toc_pages.get(("chapter", p["num"]))
    elif p["kind"] == "part":
        pdf_page = toc_pages.get(("part", p["num"]))
    ctx = dict(site=SITE, page=p, body=body, prev=prev_, next=nxt, crumbs=crumbs, pdf_page=pdf_page,
               minutes=max(1, round(p["words"] / 230)), part=part_by_n.get(p["part"]),
               chapter=chapter_by_num.get(p["chapter"], (None, None))[1], current=s,
               color=PART_COLORS.get(p["part"], "#3646F0"))
    READER_CTX.append((s, ctx))     # rendered at the end, once the explore data (resources per section) exists

# references page (numbered like the PDF)
ref_list = sorted(refs.values(), key=lambda r: r["num"])
out("/read/references/", env.get_template("references.html").render(site=SITE, refs=ref_list, current="references",
                                                                   page=dict(title="References", kind="back", slug="references")))

# data for the client
(DIST / "data").mkdir(parents=True, exist_ok=True)
(DIST / "data" / "xref.json").write_text(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "full"} for k, v in xref.items()}, ensure_ascii=False, separators=(",", ":")))
(DIST / "data" / "refs.json").write_text(json.dumps(
    {k: {"n": v["num"], "t": v["title"], "a": v["authors"][:8], "y": v["year"], "v": v["venue"], "x": v["arxiv"],
         "d": v["doi"], "u": v["url"], "c": sorted(set(cited_in.get(k, [])), key=lambda s: order.index(s) if s in order else 999)}
     for k, v in refs.items()}, ensure_ascii=False, separators=(",", ":")))
(DIST / "data" / "toc.json").write_text(json.dumps(dict(parts=toc, front=front, back=back,
                                                        titles={s: pages[s]["title"] for s in pages}), ensure_ascii=False))
quick = []
for s_ in order[:-1]:
    p = pages[s_]
    n = p["num"] if p["kind"] == "section" else (f"Ch. {p['num']}" if p["kind"] == "chapter" else (f"Part {p['num']}" if p["kind"] == "part" else ""))
    quick.append(dict(k="sec", n=n, t=p["title"], url=page_url(s_), s=(str(n) + " " + p["title"]).lower()))
    for o in p["outline"]:
        quick.append(dict(k="sec", n=o["num"] or "", t=o["title"], url=page_url(s_) + "#" + o["id"], s=(str(o["num"]) + " " + o["title"]).lower()))
for k, v in xref.items():
    if v["kind"] in ("figure", "table") and v.get("url"):
        cap = v["caption"]
        quick.append(dict(k="fig", n=v["label"], t=cap[:110], url=v["url"], s=(v["label"] + " " + cap).lower()))
for k, r in refs.items():
    quick.append(dict(k="ref", n=f"[{r['num']}]", t=r["title"], url=f"/explore/literature/?k={k}",
                      s=(r["title"] + " " + " ".join(r["authors"][:3]) + " " + str(r["year"])).lower()))
(DIST / "data" / "search-quick.json").write_text(json.dumps(quick, ensure_ascii=False, separators=(",", ":")))
json.dump(dict(order=order, cited_in={k: sorted(set(v)) for k, v in cited_in.items()}),
          open(DATA / "site_index.json", "w"))

# assets
for sub in ("css", "js", "fonts", "img"):
    if (SRC / sub).exists():
        shutil.copytree(SRC / sub, DIST / "assets" / sub, dirs_exist_ok=True)
shutil.copytree(HERE / "build" / "figures", DIST / "assets" / "figures", dirs_exist_ok=True)
shutil.copy2(SRC / "img" / "favicon.ico", DIST / "favicon.ico")
(DIST / "site.webmanifest").write_text(json.dumps(dict(
    name="Spatial Intelligence Handbook", short_name="Spatial Intelligence", start_url="/", display="standalone",
    background_color="#ffffff", theme_color="#3646F0",
    icons=[dict(src="/assets/img/icon-192.png", sizes="192x192", type="image/png"),
           dict(src="/assets/img/icon-512.png", sizes="512x512", type="image/png")])))
for junk in (DIST / "assets" / "img" / "logos").glob("*.md"):
    junk.unlink()
if PDF_SRC.exists():
    shutil.copy2(PDF_SRC, DIST / "assets" / "spatial-intelligence-handbook.pdf")
print(f"pages {len(pages)}  parts {len(toc)}  chapters {sum(len(p['chapters']) for p in toc)}  "
      f"sections {sum(len(c['sections']) for p in toc for c in p['chapters'])}  xref {len(xref)}  cited keys {len(cited_in)}")

# ================================================================== non-reader pages
import site_data as SD
import explore as EX


def chapter_of_page(s):
    return pages[s].get("chapter")


MILESTONES = EX.milestones(refs)
DATASETS, DTABLES = EX.datasets(pages, xref, chapter_of_page)
TERMS = EX.term_tables(pages)
GALLERY = [dict(id=k, label=v["label"], caption=v["full"], img=v["img"], url=v["url"],
                chapter=pages[id2page[k]].get("chapter") if k in id2page else None,
                part=pages[id2page[k]].get("part") if k in id2page else None)
           for k, v in xref.items() if v["kind"] == "figure" and v.get("img") and v.get("label")]
import yaml
TOOLS = yaml.safe_load((HERE / "tools_curated.yaml").read_text())
verified = json.loads((DATA / "tools_verified.json").read_text())
page_text = {s_: " ".join(pages[s_]["el"].text_content().split()) for s_ in pages}
for t in TOOLS:
    pats = [re.compile(r"(?<![\w-])" + re.escape(a_) + r"(?![\w-])") for a_ in [t["name"]] + list(t.get("aka") or [])]
    hits = []
    for s_, txt in page_text.items():
        n = sum(len(p_.findall(txt)) for p_ in pats)
        if n and pages[s_]["kind"] in ("section", "chapter", "part"):
            hits.append(dict(slug=s_, num=pages[s_]["num"] if pages[s_]["kind"] == "section" else None,
                             title=pages[s_]["title"], n=n))
    t["mentions"] = sorted(hits, key=lambda h: -h["n"])
    t["verified"] = verified.get(t["repo"], False)
TOOLS = [t for t in TOOLS if t["verified"]]
for name, obj in [("tools", TOOLS), ("milestones", MILESTONES), ("datasets", DATASETS), ("dtables", DTABLES), ("gallery", GALLERY)]:
    (DATA / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False))
    (DIST / "data" / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
(DIST / "data" / "terms.json").write_text(json.dumps(TERMS, ensure_ascii=False, separators=(",", ":")))
print(f"tools {len(TOOLS)} ({sum(1 for t in TOOLS if t['mentions'])} mentioned in the book)  milestones {len(MILESTONES)}  dataset rows {len(DATASETS)} from {len(DTABLES)} tables  gallery {len(GALLERY)}  "
      f"glossary {len(TERMS.get('glossary', []))}  notation {len(TERMS.get('notation', []))}")

AUTHORS, INSTITUTIONS = SD.authors()
label2id = {lab: xid for xid, labs in labels_of.items() for lab in labs}


def label_url(lab):
    xid = label2id.get(lab) or label2id.get(lab.replace(" ", "_"))
    if not xid:
        return None
    pg = id2page.get(xid)
    if not pg:
        return None
    return page_url(pg) + ("" if pages[pg]["el"].get("id") == xid else "#" + xid)


SHORT = {1: "Introduction", 2: "Representation", 3: "Perception to Generation", 4: "Applications", 5: "Futures"}
for p in toc:
    p["short"] = SHORT[p["n"]]
eras = SD.eras()
for k, e in enumerate(eras, 1):
    lab = ["subsec:era-symbolic-cognitive", "subsec:era-geometric-probabilistic", "subsec:era-learning-based",
           "subsec:era-foundation-models", "subsec:era-world-centered"][k - 1]
    e["url"] = label_url(lab) or "/read/1.2/"
    e["sec"] = aux.get(lab, {}).get("num", "1.2")
SITE.update(n_chapters=sum(len(p["chapters"]) for p in toc), n_authors=len(AUTHORS), n_inst=len(INSTITUTIONS),
            institutions=INSTITUTIONS, eras=eras, definition=SD.definition(), bibtex=SD.bibtex(AUTHORS),
            author_line=", ".join(a["name"] for a in AUTHORS[:6]) + f", and {len(AUTHORS) - 6} more, led by Hao Fei")
SITE["plain"] = ", ".join(a["name"] for a in AUTHORS[:-1]) + ", and " + AUTHORS[-1]["name"] + \
    ". Spatial Intelligence: Foundations, Architectures, Methodologies, Applications and Challenges. 2026. https://spatial-agi.github.io"
LOGO_OF = {"University of Oxford": "oxford", "National University of Singapore": "nus", "Nanyang Technological University": "ntu",
           "University of Rochester": "rochester", "The Chinese University of Hong Kong": "cuhk", "University of Macau": "macau",
           "Stanford University": "stanford", "Imperial College London": "imperial", "Monash University": "monash",
           "University of Cambridge": "cambridge", "University of California, Los Angeles": "ucla", "Harvard University": "harvard",
           "Microsoft Research": "msr", "Columbia University": "columbia",
           "University of California, Merced": "ucmerced", "University of Illinois Urbana-Champaign": "uiuc",
           "University of Wisconsin–Madison": "uwmadison"}


def logo(name):
    """Institution logo from src/img/logos (svg or png) with its aspect ratio; None falls back to the name as text."""
    for ext in ("svg", "png"):
        f = SRC / "img" / "logos" / f"{LOGO_OF.get(name, '-')}.{ext}"
        if f.exists():
            if ext == "svg":
                vb = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', f.read_text(errors="replace"))
                ar = float(vb.group(1)) / float(vb.group(2)) if vb else 2.0
            else:
                from PIL import Image
                w, h = Image.open(f).size
                ar = w / h
            h = round(min(42, (3600 / ar) ** .5))     # equal optical area: wide wordmarks are drawn shorter
            return dict(name=name, src=f"/assets/img/logos/{f.name}", ar=round(ar, 3), h=h, w=round(h * ar))
    return dict(name=name, src=None, w=150)


SITE["inst_logos"] = [logo(i) for i in INSTITUTIONS]
# as few rows as fit the band (~1100 px), split so the widest row is as narrow as possible (rows keep title-page order)
_w = [l["w"] + 34 for l in SITE["inst_logos"]]
_rows = -(-sum(_w) // 1060)


def _split(ws, r):
    """Contiguous split of ws into r groups minimising the widest group; returns the end index of each group but the last."""
    best = (float("inf"), [])
    def go(start, left, cuts, worst):
        nonlocal best
        if worst >= best[0]:
            return
        if left == 1:
            best = min(best, (max(worst, sum(ws[start:])), cuts))
            return
        for e in range(start + 1, len(ws) - left + 2):
            go(e, left - 1, cuts + [e], max(worst, sum(ws[start:e])))
    go(0, r, [], 0)
    return best[1]


for _e in _split(_w, _rows):
    SITE["inst_logos"][_e - 1]["br"] = True
MAP = dict(canal1=[0.49, 0.3465, 0.185, 0.1215], road=[0.49, 0.355, 0.2525, 0.165], canal2=[0.49, 0.36, 0.33, 0.218],
           sea=[0.5, 0.37, 0.515, 0.40])
PIN_AT = {4: (0.385, 0.385), 5: (0.555, 0.285), 6: (0.5, 0.125), 7: (0.655, 0.47), 8: (0.275, 0.445), 9: (0.725, 0.125),
          10: (0.915, 0.335), 11: (0.86, 0.6), 12: (0.245, 0.615), 13: (0.075, 0.39), 14: (0.2, 0.14), 15: (0.5, 0.062),
          16: (0.355, 0.058)}
pins = []
for p in toc:
    for c in p["chapters"]:
        n = int(c["num"])
        if n in PIN_AT:
            pins.append(dict(n=n, x=PIN_AT[n][0], y=PIN_AT[n][1], part=p["roman"], title=c["title"], slug=c["slug"],
                             sections=[dict(num=s["num"], title=s["title"]) for s in c["sections"]]))
era_pins = [dict(x=0.525, y=fy, roman=e["roman"], name=e["name"], years=e["years"], url=e["url"], sec=e["sec"],
                 space=e["rows"][0][1]) for fy, e in zip([0.93, 0.846, 0.768, 0.722, 0.645], eras)]


def count(path):
    f = DATA / path
    return len(json.loads(f.read_text())) if f.exists() else 0


SITE["tiles"] = [
    dict(url="/explore/literature/", n=f"{len(refs):,}", title="Literature", desc="Every work the handbook cites, with the sections that cite it."),
    dict(url="/explore/datasets/", n=f"{count('datasets.json') or '—'}", title="Datasets & benchmarks", desc="Collected from the comparison tables across the chapters."),
    dict(url="/explore/tools/", n=f"{count('tools.json') or '—'}", title="Tools & platforms", desc="Simulators, libraries and open-source code, linked to where the book uses them."),
    dict(url="/explore/timeline/", n=f"{count('milestones.json') or '—'}", title="Milestones", desc="Representative works by field and year, across the five eras."),
    dict(url="/explore/figures/", n=f"{SITE['n_figures']}", title="Figures", desc="All figures of the handbook in one gallery, each linked to its context."),
    dict(url="/explore/glossary/", n="A–Z", title="Glossary & notation", desc="Terms, abbreviations and symbols, with the sections that define them."),
]
import webfigs as WF
SITE["fig21"] = WF.fig21(SD.OPERATORS)
home_json = json.dumps(dict(map=MAP, pins=pins, eraPins=era_pins, operators=SD.OPERATORS, eras=eras,
                            partColors={ROMAN[k]: v for k, v in PART_COLORS.items()}), ensure_ascii=False)
out("/", env.get_template("home.html").render(site=SITE, home_json=home_json.replace("</", "<\\/")))
(DIST / "data" / "widgets.json").write_text(home_json)
print("home ok")

# ------------------------------------------------------------------ explore pages
raw_bib = {}
for chunk in re.split(r"\n(?=@)", (BOOK / "main.bib").read_text(encoding="utf-8", errors="replace")):
    m = re.match(r"@\w+\s*\{\s*([^,\s]+)\s*,", chunk.strip())
    if m and m.group(1) in refs:
        raw_bib[m.group(1)] = chunk.strip()
(DIST / "data" / "bib.json").write_text(json.dumps(raw_bib, ensure_ascii=False, separators=(",", ":")))
XP = {
    "hub": dict(id="hub", title="Resources for the field", tpl="explore_hub.html",
                lede="Everything the handbook cites, compares and builds on, organised so that newcomers can find their footing and experts can find the exact paper, dataset or tool."),
    "literature": dict(id="literature", title="Literature", side=True, placeholder="Search titles, authors, venues, years…",
                       sorts=[("num", "PDF order [n]"), ("year", "Newest first"), ("cited", "Most cited in the book")],
                       lede=f"All {len(refs):,} works cited in the handbook, numbered as in the PDF. Filter by the part or chapter that cites them, by type or by year, and jump straight to the citing sections."),
    "datasets": dict(id="datasets", title="Datasets & benchmarks", side=True, placeholder="Search datasets, benchmarks, tasks, modalities…",
                     sorts=[("book", "Book order"), ("name", "Name A–Z")],
                     lede=f"{len(DATASETS)} datasets and benchmarks collected from {len(DTABLES)} comparison tables of the handbook, with their properties as the tables report them and a link back to each table."),
    "tools": dict(id="tools", title="Tools & platforms", side=True, placeholder="Search simulators, libraries, models…",
                  sorts=[("mentions", "Most discussed in the book"), ("name", "Name A–Z")],
                  lede=f"{len(TOOLS)} simulators, libraries, models and open-source repositories for building spatially intelligent systems. Repository links are verified automatically; each entry links to the sections that discuss it."),
    "timeline": dict(id="timeline", title="Milestones", side=True, placeholder="",
                     lede=f"The {len(MILESTONES)} representative works of Figure 1.3, by field and year, set against the five eras of representing space. Hover a point for the work; follow it into the literature."),
    "figures": dict(id="figures", title="Figures", side=True, placeholder="Search figure captions…",
                    lede=f"All {len(GALLERY)} figures of the handbook in one place. Open any figure at full size or jump to where it appears in the text."),
    "glossary": dict(id="glossary", title="Glossary & notation", side=False, placeholder="Search terms and symbols…",
                     lede="The terms, abbreviations and symbols used across the handbook, with the section that introduces each one."),
}
for k, xp in XP.items():
    tpl = env.get_template(xp.get("tpl", "explore_list.html"))
    out("/explore/" if k == "hub" else f"/explore/{k}/", tpl.render(site=SITE, xp=xp))
print("explore ok")

# ------------------------------------------------------------------ authors, cite, contents, 404
CONTRIB = SD.contributions()
aff_of = {a["name"]: a for a in AUTHORS}
num_of = lambda lab: aux.get(lab, aux.get(lab.replace("_", " "), {})).get("num") or "?"
authors_v = []
# one card per person, in title-page order; a joint contribution block is shown on each co-author's card
block_of = {}
for c in CONTRIB:
    for n in c["names"]:
        block_of[n] = c
for a0 in AUTHORS:
    c = block_of.get(a0["name"], dict(names=[a0["name"]], aff="", items=[], advisory=False))
    coauth = [n for n in c["names"] if n != a0["name"]]
    c = dict(c, names=[a0["name"]])
    items, parts = [], set()
    for it in c["items"]:
        url = label_url(it["labels"][0]) if it["labels"] else None
        txt = SD.detex(it["tex"], num_of)
        if coauth and "(with" not in txt:
            txt += f" (with {' and '.join(coauth)})"
        items.append(dict(text=txt, url=url))
        for lab in it["labels"]:
            n = num_of(lab)
            ch = int(n.split(".")[0]) if n[:1].isdigit() else None
            for p in toc:
                if ch and any(int(cc["num"]) == ch for cc in p["chapters"]):
                    parts.add(p["roman"])
        if "Part~" in it["tex"]:
            for r in re.findall(r"Parts?~([IV]+)(?:--([IV]+))?", it["tex"]):
                lo, hi = ROMAN.index(r[0]), ROMAN.index(r[1]) if r[1] else ROMAN.index(r[0])
                parts.update(ROMAN[lo:hi + 1])
    main_part = sorted(parts, key=lambda r: ROMAN.index(r))[0] if parts else None
    role = "First author" if a0.get("first") else ("Project lead" if a0.get("lead") else None)
    authors_v.append(dict(names=c["names"], aff=", ".join(a0.get("affs", [])) or c["aff"], entries=items, advisory=c["advisory"],
                          parts=sorted(parts), role=role,
                          initials="".join(w[0] for w in c["names"][0].replace("(", "").split()[:1] + c["names"][0].split()[-1:]),
                          color=PART_COLORS[ROMAN.index(main_part)] if main_part else "#6A7189"))
# Hao Fei's entry lists his drafted parts; mark him as lead even if the block sits at the end
# metadata: verified homepage / Scholar / stated interests (data/author_profiles.json), e-mails only where the book prints them
prof_file = DATA / "author_profiles.json"
PROFILES = {p["name"]: p for p in json.loads(prof_file.read_text())} if prof_file.exists() else {}
mail_file = DATA / "author_emails.json"
for m in (json.loads(mail_file.read_text()) if mail_file.exists() else []):
    if m.get("email") and m["name"] in PROFILES:
        PROFILES[m["name"]]["email"] = m["email"].strip()
PATCHES = yaml.safe_load((HERE / "author_patches.yaml").read_text()) or {}
BOOK_EMAILS = {"Shengqiong Wu": "shengqiongwu@gmail.com", "Hao Fei": "haofei7419@gmail.com"}
for a in authors_v:
    profs = []
    for n in a["names"]:
        pr = dict(PROFILES.get(n, {}))
        pr.update(PATCHES.get(n, {}) or {})
        ex = pr.get("expertise") or pr.get("interests")      # keywords from the person's own homepage / OpenReview
        if isinstance(ex, str):
            ex = [x.strip() for x in re.split(r"[,;]", ex) if x.strip()]
        pr["expertise"] = ex or []
        pr["name"] = n
        profs.append(pr)
    a["profiles"] = profs
    # e-mail per person: patch file > address printed in the book > address the person publishes on their own page
    for pr in profs:
        n = pr["name"]
        pr["email"] = (PATCHES.get(n, {}) or {}).get("email") or BOOK_EMAILS.get(n) or pr.get("email")
        if pr["email"]:     # rendered by JS from two parts, so the address is not plain text in the HTML
            user, _, dom = pr["email"].partition("@")
            pr["em_u"], pr["em_d"] = user[::-1], dom[::-1]
    a["email"] = None
out("/team/", env.get_template("authors.html").render(site=SITE, authors=authors_v))

UPDATES = [dict(date="2026-11-08", text="New website: the full handbook online with PDF-identical numbering, an interactive map of the book, and explorers for the literature, datasets and benchmarks, tools, milestones, figures and glossary.")]
REPO = "https://github.com/spatial-agi/spatial-agi.github.io"
CONTACT = [("Hao Fei", "haofei7419@gmail.com"), ("Shengqiong Wu", "shengqiongwu@gmail.com")]
out("/contribute/", env.get_template("contribute.html").render(site=SITE, updates=UPDATES, repo=REPO,
    contact=[dict(name=n, u=e.partition("@")[0][::-1], d=e.partition("@")[2][::-1]) for n, e in CONTACT]))
# old routes keep working
REDIRECT = '<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{0}"><meta http-equiv="refresh" content="0; url={0}"><script>location.replace("{0}" + location.hash)</script><a href="{0}">{0}</a>'
out("/authors/", REDIRECT.format("/team/"))
out("/cite/", REDIRECT.format("/#cite").replace('" + location.hash', '"'))

# chapter and part lengths in PDF pages
starts = [(int(c["num"]), c["page"]) for p in toc for c in p["chapters"] if c["page"]]
starts.sort()
end_page = toc_pages.get(("chapter", "17"), 0) + 14
for i, (n, pg) in enumerate(starts):
    nxt = starts[i + 1][1] if i + 1 < len(starts) else end_page
    for p in toc:
        for c in p["chapters"]:
            if int(c["num"]) == n:
                c["pages"] = max(1, nxt - pg)
for p in toc:
    p["pages"] = sum(c.get("pages", 0) for c in p["chapters"])
out("/read/", env.get_template("contents.html").render(site=SITE, n_sections=sum(len(c["sections"]) for p in toc for c in p["chapters"])))
out("/404.html", env.get_template("404.html").render(site=SITE))
print("authors, cite, contents ok")

# ------------------------------------------------------------------ reader pages, with the resources of each section
for s_, ctx in READER_CTX:
    p = ctx["page"]
    res = None
    if p["kind"] in ("section", "chapter"):
        if p["kind"] == "section":
            n_refs = sum(1 for k, v in cited_in.items() if s_ in v)
            n_ds = sum(1 for d in DATASETS if d["section"] == p["num"])
            tl = [t for t in TOOLS if any(m["slug"] == s_ for m in t["mentions"])]
            q = f"sec={s_}"
        else:
            ch = p["num"]
            n_refs = sum(1 for k, v in cited_in.items() if any(chapter_of_page(x) == ch for x in v if x in pages))
            n_ds = sum(1 for d in DATASETS if d["chapter"] == ch)
            tl = [t for t in TOOLS if any(pages[m["slug"]].get("chapter") == ch for m in t["mentions"])]
            q = f"ch={ch}"
        res = dict(q=q, refs=n_refs, datasets=n_ds, tools=len(tl), tool_names=[t["name"] for t in tl][:6])
    ctx["resources"] = res
    out(page_url(s_), reader_tpl.render(**ctx))
print("reader pages rendered", len(READER_CTX))
