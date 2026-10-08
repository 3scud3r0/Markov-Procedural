/* CPU renderer. No WebGL, Babylon, GPU, or external dependency required. */
'use strict';
class CanvasSceneEngine {
 constructor(canvas,onChange){
  this.canvas=canvas;this.ctx=canvas.getContext('2d');
  if(!this.ctx)throw Error('Canvas 2D indisponível neste navegador.');
  this.onChange=onChange;this.objects=[];this.selected=-1;this.mode='move';this.reset();
  this.resizeObserver=new ResizeObserver(()=>this.draw());this.resizeObserver.observe(canvas);
  canvas.addEventListener('contextmenu',e=>e.preventDefault());
  canvas.addEventListener('pointerdown',e=>{
   const point=this.point(e),hit=this.pick(point);
   const editing=e.button===0&&hit!==null&&this.mode!=='none';
   if(e.button===0)this.selected=hit===null?-1:hit;
   this.drag={x:point[0],y:point[1],editing};canvas.setPointerCapture(e.pointerId);this.draw();
  });
  canvas.addEventListener('pointermove',e=>{
   if(!this.drag)return;
   const point=this.point(e),dx=point[0]-this.drag.x,dy=point[1]-this.drag.y;
   this.drag.x=point[0];this.drag.y=point[1];
   if(this.drag.editing&&this.selected>=0){
    const transform=this.objects[this.selected].transform;
    if(this.mode==='move'){
     const factor=this.radius/this.height;
     for(let k=0;k<3;k++)transform.position[k]+=factor*(dx*this.right[k]-dy*this.up[k]);
    }else if(this.mode==='rotate'){transform.rotation[1]+=dx*.012;transform.rotation[0]+=dy*.012;}
    else if(this.mode==='scale'){const factor=Math.exp((dx-dy)*.007);transform.scaling=transform.scaling.map(n=>Math.max(.02,Math.min(30,n*factor)));}
   }else{this.alpha-=dx*.007;this.elevation=Math.max(.05,Math.min(1.45,this.elevation+dy*.005));}
   this.draw();
  });
  const stop=()=>{this.drag=null;};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
  canvas.addEventListener('wheel',e=>{e.preventDefault();this.radius=Math.max(3,Math.min(90,this.radius*Math.exp(e.deltaY*.001)));this.draw();},{passive:false});
 }
 reset(){this.alpha=-Math.PI/2.3;this.elevation=.45;this.radius=24;this.target=[0,2.5,0];if(this.ctx)this.draw();}
 point(event){const r=this.canvas.getBoundingClientRect();return[event.clientX-r.left,event.clientY-r.top];}
 load(data){
  this.objects=structuredClone(data.objects).map(object=>{
   if(!object.transform){
    if(object.kind==='branch'){
     const direction=object.end.map((v,k)=>v-object.start[k]),length=Math.hypot(...direction);
     object.transform={position:object.end.map((v,k)=>(v+object.start[k])/2),
      rotation:[Math.atan2(direction[2],direction[1]),0,length?-Math.asin(Math.max(-1,Math.min(1,direction[0]/length))):0],scaling:[1,1,1]};
    }else object.transform={position:[...object.position],rotation:[0,0,0],scaling:[1,.65,1]};
   }
   return object;
  });
  this.selected=-1;this.reset();this.onChange(this.objects.length);
 }
 export(){return{schema:'markovjunior.scene3d/1',objects:structuredClone(this.objects)};}
 remove(){if(this.selected<0)return;this.objects.splice(this.selected,1);this.selected=-1;this.draw();this.onChange(this.objects.length);}
 rotate(point,rotation){
  // Babylon-compatible yaw/pitch/roll: roll Z, pitch X, then yaw Y.
  let[x,y,z]=point;const[pitch,yaw,roll]=rotation;
  [x,y]=[x*Math.cos(roll)-y*Math.sin(roll),x*Math.sin(roll)+y*Math.cos(roll)];
  [y,z]=[y*Math.cos(pitch)-z*Math.sin(pitch),y*Math.sin(pitch)+z*Math.cos(pitch)];
  [x,z]=[x*Math.cos(yaw)+z*Math.sin(yaw),-x*Math.sin(yaw)+z*Math.cos(yaw)];return[x,y,z];
 }
 world(point,transform){return this.rotate(point.map((v,k)=>v*transform.scaling[k]),transform.rotation).map((v,k)=>v+transform.position[k]);}
 project(point){
  const relative=point.map((v,k)=>v-this.eye[k]),dot=v=>relative.reduce((sum,n,k)=>sum+n*v[k],0);
  const depth=dot(this.forward);if(depth<=.1)return null;
  const scale=this.height*1.2/depth;return[this.width/2+dot(this.right)*scale,this.height/2-dot(this.up)*scale,depth,scale];
 }
 draw(){
  const r=this.canvas.getBoundingClientRect();this.width=r.width||800;this.height=r.height||570;
  const dpr=Math.min(window.devicePixelRatio||1,2);this.canvas.width=Math.round(this.width*dpr);this.canvas.height=Math.round(this.height*dpr);const ctx=this.ctx;ctx.setTransform(dpr,0,0,dpr,0,0);
  const ca=Math.cos(this.alpha),sa=Math.sin(this.alpha),ce=Math.cos(this.elevation),se=Math.sin(this.elevation);
  this.eye=this.target.map((v,k)=>v+[ca*ce,se,sa*ce][k]*this.radius);
  this.forward=[-ca*ce,-se,-sa*ce];this.right=[-sa,0,ca];this.up=[-ca*se,ce,-sa*se];
  const background=ctx.createLinearGradient(0,0,0,this.height);background.addColorStop(0,'#0c1321');background.addColorStop(1,'#182d34');ctx.fillStyle=background;ctx.fillRect(0,0,this.width,this.height);
  const ground=[[-15,0,-15],[15,0,-15],[15,0,15],[-15,0,15]].map(p=>this.project(p));
  if(ground.every(Boolean)){ctx.beginPath();ground.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle='#244437';ctx.fill();}
  this.projected=[];
  for(let index=0;index<this.objects.length;index++){
   const object=this.objects[index],t=object.transform;
   if(object.kind==='branch'){
    const length=Math.hypot(...object.end.map((v,k)=>v-object.start[k]));
    const a=this.project(this.world([0,-length/2,0],t)),b=this.project(this.world([0,length/2,0],t));
    if(a&&b)this.projected.push({index,kind:'branch',a,b,depth:(a[2]+b[2])/2,radius:Math.max(1,object.radius*(Math.abs(t.scaling[0])+Math.abs(t.scaling[2]))/2*(a[3]+b[3])/2),color:object.color});
   }else{const p=this.project(t.position);if(p)this.projected.push({index,kind:'leaf',p,depth:p[2],radius:object.radius*p[3],scaling:t.scaling,rotation:t.rotation,color:object.color});}
  }
  this.projected.sort((a,b)=>b.depth-a.depth);
  for(const obj of this.projected){
   if(obj.kind==='branch'){ctx.beginPath();ctx.moveTo(obj.a[0],obj.a[1]);ctx.lineTo(obj.b[0],obj.b[1]);ctx.lineWidth=obj.radius*2;ctx.lineCap='round';ctx.strokeStyle=obj.index===this.selected?'#ffffff':obj.color;ctx.stroke();}
   else{ctx.save();ctx.translate(obj.p[0],obj.p[1]);ctx.rotate(obj.rotation[2]);ctx.beginPath();ctx.ellipse(0,0,Math.max(.2,obj.radius*Math.abs(obj.scaling[0])),Math.max(.2,obj.radius*Math.abs(obj.scaling[1])),0,0,Math.PI*2);ctx.fillStyle=obj.color;ctx.fill();if(obj.index===this.selected){ctx.strokeStyle='#ffffff';ctx.lineWidth=2;ctx.stroke();}ctx.restore();}
  }
  if(this.selected>=0){ctx.fillStyle='#d5f4e3';ctx.font='12px sans-serif';ctx.fillText('Selecionado · '+({move:'arraste para mover',rotate:'arraste para girar',scale:'arraste para escalar',none:'sem transformação'}[this.mode]),18,this.height-20);}
 }
 pick(point){
  for(let k=this.projected.length-1;k>=0;k--){const obj=this.projected[k];
   if(obj.kind==='leaf'){const rx=Math.max(6,obj.radius*Math.abs(obj.scaling[0])),ry=Math.max(6,obj.radius*Math.abs(obj.scaling[1]));if(((point[0]-obj.p[0])/rx)**2+((point[1]-obj.p[1])/ry)**2<=1)return obj.index;}
   else{const dx=obj.b[0]-obj.a[0],dy=obj.b[1]-obj.a[1],length=dx*dx+dy*dy;const t=length?Math.max(0,Math.min(1,((point[0]-obj.a[0])*dx+(point[1]-obj.a[1])*dy)/length)):0;if(Math.hypot(point[0]-obj.a[0]-t*dx,point[1]-obj.a[1]-t*dy)<=Math.max(6,obj.radius))return obj.index;}
  }return null;
 }
 dispose(){this.resizeObserver.disconnect();}
}
window.CanvasSceneEngine=CanvasSceneEngine;
