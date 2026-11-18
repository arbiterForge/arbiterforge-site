/* Interactive illustrations only. Real behavior belongs to the linked source projects. */
(()=>{'use strict';
const selected=(root,attribute,value)=>root.querySelectorAll('['+attribute+']').forEach(b=>b.setAttribute('aria-pressed',String(b.getAttribute(attribute)===value)));
const gate=document.querySelector('[data-gate-demo]');
if(gate){
const cases={
docs:['Small docs lane','Editorial checks and appropriate review. A prose edit does not have the same test requirement as feature code.','Scoped path'],
feature:['Regression-test-first feature','Require the failing test, minimal change, focused proof, full verification, and review before an authorized commit.','Requires evidence'],
security:['Security-sensitive feature','A full specification and review path. Missing decisions or blocking security findings stop dependent work until addressed.','Blocking gate']};
const choose=k=>{const c=cases[k];if(!c)return;selected(gate,'data-gate',k);gate.querySelector('[data-gate-title]').textContent=c[0];gate.querySelector('[data-gate-copy]').textContent=c[1];gate.querySelector('[data-gate-verdict]').textContent=c[2];};
gate.querySelectorAll('[data-gate]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.gate)));choose('feature');
}
const sim=document.querySelector('[data-sim-demo]');
if(sim){
const cases={
app:['App portal','Consumes Identity and Monitoring. Two outgoing dependencies cross network boundaries.'],
identity:['Identity','Provides identity to the App portal and consumes the fictional SSO provider.'],
monitor:['Monitoring','Provides an operational service consumed by the App portal. Incoming links belong to the consuming service.']};
const choose=k=>{const c=cases[k];if(!c)return;sim.dataset.focus=k;selected(sim,'data-sim-focus',k);sim.querySelector('[data-sim-title]').textContent=c[0];sim.querySelector('[data-sim-copy]').textContent=c[1];};
sim.querySelectorAll('[data-sim-focus]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.simFocus)));choose('app');
}
const shot=document.querySelector('[data-trajectory-demo]');
if(shot){
const angle=shot.querySelector('[data-angle]'),power=shot.querySelector('[data-power]'),wind=shot.querySelector('[data-wind]');
const path=shot.querySelector('[data-shot-path]'),impact=shot.querySelector('[data-impact]');
const render=()=>{
const a=Number(angle.value)*Math.PI/180,p=Number(power.value),w=Number(wind.value);
shot.querySelector('[data-angle-output]').textContent=angle.value+'°';
shot.querySelector('[data-power-output]').textContent=power.value+'%';
shot.querySelector('[data-wind-output]').textContent=(w>0?'+':'')+wind.value;
const ox=126,oy=244,v=6.5+p*.15,vx=Math.cos(a)*v,vy=Math.sin(a)*v,g=.54,ground=270;
let d='M '+ox+' '+oy,x=ox,y=oy;
for(let t=1;t<=95;t++){x=ox+vx*t+.045*w*t*t;y=oy-vy*t+.5*g*t*t;if(x>=800){x=800;d+=' L '+x+' '+Math.max(0,y).toFixed(1);break}
if(y>=ground){y=ground;d+=' L '+x.toFixed(1)+' '+y;break}
d+=' L '+x.toFixed(1)+' '+y.toFixed(1)}
path.setAttribute('d',d);impact.setAttribute('cx',String(Math.min(800,Math.max(0,x))));impact.setAttribute('cy',String(y));
shot.querySelector('[data-range-title]').textContent='Impact about '+Math.max(0,Math.round(x-ox))+' illustration units away';
};
[angle,power,wind].forEach(n=>n.addEventListener('input',render));render();
}
})();