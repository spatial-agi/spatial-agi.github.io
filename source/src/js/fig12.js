export function fig12(el) {
const root = el.querySelector('.evolution');
const svg = root.querySelector('svg');
const eras = [...svg.querySelectorAll('.era')];
const card = root.querySelector('.reading-card');
const info = JSON.parse(el.querySelector('.nf-info').textContent);
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const NS = 'http://www.w3.org/2000/svg';
let pinned = null, focused = null, hovered = null, paused = reduced.matches;
let visible = false, time = 0, last = 0, raf = 0, leaveTimer = 0;
const particles = [];
for (const [i, era] of eras.entries()) {
  for (const [j, path] of [...era.querySelectorAll('.flow')].entries()) {
    const dot = document.createElementNS(NS, 'circle');
    dot.setAttribute('r', i === 1 ? 7 : 5);
    dot.setAttribute('class', 'particle');
    svg.querySelector('.particles').append(dot);
    particles.push({path, dot, era: i, offset: j * 440, length: path.getTotalLength()});
  }
}
const positionCard = era => {
  const box = root.getBoundingClientRect(), b = era.getBoundingClientRect();
  const cw = card.offsetWidth, ch = card.offsetHeight;
  // Use a neighbouring, dimmed column; leave the inspected column unobstructed.
  let left = b.right - box.left + 12;
  if (left + cw > box.width - 8) left = b.left - box.left - cw - 12;
  card.style.left = Math.max(8, Math.min(left, box.width - cw - 8)) + 'px';
  card.style.top = Math.max(8, Math.min(b.top - box.top + b.height * .38, box.height - ch - 8)) + 'px';
};
const inspect = era => {
  clearTimeout(leaveTimer);
  root.classList.add('is-focus');
  eras.forEach(e => e.classList.toggle('is-on', e === era));
  const d = info[Number(era.dataset.era)];
  const heading = document.createElement('strong'); heading.textContent = d.title;
  const body = document.createElement('p'); body.textContent = d.body;
  const detail = document.createElement('small'); detail.textContent = d.detail;
  card.replaceChildren(heading, body, detail); card.hidden = false;
  positionCard(era); sync();
};
const release = () => {
  if (pinned || focused || hovered || card.matches(':hover')) return;
  root.classList.remove('is-focus'); eras.forEach(e => e.classList.remove('is-on'));
  card.hidden = true; sync();
};
const refresh = () => { const target = pinned || hovered || focused; if (target) inspect(target); else release(); };
const clear = () => {
  pinned = null; focused = null; hovered = null;
  eras.forEach(e => e.setAttribute('aria-pressed', 'false'));
  root.classList.remove('is-focus'); eras.forEach(e => e.classList.remove('is-on'));
  card.hidden = true; sync();
};
const pin = era => {
  pinned = pinned === era ? null : era;
  eras.forEach(e => e.setAttribute('aria-pressed', String(e === pinned)));
  refresh();
};
for (const era of eras) {
  era.addEventListener('pointerenter', () => { hovered = era; if (!pinned) inspect(era); });
  era.addEventListener('pointerleave', () => {
    if (hovered === era) hovered = null;
    leaveTimer = setTimeout(refresh, 100);
  });
  era.addEventListener('focus', () => { focused = era; if (!pinned) inspect(era); });
  era.addEventListener('blur', () => { if (focused === era) focused = null; refresh(); });
  era.addEventListener('click', () => pin(era));
  era.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pin(era); }
  });
}
card.addEventListener('pointerenter', () => clearTimeout(leaveTimer));
card.addEventListener('pointerleave', refresh);
root.addEventListener('keydown', e => { if (e.key === 'Escape') clear(); });
document.addEventListener('click', e => { if (!root.contains(e.target)) clear(); });
const draw = () => {
  for (const p of particles) {
    const period = p.era === 1 ? 5000 : 3200;
    const local = ((time - p.offset) % period + period) % period;
    const f = local / (period * .72);
    const pt = p.path.getPointAtLength(Math.min(f, 1) * p.length);
    p.dot.setAttribute('cx', pt.x); p.dot.setAttribute('cy', pt.y);
    p.dot.classList.toggle('on', f < 1);
  }
};
const loop = now => {
  if (last) time += Math.min(now - last, 64);
  last = now; draw(); raf = requestAnimationFrame(loop);
};
function sync() {
  const running = visible && !document.hidden && !paused && !root.classList.contains('is-focus');
  root.classList.toggle('is-paused', !running);
  if (running && !raf) { last = 0; raf = requestAnimationFrame(loop); }
  if (!running && raf) { cancelAnimationFrame(raf); raf = 0; last = 0; }
}
new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(root);
document.addEventListener('visibilitychange', sync);
reduced.addEventListener('change', e => { paused = e.matches; sync(); });
new ResizeObserver(() => { const era = pinned || hovered || focused; if (era) positionCard(era); }).observe(root);
el.querySelector('.nf12-scroll').addEventListener('scroll', () => { const era = pinned || hovered || focused; if (era) positionCard(era); });
// This instance is self-contained and has no preview toolbar dependencies.
root.dataset.ready = 'true';
sync();

}
