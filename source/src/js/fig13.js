// Figure 1.3 (representative works by field and year), drawn from the print TikZ by pipeline/fig13.py.
// Hover or focus a work: its year is marked on the axis and across all fields, and its label is a citation
// (the reader's reference popover applies). Hover a field heading or an era numeral to see only its works;
// click to keep that view, click again or press Esc to clear. Works appear in time order the first time
// the figure scrolls into view.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

export function fig13(el) {
  const svg = $('svg', el), card = $('.nf-card', el);
  const info = JSON.parse($('.nf-info', el).textContent);
  const works = $$('.ms', svg), heads = $$('.fh', svg), eras = $$('.eh', svg);
  const bands = $$('.eraband', svg), cols = $$('.fl', svg);
  const guides = $$('.yguide', svg), pill = $('.ypill text', svg), hl = $('.hl', svg);

  // ---------------- one work
  let cur = null;
  const mark = g => {
    if (g === cur) return;
    cur = g;
    works.forEach(w => w.classList.toggle('is-on', w === g));
    guides.forEach(x => x.classList.toggle('on', !!g)); hl.classList.toggle('on', !!g);
    if (!g) return;
    const c = g.style.getPropertyValue('--c');
    guides.forEach(x => { x.style.setProperty('--c', c); x.setAttribute('transform', `translate(0 ${g.dataset.cy})`); });
    hl.style.setProperty('--c', c);
    pill.textContent = g.dataset.y;
    const b = $('.lb', g).getBBox();
    hl.setAttribute('x', b.x - 1.4); hl.setAttribute('y', b.y - 0.5);
    hl.setAttribute('width', b.width + 2.8); hl.setAttribute('height', b.height + 1);
  };
  svg.addEventListener('pointerover', e => mark(e.target.closest('.ms')));
  svg.addEventListener('pointerleave', () => mark(null));
  svg.addEventListener('focusin', e => mark(e.target.closest('.ms')));
  svg.addEventListener('focusout', () => mark(null));

  // ---------------- one field or one era
  let lock = null, peek = null;
  const same = (a, b) => a && b && a.kind === b.kind && a.v === b.v;
  const eraCard = r => {
    const d = info.eras[r]; if (!d) { card.hidden = true; return; }
    card.innerHTML = `<div class="nfc-t">${esc(r)}. ${esc(d.name)}</div><p class="nfc-sub">${esc(d.years)} · ${d.n} works in this figure</p>`
      + d.rows.map(([k, v]) => `<p><b>${esc(k)}:</b> ${esc(v)}</p>`).join('')
      + (info.table ? `<a class="nfc-go" href="${esc(info.table)}">Table 1.1 →</a>` : '');
    card.hidden = false;
    // put the card where it hides the least of this era's works: inside its band or just above / below it (other eras are dimmed)
    const box = el.getBoundingClientRect(), band = bands.find(x => x.dataset.era === r).getBoundingClientRect();
    const cw = card.offsetWidth, ch = card.offsetHeight;
    const own = works.filter(w => w.dataset.era === r).map(w => w.getBoundingClientRect());
    const xs = [box.width - cw - 8, ...heads.map(h => h.getBoundingClientRect().left - box.left - 6)];
    const ys = [band.top - box.top + 8, band.bottom - box.top - ch - 8, band.top - box.top - ch - 6, band.bottom - box.top + 6];
    let best = null;
    for (const x0 of xs) for (const y0 of ys) {
      const x = Math.max(4, Math.min(x0, box.width - cw - 4)), y = Math.max(4, Math.min(y0, box.height - ch - 4));
      const L = box.left + x, T = box.top + y;
      let hid = 0;
      for (const q of own) hid += Math.max(0, Math.min(L + cw, q.right) - Math.max(L, q.left)) * Math.max(0, Math.min(T + ch, q.bottom) - Math.max(T, q.top));
      if (!best || hid < best.hid - 1) best = { hid, x, y };
    }
    card.style.left = best.x + 'px';
    card.style.top = best.y + 'px';
  };
  const apply = () => {
    const s = peek || lock;
    el.classList.toggle('is-filter', !!s);
    works.forEach(w => w.classList.toggle('is-in', !!s && (s.kind === 'f' ? w.dataset.f : w.dataset.era) === s.v));
    heads.forEach(h => { h.classList.toggle('is-on', !!s && s.kind === 'f' && h.dataset.f === s.v); h.setAttribute('aria-pressed', String(same(lock, { kind: 'f', v: h.dataset.f }))); });
    eras.forEach(h => { h.classList.toggle('is-on', !!s && s.kind === 'era' && h.dataset.era === s.v); h.setAttribute('aria-pressed', String(same(lock, { kind: 'era', v: h.dataset.era }))); });
    cols.forEach(l => l.classList.toggle('is-on', !!s && s.kind === 'f' && l.dataset.f === s.v));
    bands.forEach(b => b.classList.toggle('is-on', !!s && s.kind === 'era' && b.dataset.era === s.v));
    if (s && s.kind === 'era') eraCard(s.v); else card.hidden = true;
  };
  const bind = (nodes, kind, key) => nodes.forEach(h => {
    const sel = { kind, v: h.dataset[key] };
    h.addEventListener('pointerenter', () => { peek = sel; apply(); });
    h.addEventListener('pointerleave', () => { peek = null; apply(); });
    const toggle = () => { lock = same(lock, sel) ? null : sel; peek = null; apply(); };
    h.addEventListener('click', toggle);
    h.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
  });
  bind(heads, 'f', 'f');
  bind(eras, 'era', 'era');
  el.addEventListener('keydown', e => { if (e.key === 'Escape' && lock) { lock = peek = null; apply(); } });
  svg.addEventListener('click', e => { if (lock && !e.target.closest('.fh, .eh, .ms')) { lock = null; apply(); } });

  // ---------------- entrance: works appear in time order, once
  if (!reduce && 'IntersectionObserver' in window) {
    el.classList.add('pre');
    const io = new IntersectionObserver(es => {
      if (!es.some(x => x.isIntersecting)) return;
      io.disconnect();
      el.classList.replace('pre', 'go');
      setTimeout(() => el.classList.remove('go'), 1600);
    }, { threshold: 0.12 });
    io.observe(el);
  }
}
