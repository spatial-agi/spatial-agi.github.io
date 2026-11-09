// Reader: citation and cross-reference popovers, footnotes, figure lightbox, scroll-spy, progress, text size, cite.
import { $, $$, copy, toast, getJSON, esc } from './site.js';

const prose = $('.prose');
// ---------------- text size ----------------
const FS = [0.94, 1.0, 1.075, 1.15, 1.24];
let fs = +(localStorage.getItem('fs') ?? 2);
const applyFs = () => document.documentElement.style.setProperty('--reading', FS[fs] + 'rem');
applyFs();
$$('[data-fs]').forEach(b => b.addEventListener('click', () => { fs = Math.max(0, Math.min(FS.length - 1, fs + +b.dataset.fs)); localStorage.setItem('fs', fs); applyFs(); }));

// ---------------- progress + scroll-spy ----------------
const bar = $('.progress span');
const spyLinks = $$('[data-spy]');
const targets = spyLinks.map(a => document.getElementById(a.dataset.spy)).filter(Boolean);
function onScroll() {
  if (bar && prose) {
    const r = prose.getBoundingClientRect(), h = r.height - innerHeight * 0.6;
    bar.style.width = Math.max(0, Math.min(1, -r.top / Math.max(h, 1))) * 100 + '%';
  }
  let cur = null;
  for (const t of targets) { if (t.getBoundingClientRect().top < 120) cur = t.id; else break; }
  spyLinks.forEach(a => a.classList.toggle('is-active', a.dataset.spy === cur));
}
addEventListener('scroll', onScroll, { passive: true }); onScroll();
// keep current item visible in the left toc
$('.toc .is-current')?.scrollIntoView({ block: 'center' });

// ---------------- popovers ----------------
let pop, popFor, hideT;
function placePop(el, html) {
  hidePop(true);
  pop = document.createElement('div'); pop.className = 'pop'; pop.innerHTML = html; document.body.append(pop);
  const r = el.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
  let left = Math.min(Math.max(12, r.left + r.width / 2 - w / 2), innerWidth - w - 12);
  let top = r.bottom + 8; if (top + h > innerHeight - 8) top = r.top - h - 8;
  pop.style.left = left + scrollX + 'px'; pop.style.top = top + scrollY + 'px';
  popFor = el;
  pop.addEventListener('mouseenter', () => clearTimeout(hideT));
  pop.addEventListener('mouseleave', () => hidePop());
}
function hidePop(now) { clearTimeout(hideT); const f = () => { pop?.remove(); pop = popFor = null; }; now ? f() : (hideT = setTimeout(f, 220)); }
const refsP = () => getJSON('/data/refs.json');
const xrefP = () => getJSON('/data/xref.json');
async function citeHTML(k) {
  const r = (await refsP())[k]; if (!r) return '';
  const au = r.a.length ? r.a.slice(0, 6).join(', ') + (r.a.length > 6 ? ', et al.' : '') : '';
  const q = encodeURIComponent(r.t);
  const links = [r.x && `<a href="https://arxiv.org/abs/${r.x}" target="_blank" rel="noopener">arXiv</a>`,
    r.d && `<a href="https://doi.org/${r.d}" target="_blank" rel="noopener">DOI</a>`,
    r.u && !r.x && `<a href="${esc(r.u)}" target="_blank" rel="noopener">Link</a>`,
    `<a href="https://scholar.google.com/scholar?q=${q}" target="_blank" rel="noopener">Scholar</a>`,
    `<a href="/explore/literature/?q=${q}">In literature explorer</a>`].filter(Boolean).join('');
  return `<div class="p-kind">Reference</div><div class="p-title"><span class="p-num">[${r.n}]</span>${esc(r.t)}</div>${au ? `<div class="p-auth">${esc(au)}</div>` : ''}<div class="p-ven">${esc([r.v, r.y].filter(Boolean).join(', '))}</div><div class="p-links">${links}</div>`;
}
async function xrefHTML(id) {
  const x = (await xrefP())[id]; if (!x) return '';
  if (x.kind === 'figure' || x.kind === 'table')
    return `<div class="p-kind">${x.kind}</div>${x.img ? `<img src="${x.img}" alt="">` : ''}<div class="p-cap"><b>${esc(x.label)}.</b> ${esc(x.caption)}</div>`;
  return `<div class="p-kind">${esc(x.kind)}</div><div class="p-title">${x.label ? `<span class="p-num" style="color:var(--cobalt)">${esc(x.label)}</span>` : ''}${esc(x.caption)}</div>`;
}
const hoverable = matchMedia('(hover: hover)').matches;
async function show(el) {
  let html = '';
  if (el.classList.contains('cite')) html = await citeHTML(el.dataset.k);
  else if (el.classList.contains('xref')) html = await xrefHTML(el.dataset.x);
  else if (el.dataset.fn) { const li = document.getElementById(el.dataset.fn); html = li ? `<div class="p-kind">Footnote</div><div>${li.querySelector('span')?.innerHTML ?? ''}</div>` : ''; }
  if (html && popFor !== el) placePop(el, html);
}
document.addEventListener('mouseover', e => {
  const el = e.target.closest('a.cite, a.xref, sup.fn a'); if (!el || !hoverable) return;
  clearTimeout(hideT); el._t = setTimeout(() => show(el), 160);
  el.addEventListener('mouseleave', () => { clearTimeout(el._t); hidePop(); }, { once: true });
});
document.addEventListener('click', e => {
  const el = e.target.closest('a.cite, sup.fn a');
  if (el && !hoverable) { e.preventDefault(); show(el); return; }
  if (pop && !e.target.closest('.pop')) hidePop(true);
});
addEventListener('scroll', () => pop && !pop.matches(':hover') && hidePop(true), { passive: true });

// ---------------- lightbox ----------------
document.addEventListener('click', e => {
  const img = e.target.closest('.prose img.fig-img'); if (!img) return;
  const fig = img.closest('figure'), cap = fig?.querySelector('figcaption');
  const lb = document.createElement('div'); lb.className = 'lightbox';
  lb.innerHTML = `<img src="${img.src}" alt="">${cap ? `<div class="lb-cap">${cap.innerHTML.replace(/<span class="cap-tag">([^<]*)<\/span>/, '<b>$1.</b>')}</div>` : ''}`;
  const close = () => { lb.remove(); removeEventListener('keydown', onKey); };
  const onKey = ev => ev.key === 'Escape' && close();
  lb.addEventListener('click', close); addEventListener('keydown', onKey); document.body.append(lb);
});

// ---------------- tools ----------------
$('[data-copy-link]')?.addEventListener('click', () => copy(location.href.split('#')[0], 'Link copied'));
$('[data-cite-section]')?.addEventListener('click', e => {
  const b = e.currentTarget, url = 'https://spatial-agi.github.io' + b.dataset.url;
  const key = 'wu2026spatial' + (b.dataset.title.match(/^[\d.]+/)?.[0]?.replace(/\./g, '_') ?? '');
  const bib = `@incollection{${key},\n  title     = {${b.dataset.title}},\n  booktitle = {Spatial Intelligence: Foundations, Architectures, Methodologies, Applications and Challenges},\n  author    = {Wu, Shengqiong and others and Fei, Hao},\n  year      = {2026},\n  url       = {${url}}\n}`;
  copy(bib, 'BibTeX copied');
});
// keyboard: [ and ] for previous / next page
document.addEventListener('keydown', e => {
  if (/input|textarea/i.test(document.activeElement.tagName) || e.metaKey || e.ctrlKey) return;
  if (e.key === '[') $('a[rel=prev]')?.click();
  if (e.key === ']') $('a[rel=next]')?.click();
});

// ---------------- interactive versions of key figures ----------------
$$('.figtoggle').forEach(t => t.addEventListener('click', async e => {
  const b = e.target.closest('[data-fv]'); if (!b) return;
  const fig = t.closest('figure'), live = fig.querySelector('.fig-live'), img = fig.querySelector('img.fig-img');
  const isLive = b.dataset.fv === 'live';
  $$('[data-fv]', t).forEach(x => x.setAttribute('aria-selected', String(x === b)));
  if (isLive && !live.dataset.ready) {
    const [W, D] = await Promise.all([import('./widgets.js'), getJSON('/data/widgets.json')]);
    await ({ eras: W.mountEras, timeline: W.mountTimeline })[live.dataset.widget](live, D);
    live.dataset.ready = '1';
  }
  live.hidden = !isLive; img.hidden = isLive;
}));
$$('.figtoggle[data-default="live"] [data-fv="live"]').forEach(b => b.click());
// figures drawn natively for the web (Fig. 1.1, Fig. 2.1)
if ($('.nf[data-nf]')) import('./nfig.js').then(m => m.mountNative());
