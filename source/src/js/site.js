// Site-wide behaviour: theme, mobile menu, toasts, search palette (Pagefind full text + quick title index).
export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
export function toast(msg) {
  const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg; document.body.append(t);
  setTimeout(() => t.remove(), 1800);
}
export async function copy(text, msg = 'Copied') {
  try { await navigator.clipboard.writeText(text); toast(msg); } catch { toast('Copy failed'); }
}
const cache = {};
export async function getJSON(url) { return cache[url] ??= fetch(url).then(r => r.json()); }
export const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// theme
$('[data-theme-toggle]')?.addEventListener('click', () => {
  const d = document.documentElement, t = d.dataset.theme === 'dark' ? 'light' : 'dark';
  d.dataset.theme = t; try { localStorage.setItem('theme', t); } catch {}
});
// back / forward through the browser history (the Navigation API, where available, tells whether each way is open)
{
  const back = $('[data-hist="back"]'), fwd = $('[data-hist="forward"]'), nav = window.navigation;
  const sync = () => {
    if (back) back.disabled = nav && 'canGoBack' in nav ? !nav.canGoBack : history.length < 2;
    if (fwd && nav && 'canGoForward' in nav) fwd.disabled = !nav.canGoForward;
  };
  back?.addEventListener('click', () => history.back());
  fwd?.addEventListener('click', () => history.forward());
  sync();
  nav?.addEventListener?.('currententrychange', sync);
  addEventListener('pageshow', sync);
}
// star count of the awesome list (shown once it is worth showing; cached for the session)
{
  const els = $$('[data-stars]');
  const fmt = n => n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + 'k' : String(n);
  const paint = n => { if (n >= 10) els.forEach(e => { e.textContent = '★ ' + fmt(n); }); };
  if (els.length) {
    let cached = null;
    try { cached = sessionStorage.getItem('si-stars'); } catch {}
    if (cached !== null) paint(+cached);
    else fetch('https://api.github.com/repos/spatial-agi/awesome-spatial-intelligence')
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (!d) return; try { sessionStorage.setItem('si-stars', d.stargazers_count); } catch {} paint(d.stargazers_count); })
      .catch(() => {});
  }
}
// mobile menu / toc
$('[data-menu]')?.addEventListener('click', () => {
  if (document.body.classList.contains('is-reader')) document.body.classList.toggle('toc-open');
  else document.body.classList.toggle('menu-open');
});

// ---------------- search palette ----------------
const overlay = $('[data-search]'), input = $('[data-search-input]'), box = $('[data-search-results]');
let pagefind, quick, active = -1, timer;
async function loadEngines() {
  if (!quick) quick = getJSON('/data/search-quick.json').catch(() => []);
  if (pagefind === undefined) {
    try { pagefind = await import('/pagefind/pagefind.js'); await pagefind.options?.({ excerptLength: 22 }); }
    catch { pagefind = null; }
  }
}
function openSearch() { overlay.hidden = false; input.value = ''; render([], ''); input.focus(); loadEngines(); }
function closeSearch() { overlay.hidden = true; }
$$('[data-open-search]').forEach(b => b.addEventListener('click', openSearch));
overlay?.addEventListener('click', e => { if (e.target === overlay) closeSearch(); });
document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); overlay.hidden ? openSearch() : closeSearch(); }
  else if (e.key === '/' && overlay.hidden && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
  else if (!overlay.hidden) {
    const items = $$('.sr-item', box);
    if (e.key === 'Escape') closeSearch();
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault(); active = Math.max(0, Math.min(items.length - 1, active + (e.key === 'ArrowDown' ? 1 : -1)));
      items.forEach((it, i) => it.classList.toggle('is-active', i === active)); items[active]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && items[Math.max(active, 0)]) { items[Math.max(active, 0)].click(); }
  }
});
function render(groups, q) {
  active = -1;
  if (!q) { box.innerHTML = '<div class="sr-empty">Search the full text of the handbook, figure captions, the literature and the glossary.</div>'; return; }
  const html = groups.filter(g => g.items.length).map(g => `<div class="sr-group">${g.name}</div>` + g.items.map(it =>
    `<a class="sr-item" href="${it.url}"><div class="sr-title">${it.n ? `<span class="n">${esc(it.n)}</span>` : ''}${esc(it.t)}</div>${it.ex ? `<div class="sr-ex">${it.ex}</div>` : ''}</a>`).join('')).join('');
  box.innerHTML = html || `<div class="sr-empty">No results for “${esc(q)}”.</div>`;
}
input?.addEventListener('input', () => {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    const q = input.value.trim(); await loadEngines();
    if (!q) return render([], '');
    const ql = q.toLowerCase(), terms = ql.split(/\s+/);
    const qi = (await quick).filter(x => terms.every(t => x.s.includes(t))).slice(0, 40);
    const groups = [
      { name: 'Sections', items: qi.filter(x => x.k === 'sec').slice(0, 6) },
      { name: 'Figures & tables', items: qi.filter(x => x.k === 'fig').slice(0, 4) },
      { name: 'Glossary', items: qi.filter(x => x.k === 'term').slice(0, 3) },
      { name: 'Literature', items: qi.filter(x => x.k === 'ref').slice(0, 4) },
    ];
    if (pagefind) {
      const r = await pagefind.search(q);
      const docs = await Promise.all(r.results.slice(0, 8).map(x => x.data()));
      groups.splice(1, 0, { name: 'Full text', items: docs.map(d => ({ url: d.url, t: d.meta.title, ex: d.excerpt })) });
    }
    if (input.value.trim() === q) render(groups, q);
  }, 120);
});
