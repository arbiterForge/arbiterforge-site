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
    if (meta) meta.content = dark ? '#181e1b' : '#f7f6f2';
  }

  applyTheme(document.documentElement.dataset.theme);
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(theme);
    try { localStorage.setItem('suadtl-theme', theme); } catch (_) { /* Storage is optional. */ }
  });
})();
