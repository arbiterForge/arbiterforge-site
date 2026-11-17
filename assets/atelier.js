/* Original, dependency-free ambient filament renderer. The artwork and all
   navigation exist without Canvas or JavaScript. No network calls or tracking. */
(() => {
  'use strict';
  const hero = document.querySelector('[data-machine-hero]');
  const canvas = hero?.querySelector('[data-machine-canvas]');
  if (!hero || !canvas) return;
  let ctx;
  try { ctx = canvas.getContext('2d', {alpha: true}); } catch (_) { return; }
  if (!ctx) return;
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = matchMedia('(hover: hover) and (pointer: fine)');
  const connection = navigator.connection;
  let visible = false, width = 0, height = 0, frame = 0, last = 0;
  let elapsed = 0, paths = [], targetX = 0, targetY = 0, x = 0, y = 0;
  const TAU = Math.PI * 2;

  function resize() {
    const rect = hero.getBoundingClientRect();
    width = Math.round(rect.width); height = Math.round(rect.height);
    const mobile = width <= 760;
    const ratio = Math.min(devicePixelRatio || 1, mobile ? 1.25 : 1.5);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    paths = Array.from({length: mobile ? 12 : 22}, (_, index) => {
      // Braided, camera-facing curves, rather than a random particle field.
      const phase = index / 22 * TAU;
      const points = Array.from({length: 141}, (_, n) => {
        const t = n / 140;
        const theta = t * TAU * 1.12 + phase * .11;
        return {
          x: width * (-.06 + t * 1.16),
          y: height * ((mobile ? .80 : .73) - .23 * Math.sin(t * Math.PI)
            + Math.sin(theta) * (mobile ? .065 : .09) + Math.sin(t * Math.PI * 3 + phase) * .016
            + (index - 10) * .0022),
        };
      });
      return {points, phase, speed: .018 + (index % 5) * .003, offset: (index * .618) % 1};
    });
    draw();
  }

  function draw() {
    if (!width || !height) return;
    ctx.clearRect(0, 0, width, height);
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < paths.length; i++) {
      const {points, phase, speed, offset} = paths[i];
      const drift = Math.sin(elapsed * .16 + phase) * (width <= 760 ? 3 : 6);
      ctx.beginPath();
      for (let p = 0; p < points.length; p++) {
        const point = points[p];
        if (p === 0) ctx.moveTo(point.x, point.y + drift);
        else ctx.lineTo(point.x, point.y + drift);
      }
      ctx.strokeStyle = i % 5 === 0 ? 'rgba(169,190,141,.14)' : 'rgba(222,189,118,.11)';
      ctx.lineWidth = i % 5 === 0 ? .9 : .55;
      ctx.stroke();
      const position = ((elapsed * speed + offset) % 1) * (points.length - 1);
      const n = Math.floor(position), blend = position - n;
      const p = points[n], next = points[Math.min(n + 1, points.length - 1)];
      const px = p.x + (next.x - p.x) * blend;
      const py = p.y + (next.y - p.y) * blend + drift;
      const fade = Math.min(1, position / 9, (140 - position) / 9);
      const glow = ctx.createRadialGradient(px, py, 0, px, py, 8);
      glow.addColorStop(0, `rgba(255,235,180,${.65 * fade})`);
      glow.addColorStop(.18, `rgba(235,202,135,${.32 * fade})`);
      glow.addColorStop(1, 'rgba(235,202,135,0)');
      ctx.fillStyle = glow;
      ctx.fillRect(px - 8, py - 8, 16, 16);
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  function allowed() {
    return visible && !document.hidden && !reduced.matches
      && root.dataset.motion === 'on' && !connection?.saveData;
  }
  function tick(now) {
    frame = 0;
    if (!allowed()) { sync(); return; }
    if (!last) last = now;
    const delta = now - last;
    // A fixed visual budget, independent of the display's refresh rate.
    if (delta >= 1000 / 30) {
      elapsed += Math.min(delta, 100) / 1000;
      last = now;
      x += (targetX - x) * .08; y += (targetY - y) * .08;
      hero.style.setProperty('--machine-x', `${x.toFixed(2)}px`);
      hero.style.setProperty('--machine-y', `${y.toFixed(2)}px`);
      draw();
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    const active = allowed();
    hero.dataset.sceneActive = String(active);
    if (active && !frame) { last = 0; frame = requestAnimationFrame(tick); }
    if (!active) {
      if (frame) cancelAnimationFrame(frame);
      frame = 0; last = 0; targetX = targetY = x = y = 0;
      hero.style.removeProperty('--machine-x'); hero.style.removeProperty('--machine-y');
    }
  }
  hero.addEventListener('pointermove', event => {
    if (!allowed() || !pointer.matches) return;
    const rect = hero.getBoundingClientRect();
    targetX = ((event.clientX - rect.left) / rect.width - .5) * 7;
    targetY = ((event.clientY - rect.top) / rect.height - .5) * 5;
  }, {passive: true});
  hero.addEventListener('pointerleave', () => { targetX = targetY = 0; });
  new MutationObserver(sync).observe(root, {attributes:true, attributeFilter:['data-motion']});
  reduced.addEventListener('change', sync);
  pointer.addEventListener('change', () => { targetX = targetY = 0; });
  connection?.addEventListener?.('change', sync);
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', () => { visible = false; sync(); });
  window.addEventListener('pageshow', () => {
    const box = hero.getBoundingClientRect(); visible = box.bottom > 0 && box.top < innerHeight; sync();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting; sync();
    }, {threshold:0}).observe(hero);
  } else { visible = true; }
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(hero);
  else window.addEventListener('resize', resize, {passive:true});
  resize(); sync();
})();
