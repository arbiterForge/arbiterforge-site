/* suadtl / Living forms.
   Three continuous parametric surfaces, drawn as projected contour threads.
   Geometry is cached; a frame projects at most 104 × 145 points. Canvas drawing
   is capped at 30 fps, DPR 1.65 (1.4 compact), and 1.15 million backing pixels.
   Slow animated frames sample fewer points; paused artwork keeps full detail.
   Pointer attraction and expanding waves deform the projected silk, while a
   small camera tilt makes depth tangible. No dependencies, requests, or storage. */
(() => {
  'use strict';
  const TAU = Math.PI * 2;
  const FRAME_MS = 1000 / 30;
  const PIXEL_BUDGET = 1150000;
  const NAMES = { weave: 'Weave', orbit: 'Orbit', bloom: 'Bloom' };
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
  const ease = value => value * value * (3 - 2 * value);
  const palette = [[232, 235, 214], [150, 184, 157], [165, 204, 221], [210, 153, 114], [239, 226, 195]];

  function create(host) {
    const stage = host.querySelector('[data-hero-stage]');
    const canvas = host.querySelector('[data-hero-canvas]');
    if (!stage || !canvas) return;
    let ctx;
    try { ctx = canvas.getContext('2d', { alpha: true, desynchronized: true }); } catch (_) { return; }
    if (!ctx) return;

    const root = document.documentElement;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const coarse = window.matchMedia('(pointer: coarse)');
    const connection = navigator.connection;
    const controls = host.querySelector('[data-hero-controls]');
    const modes = [...host.querySelectorAll('[data-hero-mode]')];
    const pulseButton = host.querySelector('[data-hero-pulse]');
    const hint = host.querySelector('[data-hero-hint]');
    const formLabel = host.querySelector('[data-hero-form]');
    const stateLabel = host.querySelector('[data-hero-state]');
    const status = host.querySelector('[data-hero-status]');
    let width = 0, height = 0, dpr = 1, scale = 1, bounds;
    let lines = 0, segments = 0, stride = 0;
    let shapes = {}, source, target, projected, lineOrder = [], colors = [];
    let waveA, waveB, lineCos, lineSin, glow;
    let mode = 'weave', morph = 1, playTime = 0;
    let frame = 0, lastPaint = 0, nextPaintAt = 0, dirty = true, failed = false;
    let detail = 0, slowFrames = 0, frameSample = null, feedbackUntil = 0;
    let inViewport = false, intersecting = true, pageActive = true, wasAnimating = false;
    let down = null;
    const pointer = { active: false, pending: false, clientX: 0, clientY: 0,
      x: .5, y: .5, strength: 0, tiltX: 0, tiltY: 0 };
    const pulses = [];

    function permitted() {
      return !failed && pageActive && !document.hidden && width > 0 && height > 0 && inViewport && intersecting;
    }
    function motionPermitted() {
      return root.dataset.motion === 'on' && !reduced.matches && !connection?.saveData;
    }
    function animate() { return permitted() && motionPermitted(); }
    function announce(message) { if (status) status.textContent = message; }
    function setText(element, value) {
      if (element && element.textContent !== value) element.textContent = value;
    }
    function updateControls() {
      if (failed) {
        if (controls) controls.hidden = true;
        if (pulseButton) pulseButton.disabled = true;
        setText(formLabel, NAMES.weave);
        setText(stateLabel, 'Still artwork');
        setText(hint, 'The static sculpture is shown.');
        host.dataset.heroMode = 'weave';
        return;
      }
      modes.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.heroMode === mode)));
      if (pulseButton) pulseButton.disabled = !animate();
      setText(formLabel, NAMES[mode]);
      let state = 'Live · interactive';
      let instruction = coarse.matches ? 'Drag sideways to bend the threads. Tap to send a pulse.' : 'Move across the form to pull the threads. Click to send a pulse.';
      if (reduced.matches) {
        state = 'Still · reduced motion';
        instruction = 'Reduced motion is on. Choose a form to explore its still shape.';
      } else if (connection?.saveData) {
        state = 'Still · data saving';
        instruction = 'Data saving is on. All three forms are available as still artwork.';
      } else if (root.dataset.motion !== 'on') {
        state = 'Motion paused';
        instruction = 'Motion is paused. Choose a form, or turn motion on to interact.';
      } else if (!permitted()) {
        state = 'Motion resting';
        instruction = 'Motion resumes when this sculpture is in view.';
      }
      setText(stateLabel, state);
      setText(hint, instruction);
      host.dataset.heroMode = mode;
    }

    function buildGeometry(compact) {
      lines = compact ? 76 : 104;
      segments = compact ? 112 : 144;
      stride = (segments + 1) * 3;
      shapes = {};
      projected = new Float32Array(lines * stride);
      waveA = new Float32Array(segments + 1);
      waveB = new Float32Array(segments + 1);
      lineCos = new Float32Array(lines);
      lineSin = new Float32Array(lines);
      lineOrder = Array.from({ length: lines }, (_, index) => ({ index, depth: 0 }));
      colors = [];
      for (let i = 0; i < lines; i++) {
        const v = TAU * (i + .5) / lines;
        lineCos[i] = Math.cos(v); lineSin[i] = Math.sin(v);
        const position = i / (lines - 1) * (palette.length - 1);
        const colorIndex = Math.min(palette.length - 2, Math.floor(position));
        const fraction = position - colorIndex;
        colors.push(palette[colorIndex].map((value, channel) => Math.round(value + (palette[colorIndex + 1][channel] - value) * fraction)).join(','));
      }
      // Every thread shares the same samples around the form. Cache those
      // angles once rather than evaluating trigonometry for every 3D point.
      const samples = Array.from({ length: segments + 1 }, (_, j) => {
        const u = TAU * j / segments;
        const sin2 = Math.sin(2 * u), cos3 = Math.cos(3 * u);
        return {
          cos: Math.cos(u), sin: Math.sin(u), cos2: Math.cos(2 * u), sin2,
          tube: .19 + .035 * cos3, weaveRadius: .94 + .33 * cos3,
          weaveZ: .42 * Math.sin(3 * u),
          twistCos: Math.cos(.5 * sin2), twistSin: Math.sin(.5 * sin2),
          petals: .91 + .3 * Math.cos(5 * u),
          bloomZ: .23 * Math.sin(5 * u) + .12 * Math.cos(2 * u),
        };
      });
      const weave = shapes.weave = new Float32Array(lines * stride);
      const orbit = shapes.orbit = new Float32Array(lines * stride);
      const bloom = shapes.bloom = new Float32Array(lines * stride);
      for (let i = 0; i < lines; i++) {
        const v = TAU * (i + .5) / lines;
        const cos = Math.cos(v), sin = Math.sin(v);
        for (let j = 0; j <= segments; j++) {
          const sample = samples[j], k = i * stride + j * 3;
          const weaveRadius = sample.weaveRadius + sample.tube * cos;
          weave[k] = 1.07 * weaveRadius * sample.cos2;
          weave[k + 1] = weaveRadius * sample.sin2;
          weave[k + 2] = sample.weaveZ + sample.tube * sin;
          const twistCos = cos * sample.twistCos - sin * sample.twistSin;
          const twistSin = sin * sample.twistCos + cos * sample.twistSin;
          const orbitRadius = 1.02 + .3 * twistCos;
          orbit[k] = 1.08 * orbitRadius * sample.cos;
          orbit[k + 1] = .94 * orbitRadius * sample.sin;
          orbit[k + 2] = .31 * twistSin + .18 * sample.sin2;
          const bloomRadius = sample.petals + .18 * cos;
          bloom[k] = bloomRadius * sample.cos;
          bloom[k + 1] = bloomRadius * sample.sin;
          bloom[k + 2] = .29 * sin + sample.bloomZ;
        }
      }
      target = shapes[mode]; source = target; morph = 1;
    }

    function readBounds() {
      bounds = stage.getBoundingClientRect();
      inViewport = bounds.width > 0 && bounds.height > 0 && bounds.bottom > 0 && bounds.right > 0 && bounds.top < window.innerHeight && bounds.left < window.innerWidth;
      return bounds;
    }
    function resize() {
      if (failed) return;
      const box = readBounds();
      const nextWidth = Math.max(0, Math.round(box.width));
      const nextHeight = Math.max(0, Math.round(box.height));
      const compact = nextWidth < 480 || coarse.matches;
      const nextDpr = nextWidth && nextHeight ? Math.min(window.devicePixelRatio || 1, compact ? 1.4 : 1.65, Math.sqrt(PIXEL_BUDGET / (nextWidth * nextHeight))) : 1;
      if (nextWidth !== width || nextHeight !== height || nextDpr !== dpr || !target || lines !== (compact ? 76 : 104)) {
        width = nextWidth; height = nextHeight; dpr = nextDpr;
        if (width && height) {
          canvas.width = Math.max(1, Math.floor(width * dpr));
          canvas.height = Math.max(1, Math.floor(height * dpr));
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          scale = Math.min(width, height) * .30;
          glow = null;
          if (!target || lines !== (compact ? 76 : 104)) buildGeometry(compact);
        }
        dirty = true;
      }
      sync();
    }

    function resetInteraction() {
      pointer.active = false; pointer.pending = false; pointer.strength = 0; pointer.tiltX = 0; pointer.tiltY = 0;
      down = null; pulses.length = 0;
    }
    function stop() {
      if (frame) cancelAnimationFrame(frame);
      frame = 0; lastPaint = 0; nextPaintAt = 0;
      detail = 0; slowFrames = 0; frameSample = null; feedbackUntil = 0;
    }
    function schedule() { if (animate() && !frame) frame = requestAnimationFrame(tick); }
    function yieldForFeedback() {
      if (!animate()) return;
      // Let pressed/focused controls reach the screen before the next canvas
      // frame. This does not delay their DOM updates or start another loop.
      feedbackUntil = performance.now() + 50;
    }
    function measureFrame(now) {
      if (!frameSample) return;
      // Canvas may rasterize after paint() returns. Include the gap to the next
      // RAF so command-submission timing cannot hide a busy renderer.
      const slow = frameSample.duration > FRAME_MS * .75 || now - frameSample.finished > FRAME_MS * 1.5;
      slowFrames = slow ? slowFrames + 1 : Math.max(0, slowFrames - 1);
      if (slowFrames >= 2 && detail < 2) {
        detail++; slowFrames = 0;
      }
      frameSample = null;
    }
    function sync() {
      const running = animate();
      if (!running) {
        stop();
        if (wasAnimating || pointer.active || pulses.length) {
          resetInteraction();
          morph = 1;
          dirty = true;
        }
      }
      wasAnimating = running;
      updateControls();
      if (dirty && permitted()) paint();
      schedule();
    }

    function pathForLine(index, onlyFront = false, sampleStep = 1) {
      const offset = index * stride;
      ctx.beginPath();
      let open = false;
      for (let j = 0; j <= segments; j += sampleStep) {
        const k = offset + j * 3;
        if (onlyFront && projected[k + 2] > -.06) { open = false; continue; }
        if (!open) { ctx.moveTo(projected[k], projected[k + 1]); open = true; }
        else ctx.lineTo(projected[k], projected[k + 1]);
      }
    }
    function project(sampleStep, contourStep) {
      // Input can arrive far faster than the 30fps drawing budget. Read layout
      // only for the latest position, once per painted frame.
      if (pointer.pending) {
        const position = point(pointer);
        pointer.x = position.x; pointer.y = position.y; pointer.pending = false;
      }
      const blend = ease(morph);
      const follow = .14;
      pointer.strength += ((pointer.active ? 1 : 0) - pointer.strength) * follow;
      pointer.tiltX += ((pointer.active ? (pointer.x - .5) * .65 : 0) - pointer.tiltX) * follow;
      pointer.tiltY += ((pointer.active ? (pointer.y - .5) * .42 : 0) - pointer.tiltY) * follow;
      const rx = -.56 + pointer.tiltY + .055 * Math.sin(playTime * .23);
      const ry = .42 + pointer.tiltX + .11 * Math.sin(playTime * .17);
      const rz = .22 + .035 * Math.sin(playTime * .19);
      const sx = Math.sin(rx), cx = Math.cos(rx), sy = Math.sin(ry), cy = Math.cos(ry), sz = Math.sin(rz), cz = Math.cos(rz);
      const centerX = width * .5, centerY = height * .5;
      const fieldRadius = Math.min(width, height) * .54;
      const pullX = pointer.x * width, pullY = pointer.y * height;
      const pulseScale = Math.min(width, height);
      for (let j = 0; j <= segments; j += sampleStep) {
        const u = TAU * j / segments;
        waveA[j] = (Math.sin(2 * u + playTime * .55) - Math.sin(2 * u)) * .021;
        waveB[j] = (Math.cos(3 * u - playTime * .43) - Math.cos(3 * u)) * .018;
      }
      for (const line of lineOrder) {
        const i = line.index;
        if (i % contourStep) continue;
        let depth = 0;
        for (let j = 0; j <= segments; j += sampleStep) {
          const k = i * stride + j * 3;
          const x = source[k] + (target[k] - source[k]) * blend + waveA[j] * lineCos[i];
          const y = source[k + 1] + (target[k + 1] - source[k + 1]) * blend + waveB[j];
          const z = source[k + 2] + (target[k + 2] - source[k + 2]) * blend + waveA[j] * lineSin[i];
          const y1 = y * cx - z * sx, z1 = y * sx + z * cx;
          const x2 = x * cy + z1 * sy, z2 = -x * sy + z1 * cy;
          const x3 = x2 * cz - y1 * sz, y3 = x2 * sz + y1 * cz;
          const perspective = 5.5 / (5.5 + z2);
          let px = centerX + x3 * scale * perspective;
          let py = centerY + y3 * scale * perspective;
          if (pointer.strength > .002) {
            const dx = pullX - px, dy = pullY - py;
            const field = Math.exp(-(dx * dx + dy * dy) / (fieldRadius * fieldRadius)) * pointer.strength;
            px += (dx * .34 - dy * .075) * field;
            py += (dy * .34 + dx * .075) * field;
          }
          for (const pulse of pulses) {
            const dx = px - pulse.x * width, dy = py - pulse.y * height;
            const distance = Math.sqrt(dx * dx + dy * dy) || .001;
            const front = pulse.age * pulseScale * .62;
            const band = pulseScale * .075;
            const separation = (distance - front) / band;
            const amplitude = Math.exp(-separation * separation) * (1 - pulse.age / 1.8) * pulseScale * .075;
            px += dx / distance * amplitude;
            py += dy / distance * amplitude;
          }
          projected[k] = px; projected[k + 1] = py; projected[k + 2] = z2;
          depth += z2;
        }
        line.depth = depth / (segments / sampleStep + 1);
      }
      lineOrder.sort((a, b) => b.depth - a.depth);
    }
    function paint() {
      if (!permitted() || !target || failed) return;
      const started = performance.now();
      const liveDetail = animate() ? detail : 0;
      const sampleStep = liveDetail ? 2 : 1, contourStep = liveDetail > 1 ? 2 : 1;
      const brightness = contourStep === 1 ? 1 : 1.6;
      try {
        project(sampleStep, contourStep);
        ctx.clearRect(0, 0, width, height);
        if (!glow) {
          glow = ctx.createRadialGradient(width * .5, height * .5, 0, width * .5, height * .5, scale * 1.8);
          glow.addColorStop(0, 'rgba(137,176,153,.08)');
          glow.addColorStop(.55, 'rgba(114,147,145,.035)');
          glow.addColorStop(1, 'rgba(114,147,145,0)');
        }
        ctx.fillStyle = glow; ctx.fillRect(0, 0, width, height);
        ctx.globalCompositeOperation = 'lighter';
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        for (const line of lineOrder) {
          const i = line.index;
          if (i % contourStep) continue;
          if (i % 9 === 0) {
            pathForLine(i, false, sampleStep);
            ctx.strokeStyle = `rgba(${colors[i]},${.035 * brightness})`; ctx.lineWidth = 4; ctx.stroke();
          }
          pathForLine(i, false, sampleStep);
          const opacity = clamp(.29 - line.depth * .11, .19, .42) * brightness;
          ctx.strokeStyle = `rgba(${colors[i]},${opacity})`;
          ctx.lineWidth = lines < 100 ? .75 : .65;
          ctx.stroke();
        }
        for (let i = contourStep; i < lines; i += 5 * contourStep) {
          pathForLine(i, true, sampleStep);
          ctx.strokeStyle = `rgba(243,242,220,${contourStep === 1 ? .58 : .74})`; ctx.lineWidth = .85; ctx.stroke();
        }
        ctx.globalCompositeOperation = 'source-over';
        dirty = false;
        if (host.dataset.heroReady !== 'true') {
          host.dataset.heroReady = 'true';
          if (controls) controls.hidden = false;
        }
      } catch (_) {
        failed = true; stop();
        delete host.dataset.heroReady;
        updateControls();
      } finally {
        // A frame-rate ceiling alone can repaint continuously on a slow canvas.
        // Leave as much time for other work as this draw used. On fast devices
        // the existing 30fps interval remains the limiting factor.
        const finished = performance.now();
        nextPaintAt = finished + Math.max(0, finished - started);
        frameSample = animate() ? { finished, duration: finished - started } : null;
      }
    }
    function tick(timestamp) {
      frame = 0;
      if (!animate()) { sync(); return; }
      measureFrame(performance.now());
      if (!lastPaint) lastPaint = timestamp - FRAME_MS;
      const elapsed = timestamp - lastPaint;
      if (elapsed >= FRAME_MS - .01 && timestamp >= Math.max(nextPaintAt, feedbackUntil)) {
        const delta = Math.min(elapsed / 1000, .08);
        playTime += delta;
        morph = Math.min(1, morph + delta / 1.25);
        for (let i = pulses.length - 1; i >= 0; i--) {
          pulses[i].age += delta;
          if (pulses[i].age >= 1.8) pulses.splice(i, 1);
        }
        paint();
        // Start the next interval at this actual paint. Retaining a nearly-full
        // modulo remainder after a slightly early frame can cause a 60 Hz pair.
        lastPaint = timestamp;
      }
      schedule();
    }

    function selectMode(next) {
      if (!(next in NAMES) || next === mode || failed || !target) return;
      if (animate()) {
        yieldForFeedback();
        const blend = ease(morph);
        const blended = new Float32Array(target.length);
        for (let i = 0; i < target.length; i++) blended[i] = source[i] + (target[i] - source[i]) * blend;
        source = blended;
        morph = 0;
      } else { source = shapes[next]; morph = 1; }
      mode = next; target = shapes[next]; dirty = true;
      updateControls();
      if (!animate() && permitted()) paint();
      schedule();
      announce(`${NAMES[mode]} form selected.${motionPermitted() ? '' : ' Motion is paused.'}`);
    }
    function sendPulse(x = .5, y = .5) {
      if (!animate()) return;
      yieldForFeedback();
      if (pulses.length === 3) pulses.shift();
      pulses.push({ x: clamp(x, 0, 1), y: clamp(y, 0, 1), age: 0 });
      schedule();
      announce(`Pulse sent through the ${NAMES[mode]} form.`);
    }
    function point(event) {
      const box = stage.getBoundingClientRect();
      return { x: clamp((event.clientX - box.left) / (box.width || 1), 0, 1), y: clamp((event.clientY - box.top) / (box.height || 1), 0, 1) };
    }
    function pointerMove(event) {
      if (!animate()) return;
      const touch = event.pointerType === 'touch';
      if (touch) {
        if (!down || down.id !== event.pointerId) return;
        const dx = event.clientX - down.x, dy = event.clientY - down.y;
        if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 8) { pointer.active = false; pointer.pending = false; return; }
        if (Math.abs(dx) < 8) return;
        down.dragged = true;
      }
      pointer.clientX = event.clientX; pointer.clientY = event.clientY;
      pointer.active = true; pointer.pending = true;
      schedule();
    }
    function pointerDown(event) {
      if (!animate() || event.button > 0) return;
      down = { id: event.pointerId, x: event.clientX, y: event.clientY, time: performance.now(), dragged: false };
      if (event.pointerType !== 'touch') pointerMove(event);
    }
    function pointerUp(event) {
      if (!down || down.id !== event.pointerId) return;
      const tap = !down.dragged && Math.hypot(event.clientX - down.x, event.clientY - down.y) < 12 && performance.now() - down.time < 700;
      down = null;
      if (tap && animate()) { const position = point(event); sendPulse(position.x, position.y); }
      if (event.pointerType === 'touch') { pointer.active = false; pointer.pending = false; }
    }
    function pointerCancel() { down = null; pointer.active = false; pointer.pending = false; }

    modes.forEach(button => button.addEventListener('click', () => selectMode(button.dataset.heroMode)));
    if (pulseButton) pulseButton.addEventListener('click', () => sendPulse());
    controls?.addEventListener('pointerdown', yieldForFeedback, { passive: true });
    controls?.addEventListener('keydown', yieldForFeedback);
    stage.addEventListener('pointermove', pointerMove, { passive: true });
    stage.addEventListener('pointerdown', pointerDown, { passive: true });
    stage.addEventListener('pointerup', pointerUp, { passive: true });
    stage.addEventListener('pointercancel', pointerCancel, { passive: true });
    stage.addEventListener('pointerleave', pointerCancel, { passive: true });
    window.addEventListener('pointerup', pointerUp, { passive: true });
    window.addEventListener('pointercancel', pointerCancel, { passive: true });
    document.addEventListener('visibilitychange', () => { readBounds(); sync(); });
    window.addEventListener('pagehide', () => { pageActive = false; dirty = true; sync(); });
    window.addEventListener('pageshow', () => {
      pageActive = true;
      intersecting = readBounds().width > 0 && inViewport;
      dirty = true; resize();
    });
    window.addEventListener('resize', resize, { passive: true });
    reduced.addEventListener('change', sync);
    coarse.addEventListener('change', resize);
    connection?.addEventListener?.('change', sync);
    new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ['data-motion'] });
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(stage);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.target !== stage) return;
          intersecting = entry.isIntersecting && entry.intersectionRatio > 0;
          readBounds(); sync();
        });
      }, { threshold: [0, .001] }).observe(stage);
    } else {
      window.addEventListener('scroll', () => { readBounds(); sync(); }, { passive: true });
    }
    resize();
  }

  document.querySelectorAll('[data-living-hero]').forEach(create);
})();
