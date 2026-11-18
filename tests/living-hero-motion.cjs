/* Behavioral lifecycle checks for the optional homepage canvas renderer. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/living-hero.js'), 'utf8');

function eventTarget() {
  const listeners = new Map();
  return {
    addEventListener(type, fn) {
      if (!listeners.has(type)) listeners.set(type, new Set());
      listeners.get(type).add(fn);
    },
    removeEventListener(type, fn) { listeners.get(type)?.delete(fn); },
    dispatch(type, details = {}) {
      const event = {type, target: this, currentTarget: this, preventDefault() {},
        stopPropagation() {}, ...details};
      for (const fn of [...(listeners.get(type) || [])]) fn(event);
    },
  };
}

function element(tag = 'div', dataset = {}) {
  const attributes = new Map(), properties = new Map(), classes = new Set();
  const dataKey = name => name.startsWith('data-')
    ? name.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase()) : null;
  const node = Object.assign(eventTarget(), {
    tagName: tag.toUpperCase(), dataset, hidden: false, disabled: false,
    textContent: '', parentElement: null,
    style: {
      setProperty: (name, value) => properties.set(name, String(value)),
      getPropertyValue: name => properties.get(name) || '',
      removeProperty: name => properties.delete(name),
    },
    classList: {
      add: (...names) => names.forEach(name => classes.add(name)),
      remove: (...names) => names.forEach(name => classes.delete(name)),
      contains: name => classes.has(name),
      toggle(name, force = !classes.has(name)) {
        if (force) classes.add(name); else classes.delete(name);
        return force;
      },
    },
    setAttribute(name, value) {
      const key = dataKey(name);
      if (key) dataset[key] = String(value);
      else attributes.set(name, String(value));
      if (name === 'hidden' || name === 'disabled') this[name] = true;
    },
    getAttribute(name) {
      const key = dataKey(name);
      if (key) return dataset[key] ?? null;
      if (name === 'hidden' || name === 'disabled') return this[name] ? '' : null;
      return attributes.get(name) ?? null;
    },
    hasAttribute(name) { return this.getAttribute(name) !== null; },
    removeAttribute(name) {
      const key = dataKey(name);
      if (key) delete dataset[key]; else attributes.delete(name);
      if (name === 'hidden' || name === 'disabled') this[name] = false;
    },
    matches(selector) {
      return selector.split(',').some(part => {
        const value = part.trim();
        if (value === tag) return true;
        const match = /^\[data-([\w-]+)\]$/.exec(value);
        const key = match?.[1].replace(/-([a-z])/g, (_, c) => c.toUpperCase());
        return key ? Object.hasOwn(dataset, key) : false;
      });
    },
    closest(selector) {
      for (let current = this; current; current = current.parentElement) {
        if (current.matches(selector)) return current;
      }
      return null;
    },
    querySelector() { return null; }, querySelectorAll() { return []; },
    setPointerCapture() {}, releasePointerCapture() {},
  });
  return node;
}

function setup(options = {}) {
  const frames = new Map(), mutations = [], intersections = [], resizes = [];
  let frameId = 0, clock = 0, paints = 0, commands = [], boundsReads = 0, gradients = 0;
  let bounds = {width: 1200, height: 680, top: 0, left: 0, ...options.bounds};
  const rect = () => {
    boundsReads++;
    return {...bounds, right: bounds.left + bounds.width,
      bottom: bounds.top + bounds.height};
  };
  const root = element('html', {motion: options.motion ?? 'on', theme: 'light'});
  const host = element('section', {livingHero: ''});
  const stage = element('div', {heroStage: ''});
  const canvas = element('canvas', {heroCanvas: ''});
  const fallback = element('img', {heroFallback: ''});
  const controls = element('div', {heroControls: ''});
  const pulse = element('button', {heroPulse: ''});
  const modes = ['weave', 'orbit', 'bloom'].map(mode => element('button', {heroMode: mode}));
  controls.hidden = true;
  modes.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.heroMode === 'weave')));
  for (const node of [stage, controls]) node.parentElement = host;
  for (const node of [canvas, fallback]) node.parentElement = stage;
  for (const node of [...modes, pulse]) node.parentElement = controls;
  host.getBoundingClientRect = stage.getBoundingClientRect = canvas.getBoundingClientRect = rect;
  const nodes = new Map([
    ['[data-hero-stage]', stage], ['[data-hero-canvas]', canvas],
    ['[data-hero-fallback]', fallback], ['[data-hero-controls]', controls],
    ['[data-hero-pulse]', pulse],
    ...['hint', 'form', 'state', 'status'].map(name => [`[data-hero-${name}]`, element()]),
  ]);
  host.querySelector = stage.querySelector = selector => nodes.get(selector) || null;
  host.querySelectorAll = selector => selector === '[data-hero-mode]' ? modes : [];

  function record(name, args) {
    for (const arg of args) {
      if (typeof arg === 'number') assert.ok(Number.isFinite(arg), `${name} received a nonfinite coordinate`);
    }
    commands.push([name, ...args]);
  }
  const context = {};
  for (const name of ['setTransform', 'resetTransform', 'save', 'restore', 'translate',
    'rotate', 'scale', 'beginPath', 'closePath', 'moveTo', 'lineTo', 'bezierCurveTo',
    'quadraticCurveTo', 'arc', 'ellipse', 'rect', 'roundRect', 'clip', 'stroke',
    'fill', 'fillRect', 'strokeRect', 'setLineDash']) {
    context[name] = (...args) => record(name, args);
  }
  context.clearRect = (...args) => {
    if (options.paintThrows) throw new Error('Canvas painting failed');
    clock += options.paintCostMs || 0;
    paints++; commands = []; record('clearRect', args);
  };
  for (const name of ['createLinearGradient', 'createRadialGradient']) {
    context[name] = (...args) => {
      gradients++;
      record(name, args);
      return {addColorStop: (...stop) => record('addColorStop', stop)};
    };
  }
  canvas.width = canvas.height = 0;
  canvas.getContext = () => {
    if (options.contextThrows) throw new Error('Canvas unavailable');
    return options.noContext ? null : context;
  };

  const reduced = Object.assign(eventTarget(), {matches: !!options.reduced});
  const coarse = Object.assign(eventTarget(), {matches: !!options.coarse});
  const connection = Object.assign(eventTarget(), {saveData: !!options.saveData});
  const document = Object.assign(eventTarget(), {
    hidden: !!options.hidden, documentElement: root,
    querySelectorAll: selector => selector === '[data-living-hero]' && !options.noHero ? [host] : [],
    querySelector: selector => selector === '[data-living-hero]' && !options.noHero ? host : null,
  });
  Object.defineProperty(document, 'visibilityState', {get: () => document.hidden ? 'hidden' : 'visible'});
  const window = Object.assign(eventTarget(), {innerHeight: 900, innerWidth: 1440,
    devicePixelRatio: options.dpr ?? 3});
  class IntersectionObserver {
    constructor(callback, config = {}) {
      this.callback = callback;
      this.thresholds = [].concat(config.threshold ?? 0).sort((a, b) => a - b);
      intersections.push(this);
    }
    observe(target) { this.target = target; }
    disconnect() { this.target = null; }
  }
  class ResizeObserver {
    constructor(callback) { this.callback = callback; resizes.push(this); }
    observe(target) { this.target = target; }
    disconnect() { this.target = null; }
  }
  if (!options.noIntersectionObserver) window.IntersectionObserver = IntersectionObserver;
  if (!options.noResizeObserver) window.ResizeObserver = ResizeObserver;
  let randomState = 2026;
  const math = Object.create(Math);
  math.random = () => ((randomState = (Math.imul(randomState, 1664525) + 1013904223) >>> 0) / 0x100000000);
  const sandbox = {
    document, window, navigator: {connection}, console, Math: math,
    devicePixelRatio: window.devicePixelRatio, innerHeight: window.innerHeight,
    innerWidth: window.innerWidth, performance: {now: () => clock},
    matchMedia: query => query.includes('reduced-motion') ? reduced : coarse,
    requestAnimationFrame(callback) { frames.set(++frameId, callback); return frameId; },
    cancelAnimationFrame(id) { frames.delete(id); },
    MutationObserver: class {
      constructor(callback) { this.callback = callback; mutations.push(this); }
      observe(target, config) { this.target = target; this.config = config; }
      disconnect() { this.target = null; }
    },
  };
  if (!options.noIntersectionObserver) sandbox.IntersectionObserver = IntersectionObserver;
  if (!options.noResizeObserver) sandbox.ResizeObserver = ResizeObserver;
  Object.assign(window, {matchMedia: sandbox.matchMedia, performance: sandbox.performance,
    requestAnimationFrame: sandbox.requestAnimationFrame, cancelAnimationFrame: sandbox.cancelAnimationFrame});
  vm.runInNewContext(source, sandbox, {filename: 'living-hero.js'});

  const environment = {
    host, stage, canvas, fallback, controls, modes, pulse, document, root, connection, frames,
    get paints() { return paints; },
    get boundsReads() { return boundsReads; },
    get gradients() { return gradients; },
    get picture() { return JSON.stringify(commands); },
    get text() { return [...nodes.values()].map(node => node.textContent).join('|'); },
    step(time = clock + 50) {
      clock = time;
      for (const [id, callback] of [...frames]) {
        if (!frames.has(id)) continue;
        frames.delete(id);
        callback(clock);
      }
    },
    motion(value) {
      root.dataset.motion = value;
      for (const observer of mutations) {
        if (observer.target === root && (!observer.config.attributeFilter || observer.config.attributeFilter.includes('data-motion'))) {
          observer.callback([{type: 'attributes', target: root, attributeName: 'data-motion'}]);
        }
      }
    },
    reduce(value) { reduced.matches = value; reduced.dispatch('change'); },
    saveData(value) { connection.saveData = value; connection.dispatch('change'); },
    hide(value) { document.hidden = value; document.dispatch('visibilitychange'); },
    intersect(value, ratio = value ? 1 : 0) {
      for (const observer of intersections) if (observer.target) {
        // Browsers notify on threshold/isIntersecting changes, not every scroll.
        const nextThreshold = observer.thresholds.filter(threshold => threshold <= ratio).length;
        if (observer.previousIntersection !== value || observer.previousThreshold !== nextThreshold) {
          observer.previousIntersection = value;
          observer.previousThreshold = nextThreshold;
          observer.callback([{target: observer.target, isIntersecting: value,
            intersectionRatio: ratio, boundingClientRect: rect()}]);
        }
      }
    },
    resize(values) {
      bounds = {...bounds, ...values};
      for (const observer of resizes) if (observer.target) {
        observer.callback([{target: observer.target, contentRect: rect()}]);
      }
      window.dispatch('resize');
    },
    setBounds(values) { bounds = {...bounds, ...values}; },
    pagehide() { window.dispatch('pagehide', {persisted: true}); },
    pageshow() { window.dispatch('pageshow', {persisted: true}); },
    scroll() { window.dispatch('scroll'); },
  };
  environment.intersect(bounds.width > 0 && bounds.height > 0 && bounds.top < window.innerHeight && bounds.top + bounds.height > 0);
  return environment;
}

let checks = 0;
function test(name, check) {
  try { check(); checks++; }
  catch (error) { error.message = `${name}: ${error.message}`; throw error; }
}
function assertPaused(scene, message) {
  assert.equal(scene.frames.size, 0, `${message}: no scheduled animation`);
  const paints = scene.paints;
  scene.step(); scene.step();
  assert.equal(scene.paints, paints, `${message}: no background painting`);
}

test('Motion and lifecycle gates keep one animation loop', () => {
  const scene = setup();
  assert.equal(scene.host.dataset.heroReady, 'true');
  assert.equal(scene.controls.hidden, false);
  assert.equal(scene.frames.size, 1);
  const firstPaints = scene.paints;
  scene.step(100); scene.step(150);
  assert.ok(scene.paints > firstPaints, 'Enabled scenes animate');
  scene.motion('off'); assertPaused(scene, 'Motion off');
  assert.equal(scene.pulse.disabled, true);
  scene.motion('on'); scene.motion('on'); scene.intersect(true);
  assert.equal(scene.frames.size, 1, 'Repeated resume signals cannot duplicate the loop');
  scene.intersect(false); assertPaused(scene, 'Offscreen');
  scene.intersect(true); assert.equal(scene.frames.size, 1);
  scene.hide(true); assertPaused(scene, 'Hidden document');
  scene.motion('off'); scene.hide(false); assertPaused(scene, 'Visibility cannot override motion off');
  scene.motion('on'); assert.equal(scene.frames.size, 1);
  scene.reduce(true); assertPaused(scene, 'Reduced motion');
  scene.motion('on'); assertPaused(scene, 'Motion on cannot override reduced motion');
  scene.reduce(false); assert.equal(scene.frames.size, 1);
  scene.saveData(true); assertPaused(scene, 'Save-Data');
  scene.saveData(false); assert.equal(scene.frames.size, 1);
});

test('BFcache restores only an onscreen stage', () => {
  const scene = setup();
  scene.pagehide(); assertPaused(scene, 'Page hidden for navigation');
  scene.setBounds({top: 1500});
  scene.pageshow(); assertPaused(scene, 'Restored page with offscreen stage');
  scene.setBounds({top: 0});
  scene.pageshow(); scene.pageshow();
  assert.equal(scene.frames.size, 1, 'Onscreen BFcache restore restarts one loop');
});

test('Crossing an edge-adjacent intersection wakes the renderer', () => {
  const scene = setup({bounds: {top: 1500}});
  assertPaused(scene, 'Initially below the viewport');
  scene.setBounds({top: 900}); scene.intersect(true, 0);
  assertPaused(scene, 'Edge contact without visible area');
  scene.setBounds({top: 890}); scene.intersect(true, 10 / 680);
  assert.equal(scene.frames.size, 1, 'Positive visible area must cause an observer callback and resume');
  assert.equal(scene.host.dataset.heroReady, 'true');
});

test('Viewport and resize fallback works without observers', () => {
  const scene = setup({noIntersectionObserver: true, noResizeObserver: true,
    bounds: {top: 1500}});
  assertPaused(scene, 'Initially offscreen without observers');
  assert.equal(scene.controls.hidden, true, 'Fallback stays until the first visible render');
  scene.setBounds({top: 0}); scene.scroll();
  assert.equal(scene.frames.size, 1);
  scene.step(); scene.step();
  assert.ok(scene.paints > 0);
  scene.resize({width: 390, height: 600});
  assert.ok(scene.canvas.width <= 390 * 1.4);
  scene.setBounds({top: -700}); scene.scroll();
  assertPaused(scene, 'Scrolled fully above viewport without observers');
});

test('Canvas resolution remains bounded after resize', () => {
  const scene = setup();
  assert.ok(scene.canvas.width <= 1200 * 1.65);
  assert.ok(scene.canvas.height <= 680 * 1.65);
  assert.ok(scene.canvas.width * scene.canvas.height <= 1_150_000);
  scene.resize({width: 10000, height: 6000});
  assert.ok(scene.canvas.width > 0 && scene.canvas.height > 0);
  assert.ok(scene.canvas.width * scene.canvas.height <= 1_150_000, 'Large displays keep the pixel budget');
  scene.resize({width: 390, height: 600});
  assert.ok(scene.canvas.width <= 390 * 1.4, 'Compact DPR is capped');
  assert.ok(scene.canvas.height <= 600 * 1.4);
  assert.equal(scene.frames.size, 1, 'Resizing does not create another loop');
});

test('An unmeasurable stage pauses and recovers', () => {
  const scene = setup({bounds: {width: 0, height: 0}});
  assertPaused(scene, 'Stage initially has no size');
  assert.notEqual(scene.host.dataset.heroReady, 'true');
  assert.equal(scene.controls.hidden, true);
  scene.resize({width: 800, height: 600}); scene.intersect(true);
  assert.ok(scene.canvas.width > 0 && scene.canvas.height > 0);
  assert.equal(scene.host.dataset.heroReady, 'true');
  assert.equal(scene.frames.size, 1);
  scene.resize({width: 0, height: 0});
  assertPaused(scene, 'Stage hidden by layout');
});

test('Painting respects its frame-rate and elapsed-time budgets', () => {
  const scene = setup();
  scene.step(100);
  const painted = scene.paints;
  for (const time of [105, 110, 115, 120, 125, 130, 132.9]) scene.step(time);
  assert.equal(scene.paints, painted, 'High-refresh RAF callbacks do not cause extra canvas paints');
  scene.step(134);
  assert.equal(scene.paints, painted + 1, 'Painting resumes after one 30fps interval');

  const shortGap = setup(), longGap = setup();
  shortGap.step(100); longGap.step(100);
  shortGap.step(180); longGap.step(1_000_000);
  assert.equal(longGap.picture, shortGap.picture, 'A long stall advances the scene by at most 80ms');
});

test('Slow canvas frames leave an equal idle interval for other work', () => {
  const scene = setup({paintCostMs: 50});
  scene.step(100); // This paint finishes at 150ms and yields until 200ms.
  const painted = scene.paints;
  for (const time of [150, 166.7, 183.4, 199.9]) scene.step(time);
  assert.equal(scene.paints, painted, 'An over-budget draw cannot repaint immediately on the next RAF');
  assert.equal(scene.frames.size, 1, 'The idle interval retains just one lightweight RAF');
  scene.step(200);
  assert.equal(scene.paints, painted + 1, 'The next frame draws after its full idle interval');
  scene.motion('off'); assertPaused(scene, 'Pausing during adaptive frame pacing');
  scene.motion('on');
  assert.equal(scene.frames.size, 1, 'Resume still owns one loop');

  const fast = setup({paintCostMs: 5});
  fast.step(100);
  const fastPaints = fast.paints;
  fast.step(130);
  assert.equal(fast.paints, fastPaints, 'Fast frames retain the 30fps ceiling');
  fast.step(134);
  assert.equal(fast.paints, fastPaints + 1, 'A fast canvas keeps the existing cadence');
});

test('Mode buttons change a paused still without starting animation', () => {
  for (const options of [{motion: 'off'}, {reduced: true}, {saveData: true}]) {
    const scene = setup(options);
    assert.ok(scene.paints > 0, 'Paused visible stage has a still');
    assertPaused(scene, 'Initially paused');
    let previous = scene.picture;
    for (const mode of ['orbit', 'bloom', 'weave']) {
      const button = scene.modes.find(item => item.dataset.heroMode === mode);
      const before = scene.paints;
      button.dispatch('click');
      assert.ok(scene.paints > before, `${mode} redraws immediately`);
      assert.notEqual(scene.picture, previous, `${mode} produces a different composition`);
      assert.equal(button.getAttribute('aria-pressed'), 'true');
      assert.equal(scene.modes.filter(item => item.getAttribute('aria-pressed') === 'true').length, 1);
      assertPaused(scene, 'Explicit mode selection');
      previous = scene.picture;
    }
  }
});

test('Pointer and pulse input cannot disturb a paused still', () => {
  const scene = setup({motion: 'off'});
  const before = {picture: scene.picture, paints: scene.paints, text: scene.text};
  for (const type of ['pointermove', 'pointerdown', 'pointerup', 'click']) {
    scene.stage.dispatch(type, {clientX: 950, clientY: 120, pointerId: 1,
      pointerType: 'touch', button: 0, isPrimary: true});
  }
  scene.pulse.dispatch('click');
  assert.equal(scene.paints, before.paints);
  assert.equal(scene.picture, before.picture);
  assert.equal(scene.text, before.text);
  assertPaused(scene, 'Paused pointer input');
  const control = setup({motion: 'off'});
  scene.motion('on'); control.motion('on');
  scene.step(100); control.step(100); scene.step(150); control.step(150);
  assert.equal(scene.picture, control.picture, 'Ignored input must not leave a latent impulse on resume');
});

test('Enabled pointer, pulse button, and touch tap change the artwork', () => {
  const scene = setup(), control = setup();
  const inputs = [
    ['pointer', () => scene.stage.dispatch('pointermove', {
      clientX: 1000, clientY: 120, pointerType: 'mouse', pointerId: 1,
    })],
    ['pulse button', () => scene.pulse.dispatch('click')],
    ['touch tap', () => {
      const touch = {clientX: 600, clientY: 340, pointerType: 'touch', pointerId: 2, button: 0};
      scene.stage.dispatch('pointerdown', touch);
      scene.stage.dispatch('pointerup', touch);
    }],
  ];
  for (const [name, input] of inputs) {
    scene.motion('on'); control.motion('on');
    input();
    for (let frame = 0; frame < 6; frame++) { scene.step(); control.step(); }
    assert.notEqual(scene.picture, control.picture, `${name} visibly changes the projected geometry`);
    assert.equal(scene.frames.size, 1, `${name} preserves a single animation loop`);
    scene.motion('off'); control.motion('off');
    assert.equal(scene.picture, control.picture, 'Pausing clears the existing interaction');
  }
});

test('High-frequency pointer input coalesces layout reads into one paint', () => {
  const scene = setup(), finalInput = setup();
  scene.step(100); finalInput.step(100);
  const reads = scene.boundsReads, paints = scene.paints;
  for (let i = 0; i < 100; i++) scene.stage.dispatch('pointermove', {
    clientX: 600 + i * 4, clientY: 250 - i, pointerType: 'mouse', pointerId: 1,
  });
  finalInput.stage.dispatch('pointermove', {
    clientX: 996, clientY: 151, pointerType: 'mouse', pointerId: 1,
  });
  assert.equal(scene.boundsReads, reads, 'Pointer callbacks do not force layout');
  assert.equal(scene.paints, paints, 'Pointer callbacks do not paint synchronously');
  assert.equal(scene.frames.size, 1, 'Burst input retains one scheduled paint');
  scene.step(150); finalInput.step(150);
  assert.equal(scene.boundsReads, reads + 1, 'One frame reads the latest position once');
  assert.equal(scene.picture, finalInput.picture, 'Intermediate pointer positions are discarded');
  scene.step(200);
  assert.equal(scene.boundsReads, reads + 1, 'A frame without new input does not read layout');

  // A queued point must not reappear after leaving the form or pausing it.
  scene.stage.dispatch('pointermove', {clientX: 1100, clientY: 20, pointerType: 'mouse'});
  scene.stage.dispatch('pointerleave');
  scene.step(250);
  assert.equal(scene.boundsReads, reads + 1, 'Pointer exit clears pending input');
  scene.stage.dispatch('pointermove', {clientX: 1100, clientY: 20, pointerType: 'mouse'});
  scene.motion('off');
  assert.equal(scene.boundsReads, reads + 1, 'Pausing clears pending input before its still redraw');
});

test('Queued pointer input uses fresh bounds and respects touch cancellation', () => {
  const scene = setup(), moved = setup();
  const input = {clientX: 620, clientY: 240, pointerType: 'mouse', pointerId: 1};
  scene.stage.dispatch('pointermove', input);
  scene.setBounds({left: 100, top: 20});
  moved.setBounds({left: 100, top: 20});
  moved.stage.dispatch('pointermove', input);
  scene.step(100); moved.step(100);
  assert.equal(scene.picture, moved.picture, 'A move queued before a scroll uses the current rectangle');

  const resizing = setup(), resized = setup();
  const nextBounds = {left: 80, width: 800, height: 600};
  resizing.stage.dispatch('pointermove', input);
  resized.setBounds(nextBounds);
  resized.stage.dispatch('pointermove', input);
  resizing.resize(nextBounds); resized.resize(nextBounds);
  assert.equal(resizing.picture, resized.picture, 'A resize maps pending input into the new dimensions');

  for (const cancel of ['pointercancel', 'vertical-scroll']) {
    const touchScene = setup(), untouched = setup();
    const touch = {clientX: 600, clientY: 200, pointerType: 'touch', pointerId: 2, button: 0};
    touchScene.stage.dispatch('pointerdown', touch);
    touchScene.stage.dispatch('pointermove', {...touch, clientX: 620});
    if (cancel === 'pointercancel') touchScene.stage.dispatch('pointercancel', touch);
    else touchScene.stage.dispatch('pointermove', {...touch, clientX: 620, clientY: 280});
    touchScene.step(100); untouched.step(100);
    assert.equal(touchScene.picture, untouched.picture, `${cancel} clears queued touch attraction`);
  }
});

test('The unchanged canvas glow is reused until its dimensions change', () => {
  const scene = setup();
  assert.equal(scene.gradients, 1);
  for (let frame = 1; frame <= 10; frame++) scene.step(frame * 50);
  scene.pulse.dispatch('click'); scene.step(600);
  scene.modes[1].dispatch('click'); scene.step(650);
  assert.equal(scene.gradients, 1, 'Animation and interactions reuse the same gradient');
  scene.resize({width: 390, height: 600});
  assert.equal(scene.gradients, 2, 'Resizing recreates the gradient for the new canvas');
});

test('Fallback remains available after canvas failure', () => {
  for (const options of [{noContext: true}, {contextThrows: true}, {paintThrows: true}, {noHero: true}]) {
    const scene = setup(options);
    assert.equal(scene.paints, 0);
    assert.equal(scene.frames.size, 0);
    assert.notEqual(scene.host.dataset.heroReady, 'true');
    assert.equal(scene.controls.hidden, true);
    assert.equal(scene.fallback.hidden, false);
    const fallbackText = scene.text;
    for (const update of [() => scene.motion('off'), () => scene.motion('on'),
      () => scene.hide(true), () => scene.hide(false), () => scene.pageshow()]) {
      update();
      assert.equal(scene.frames.size, 0);
      assert.equal(scene.controls.hidden, true);
      assert.notEqual(scene.host.dataset.heroReady, 'true');
      assert.equal(scene.text, fallbackText, 'Lifecycle events preserve the failed renderer fallback state');
    }
  }
});

console.log(`Living hero lifecycle checks passed: ${checks} behavior groups.`);
