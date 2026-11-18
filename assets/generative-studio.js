/* suadtl / Generative Studio: a tiny, locally rendered kinetic sculpture.
   No libraries, no network calls, no tracking. User choices are encoded in the URL. */
(() => {
  'use strict';
  const TAU = Math.PI * 2;
  const root = document.documentElement;
  const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)');
  const connection = navigator.connection;
  const clamp = (v,a,b) => Math.max(a, Math.min(b,v));
  const lerp = (a,b,t) => a + (b-a)*t;
  const modeNames = ['Foundry','Filaments','Bloom','Orbit'];
  const colors = [
    [150,166,115], [218,174,104], [165,99,71], [91,131,155], [201,198,162]
  ];
  function mixColor(a,b,k,alpha=1) {
    return `rgba(${Math.round(lerp(a[0],b[0],k))},${Math.round(lerp(a[1],b[1],k))},${Math.round(lerp(a[2],b[2],k))},${alpha})`;
  }
  function randomGen(seed) {
    let t = seed >>> 0;
    return () => {
      t += 0x6D2B79F5;
      let x = Math.imul(t ^ t >>> 15, 1 | t);
      x ^= x + Math.imul(x ^ x >>> 7, 61 | x);
      return ((x ^ x >>> 14) >>> 0) / 4294967296;
    };
  }
  function sceneData(seed, mode) {
    const random = randomGen(seed ^ (mode * 0x9e3779b9));
    const bands = Array.from({length: mode === 1 ? 3 : mode === 2 ? 9 : 7}, (_, i) => ({
      radius:.42+random()*.94, width:.055+random()*.18,
      phi:random()*TAU, theta:random()*TAU, twist:1+Math.floor(random()*3),
      lift:(random()-.5)*.58, bend:.04+random()*.14,
      speed:(random()*.3+.11)*(i%2?-1:1),
      color:i%colors.length, scatter:random(), tilt:(random()-.5)*1.2,
      shift:(random()-.5)*1.15
    }));
    const fibers = Array.from({length: mode === 1 ? 42 : 26}, (_, i) => ({
      radius:.62+random()*1.35, phase:random()*TAU,
      slope:.6+random()*1.9, spiral:1+random()*2,
      elevation:(random()-.5)*.58, speed:.2+random()*.55,
      opacity:.11+random()*.3, color:i%5
    }));
    const satellites = Array.from({length:12},(_,i)=>({
      radius:.7+random()*1.35, height:(random()-.5)*1.4,
      phase:random()*TAU, speed:.08+random()*.28, size:2.5+random()*5,
      color:i%5
    }));
    return {bands,fibers,satellites};
  }
  function rotate(p,rx,ry,rz) {
    let [x,y,z]=p;
    let c=Math.cos(rx),s=Math.sin(rx); [y,z]=[y*c-z*s,y*s+z*c];
    c=Math.cos(ry);s=Math.sin(ry);[x,z]=[x*c+z*s,-x*s+z*c];
    c=Math.cos(rz);s=Math.sin(rz);[x,y]=[x*c-y*s,x*s+y*c];
    return [x,y,z];
  }
  function create(canvas) {
    const host=canvas.closest('[data-generative]');
    if(!host) return;
    let ctx;
    try { ctx=canvas.getContext('2d', {alpha:true}); } catch (_) { return; }
    if (!ctx) return;
    const lab=host.dataset.generative==='lab';
    let mode=0, seed=2026, intensity=1, density=1;
    const params=new URLSearchParams(location.search);
    if(lab) {
      const chosen=modeNames.findIndex(n=>n.toLowerCase()===params.get('mode')?.toLowerCase());
      if(chosen>=0) mode=chosen;
      if(/^\d{1,10}$/.test(params.get('seed')||'')) seed=Number(params.get('seed'))>>>0;
    }
    let data=sceneData(seed,mode), width=0,height=0,scale=1,dpr=1;
    let playTime=0,frame=0,last=0,visible=false,holding=false;
    let cameraX=-.18,cameraY=.22,targetX=0,targetY=0,energy=0;
    let drag=null,needsDraw=true,snapshotRequested=false,pendingPulse=false;
    let touchDown=0;
    let lastPointer={x:0,y:0};
    const mobile=()=>width<700;
    const randomSeed=()=>Math.floor(Math.random()*0xffffffff)>>>0;
    const announce=message=>{
      const el=document.querySelector('[data-studio-status]');
      if(el) el.textContent=message;
    };
    const seedInput=document.querySelector('[data-studio-seed]');
    const intensityInput=document.querySelector('[data-studio-speed]');
    const densityInput=document.querySelector('[data-studio-density]');
    const pauseButton=document.querySelector('[data-studio-pause]');
    const pulseButton=document.querySelector('[data-studio-impulse]');
    const stateLabel=host.querySelector('[data-studio-state]');
    const hint=host.querySelector('[data-studio-hint]');
    const modeButtons=[...document.querySelectorAll('[data-studio-mode]')];
    if(seedInput) seedInput.value=String(seed);
    const syncing=(updateUrl=true)=>{
      data=sceneData(seed,mode);
      if(seedInput) seedInput.value=String(seed);
      modeButtons.forEach(el=>{
        const active=el.dataset.studioMode===modeNames[mode].toLowerCase();
        el.setAttribute('aria-pressed',String(active));
      });
      if(updateUrl && lab){
        const u=new URL(location.href);
        u.searchParams.set('mode',modeNames[mode].toLowerCase());
        u.searchParams.set('seed',String(seed));
        try { history.replaceState(null,'',u); } catch (_) { /* Previews may use an opaque origin. */ }
      }
      needsDraw=true;
      draw();
      announce(`${modeNames[mode]} sculpture, seed ${seed}`);
    };
    function motionBlock(){
      if(prefersReduced.matches)return 'Reduced motion';
      if(connection?.saveData)return 'Data saving';
      if(root.dataset.motion!=='on')return 'Motion off';
      return '';
    }
    function motionEnabled(){return !holding && !document.hidden && !motionBlock();}
    function allowed(){return visible && motionEnabled();}
    function sync(){
      const blocked=motionBlock(), running=allowed();
      if(pauseButton){
        pauseButton.disabled=!!blocked;
        pauseButton.setAttribute('aria-pressed',String(holding || !!blocked));
        pauseButton.textContent=blocked || (holding?'Resume sculpture':'Pause sculpture');
      }
      if(pulseButton)pulseButton.disabled=!motionEnabled();
      if(!motionEnabled())pendingPulse=false;
      if(stateLabel)stateLabel.textContent=blocked || (holding?'Paused':running?'Live':'Resting');
      if(hint)hint.textContent=running?'Drag to orbit · Tap to send a pulse':'Drag to orbit · Still view';
      if(lab)canvas.setAttribute('aria-label','Interactive sculpture; use left and right arrow keys to rotate, R to regenerate'+(blocked?'':', space to '+(holding?'resume':'pause')));
      // A paused pulse cannot progress. Clear it instead of storing an invisible
      // impulse that unexpectedly returns when motion is enabled later.
      if(!running && energy){energy=0;needsDraw=true;}
      if(running) {
        if(pendingPulse){pendingPulse=false;impulse();}
        if(!frame){last=0;frame=requestAnimationFrame(tick);}
      }
      else { if(frame)cancelAnimationFrame(frame);frame=0;last=0; if(needsDraw)draw(); }
    }
    function togglePause(){
      if(motionBlock())return;
      holding=!holding;sync();
    }
    function resize(){
      const bounds=host.getBoundingClientRect();
      width=Math.round(bounds.width);height=Math.round(bounds.height);
      if(width<1||height<1)return;
      dpr=Math.min(devicePixelRatio||1,mobile()?1.15:1.5);
      const maxPixels=lab?1400000:1000000;
      dpr=Math.min(dpr,Math.sqrt(maxPixels/(width*height)));
      canvas.width=Math.max(1,Math.floor(width*dpr));canvas.height=Math.max(1,Math.floor(height*dpr));
      ctx.setTransform(dpr,0,0,dpr,0,0);
      scale=Math.min(width/(lab?4.15:4.4),height/(lab?3.15:3.2));
      needsDraw=true;draw();
    }
    function project(p){
      const rotated=rotate(p,cameraX+targetY,cameraY+targetX,.03);
      const ratio=6.3/(6.3+rotated[2]);
      const cx=width*(lab?.50:(width<700?.53:.65));
      const cy=height*(lab?.53:.55);
      return {x:cx+rotated[0]*scale*ratio,y:cy+rotated[1]*scale*ratio,z:rotated[2],ratio};
    }
    const base=(time)=>{
      // Transparent sculpture on the homepage, independent theatrical stage in the lab.
      ctx.clearRect(0,0,width,height);
      if(lab){
        const bg=ctx.createRadialGradient(width*.58,height*.4,0,width*.52,height*.5,Math.max(width,height)*.8);
        bg.addColorStop(0,'#27362f');bg.addColorStop(.38,'#111f1e');bg.addColorStop(1,'#080d0e');
        ctx.fillStyle=bg;ctx.fillRect(0,0,width,height);
        const bloom=ctx.createRadialGradient(width*.55,height*.47,0,width*.55,height*.47,scale*2.5);
        bloom.addColorStop(0,'rgba(159,119,65,.14)');bloom.addColorStop(1,'rgba(0,0,0,0)');
        ctx.fillStyle=bloom;ctx.fillRect(0,0,width,height);
      }
      const glow=project([0,0,0]);
      const field=ctx.createRadialGradient(glow.x,glow.y,0,glow.x,glow.y,scale*1.7);
      field.addColorStop(0,lab?'rgba(144,168,112,.18)':'rgba(179,194,139,.10)');
      field.addColorStop(1,'rgba(15,20,18,0)');
      ctx.fillStyle=field;ctx.fillRect(glow.x-scale*1.7,glow.y-scale*1.7,scale*3.4,scale*3.4);
      // Never randomize per frame. Small elements have stable seeded positions.
      const rand=randomGen(seed+17);
      for(let i=0;i<(lab?110:55);i++){
        const xx=rand()*width,yy=rand()*height,r=.35+rand()*1.1;
        ctx.fillStyle=i%6===0?'rgba(225,197,128,.27)':'rgba(191,211,194,.12)';
        ctx.fillRect(xx,yy,r,r);
      }
    };
    function bandAt(b,t,side,time){
      let turns= mode===2?3: mode===3?2:1;
      const u=t*TAU*turns;
      const bend=b.bend*Math.sin(u*2+time*.3+b.phi);
      const twist= (b.twist*t*TAU + b.theta + time*b.speed*.3);
      const r=b.radius+side*b.width*Math.cos(twist)+bend;
      let p=[r*Math.cos(u),r*Math.sin(u),b.lift+side*b.width*Math.sin(twist)+.18*Math.sin(u+b.phi+time*.18)];
      if(mode===2) p=[p[0]*(.9+.13*Math.cos(u)),p[1]*(.78+.24*Math.sin(u*2)),p[2]+side*.1*Math.sin(u*2)];
      p=rotate(p,b.tilt+time*b.speed*.14,b.phi+time*b.speed*.22,b.theta*.3);
      return [p[0]+b.shift,p[1],p[2]];
    }
    function polygons(time){
      const tiles=[];
      const count=mobile()?34:48;
      for(let j=0;j<Math.ceil(data.bands.length*density);j++){
        const b=data.bands[j%data.bands.length];
        for(let i=0;i<count;i++){
          const t0=i/count,t1=(i+1)/count;
          const coords=[project(bandAt(b,t0,-1,time)),project(bandAt(b,t0,1,time)),project(bandAt(b,t1,1,time)),project(bandAt(b,t1,-1,time))];
          const depth=coords.reduce((a,p)=>a+p.z,0)/4;
          const luminosity=.34+.44*(Math.cos(t0*TAU*2+b.phi+time*.14)+1)*.5;
          tiles.push({coords,depth,luminosity,b,t0,j});
        }
      }
      tiles.sort((a,b)=>b.depth-a.depth);
      for(const tile of tiles){
        const {coords,b,luminosity}=tile;
        const c=colors[b.color],cc=colors[(b.color+2)%colors.length];
        ctx.beginPath();ctx.moveTo(coords[0].x,coords[0].y);
        for(let k=1;k<4;k++)ctx.lineTo(coords[k].x,coords[k].y);
        ctx.closePath();
        ctx.fillStyle=mixColor([24,29,27],c,luminosity,lab?.83:.65);
        ctx.fill();
        ctx.strokeStyle=mixColor(c,cc,.45, .16+luminosity*.21);
        ctx.lineWidth=.6;ctx.stroke();
      }
    }
    function cores(time){
      const center=project([0,0,.1]);
      const radius=scale*(mode===1?.24:.37)*center.ratio;
      const gr=ctx.createRadialGradient(center.x-radius*.36,center.y-radius*.42,2,center.x,center.y,radius);
      gr.addColorStop(0,'rgba(242,228,179,.56)');
      gr.addColorStop(.13,'rgba(124,179,159,.34)');
      gr.addColorStop(.54,'rgba(39,99,92,.28)');
      gr.addColorStop(1,'rgba(180,203,168,.07)');
      ctx.fillStyle=gr;ctx.beginPath();ctx.arc(center.x,center.y,radius,0,TAU);ctx.fill();
      ctx.strokeStyle='rgba(216,225,192,.34)';ctx.lineWidth=1.2;ctx.stroke();
      for(let i=0;i<3;i++){
        ctx.save();ctx.translate(center.x,center.y);
        ctx.rotate(.48*i+time*(i%2?-.045:.032));
        ctx.beginPath();ctx.ellipse(0,0,radius*(1.25+i*.16),radius*(.25+i*.06),0,0,TAU);
        ctx.strokeStyle=`rgba(${i===1?'204,163,106':'143,192,164'},${lab?.38:.26})`;
        ctx.lineWidth=1.7;ctx.stroke();ctx.restore();
      }
      const tiny=ctx.createRadialGradient(center.x,center.y,0,center.x,center.y,radius*.4);
      tiny.addColorStop(0,'rgba(246,220,152,.40)');tiny.addColorStop(1,'rgba(246,220,152,0)');
      ctx.fillStyle=tiny;ctx.beginPath();ctx.arc(center.x,center.y,radius*.45,0,TAU);ctx.fill();
    }
    function fiberAt(f,t,time){
      const u=t*TAU*f.spiral + f.phase;
      let r=f.radius*(.82+.18*Math.sin(t*TAU+f.phase+time*.13));
      const height=f.elevation + .6*Math.sin(u*f.slope + time*.28);
      return [r*Math.cos(u+time*.025),height,r*Math.sin(u+time*.025)];
    }
    function filaments(time){
      ctx.save();ctx.globalCompositeOperation='lighter';
      const n=Math.min(data.fibers.length, Math.floor(data.fibers.length*density));
      for(let i=0;i<n;i++){
        const f=data.fibers[i];
        const steps=mobile()?38:60;
        ctx.beginPath();
        for(let k=0;k<=steps;k++){
          const q=project(fiberAt(f,k/steps,time));
          if(k===0)ctx.moveTo(q.x,q.y);else ctx.lineTo(q.x,q.y);
        }
        const c=f.color===3?'125,184,212':'238,194,122';
        ctx.lineWidth=i%5===0?1.3:.55;
        ctx.strokeStyle=`rgba(${c},${f.opacity*(lab?.62:.5)})`;ctx.stroke();
        const t=(time*f.speed*.032+(i*.6180339)%1)%1;
        const p=project(fiberAt(f,t,time));
        const glow=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,9);
        glow.addColorStop(0,`rgba(255,236,188,${lab?.83:.71})`);
        glow.addColorStop(.22,`rgba(238,193,124,.45)`);
        glow.addColorStop(1,'rgba(238,193,124,0)');
        ctx.fillStyle=glow;ctx.beginPath();ctx.arc(p.x,p.y,9,0,TAU);ctx.fill();
      }
      ctx.restore();
    }
    function satellites(time){
      for(let i=0;i<data.satellites.length;i++){
        const s=data.satellites[i],angle=s.phase+time*s.speed;
        const p=project([s.radius*Math.cos(angle),s.height+.24*Math.sin(angle*2),s.radius*Math.sin(angle)]);
        const rad=s.size*p.ratio+(energy*.7);
        const gl=ctx.createRadialGradient(p.x-rad*.28,p.y-rad*.3,0,p.x,p.y,rad*2.4);
        gl.addColorStop(0,'rgba(249,233,191,.88)');gl.addColorStop(.25,'rgba(195,206,171,.58)');gl.addColorStop(1,'rgba(188,210,178,0)');
        ctx.fillStyle=gl;ctx.beginPath();ctx.arc(p.x,p.y,rad*2.4,0,TAU);ctx.fill();
      }
    }
    function draw(){
      if(width<1||height<1)return;
      const t=playTime;
      base(t);
      // Transformations are genuine computed 3D geometry, not animated artwork.
      polygons(t);cores(t);filaments(t);satellites(t);
      if(energy>0){
        const radius=(1-energy)*scale*2.6;
        const center=project([0,0,0]);
        ctx.strokeStyle=`rgba(230,199,143,${energy*.48})`;
        ctx.lineWidth=2.3;ctx.beginPath();ctx.ellipse(center.x,center.y,radius,radius*.56,0,0,TAU);ctx.stroke();
      }
      needsDraw=false;
    }
    function tick(now){
      frame=0;
      if(!allowed()){sync();return;}
      if(!last)last=now;
      const delta=now-last;
      const goal=mobile()?1000/22:1000/30;
      if(delta>=goal){
        playTime+=Math.min(delta,100)/1000*intensity;
        energy=Math.max(0,energy-delta*.0007);
        targetX=lerp(targetX,0,.018);
        targetY=lerp(targetY,0,.018);
        last=now;draw();
      }
      frame=requestAnimationFrame(tick);
    }
    function impulse(ev){
      if(!allowed())return;
      energy=1;
      if(ev&&ev.clientX!=null){
        const r=host.getBoundingClientRect();
        targetX=clamp(((ev.clientX-r.left)/r.width-.5)*.4,-.3,.3);
        targetY=clamp(((ev.clientY-r.top)/r.height-.5)*.4,-.3,.3);
      }
      draw();
    }
    function stageInView(){
      const box=host.getBoundingClientRect();
      return box.width>0 && box.height>0 && box.bottom>0 && box.top<window.innerHeight;
    }
    function requestPulse(){
      if(!motionEnabled())return;
      if(stageInView()){visible=true;impulse();sync();return;}
      // The mobile action panel sits below the sculpture. An explicit request
      // returns to the artwork without moving keyboard focus. Observation then
      // delivers the pulse once its drawing surface is visible.
      pendingPulse=true;
      host.scrollIntoView({behavior:'instant',block:'center',inline:'nearest'});
      if(!('IntersectionObserver' in window)){visible=stageInView();sync();}
    }
    if(lab){
      modeButtons.forEach(el=>el.addEventListener('click',()=>{
        const idx=modeNames.findIndex(name=>name.toLowerCase()===el.dataset.studioMode);
        if(idx<0)return;mode=idx;syncing();
      }));
      document.querySelector('[data-studio-reroll]')?.addEventListener('click',()=>{seed=randomSeed();syncing();});
      pulseButton?.addEventListener('click',requestPulse);
      pauseButton?.addEventListener('click',togglePause);
      seedInput?.addEventListener('change',()=>{
        const n=Number(seedInput.value);
        if(!Number.isSafeInteger(n)||n<0||n>4294967295){seedInput.value=String(seed);announce('Use a seed between 0 and 4294967295');return;}
        seed=n;syncing();
      });
      intensityInput?.addEventListener('input',()=>{intensity=Number(intensityInput.value)||1;});
      densityInput?.addEventListener('input',()=>{density=Number(densityInput.value)||1;needsDraw=true;draw();});
      document.querySelector('[data-studio-share]')?.addEventListener('click',async()=>{
        const url=new URL(location.href);url.searchParams.set('mode',modeNames[mode].toLowerCase());url.searchParams.set('seed',String(seed));
        try {await navigator.clipboard.writeText(url.href);announce('Share link copied');}
        catch(_) {announce('Copy this address: '+url.href);}
      });
      document.querySelector('[data-studio-capture]')?.addEventListener('click',()=>{
        try {
          canvas.toBlob(blob=>{
            if(!blob){announce('Unable to save image');return;}
            const url=URL.createObjectURL(blob),a=document.createElement('a');
            a.href=url;a.download=`suadtl-${modeNames[mode].toLowerCase()}-${seed}.png`;a.click();
            setTimeout(()=>URL.revokeObjectURL(url),2000);
            announce('Sculpture image prepared');
          },'image/png');
        }catch(_){announce('Unable to save image');}
      });
      host.addEventListener('pointerdown',e=>{
        if(e.target!==canvas)return;
        drag={x:e.clientX,y:e.clientY,originX:targetX,originY:targetY,moved:false};
        host.setPointerCapture?.(e.pointerId);
        touchDown=performance.now();
      });
      host.addEventListener('pointermove',e=>{
        if(!drag)return;
        const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
        if(Math.abs(dx)+Math.abs(dy)>6)drag.moved=true;
        targetX=clamp(drag.originX+dx/Math.max(320,width)*1.1,-.7,.7);
        targetY=clamp(drag.originY+dy/Math.max(300,height)*1.1,-.5,.5);
        draw();
      },{passive:true});
      const end=e=>{if(!drag)return;if(!drag.moved)impulse(e);drag=null;};
      host.addEventListener('pointerup',end);host.addEventListener('pointercancel',()=>{drag=null;});
      document.addEventListener('keydown',e=>{
        if(document.activeElement!==canvas)return;
        if(e.key===' '){e.preventDefault();togglePause();}
        if(e.key.toLowerCase()==='r'){seed=randomSeed();syncing();}
        if(e.key==='ArrowLeft'){e.preventDefault();targetX=clamp(targetX-.07,-.7,.7);draw();}
        if(e.key==='ArrowRight'){e.preventDefault();targetX=clamp(targetX+.07,-.7,.7);draw();}
      });
    }else{
      // Hero points to the full lab; pointer subtly alters the generative assembly.
      host.addEventListener('pointermove',e=>{
        if(matchMedia('(hover: hover) and (pointer: fine)').matches && allowed()){
          const r=host.getBoundingClientRect();
          targetX=clamp(((e.clientX-r.left)/r.width-.5)*.12,-.08,.08);
          targetY=clamp(((e.clientY-r.top)/r.height-.5)*.1,-.06,.06);
        }
      },{passive:true});
    }
    new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['data-motion']});
    prefersReduced.addEventListener('change',()=>{needsDraw=true;sync();});
    connection?.addEventListener?.('change',sync);
    document.addEventListener('visibilitychange',sync);
    window.addEventListener('pagehide',()=>{pendingPulse=false;visible=false;sync();});
    window.addEventListener('pageshow',()=>{visible=stageInView();sync();});
    if('IntersectionObserver' in window){
      new IntersectionObserver(entries=>{visible=entries[0].isIntersecting && entries[0].intersectionRatio>0;sync();},{threshold:[0,.001]}).observe(host);
    }else visible=true;
    if('ResizeObserver' in window)new ResizeObserver(resize).observe(host);
    else window.addEventListener('resize',resize,{passive:true});
    syncing(false);resize();sync();
  }
  document.querySelectorAll('canvas[data-generative-scene]').forEach(create);
})();
