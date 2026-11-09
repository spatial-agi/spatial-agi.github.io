// Explore: literature, datasets & benchmarks, tools & platforms, milestones timeline, figure gallery, glossary & notation.
import { $, $$, copy, getJSON, esc } from './site.js';

const root = $('[data-explore]'); const page = root?.dataset.explore;
const qIn = $('[data-q]'), sortSel = $('[data-sort]'), out = $('[data-results]'), countEl = $('[data-count]'),
  more = $('[data-more]'), facetsEl = $('[data-facets]'), viz = $('[data-viz]');
const params = new URLSearchParams(location.search);
const SEC = params.get('sec');
function secBanner(label) {
  if (!SEC) return;
  const b = document.createElement('div'); b.className = 'secbanner';
  b.innerHTML = 'Showing ' + label + ' for <b>' + (/^\d/.test(SEC) ? 'Section ' + SEC : SEC) + '</b> <a href="' + location.pathname + '">Show all</a>';
  countEl.before(b);
}
const PARTC = { I: 'var(--p1)', II: 'var(--p2)', III: 'var(--p3)', IV: 'var(--p4)', V: 'var(--p5)' };
const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V'];
const norm = s => (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');
const debounce = (f, ms = 120) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => f(...a), ms); }; };

let toc, chapterTitle = {}, chapterPart = {};
async function loadToc() {
  toc = await getJSON('/data/toc.json');
  for (const p of toc.parts) for (const c of p.chapters) { chapterTitle[c.num] = c.title; chapterPart[c.num] = p.roman; }
}
const chOfSlug = s => { let m = s.match(/^(\d+)\./) || s.match(/^chapter-(\d+)$/); return m ? m[1] : null; };
const secLabel = s => /^\d/.test(s) ? s : s.startsWith('chapter-') ? 'Ch. ' + s.slice(8) : s.startsWith('part-') ? 'Part ' + s.slice(5).toUpperCase() : s;

// generic paged renderer
function pager(items, renderItem, step = 50) {
  let shown = 0;
  out.innerHTML = ''; more.innerHTML = '';
  const add = () => {
    const chunk = items.slice(shown, shown + step); shown += chunk.length;
    out.insertAdjacentHTML('beforeend', chunk.map(renderItem).join(''));
    more.innerHTML = shown < items.length ? `<button type="button" class="btn">Show more (${items.length - shown} left)</button>` : '';
    more.querySelector('button')?.addEventListener('click', add);
  };
  add();
}
// facet group: [{value,label,count,color}] with single or multi selection
function facetGroup(title, opts, selected, onChange, { multi = true, max = 30 } = {}) {
  const box = document.createElement('div'); box.className = 'facet';
  const render = () => {
    box.innerHTML = `<div class="facet-h">${esc(title)}${selected.size ? '<button type="button" class="facet-clear">Clear</button>' : ''}</div>` +
      opts.filter(o => o.count !== 0).slice(0, max).map(o => `<button type="button" class="facet-opt ${selected.has(o.value) ? 'is-on' : ''}" data-v="${esc(o.value)}" ${o.color ? `style="--fc:${o.color}"` : ''}><span class="fo-l">${o.label}</span><span class="fo-n">${o.count ?? ''}</span></button>`).join('');
    box.querySelector('.facet-clear')?.addEventListener('click', () => { selected.clear(); render(); onChange(); });
    $$('.facet-opt', box).forEach(b => b.addEventListener('click', () => {
      const v = b.dataset.v;
      if (selected.has(v)) selected.delete(v); else { if (!multi) selected.clear(); selected.add(v); }
      render(); onChange();
    }));
  };
  render(); return box;
}

// ======================================================= LITERATURE
async function literature() {
  await loadToc();
  const refs = await getJSON('/data/refs.json');
  const items = Object.entries(refs).map(([k, r]) => {
    const chs = [...new Set(r.c.map(chOfSlug).filter(Boolean))];
    const v = r.v || '';
    const type = /arxiv/i.test(v) || r.x ? 'arXiv preprint' : /proceed|conference|workshop|symposium|cvpr|iccv|eccv|neurips|icml|iclr|aaai|ijcai|acl|emnlp|naacl|siggraph|icra|iros|corl|rss/i.test(v) ? 'Conference' : v ? 'Journal & other' : 'Other';
    return { k, ...r, chs, parts: [...new Set(chs.map(c => chapterPart[c]))], type, yr: parseInt(r.y) || 0,
      s: norm(`${r.t} ${r.a.join(' ')} ${v} ${r.y} ${k}`) };
  });
  const selPart = new Set(), selCh = new Set(), selType = new Set();
  let yearRange = null;
  if (params.get('ch')) selCh.add(params.get('ch'));
  secBanner('the works cited');
  if (params.get('q')) qIn.value = params.get('q');
  if (params.get('k')) qIn.value = params.get('k');
  const count = (f) => { const m = new Map(); items.forEach(it => f(it).forEach(v => m.set(v, (m.get(v) || 0) + 1))); return m; };
  const pc = count(it => it.parts), cc = count(it => it.chs), tc = count(it => [it.type]);
  const update = () => apply();
  facetsEl.append(
    facetGroup('Part', ['I', 'II', 'III', 'IV', 'V'].map(r => ({ value: r, label: `<span class="dotc" style="background:${PARTC[r]}"></span>Part ${r}`, count: pc.get(r) || 0 })), selPart, update),
    facetGroup('Cited in chapter', Object.keys(chapterTitle).map(c => ({ value: c, label: `<b>${c}</b> ${esc(chapterTitle[c].replace('Spatial Intelligence for ', ''))}`, count: cc.get(c) || 0 })), selCh, update),
    facetGroup('Type', ['Conference', 'Journal & other', 'arXiv preprint', 'Other'].map(t => ({ value: t, label: t, count: tc.get(t) || 0 })), selType, update));
  // year histogram
  const years = items.map(i => i.yr).filter(y => y >= 1940 && y <= 2030);
  const y0 = 1990, y1 = Math.max(...years);
  const bins = []; for (let y = y0; y <= y1; y++) bins.push({ y, n: 0 });
  let older = 0; years.forEach(y => y < y0 ? older++ : bins[y - y0].n++);
  const maxN = Math.max(...bins.map(b => b.n));
  viz.innerHTML = `<div class="hist" role="group" aria-label="Filter by year"><div class="hist-bars">${`<button type="button" class="hb hb-old" data-y="old" title="before ${y0}: ${older}" style="--h:${Math.max(4, older / maxN * 100)}%"><span>&lt;${y0}</span></button>`}${bins.map(b => `<button type="button" class="hb" data-y="${b.y}" title="${b.y}: ${b.n} works" style="--h:${Math.max(2, b.n / maxN * 100)}%"><span>${b.y % 5 === 0 ? b.y : ''}</span></button>`).join('')}</div><div class="hist-cap">Works per year · click a bar to filter, click again to clear</div></div>`;
  $$('.hb', viz).forEach(b => b.addEventListener('click', () => {
    const v = b.dataset.y; yearRange = yearRange === v ? null : v;
    $$('.hb', viz).forEach(x => x.classList.toggle('is-on', x.dataset.y === yearRange)); apply();
  }));
  const render = it => `<article class="lit" id="k-${esc(it.k)}">
      <div class="lit-n">[${it.n}]</div>
      <div class="lit-b"><h3>${esc(it.t)}</h3>
        <div class="lit-a">${esc(it.a.slice(0, 8).join(', '))}${it.a.length > 8 ? ', et al.' : ''}</div>
        <div class="lit-v">${esc([it.v, it.y].filter(Boolean).join(' · '))}</div>
        <div class="lit-c">${it.c.slice(0, 10).map(s => `<a href="/read/${s}/" class="secchip" style="--pc:${PARTC[chapterPart[chOfSlug(s)]] || 'var(--cobalt)'}">${esc(secLabel(s))}</a>`).join('')}${it.c.length > 10 ? `<span class="muted">+${it.c.length - 10}</span>` : ''}</div>
        <div class="lit-l">${it.x ? `<a href="https://arxiv.org/abs/${it.x}" target="_blank" rel="noopener">arXiv</a>` : ''}${it.d ? `<a href="https://doi.org/${it.d}" target="_blank" rel="noopener">DOI</a>` : ''}${it.u && !it.x ? `<a href="${esc(it.u)}" target="_blank" rel="noopener">Link</a>` : ''}<a href="https://scholar.google.com/scholar?q=${encodeURIComponent(it.t)}" target="_blank" rel="noopener">Scholar</a><button type="button" data-bib="${esc(it.k)}">BibTeX</button></div>
      </div></article>`;
  function apply() {
    const terms = norm(qIn.value).split(/\s+/).filter(Boolean);
    let res = items.filter(it => (!SEC || it.c.includes(SEC)) && (!selPart.size || it.parts.some(p => selPart.has(p))) && (!selCh.size || it.chs.some(c => selCh.has(c)))
      && (!selType.size || selType.has(it.type)) && (!yearRange || (yearRange === 'old' ? it.yr < y0 : it.yr === +yearRange))
      && terms.every(t => it.s.includes(t)));
    const s = sortSel.value;
    res.sort(s === 'year' ? (a, b) => b.yr - a.yr || a.n - b.n : s === 'cited' ? (a, b) => b.c.length - a.c.length || a.n - b.n : (a, b) => a.n - b.n);
    countEl.textContent = `${res.length.toLocaleString()} of ${items.length.toLocaleString()} works`;
    pager(res, render);
  }
  out.addEventListener('click', async e => {
    const b = e.target.closest('[data-bib]'); if (!b) return;
    const bib = await getJSON('/data/bib.json'); copy(bib[b.dataset.bib] || '', 'BibTeX copied');
  });
  qIn.addEventListener('input', debounce(apply)); sortSel.addEventListener('change', apply);
  apply();
}

// ======================================================= DATASETS & BENCHMARKS
async function datasets() {
  await loadToc();
  const [rows, tables, refs] = await Promise.all([getJSON('/data/datasets.json'), getJSON('/data/dtables.json'), getJSON('/data/refs.json')]);
  const items = rows.map(r => ({ ...r, s: norm(`${r.name} ${r.group || ''} ${r.attrs.map(a => a[1]).join(' ')} ${r.table}`) }));
  const selCh = new Set(), selTab = new Set();
  if (params.get('ch')) selCh.add(params.get('ch'));
  secBanner('the datasets and benchmarks');
  const cc = new Map(); items.forEach(i => cc.set(i.chapter, (cc.get(i.chapter) || 0) + 1));
  const update = () => apply();
  facetsEl.append(facetGroup('Chapter', [...cc.keys()].sort((a, b) => a - b).map(c => ({ value: c, label: `<b>${c}</b> ${esc((chapterTitle[c] || '').replace('Spatial Intelligence for ', ''))}`, count: cc.get(c), color: PARTC[chapterPart[c]] })), selCh, update));
  const tabBox = document.createElement('div'); facetsEl.append(tabBox);
  const renderTabs = () => {
    tabBox.innerHTML = '';
    const ts = tables.filter(t => !selCh.size || selCh.has(t.chapter));
    tabBox.append(facetGroup('Source table', ts.map(t => ({ value: t.label, label: `<b>${t.label.replace('Table ', '')}</b> ${esc(t.caption.split(/[.;:(]/)[0].slice(0, 58))}`, count: t.n })), selTab, apply, { max: 80 }));
  };
  const card = r => {
    const cites = r.keys.map(k => refs[k]).filter(Boolean);
    return `<article class="ds" style="--pc:${PARTC[chapterPart[r.chapter]] || 'var(--cobalt)'}">
      <div class="ds-top"><h3>${esc(r.name)}</h3>${cites.map(c => `<a class="cite" href="/explore/literature/?k=${encodeURIComponent(r.keys[0])}" title="${esc(c.t)}">[${c.n}]</a>`).join('')}</div>
      ${r.group ? `<div class="ds-group">${esc(r.group)}</div>` : ''}
      <dl class="ds-attrs">${r.attrs.slice(0, 6).map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>
      <a class="ds-src" href="${r.url}">${esc(r.table)} · ${r.section ? 'Section ' + esc(r.section) : 'Chapter ' + esc(r.chapter)}</a></article>`;
  };
  function apply() {
    if (this !== 'tabs') renderTabs();
    const terms = norm(qIn.value).split(/\s+/).filter(Boolean);
    const res = items.filter(i => (!SEC || i.section === SEC) && (!selCh.size || selCh.has(i.chapter)) && (!selTab.size || selTab.has(i.table)) && terms.every(t => i.s.includes(t)));
    if (sortSel.value === 'name') res.sort((a, b) => a.name.localeCompare(b.name));
    countEl.textContent = `${res.length} of ${items.length} datasets and benchmarks from ${tables.length} tables`;
    out.className = 'xp-results grid-ds'; pager(res, card, 60);
  }
  viz.innerHTML = `<div class="ds-bars">${[...cc.keys()].sort((a, b) => a - b).map(c => `<button type="button" data-c="${c}" style="--w:${cc.get(c) / Math.max(...cc.values()) * 100}%;--pc:${PARTC[chapterPart[c]]}"><span class="dsb-l">Ch. ${c}</span><span class="dsb-bar"><span></span></span><span class="dsb-n">${cc.get(c)}</span></button>`).join('')}</div>`;
  $$('[data-c]', viz).forEach(b => b.addEventListener('click', () => { const c = b.dataset.c; selCh.has(c) ? selCh.delete(c) : (selCh.clear(), selCh.add(c)); facetsEl.firstChild.replaceWith(facetGroup('Chapter', [...cc.keys()].sort((a, b) => a - b).map(c => ({ value: c, label: `<b>${c}</b> ${esc((chapterTitle[c] || '').replace('Spatial Intelligence for ', ''))}`, count: cc.get(c), color: PARTC[chapterPart[c]] })), selCh, update)); apply(); }));
  if (params.get('q')) qIn.value = params.get('q');
  qIn.addEventListener('input', debounce(apply)); sortSel?.addEventListener('change', apply);
  apply();
}

// ======================================================= TOOLS & PLATFORMS
async function tools() {
  const data = await getJSON('/data/tools.json');
  const cats = [...new Set(data.map(t => t.cat))];
  const selCat = new Set(), selM = new Set();
  const CH = params.get('ch');
  secBanner('the tools and platforms');
  if (CH && !SEC) { const b = document.createElement('div'); b.className = 'secbanner'; b.innerHTML = 'Showing tools discussed in <b>Chapter ' + CH + '</b> <a href="' + location.pathname + '">Show all</a>'; countEl.before(b); }
  const update = () => apply();
  facetsEl.append(facetGroup('Category', cats.map(c => ({ value: c, label: esc(c), count: data.filter(t => t.cat === c).length })), selCat, update),
    facetGroup('In the handbook', [{ value: 'yes', label: 'Discussed in the text', count: data.filter(t => t.mentions.length).length }, { value: 'no', label: 'Related, not discussed', count: data.filter(t => !t.mentions.length).length }], selM, update, { multi: false }));
  const card = t => `<article class="tool">
      <div class="tool-top"><h3>${esc(t.name)}</h3><span class="tool-cat">${esc(t.cat)}</span></div>
      <p>${esc(t.desc)}</p>
      <a class="tool-repo" href="https://github.com/${t.repo}" target="_blank" rel="noopener"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 .2a8 8 0 0 0-2.5 15.6c.4 0 .5-.2.5-.4v-1.5c-2.2.5-2.7-1-2.7-1-.4-.9-.9-1.2-.9-1.2-.7-.5.1-.5.1-.5.8.1 1.2.8 1.2.8.7 1.3 1.9.9 2.3.7.1-.5.3-.9.5-1.1-1.8-.2-3.6-.9-3.6-4 0-.9.3-1.6.8-2.1-.1-.2-.4-1 .1-2.1 0 0 .7-.2 2.2.8a7.6 7.6 0 0 1 4 0c1.5-1 2.2-.8 2.2-.8.4 1.1.2 1.9.1 2.1.5.6.8 1.3.8 2.1 0 3.1-1.9 3.8-3.6 4 .3.3.6.8.6 1.5v2.2c0 .2.1.5.6.4A8 8 0 0 0 8 .2z"/></svg>${esc(t.repo)}</a>
      ${t.mentions.length ? `<div class="tool-m"><span>In the handbook</span>${t.mentions.slice(0, 6).map(m => `<a class="secchip" href="/read/${m.slug}/" title="${esc(m.title)}">${esc(m.num || m.title.slice(0, 24))}</a>`).join('')}${t.mentions.length > 6 ? `<span class="muted">+${t.mentions.length - 6}</span>` : ''}</div>` : `<div class="tool-m tool-nm">Related infrastructure, not discussed in the text</div>`}
    </article>`;
  function apply() {
    const terms = norm(qIn.value).split(/\s+/).filter(Boolean);
    const res = data.filter(t => (!SEC || t.mentions.some(m => m.slug === SEC)) && (!CH || t.mentions.some(m => (m.slug.split('.')[0] === CH) || m.slug === 'chapter-' + CH)) && (!selCat.size || selCat.has(t.cat)) && (!selM.size || (selM.has('yes') ? t.mentions.length : !t.mentions.length))
      && terms.every(q => norm(`${t.name} ${t.desc} ${t.repo} ${t.cat} ${(t.aka || []).join(' ')}`).includes(q)));
    const s = sortSel.value;
    res.sort(s === 'name' ? (a, b) => a.name.localeCompare(b.name) : (a, b) => b.mentions.reduce((x, m) => x + m.n, 0) - a.mentions.reduce((x, m) => x + m.n, 0) || a.name.localeCompare(b.name));
    countEl.textContent = `${res.length} of ${data.length} tools and platforms · every repository link verified`;
    out.className = 'xp-results grid-tools'; pager(res, card, 60);
  }
  qIn.addEventListener('input', debounce(apply)); sortSel.addEventListener('change', apply);
  apply();
}

// ======================================================= MILESTONES TIMELINE (Figure 1.3, interactive)
async function timeline() {
  $('.xp-toolbar').hidden = true;
  const [data, { timelineChart, TL_CAPTION }] = await Promise.all([getJSON('/data/milestones.json'), import('./widgets.js')]);
  const fields = [...new Set(data.map(d => d.field))];
  const colorOf = Object.fromEntries(data.map(d => [d.field, d.color]));
  const sel = new Set();
  facetsEl.append(facetGroup('Field', fields.map(f => ({ value: f, label: esc(f), count: data.filter(d => d.field === f).length, color: colorOf[f] })), sel, () => draw()));
  viz.innerHTML = '<div class="tl-host"></div><div class="hist-cap">' + TL_CAPTION + '</div>';
  const host = $('.tl-host', viz);
  function draw() {
    const vis = data.filter(d => !sel.size || sel.has(d.field));
    timelineChart(host, data, vis);
    countEl.textContent = vis.length + ' milestones';
    const list = [...vis].sort((a, b) => a.year - b.year);
    out.className = 'xp-results tl-list';
    out.innerHTML = list.map(d => '<div class="tl-row"><span class="tl-y">' + d.year + '</span><span class="dotc" style="background:' + d.color + '"></span><span class="tl-l">' + esc(d.label) + '</span><span class="tl-f">' + esc(d.field) + '</span><a class="cite" href="/explore/literature/?k=' + encodeURIComponent(d.keys[0]) + '">[' + d.num + ']</a></div>').join('');
  }
  draw();
}

// ======================================================= FIGURES GALLERY
async function figures() {
  await loadToc();
  const data = await getJSON('/data/gallery.json');
  const selPart = new Set();
  facetsEl.append(facetGroup('Part', ['I', 'II', 'III', 'IV', 'V'].map((r, i) => ({ value: String(i + 1), label: `<span class="dotc" style="background:${PARTC[r]}"></span>Part ${r}`, count: data.filter(d => d.part === i + 1).length })), selPart, () => apply()));
  const card = d => `<figure class="gal" data-src="${d.img.replace('.thumb.webp', '.webp')}"><button type="button" class="gal-img" aria-label="Enlarge ${esc(d.label)}"><img src="${d.img}" alt="" loading="lazy"></button><figcaption><b>${esc(d.label)}</b> ${esc(d.caption.slice(0, 140))}${d.caption.length > 140 ? '…' : ''}<a href="${d.url}">In context →</a></figcaption></figure>`;
  let res = [];
  function apply() {
    const terms = norm(qIn.value).split(/\s+/).filter(Boolean);
    res = data.filter(d => (!selPart.size || selPart.has(String(d.part))) && terms.every(t => norm(d.label + ' ' + d.caption).includes(t)));
    countEl.textContent = `${res.length} of ${data.length} figures`;
    out.className = 'xp-results grid-gal'; pager(res, card, 36);
  }
  out.addEventListener('click', e => {
    const b = e.target.closest('.gal-img'); if (!b) return;
    const f = b.closest('.gal'), d = res.find(x => f.dataset.src.includes(x.img.replace('.thumb.webp', '')));
    const lb = document.createElement('div'); lb.className = 'lightbox';
    lb.innerHTML = `<img src="${f.dataset.src}" alt=""><div class="lb-cap"><b>${esc(d?.label)}.</b> ${esc(d?.caption)} <a href="${d?.url}" style="color:#aab2ff">Open in context →</a></div>`;
    const close = ev => { if (ev.target.tagName !== 'A') lb.remove(); }; lb.addEventListener('click', close);
    addEventListener('keydown', ev => ev.key === 'Escape' && lb.remove(), { once: true }); document.body.append(lb);
  });
  qIn.addEventListener('input', debounce(apply)); apply();
}

// ======================================================= GLOSSARY & NOTATION
async function glossary() {
  const data = await getJSON('/data/terms.json');
  let tab = params.get('tab') === 'notation' ? 'notation' : 'glossary';
  viz.innerHTML = `<div class="segtabs" role="tablist"><button type="button" role="tab" data-tab="glossary">Glossary (${data.glossary.length})</button><button type="button" role="tab" data-tab="notation">Notation (${data.notation.length})</button></div>`;
  const row = t => `<div class="term"><div class="term-k">${t.term_html}</div><div class="term-d">${t.desc_html}</div>${t.url ? `<a class="secchip" href="${t.url}">${esc(t.ref)}</a>` : `<span class="muted">${esc(t.ref)}</span>`}</div>`;
  function apply() {
    $$('[data-tab]', viz).forEach(b => b.setAttribute('aria-selected', b.dataset.tab === tab));
    const terms = norm(qIn.value).split(/\s+/).filter(Boolean);
    const res = data[tab].filter(t => terms.every(q => norm(t.term + ' ' + t.desc).includes(q)));
    countEl.textContent = `${res.length} ${tab === 'glossary' ? 'terms, in order of first appearance' : 'symbols, in chapter order'}`;
    out.className = 'xp-results terms prose-lite'; out.innerHTML = res.map(row).join('') || '<p class="muted">No match.</p>'; more.innerHTML = '';
  }
  $$('[data-tab]', viz).forEach(b => b.addEventListener('click', () => { tab = b.dataset.tab; apply(); }));
  qIn.addEventListener('input', debounce(apply)); apply();
}

({ literature, datasets, tools, timeline, figures, glossary })[page]?.();
