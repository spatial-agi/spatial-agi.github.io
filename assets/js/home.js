// Home page: wires the shared widgets to the page.
import { $, $$, copy } from './site.js';
import { worldmap, eras } from './widgets.js';
import { mountNative } from './nfig.js';

const D = JSON.parse($('#home-data').textContent);
worldmap($('[data-worldmap]'), D);
mountNative($('#definition'), { panel: $('[data-def-panel]'), idle: 'rep' });
eras($('[data-eras]'), D);

const tabs = $$('[data-ct]');
let active = 'bib-main';
tabs.forEach(b => b.addEventListener('click', () => {
  active = b.dataset.ct;
  tabs.forEach(x => x.setAttribute('aria-selected', String(x === b)));
  tabs.forEach(x => { $('#' + x.dataset.ct).hidden = x !== b; });
}));
$('[data-copy-active]')?.addEventListener('click', () =>
  copy($('#' + active).textContent, active === 'bib-main' ? 'BibTeX copied' : 'Citation copied'));
