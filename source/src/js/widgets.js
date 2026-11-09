// Interactive widgets shared by the home page and the reader: live world map (teaser), five-eras explorer (Table 1.1), milestones timeline (Fig. 1.3).
import { $, $$, esc, getJSON } from './site.js';

const NS = 'http://www.w3.org/2000/svg';
const el = (tag, attrs = {}, parent) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  parent?.append(e); return e;
};
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ======================= world map =======================
export function worldmap(fig, D) {
  if (!fig) return;
  const svg = $('.wm-svg', fig), card = $('.wm-card', fig), stage = $('.wm-stage', fig);
  const W = 1000, H = 1259.3, X = f => f * W, Y = f => f * H;
  const E = ([cx, cy, a, b]) => ({ cx: X(cx), cy: Y(cy), a: X(a), b: Y(b) });
  const g = D.map, C1 = E(g.canal1), RD = E(g.road), C2 = E(g.canal2), SEA = E(g.sea);
  const pt = (e, t) => { t = t * Math.PI / 180; return [e.cx + e.a * Math.sin(t), e.cy - e.b * Math.cos(t)]; };
  const arc = (e, t0, t1) => { const [x0, y0] = pt(e, t0), [x1, y1] = pt(e, t1); return `M${x0},${y0} A${e.a},${e.b} 0 ${Math.abs(t1 - t0) > 180 ? 1 : 0} ${t1 > t0 ? 1 : 0} ${x1},${y1}`; };
  const color = r => D.partColors[r];
  const defs = el('defs', {}, svg);
  const mk = el('marker', { id: 'wm-ah', viewBox: '0 0 10 10', refX: 6, refY: 5, markerWidth: 4.2, markerHeight: 4.2, orient: 'auto-start-reverse' }, defs);
  el('path', { d: 'M0,0 L10,5 L0,10 z', fill: color('III') }, mk);

  // focus veil: dims the drawing except the regions of the highlighted part (soft-edged holes in a mask)
  const blur = el('filter', { id: 'wm-blur', x: '-30%', y: '-30%', width: '160%', height: '160%' }, defs);
  el('feGaussianBlur', { stdDeviation: 16 }, blur);
  const mask = el('mask', { id: 'wm-mask', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: W, height: H }, defs);
  el('rect', { width: W, height: H, fill: '#fff' }, mask);
  const holes = {};
  for (const r of ['I', 'II', 'III', 'IV', 'V']) holes[r] = el('g', { fill: '#000', filter: 'url(#wm-blur)', display: 'none' }, mask);
  const ell = (e, d = 0) => `M${e.cx - e.a - d},${e.cy} a${e.a + d},${e.b + d} 0 1 0 ${2 * (e.a + d)},0 a${e.a + d},${e.b + d} 0 1 0 ${-2 * (e.a + d)},0z`;
  const OUT = E([0.5, 0.40, 0.53, 0.335]);
  el('path', { d: ell(C1, 12) }, holes.II);
  el('path', { d: ell(C2, 12) + ell(C1, -10), 'fill-rule': 'evenodd' }, holes.III);
  el('path', { d: ell(OUT) + ell(C2, -10), 'fill-rule': 'evenodd' }, holes.IV);
  el('rect', { x: 0, y: 0, width: W, height: Y(0.075) }, holes.V);
  el('rect', { x: X(0.39), y: Y(0.63), width: X(0.22), height: Y(0.34), rx: 50 }, holes.I);
  el('rect', { class: 'wm-veil', width: W, height: H, mask: 'url(#wm-mask)' }, svg);

  // rings (canals) as soft part-coloured washes
  const rings = el('g', { class: 'wm-rings' }, svg);
  el('ellipse', { cx: C1.cx, cy: C1.cy, rx: C1.a, ry: C1.b, class: 'wm-ring', 'data-p': 'II', stroke: color('II') }, rings);
  el('ellipse', { cx: C2.cx, cy: C2.cy, rx: C2.a, ry: C2.b, class: 'wm-ring', 'data-p': 'III', stroke: color('III') }, rings);
  // the loop: perception -> reasoning -> generation, clockwise on the ring road
  const loop = el('g', { class: 'wm-loop', 'data-p': 'III' }, svg);
  for (const [t0, t1] of [[12, 112], [146, 222], [252, 348]]) {
    el('path', { d: arc(RD, t0, t1), class: 'wm-loop-halo' }, loop);
    el('path', { d: arc(RD, t0, t1), class: 'wm-loop-line', stroke: color('III'), 'marker-end': 'url(#wm-ah)' }, loop);
  }
  // part ribbons with text on a path
  const ribbons = el('g', { class: 'wm-ribbons' }, svg);
  const ribbon = (id, d, text, r, size, len) => {
    el('path', { id, d, fill: 'none' }, defs);
    const gg = el('g', { class: 'wm-ribbon', 'data-p': r }, ribbons);
    const u = el('use', { href: '#' + id, class: 'wm-ribbon-band', stroke: color(r), 'stroke-dasharray': `${len} 4000`, 'stroke-dashoffset': 0 }, gg);
    const t = el('text', { class: 'wm-ribbon-text', 'font-size': size }, gg);
    const tp = el('textPath', { href: '#' + id, startOffset: '50%', 'text-anchor': 'middle' }, t);
    tp.textContent = text;
    requestAnimationFrame(() => { // trim the band to the text length
      const p = $('#' + id), L = p.getTotalLength(), tl = t.getComputedTextLength() + size * 1.6;
      u.setAttribute('stroke-dasharray', `${tl} ${L}`); u.setAttribute('stroke-dashoffset', -(L - tl) / 2);
    });
  };
  ribbon('rb2', arc(C1, 245, 115), 'II · REPRESENTATION', 'II', 17);
  ribbon('rb3', arc(C2, 236, 124), 'III · FROM PERCEPTION TO GENERATION', 'III', 17);
  ribbon('rb4', arc(SEA, 274, 350), 'IV · APPLICATIONS', 'IV', 17);
  // Part V banner on the horizon and Part I along the stepping stones
  const banner = (x, y, text, r, rot, href) => {
    const a = el('a', { href, class: 'wm-banner', 'data-p': r }, svg);
    const gg = el('g', { transform: `translate(${x},${y}) rotate(${rot})` }, a);
    const rect = el('rect', { rx: 9, fill: color(r) }, gg);
    const t = el('text', { class: 'wm-banner-text', 'text-anchor': 'middle', 'dominant-baseline': 'central' }, gg);
    t.textContent = text;
    requestAnimationFrame(() => { const b = t.getBBox(); rect.setAttribute('x', b.x - 14); rect.setAttribute('y', b.y - 7); rect.setAttribute('width', b.width + 28); rect.setAttribute('height', b.height + 14); });
  };
  banner(500, 30, 'V · DISCUSSIONS AND FUTURES', 'V', 0, '/read/part-v/');
  banner(398, 1010, 'I · INTRODUCTION AND BACKGROUND', 'I', -90, '/read/part-i/');

  // chapter pins
  const pins = el('g', { class: 'wm-pins' }, svg);
  const showCard = (item, x, y) => {
    card.innerHTML = item.html; card.hidden = false;
    const sw = stage.clientWidth, sh = stage.clientHeight, cw = card.offsetWidth, ch = card.offsetHeight;
    const px = x / W * sw, py = y / H * sh;
    let left = px + 18, top = py - ch / 2;
    if (left + cw > sw - 6) left = px - cw - 18;
    left = Math.max(6, left); top = Math.max(6, Math.min(sh - ch - 6, top));
    card.style.left = left + 'px'; card.style.top = top + 'px';
  };
  const hideCard = () => { card.hidden = true; };
  let hideTimer;
  const addPin = (item) => {
    const [x, y] = [X(item.x), Y(item.y)];
    const a = el('a', { href: item.url, class: 'wm-pin ' + (item.small ? 'is-small' : ''), 'data-p': item.part, tabindex: 0, 'aria-label': item.label }, pins);
    el('circle', { cx: x, cy: y, r: item.small ? 11 : 19, class: 'wm-halo', stroke: color(item.part) }, a);
    el('circle', { cx: x, cy: y, r: item.small ? 11 : 19, class: 'wm-dot', fill: color(item.part) }, a);
    el('circle', { cx: x, cy: y, r: item.small ? 46 : 70 }, holes[item.part]);
    if (item.n) { const t = el('text', { x, y: y + 0.5, 'text-anchor': 'middle', 'dominant-baseline': 'central' }, a); t.textContent = item.n; }
    const on = () => { clearTimeout(hideTimer); showCard(item, x, y); a.classList.add('is-on'); };
    const off = () => { a.classList.remove('is-on'); hideTimer = setTimeout(hideCard, 120); };
    a.addEventListener('mouseenter', on); a.addEventListener('mouseleave', off);
    a.addEventListener('focus', on); a.addEventListener('blur', off);
    a.addEventListener('click', e => { if (matchMedia('(hover: none)').matches && card.hidden) { e.preventDefault(); on(); } });
  };
  card.addEventListener('mouseenter', () => clearTimeout(hideTimer));
  card.addEventListener('mouseleave', () => { hideTimer = setTimeout(hideCard, 120); });
  for (const c of D.pins) {
    const secs = c.sections.slice(0, 5).map(s => `<li><span>${esc(s.num)}</span>${esc(s.title)}</li>`).join('') + (c.sections.length > 5 ? `<li class="more">+${c.sections.length - 5} more sections</li>` : '');
    addPin({ ...c, url: '/read/' + c.slug + '/', label: `Chapter ${c.n}: ${c.title}`,
      html: `<div class="wmc-k" style="color:${color(c.part)}">Chapter ${c.n} · Part ${c.part}</div><div class="wmc-t">${esc(c.title)}</div><ol class="wmc-s">${secs}</ol><a class="wmc-go" href="/read/${c.slug}/">Read chapter →</a>` });
  }
  for (const e of D.eraPins) addPin({ ...e, small: true, part: 'I', url: e.url, label: e.name,
    html: `<div class="wmc-k" style="color:${color('I')}">Era ${e.roman} · ${esc(e.years)}</div><div class="wmc-t">${esc(e.name)}</div><p class="wmc-p">Space treated as ${esc(e.space)}.</p><a class="wmc-go" href="${e.url}">Read Section ${e.sec} →</a>` });

  // legend: highlight a part
  // every element of the part (ring wash, loop, ribbon or banner, pins) is lifted; the rest of the drawing is veiled
  const setPart = r => {
    fig.dataset.focus = r || '';
    fig.classList.toggle('is-focus', !!r);
    $$('[data-p]', svg).forEach(n => n.classList.toggle('is-hl', n.dataset.p === r));
    Object.entries(holes).forEach(([k, h]) => h.setAttribute('display', k === r ? 'inline' : 'none'));
    $$('[data-part]', fig).forEach(b => b.classList.toggle('is-on', b.dataset.part === r));
  };
  $$('[data-part]', fig).forEach(b => {
    b.addEventListener('mouseenter', () => setPart(b.dataset.part));
    b.addEventListener('mouseleave', () => setPart(''));
    b.addEventListener('focus', () => setPart(b.dataset.part));
    b.addEventListener('blur', () => setPart(''));
    b.addEventListener('click', () => location.href = `/read/part-${b.dataset.part.toLowerCase()}/`);
  });
  $$('.wm-ribbon, .wm-banner', svg).forEach(n => {
    n.addEventListener('mouseenter', () => setPart(n.dataset.p));
    n.addEventListener('mouseleave', () => setPart(''));
  });
}

// ======================= five eras =======================
export function eras(root, D) {
  if (!root) return;
  const panel = $('[data-era-panel]', root);
  const show = i => {
    const e = D.eras[i];
    $$('.era-tab', root).forEach((b, j) => b.setAttribute('aria-selected', j === i ? 'true' : 'false'));
    panel.innerHTML = `<div class="ep-head"><span class="ep-roman">${e.roman}</span><div><div class="ep-name">${esc(e.name)}</div><div class="ep-years">${esc(e.years)}</div></div><a class="ep-go" href="${e.url}">Read Section ${e.sec} →</a></div>
      <dl class="ep-grid">${e.rows.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;
  };
  $$('.era-tab', root).forEach((b, i) => b.addEventListener('click', () => show(i)));
  show(0);
}

// ---------------- mount helpers for the reader (build the markup, then wire it) ----------------
export function mountEras(box, D) {
  box.innerHTML = `<div class="eras live-eras"><div class="era-track" role="tablist">${D.eras.map((e, i) => `<button type="button" role="tab" class="era-tab" aria-selected="${i === 0}"><img src="/assets/img/era-${i + 1}.webp" alt="" width="260" height="360"><span class="era-roman">${e.roman}</span><span class="era-name">${esc(e.name)}</span><span class="era-years">${esc(e.years)}</span></button>`).join('')}</div><div class="era-panel" data-era-panel></div></div>`;
  eras(box.querySelector('.eras'), D);
}

// ======================= milestones timeline (Fig. 1.3, interactive) =======================
const TL_ERAS = [{ r: 'I', a: 1940, b: 1980 }, { r: 'II', a: 1980, b: 2012 }, { r: 'III', a: 2012, b: 2019 }, { r: 'IV', a: 2019, b: 2023 }, { r: 'V', a: 2023, b: 2027 }];
const TL_YEARS = [1950, 1960, 1970, 1980, 1990, 2000, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026];
export const TL_CAPTION = 'The time axis is compressed before 1980 and expanded after 2012, as in Figure 1.3. Shaded bands are the five eras of Table 1.1.';

// draws `vis` (a subset of `data`) into host; lanes come from the full data, so they stay put while filtering
export function timelineChart(host, data, vis = data) {
  const fields = [...new Set(data.map(d => d.field))];
  const colorOf = Object.fromEntries(data.map(d => [d.field, d.color]));
  // piecewise scale as in the print figure: compressed before 1980, expanded after 2012
  const W = 1180, L = 196, R = 34, top = 34, lane = 54, H = top + lane * fields.length + 40;
  const segs = [[1945, 1980, 0.22], [1980, 2012, 0.28], [2012, 2027, 0.50]];
  const xs = y => { let x = L; const w = W - L - R; for (const [a, b, f] of segs) { if (y <= b) return x + (Math.max(y, a) - a) / (b - a) * w * f; x += w * f; } return W - R; };
  const parts = [`<svg class="tl" viewBox="0 0 ${W} ${H}" role="img" aria-label="Milestones of spatial intelligence by field and year">`];
  TL_ERAS.forEach((e, i) => { const x0 = xs(e.a), x1 = xs(e.b); parts.push(`<rect x="${x0}" y="${top - 26}" width="${x1 - x0}" height="${H - top}" class="tl-era ${i % 2 ? 'odd' : ''}"/><text x="${x0 + 6}" y="${top - 10}" class="tl-era-t">${e.r}</text>`); });
  TL_YEARS.forEach(y => parts.push(`<line x1="${xs(y)}" x2="${xs(y)}" y1="${top}" y2="${H - 30}" class="tl-grid"/><text x="${xs(y)}" y="${H - 12}" class="tl-year">${y}</text>`));
  fields.forEach((f, i) => { const y = top + lane * i + lane / 2; parts.push(`<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" class="tl-lane" style="stroke:${colorOf[f]}"/><text x="${L - 12}" y="${y + 4}" class="tl-field" text-anchor="end" style="fill:${colorOf[f]}">${esc(f)}</text>`); });
  const byLane = {};
  vis.forEach(d => {
    const i = fields.indexOf(d.field), x = xs(d.year), k = i + ':' + Math.round(x / 9);
    byLane[k] = (byLane[k] || 0) + 1;
    const y = top + lane * i + lane / 2 + ((byLane[k] - 1) % 3 - 1) * 12;
    parts.push(`<circle cx="${x}" cy="${y}" r="6" class="tl-dot" style="fill:${d.color}" tabindex="0" data-i="${data.indexOf(d)}"><title>${esc(d.label)} (${d.year})</title></circle>`);
  });
  parts.push('</svg>');
  host.innerHTML = `<div class="tl-wrap">${parts.join('')}<div class="tl-card" hidden></div></div>`;
  const card = $('.tl-card', host), wrap = $('.tl-wrap', host);
  $$('.tl-dot', host).forEach(c => {
    const show = () => {
      const d = data[c.dataset.i], r = c.getBoundingClientRect(), w = wrap.getBoundingClientRect();
      const ref = d.title ? `<p class="wmc-p">[${d.num}] ${esc(d.title)}${d.authors.length ? '. ' + esc(d.authors.join(', ')) : ''}</p>` : '';
      card.innerHTML = `<div class="wmc-k" style="color:${d.color}">${esc(d.field)} · ${d.year}</div><div class="wmc-t">${esc(d.label)}</div>${ref}<a class="wmc-go" href="/explore/literature/?k=${encodeURIComponent(d.keys[0])}">In the literature explorer →</a>`;
      card.hidden = false;
      card.style.left = Math.max(6, Math.min(r.left - w.left + wrap.scrollLeft + 12, wrap.scrollWidth - 300)) + 'px';
      card.style.top = (r.top - w.top + 14) + 'px';
    };
    c.addEventListener('mouseenter', show); c.addEventListener('focus', show); c.addEventListener('click', show);
  });
  wrap.addEventListener('mouseleave', () => { card.hidden = true; });
}

// reader version: field chips to filter, the chart, and the scale note
export async function mountTimeline(box) {
  const data = await getJSON('/data/milestones.json');
  const fields = [...new Set(data.map(d => d.field))];
  const colorOf = Object.fromEntries(data.map(d => [d.field, d.color]));
  const chips = fields.map(f => `<button type="button" aria-pressed="false" data-f="${esc(f)}" style="--fc:${colorOf[f]}"><i></i>${esc(f)}<span>${data.filter(d => d.field === f).length}</span></button>`).join('');
  box.innerHTML = `<div class="live-tl"><div class="tl-fields" role="group" aria-label="Filter by field">${chips}</div><div class="tl-host"></div></div>`;
  const sel = new Set(), host = $('.tl-host', box);
  const draw = () => timelineChart(host, data, data.filter(d => !sel.size || sel.has(d.field)));
  $$('[data-f]', box).forEach(b => b.addEventListener('click', () => {
    const f = b.dataset.f;
    if (sel.has(f)) sel.delete(f); else sel.add(f);
    b.setAttribute('aria-pressed', String(sel.has(f)));
    draw();
  }));
  draw();
}

