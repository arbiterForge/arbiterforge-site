/* SPDX-License-Identifier: MIT. The server renders every desk and story as ordinary fragment links. */
(() => {
  'use strict';
  const list = document.querySelector('.tabs');
  if (!list) return;
  const tabs = [...list.querySelectorAll('[data-tab]')];
  const panels = tabs.map(tab => document.getElementById('panel-' + tab.dataset.tab));
  if (!tabs.length || panels.some(panel => !panel)) return;

  list.setAttribute('role', 'tablist');
  tabs.forEach((tab, index) => {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panels[index].id);
    panels[index].setAttribute('role', 'tabpanel');
    panels[index].setAttribute('aria-labelledby', tab.id);
    panels[index].tabIndex = 0;
  });

  function select(index) {
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
    });
  }

  function selectTab(index, focus = false) {
    select(index);
    if (focus) tabs[index].focus({ preventScroll: true });
    try { history.replaceState(null, '', '#' + panels[index].id); }
    catch (_) { /* Tabs remain usable when the browser restricts history. */ }
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      selectTab(i);
    });
    tab.addEventListener('keydown', event => {
      const next = { ArrowRight: (i + 1) % tabs.length, ArrowLeft: (i - 1 + tabs.length) % tabs.length, Home: 0, End: tabs.length - 1 }[event.key];
      if (next !== undefined) {
        event.preventDefault();
        selectTab(next, true);
      }
    });
  });

  function followFragment() {
    const target = document.getElementById(location.hash.slice(1));
    const index = panels.indexOf(target?.closest('[data-panel]'));
    if (index === -1) {
      if (!location.hash) select(0);
      return;
    }
    select(index);
    if (target.matches('article[id], [data-panel]')) {
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: 'start' });
    }
  }

  select(0);
  followFragment();
  window.addEventListener('hashchange', followFragment);

  let closedForScreen = [];
  window.addEventListener('beforeprint', () => {
    if (closedForScreen.length) return;
    closedForScreen = [...document.querySelectorAll('details:not([open])')];
    closedForScreen.forEach(details => { details.open = true; });
  });
  window.addEventListener('afterprint', () => {
    closedForScreen.forEach(details => { details.open = false; });
    closedForScreen = [];
  });
})();
