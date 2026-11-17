/* Small, optional enhancements. Editorial content never waits for animation. */
(() => {
  'use strict';
  const root = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const controls = [...document.querySelectorAll('[data-motion-toggle]')];
  const artworks = [...document.querySelectorAll('[data-studio-art]')];
  const replayButtons = [...document.querySelectorAll('[data-art-replay]')];
  let preference;
  try { preference = localStorage.getItem('suadtl-motion'); } catch (_) { /* Storage is optional. */ }
  let enabled = false;
  let observer;
  const pointerFrames = new Map();

  function play(art) {
    if (!enabled || !art) return;
    art.classList.remove('art-running');
    void art.getBoundingClientRect();
    art.classList.add('art-running');
  }

  function resetArt(art) {
    const pending = pointerFrames.get(art);
    if (pending) cancelAnimationFrame(pending);
    pointerFrames.delete(art);
    art.style.removeProperty('--art-x');
    art.style.removeProperty('--art-y');
  }

  function configureMotion() {
    enabled = !reduced.matches && preference !== 'off';
    root.dataset.motion = enabled ? 'on' : 'off';
    controls.forEach(button => {
      button.hidden = false;
      button.disabled = reduced.matches;
      button.setAttribute('aria-pressed', String(enabled));
      button.querySelector('[data-motion-label]').textContent = reduced.matches ? 'Motion reduced' : enabled ? 'Motion on' : 'Motion off';
      button.title = reduced.matches ? 'Reduced motion is enabled in your system settings' : enabled ? 'Turn motion effects off' : 'Turn motion effects on';
    });
    replayButtons.forEach(button => { button.hidden = false; button.disabled = !enabled; });
    observer?.disconnect();
    document.querySelectorAll('.reveal-enter').forEach(element => element.classList.remove('reveal-enter'));
    artworks.forEach(art => { resetArt(art); art.classList.remove('art-running'); });
    if (!enabled) return;
    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          if (entry.target.hasAttribute('data-studio-art')) play(entry.target);
          else entry.target.classList.add('reveal-enter');
          observer.unobserve(entry.target);
        });
      }, {threshold: .12});
      document.querySelectorAll('[data-reveal], [data-studio-art]').forEach(element => observer.observe(element));
    } else {
      artworks.forEach(play);
    }
  }

  controls.forEach(button => button.addEventListener('click', () => {
    preference = enabled ? 'off' : 'on';
    try { localStorage.setItem('suadtl-motion', preference); } catch (_) { /* Keep the page usable. */ }
    configureMotion();
  }));
  replayButtons.forEach(button => button.addEventListener('click', () => {
    play(button.closest('[data-studio]')?.querySelector('[data-studio-art]'));
  }));
  artworks.forEach(art => {
    art.addEventListener('pointermove', event => {
      if (!enabled || !finePointer.matches || pointerFrames.has(art)) return;
      const {clientX, clientY} = event;
      pointerFrames.set(art, requestAnimationFrame(() => {
        pointerFrames.delete(art);
        if (!enabled) return;
        const bounds = art.getBoundingClientRect();
        if (!bounds.width || !bounds.height) return;
        const x = Math.max(-1, Math.min(1, (clientX - bounds.left) / bounds.width * 2 - 1));
        const y = Math.max(-1, Math.min(1, (clientY - bounds.top) / bounds.height * 2 - 1));
        art.style.setProperty('--art-x', (x * 7).toFixed(2) + 'px');
        art.style.setProperty('--art-y', (y * 5).toFixed(2) + 'px');
      }));
    }, {passive: true});
    art.addEventListener('pointerleave', () => resetArt(art));
  });
  reduced.addEventListener('change', configureMotion);
  finePointer.addEventListener('change', () => artworks.forEach(resetArt));
  configureMotion();

  if (document.body.hasAttribute('data-reading-progress')) {
    const indicator = document.createElement('div');
    indicator.className = 'reading-progress';
    indicator.setAttribute('aria-hidden', 'true');
    document.body.append(indicator);
    let scheduled = false;
    function updateProgress() {
      scheduled = false;
      const distance = document.documentElement.scrollHeight - window.innerHeight;
      const fraction = distance > 0 ? Math.max(0, Math.min(1, window.scrollY / distance)) : 0;
      indicator.style.setProperty('--reading-progress', fraction.toFixed(4));
    }
    function scheduleProgress() {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(updateProgress);
    }
    window.addEventListener('scroll', scheduleProgress, {passive: true});
    window.addEventListener('resize', scheduleProgress, {passive: true});
    if ('ResizeObserver' in window) new ResizeObserver(scheduleProgress).observe(document.body);
    updateProgress();
  }
})();
