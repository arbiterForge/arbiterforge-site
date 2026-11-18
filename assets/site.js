(() => {
  'use strict';
  const toggle = document.querySelector('.theme-toggle');
  if (!toggle) return;
  const meta = document.querySelector('meta[name="theme-color"]');

  function applyTheme(theme) {
    const dark = theme === 'dark';
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.title = dark ? 'Switch to light appearance' : 'Switch to dark appearance';
    // Match the actual shared palette, including the homepage's dark hero.
    if (meta) meta.content = document.body.classList.contains('home-cinematic')
      ? '#0c1715'
      : getComputedStyle(document.documentElement).getPropertyValue('--paper').trim();
  }

  applyTheme(document.documentElement.dataset.theme);
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(theme);
    try { localStorage.setItem('suadtl-theme', theme); } catch (_) { /* Storage is optional. */ }
  });
})();
