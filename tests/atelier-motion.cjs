/* Dependency-free lifecycle tests for the decorative Canvas enhancement. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('assets/atelier.js', 'utf8');
function setup(options = {}) {
  const frames = new Map(), listeners = {}, mediaListeners = {};
  let next = 0, paints = 0, observeIntersection, observeMutation;
  const root = {dataset:{motion: 'on'}};
  const reduced = {matches:false,addEventListener:(_, fn)=>{mediaListeners.reduce=fn;}};
  const fine = {matches:true,addEventListener:()=>{}};
  const connection = {saveData:false,addEventListener:(_,fn)=>{listeners.connection=fn;}};
  const ctx = {setTransform(){},clearRect(){paints++;},beginPath(){},moveTo(){},lineTo(){},stroke(){},fillRect(){},createRadialGradient(){return {addColorStop(){}};}};
  const canvas = {width:0,height:0,getContext:()=>options.noContext ? null : ctx};
  const hero = {dataset:{},querySelector:()=>canvas,getBoundingClientRect:()=>({width:1440,height:760,top:0,bottom:760,left:0}),style:{setProperty(){},removeProperty(){}},addEventListener(){}};
  const document = {hidden:false,documentElement:root,querySelector:()=>options.noHero ? null : hero,addEventListener:(event,fn)=>{listeners[event]=fn;}};
  const win = {addEventListener:(event,fn)=>{listeners[event]=fn;}};
  const IO = class {constructor(fn){observeIntersection=fn;}observe(){observeIntersection([{isIntersecting:true}]);}};
  const RO = class {constructor(fn){this.fn=fn;}observe(){this.fn();}};
  Object.assign(win, {IntersectionObserver:IO,ResizeObserver:RO});
  const sandbox = {document,window:win,navigator:{connection},devicePixelRatio:3,innerHeight:960,Math,console,
    matchMedia:q=>q.includes('reduced')?reduced:fine,
    MutationObserver:class {constructor(fn){observeMutation=fn;}observe(){}},
    IntersectionObserver:IO,ResizeObserver:RO,
    requestAnimationFrame:fn=>{frames.set(++next,fn);return next;},
    cancelAnimationFrame:id=>frames.delete(id)};
  vm.runInNewContext(source,sandbox);
  return {frames,hero,root,canvas,document,connection,reduced,mediaListeners,listeners,
    motion(value){root.dataset.motion=value;observeMutation();},
    intersection(value){observeIntersection([{isIntersecting:value}]);},
    step(t){const queued=[...frames.values()];frames.clear();queued.forEach(fn=>fn(t));},
    get paints(){return paints;}};
}
const s=setup();
assert.equal(s.hero.dataset.sceneActive,'true');
assert.equal(s.frames.size,1);
assert.equal(s.canvas.width,2160, 'DPR is capped at 1.5');
s.step(100);s.step(150);const painted=s.paints;assert.ok(painted>0);
s.motion('off');assert.equal(s.frames.size,0);assert.equal(s.hero.dataset.sceneActive,'false');
s.step(300);assert.equal(s.paints,painted,'Paused scenes do not draw');
s.motion('on');assert.equal(s.frames.size,1);
s.motion('on');assert.equal(s.frames.size,1,'No duplicate animation loop');
s.intersection(false);assert.equal(s.frames.size,0);
s.intersection(true);assert.equal(s.frames.size,1);
s.document.hidden=true;s.listeners.visibilitychange();assert.equal(s.frames.size,0);
s.document.hidden=false;s.listeners.visibilitychange();assert.equal(s.frames.size,1);
s.reduced.matches=true;s.mediaListeners.reduce();assert.equal(s.frames.size,0);
s.reduced.matches=false;s.mediaListeners.reduce();assert.equal(s.frames.size,1);
s.connection.saveData=true;s.listeners.connection();assert.equal(s.frames.size,0);
s.connection.saveData=false;s.listeners.connection();assert.equal(s.frames.size,1);
s.listeners.pagehide();assert.equal(s.frames.size,0);
s.listeners.pageshow();assert.equal(s.frames.size,1);
assert.doesNotThrow(()=>setup({noContext:true}));
assert.doesNotThrow(()=>setup({noHero:true}));
console.log('Atelier lifecycle checks passed: pause, resume, offscreen, hidden, reduced motion, Save-Data, lifecycle, context fallback.');
