/* Exercise real studio event handlers with a small DOM/canvas stand-in. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/generative-studio.js'), 'utf8');
function element(dataset = {}) {
  const listeners = new Map(), attrs = new Map();
  return {
    dataset, disabled: false, value: '', textContent: '',
    addEventListener(type, callback) { if (!listeners.has(type)) listeners.set(type, []); listeners.get(type).push(callback); },
    dispatch(type, values = {}) {
      const event = { target: this, key: '', preventDefault() {}, ...values };
      return Promise.all((listeners.get(type) || []).map(callback => callback(event)));
    },
    setAttribute(name, value) { attrs.set(name, String(value)); },
    getAttribute(name) { return attrs.get(name); },
  };
}
function setup(options = {}) {
  const root = element({ motion: options.motion || 'on' });
  const host = element({ generative: 'lab' }), canvas = element();
  host.getBoundingClientRect = () => ({ width: 390, height: 660, left: 0, top: 0 });
  canvas.closest = () => host;
  const nodes = Object.fromEntries(['seed', 'speed', 'density', 'pause', 'impulse', 'status',
    'state', 'hint', 'reroll', 'capture', 'share'].map(name => [name, element()]));
  const modes = ['foundry', 'filaments', 'bloom', 'orbit'].map(mode => element({ studioMode: mode }));
  let paints = 0, fingerprint = 0, download = '', copied = '';
  const context = new Proxy({}, { get(_, name) {
    if (name === 'clearRect') return () => { paints++; fingerprint = 0; };
    if (String(name).includes('Gradient')) return () => ({ addColorStop() {} });
    return (...args) => { args.forEach(arg => { if (typeof arg === 'number') { assert.ok(Number.isFinite(arg)); fingerprint += arg; } }); };
  }, set() { return true; } });
  canvas.getContext = () => context;
  canvas.toBlob = callback => callback({ size: 1 });
  const reduced = { ...element(), matches: !!options.reduced };
  const connection = { ...element(), saveData: !!options.saveData };
  const document = { ...element(), documentElement: root, hidden: false, activeElement: canvas,
    querySelector(selector) { const key = /^\[data-studio-(.+)\]$/.exec(selector)?.[1]; return nodes[key] || null; },
    querySelectorAll(selector) { return selector === 'canvas[data-generative-scene]' ? [canvas] : modes; },
    createElement() { return { click() { download = this.download; } }; },
  };
  host.querySelector = document.querySelector;
  const window = element();
  const mutations = [], intersections = [], frames = new Map();
  let nextFrame = 0;
  class IntersectionObserver {
    constructor(callback) { intersections.push(callback); }
    observe() {}
  }
  window.IntersectionObserver = IntersectionObserver;
  const location = { href: 'https://example.invalid/lab/?mode=orbit&seed=2026', search: '?mode=orbit&seed=2026' };
  class TestURL extends URL {}
  TestURL.createObjectURL = () => 'blob:studio-test';
  TestURL.revokeObjectURL = () => {};
  vm.runInNewContext(source, {
    document, window, navigator: { connection, clipboard: { async writeText(value) { copied = value; } } },
    matchMedia: () => reduced, location, URLSearchParams, URL: TestURL,
    history: { replaceState(_state, _title, url) { location.href = String(url); } },
    devicePixelRatio: 1, performance: { now: () => 10 }, setTimeout: callback => callback(),
    requestAnimationFrame(callback) { frames.set(++nextFrame, callback); return nextFrame; },
    cancelAnimationFrame(id) { frames.delete(id); }, IntersectionObserver,
    MutationObserver: class { constructor(callback) { mutations.push(callback); } observe() {} },
  });
  intersections.forEach(callback => callback([{ isIntersecting: true }]));
  return {
    root, host, canvas, document, nodes, modes, frames, location,
    get paints() { return paints; }, get picture() { return fingerprint; },
    get download() { return download; }, get copied() { return copied; },
    motion(value) { root.dataset.motion = value; mutations.forEach(callback => callback()); },
    reduce(value) { reduced.matches = value; reduced.dispatch('change'); },
    saveData(value) { connection.saveData = value; connection.dispatch('change'); },
    visible(value) { intersections.forEach(callback => callback([{ isIntersecting: value }])); },
  };
}
async function check() {
  for (const [options, label] of [[{ motion: 'off' }, 'Motion off'], [{ reduced: true }, 'Reduced motion'], [{ saveData: true }, 'Data saving']]) {
    const scene = setup(options);
    assert.equal(scene.nodes.state.textContent, label);
    assert.equal(scene.nodes.pause.textContent, label);
    assert.equal(scene.nodes.pause.disabled, true);
    assert.equal(scene.nodes.impulse.disabled, true);
    assert.match(scene.nodes.hint.textContent, /Still view/);
    assert.equal(scene.frames.size, 0);
    const before = scene.paints;
    await scene.nodes.impulse.dispatch('click');
    await scene.nodes.pause.dispatch('click');
    await scene.document.dispatch('keydown', { key: ' ' });
    assert.equal(scene.paints, before, 'Blocked pulse and pause inputs do not redraw or queue animation');
    assert.equal(scene.frames.size, 0);
    await scene.host.dispatch('pointerdown', { target: scene.canvas, clientX: 100, clientY: 100 });
    await scene.host.dispatch('pointerup', { clientX: 100, clientY: 100 });
    assert.equal(scene.paints, before, 'A tap does not store a paused impulse');
    const picture = scene.picture;
    await scene.document.dispatch('keydown', { key: 'ArrowRight' });
    assert.notEqual(scene.picture, picture, 'Manual orbit remains available');
    await scene.modes[2].dispatch('click');
    assert.equal(scene.modes[2].getAttribute('aria-pressed'), 'true');
    assert.match(scene.location.href, /mode=bloom&seed=2026/);
    scene.nodes.seed.value = '42'; await scene.nodes.seed.dispatch('change');
    assert.match(scene.location.href, /seed=42/);
    await scene.nodes.capture.dispatch('click');
    assert.equal(scene.download, 'suadtl-bloom-42.png');
    await scene.nodes.share.dispatch('click');
    assert.match(scene.copied, /mode=bloom&seed=42/);
    assert.equal(scene.frames.size, 0, 'Editing and exporting a still does not enable motion');
    scene.reduce(false); scene.saveData(false); scene.motion('on');
    assert.equal(scene.nodes.pause.textContent, 'Pause sculpture', 'Blocked space input must not leave a latent local pause');
    assert.equal(scene.nodes.impulse.disabled, false);
    assert.equal(scene.frames.size, 1);
  }
  const scene = setup();
  assert.equal(scene.nodes.state.textContent, 'Live');
  const still = scene.picture;
  await scene.nodes.impulse.dispatch('click');
  assert.notEqual(scene.picture, still);
  await scene.nodes.pause.dispatch('click');
  assert.equal(scene.nodes.state.textContent, 'Paused');
  assert.equal(scene.nodes.pause.textContent, 'Resume sculpture');
  assert.equal(scene.nodes.impulse.disabled, true);
  assert.equal(scene.picture, still, 'Pausing clears an in-flight pulse');
  assert.equal(scene.frames.size, 0);
  await scene.document.dispatch('keydown', { key: ' ' });
  assert.equal(scene.nodes.state.textContent, 'Live');
  assert.equal(scene.frames.size, 1);
  scene.visible(false);
  assert.equal(scene.nodes.state.textContent, 'Resting');
  assert.equal(scene.nodes.impulse.disabled, true);
  assert.equal(scene.frames.size, 0);
  console.log('Generative Studio state checks passed');
}
check().catch(error => { console.error(error); process.exitCode = 1; });
