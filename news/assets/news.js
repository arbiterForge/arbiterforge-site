/* SPDX-License-Identifier: MIT. Progressive enhancement: all panels work without JS. */
(() => {
  'use strict';
  const list = document.querySelector('.tabs');
  if (!list) return;
  const tabs = [...list.querySelectorAll('[data-tab]')];
  const panels = [...document.querySelectorAll('[data-panel]')];
  const keys = new Set(panels.map(p => p.dataset.panel));
  if (!tabs.length || tabs.some(t => !keys.has(t.dataset.tab))) return;
  list.setAttribute('role', 'tablist');
  function activate(tab, focus = false, writeHash = false) {
    for (const t of tabs) {
      t.setAttribute('role', 'tab');
      t.setAttribute('aria-controls', 'panel-' + t.dataset.tab);
      t.setAttribute('aria-selected', String(t === tab));
      t.tabIndex = t === tab ? 0 : -1;
    }
    for (const p of panels) {
      p.setAttribute('role', 'tabpanel');
      p.setAttribute('aria-labelledby', 'tab-' + p.dataset.panel);
      p.tabIndex = 0;
      p.hidden = p.dataset.panel !== tab.dataset.tab;
    }
    if (focus) tab.focus({preventScroll: true});
    if (writeHash) {
      try { history.replaceState(null, '', '#panel-' + tab.dataset.tab); } catch (_) { /* file:// or restricted browser */ }
      // Reveal the active tab horizontally without jumping the page vertically.
      const left = tab.offsetLeft - list.offsetLeft;
      list.scrollLeft = Math.max(0, left - (list.clientWidth - tab.offsetWidth) / 2);
    }
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', e => { e.preventDefault(); activate(tab, false, true); });
    tab.addEventListener('keydown', e => {
      const next = {ArrowRight: (i+1)%tabs.length, ArrowLeft: (i-1+tabs.length)%tabs.length, Home: 0, End: tabs.length-1}[e.key];
      if (next !== undefined) { e.preventDefault(); activate(tabs[next], true, true); }
    });
  });
  const fromHash = () => tabs.find(t => '#panel-' + t.dataset.tab === location.hash) || tabs[0];
  activate(fromHash());
  window.addEventListener('hashchange', () => activate(fromHash()));
})();
