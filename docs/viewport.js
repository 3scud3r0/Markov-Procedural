'use strict';
/* Shared scene contract for Babylon.js and an independent CPU renderer. */
(()=>{
const V=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],unit=a=>{const l=Math.hypot(...a)||1;return a.map(v=>v/l);};
function rotate(p,r){let[x,y,z]=p;const[a,b,c]=r;[x,y]=[x*Math.cos(c)-y*Math.sin(c),x*Math.sin(c)+y*Math.cos(c)];[y,z]=[y*Math.cos(a)-z*Math.sin(a),y*Math.sin(a)+z*Math.cos(a)];[x,z]=[x*Math.cos(b)+z*Math.sin(b),-x*Math.sin(b)+z*Math.cos(b)];return[x,y,z];}
function world(p,o){return rotate(p.map((v,i)=>v*o.scaling[i]),o.rotation).map((v,i)=>v+o.position[i]);}
function shade(hex,amount){const rgb=hex.match(/\w\w/g).map(v=>parseInt(v,16));return'#'+rgb.map(v=>Math.max(0,Math.min(255,Math.round(v*amount))).toString(16).padStart(2,'0')).join('');}
function geometry(o){
 const g=o.geometry,v=[],f=[];const quad=(a,b,c,d)=>f.push([a,b,c],[a,c,d]);
 if(o.kind==='mesh')return{v:g.vertices,f:g.faces};
 if(o.kind==='line')return{v:g.points,lines:true};
 if(o.kind==='plane'){const w=g.width/2,d=g.depth/2;return{v:[[-w,0,-d],[w,0,-d],[w,0,d],[-w,0,d]],f:[[0,2,1],[0,3,2]]};}
 if(o.kind==='box'){const[x,y,z]=g.size.map(n=>n/2);v.push([-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]);quad(0,3,2,1);quad(4,5,6,7);quad(0,1,5,4);quad(3,7,6,2);quad(0,4,7,3);quad(1,2,6,5);}
 if(o.kind==='cylinder'||o.kind==='cone'){
  const n=12,h=g.height/2;for(let j=0;j<2;j++)for(let i=0;i<n;i++){const a=i*Math.PI*2/n,r=o.kind==='cone'&&j?0:g.radius;v.push([Math.cos(a)*r,j?h:-h,Math.sin(a)*r]);}
  v.push([0,-h,0],[0,h,0]);for(let i=0;i<n;i++){const b=(i+1)%n;quad(i,b,b+n,i+n);f.push([2*n,b,i],[2*n+1,i+n,b+n]);}
 }
 if(o.kind==='torus'){
  const n=24,m=6;for(let i=0;i<n;i++)for(let j=0;j<m;j++){const a=i*Math.PI*2/n,b=j*Math.PI*2/m,r=g.radius+Math.cos(b)*g.thickness/2;v.push([r*Math.cos(a),Math.sin(b)*g.thickness/2,r*Math.sin(a)]);}
  for(let i=0;i<n;i++)for(let j=0;j<m;j++)quad(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m);
 }
 return{v,f};
}
function validate(data){
 if(data?.schema!=='markov.scene/1'||!Array.isArray(data.objects)||data.objects.length>5000)throw Error('Cena inválida: contrato markov.scene/1, até 5.000 objetos.');
 const vector=a=>Array.isArray(a)&&a.length===3&&a.every(n=>Number.isFinite(n)&&Math.abs(n)<=1e6),positive=n=>Number.isFinite(n)&&n>0&&n<=10000;
 const ids=new Set();let vertices=0,faces=0;
 for(const o of data.objects){
  if(typeof o.id!=='string'||ids.has(o.id)||!/^#[0-9a-f]{6}$/i.test(o.color)||![o.position,o.rotation,o.scaling].every(vector))throw Error('Objeto inválido ou identificador duplicado.');ids.add(o.id);
  const g=o.geometry;
  if(!g||!['sphere','box','cylinder','cone','torus','plane','line','mesh'].includes(o.kind))throw Error('Tipo de geometria não suportado.');
  if(['sphere','cylinder','cone','torus'].includes(o.kind)&&!positive(g.radius))throw Error('Raio inválido.');
  if(['cylinder','cone'].includes(o.kind)&&!positive(g.height))throw Error('Altura inválida.');
  if(o.kind==='torus'&&(!positive(g.thickness)||g.thickness>=2*g.radius))throw Error('Espessura inválida.');
  if(o.kind==='box'&&(!vector(g.size)||!g.size.every(positive)))throw Error('Dimensões inválidas.');
  if(o.kind==='plane'&&(!positive(g.width)||!positive(g.depth)))throw Error('Plano inválido.');
  if(o.kind==='line'&&(!Array.isArray(g.points)||g.points.length<2||g.points.length>10000||!g.points.every(vector)||!positive(g.width)))throw Error('Linha inválida.');
  if(o.kind==='mesh'){
   if(!Array.isArray(g.vertices)||g.vertices.length<3||!g.vertices.every(vector)||!Array.isArray(g.faces)||!g.faces.every(f=>Array.isArray(f)&&f.length===3&&f.every(i=>Number.isInteger(i)&&i>=0&&i<g.vertices.length)))throw Error('Malha inválida.');
   vertices+=g.vertices.length;faces+=g.faces.length;
  }
 }
 if(vertices>100000||faces>150000)throw Error('Cena excede o orçamento de malhas: 100 mil vértices / 150 mil triângulos.');
 if(data.background&&!/^#[0-9a-f]{6}$/i.test(data.background)||data.ground_color&&!/^#[0-9a-f]{6}$/i.test(data.ground_color))throw Error('Cor de cena inválida.');
 if(data.camera){if(!vector(data.camera.target)||!positive(data.camera.radius)||!Number.isFinite(data.camera.alpha)||!Number.isFinite(data.camera.elevation))throw Error('Câmera inválida.');}
}
class CPUView{
 constructor(canvas,onSelect,onEdit){
  this.canvas=canvas;this.ctx=canvas.getContext('2d');if(!this.ctx)throw Error('Canvas 2D indisponível.');this.onSelect=onSelect;this.onEdit=onEdit;this.mode='none';this.selected=null;this.data={objects:[]};this.cache=new Map();this.reset();
  this.observer=new ResizeObserver(()=>this.draw());this.observer.observe(canvas);canvas.addEventListener('contextmenu',e=>e.preventDefault());
  canvas.addEventListener('pointerdown',e=>{canvas.focus();const p=this.point(e),hit=this.pick(p);if(e.button===0){this.selected=hit;this.onSelect(hit);}this.drag={x:p[0],y:p[1],edit:e.button===0&&!!hit&&this.mode!=='none'};canvas.setPointerCapture(e.pointerId);this.draw();});
  canvas.addEventListener('pointermove',e=>{if(!this.drag)return;const p=this.point(e),dx=p[0]-this.drag.x,dy=p[1]-this.drag.y;this.drag.x=p[0];this.drag.y=p[1];const o=this.data.objects.find(n=>n.id===this.selected);
   if(this.drag.edit&&o){if(this.mode==='move'){const k=this.radius/this.height;for(let i=0;i<3;i++)o.position[i]+=k*(dx*this.right[i]-dy*this.up[i]);}else if(this.mode==='rotate'){o.rotation[1]+=dx*.012;o.rotation[0]+=dy*.012;}else if(this.mode==='scale'){const k=Math.exp((dx-dy)*.007);o.scaling=o.scaling.map(n=>Math.max(.02,Math.min(30,n*k)));}this.onEdit(o);}else{this.alpha-=dx*.007;this.elevation=Math.max(.02,Math.min(1.5,this.elevation+dy*.005));}this.draw();});
  const stop=()=>{this.drag=null;};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);canvas.addEventListener('wheel',e=>{e.preventDefault();this.radius=Math.max(2,Math.min(200,this.radius*Math.exp(e.deltaY*.001)));this.draw();},{passive:false});
 }
 reset(camera){camera=camera||this.data.camera||{};this.alpha=camera.alpha??-1.15;this.elevation=camera.elevation??.5;this.radius=camera.radius??24;this.target=camera.target||[0,2,0];if(this.ctx)this.draw();}
 point(e){const r=this.canvas.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];}
 setScene(data,reset){this.data=structuredClone(data);const ids=new Set(data.objects.map(o=>o.id));for(const id of this.cache.keys())if(!ids.has(id))this.cache.delete(id);if(!ids.has(this.selected))this.selected=null;if(reset)this.reset(data.camera);else this.draw();}
 project(p){const r=V(p,this.eye),depth=dot(r,this.forward);if(depth<=.05)return null;const scale=this.height*1.25/depth;return[this.width/2+dot(r,this.right)*scale,this.height/2-dot(r,this.up)*scale,depth,scale];}
 draw(){
  const r=this.canvas.getBoundingClientRect();this.width=r.width||800;this.height=r.height||500;const dpr=Math.min(devicePixelRatio||1,2);this.canvas.width=Math.round(this.width*dpr);this.canvas.height=Math.round(this.height*dpr);const c=this.ctx;c.setTransform(dpr,0,0,dpr,0,0);c.fillStyle=this.data.background||'#10141d';c.fillRect(0,0,this.width,this.height);
  const ca=Math.cos(this.alpha),sa=Math.sin(this.alpha),ce=Math.cos(this.elevation),se=Math.sin(this.elevation);this.eye=this.target.map((v,i)=>v+[ca*ce,se,sa*ce][i]*this.radius);this.forward=[-ca*ce,-se,-sa*ce];this.right=[-sa,0,ca];this.up=[-ca*se,ce,-sa*se];
  if(this.data.ground!==false){const s=(this.data.ground_size||40)/2,p=[[-s,-.02,-s],[s,-.02,-s],[s,-.02,s],[-s,-.02,s]].map(v=>this.project(v));if(p.every(Boolean)){c.beginPath();p.forEach((a,i)=>i?c.lineTo(a[0],a[1]):c.moveTo(a[0],a[1]));c.closePath();c.fillStyle=this.data.ground_color||'#1b2329';c.fill();}c.strokeStyle='#ffffff09';c.lineWidth=1;for(let i=-20;i<=20;i+=2){for(const ends of [[[-20,0,i],[20,0,i]],[[i,0,-20],[i,0,20]]]){const[a,b]=ends.map(v=>this.project(v));if(a&&b){c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}}}}
  const commands=[],light=unit([-.4,.8,-.3]);
  for(const o of this.data.objects){if(!o.visible)continue;
   if(o.kind==='sphere'){const p=this.project(o.position);if(p)commands.push({kind:'sphere',o,p,depth:p[2],rx:Math.max(.5,o.geometry.radius*p[3]*Math.abs(o.scaling[0])),ry:Math.max(.5,o.geometry.radius*p[3]*Math.abs(o.scaling[1]))});continue;}
   const signature=JSON.stringify([o.kind,o.geometry]);let entry=this.cache.get(o.id);if(!entry||entry.signature!==signature){entry={signature,geometry:geometry(o)};this.cache.set(o.id,entry);}const g=entry.geometry,points=g.v.map(p=>world(p,o)),projected=points.map(p=>this.project(p));
   if(g.lines){for(let i=1;i<projected.length;i++){const a=projected[i-1],b=projected[i];if(a&&b)commands.push({kind:'line',o,a,b,depth:(a[2]+b[2])/2,width:Math.max(1,o.geometry.width*(a[3]+b[3])/2)});}continue;}
   for(const face of g.f){const p=face.map(i=>projected[i]);if(!p.every(Boolean))continue;const n=unit(cross(V(points[face[1]],points[face[0]]),V(points[face[2]],points[face[0]]))),brightness=.5+.5*Math.abs(dot(n,light));commands.push({kind:'triangle',o,p,depth:p.reduce((s,a)=>s+a[2],0)/3,color:shade(o.color,brightness)});}
  }
  commands.sort((a,b)=>b.depth-a.depth);this.projected=commands;
  for(const cmd of commands){
   if(cmd.kind==='sphere'){const {p,rx,ry,o}=cmd;c.save();c.translate(p[0],p[1]);c.rotate(o.rotation[2]);c.scale(rx,ry);const gradient=c.createRadialGradient(-.32,-.35,.02,0,0,1);gradient.addColorStop(0,shade(o.color,1.18));gradient.addColorStop(.6,o.color);gradient.addColorStop(1,shade(o.color,.48));c.beginPath();c.arc(0,0,1,0,Math.PI*2);c.fillStyle=gradient;c.fill();if(o.id===this.selected){c.strokeStyle='#d6ef9e';c.lineWidth=1.5/Math.max(rx,ry);c.stroke();}c.restore();}
   else if(cmd.kind==='line'){c.beginPath();c.moveTo(cmd.a[0],cmd.a[1]);c.lineTo(cmd.b[0],cmd.b[1]);c.lineCap='round';c.lineWidth=cmd.width;c.strokeStyle=cmd.o.id===this.selected?'#d6ef9e':cmd.o.color;c.stroke();}
   else{c.beginPath();cmd.p.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();c.fillStyle=cmd.color;c.fill();if(this.wireframe||cmd.o.id===this.selected){c.strokeStyle=cmd.o.id===this.selected?'#d6ef9e99':'#00000030';c.lineWidth=.6;c.stroke();}}
  }
 }
 pick(p){for(let i=(this.projected?.length||0)-1;i>=0;i--){const cmd=this.projected[i];if(cmd.kind==='sphere'){if(((p[0]-cmd.p[0])/Math.max(6,cmd.rx))**2+((p[1]-cmd.p[1])/Math.max(6,cmd.ry))**2<=1)return cmd.o.id;}else if(cmd.kind==='triangle'){const[a,b,c]=cmd.p;const sign=(p,a,b)=>(p[0]-b[0])*(a[1]-b[1])-(a[0]-b[0])*(p[1]-b[1]);const s=[sign(p,a,b),sign(p,b,c),sign(p,c,a)];if(!(s.some(n=>n<0)&&s.some(n=>n>0)))return cmd.o.id;}else{const dx=cmd.b[0]-cmd.a[0],dy=cmd.b[1]-cmd.a[1],l=dx*dx+dy*dy,t=l?Math.max(0,Math.min(1,((p[0]-cmd.a[0])*dx+(p[1]-cmd.a[1])*dy)/l)):0;if(Math.hypot(p[0]-cmd.a[0]-t*dx,p[1]-cmd.a[1]-t*dy)<Math.max(5,cmd.width/2))return cmd.o.id;}}return null;}
 dispose(){this.observer.disconnect();}
}
class StudioViewport{
 constructor(container,onSelect,onEdit,onRenderer){this.container=container;this.onSelect=onSelect;this.onEdit=onEdit;this.onRenderer=onRenderer;this.meshes=new Map();this.materials=new Map();this.data={schema:'markov.scene/1',objects:[]};this.mode='none';this.init('auto');}
 init(mode){
  this.cpu?.dispose();this.cpu=null;this.engine?.dispose();this.engine=null;this.scene=null;this.meshes.clear();this.materials.clear();this.selected=null;
  this.container.querySelector('canvas')?.remove();this.canvas=document.createElement('canvas');this.canvas.id='render';this.canvas.tabIndex=0;this.canvas.setAttribute('aria-label','Cena procedural interativa');this.container.prepend(this.canvas);
  if(mode!=='cpu'&&window.BABYLON){try{this.initGL();this.backend='Babylon.js / WebGL';this.onRenderer(this.backend);return;}catch(error){this.engine?.dispose();this.engine=null;this.canvas.remove();this.canvas=document.createElement('canvas');this.canvas.id='render';this.canvas.tabIndex=0;this.container.prepend(this.canvas);}}
  this.cpu=new CPUView(this.canvas,id=>this.select(id),o=>this.edit(o));this.backend='Canvas 2D / CPU';this.onRenderer(this.backend);this.cpu.mode=this.mode;
 }
 initGL(){
  const B=BABYLON;this.engine=new B.Engine(this.canvas,true,{preserveDrawingBuffer:true});this.scene=new B.Scene(this.engine);this.scene.clearColor=B.Color4.FromHexString('#10141dff');this.camera=new B.ArcRotateCamera('camera',-1.15,1.07,24,new B.Vector3(0,2,0),this.scene);this.camera.attachControl(this.canvas,true);this.camera.lowerRadiusLimit=2;this.camera.upperRadiusLimit=200;this.camera.wheelPrecision=30;
  const hemi=new B.HemisphericLight('sky',new B.Vector3(0,1,0),this.scene);hemi.intensity=.9;const key=new B.DirectionalLight('key',new B.Vector3(.5,-1,.45),this.scene);key.intensity=1.1;
  this.ground=B.MeshBuilder.CreateGround('grid',{width:40,height:40},this.scene);this.ground.isPickable=false;this.ground.material=new B.StandardMaterial('ground',this.scene);this.ground.material.diffuseColor=B.Color3.FromHexString('#1b2329');this.ground.material.specularColor=B.Color3.Black();
  const lines=[];for(let i=-20;i<=20;i+=2)lines.push([new B.Vector3(-20,.001,i),new B.Vector3(20,.001,i)],[new B.Vector3(i,.001,-20),new B.Vector3(i,.001,20)]);this.grid=B.MeshBuilder.CreateLineSystem('grid-lines',{lines},this.scene);this.grid.color=B.Color3.FromHexString('#323a42');this.grid.isPickable=false;
  this.gizmos=new B.GizmoManager(this.scene);this.gizmos.usePointerToAttachGizmos=false;this.setMode(this.mode);
  this.scene.onPointerObservable.add(info=>{if(info.type===B.PointerEventTypes.POINTERPICK)this.select(info.pickInfo?.pickedMesh?.metadata?.id||null);if(info.type===B.PointerEventTypes.POINTERUP&&this.selected){const mesh=this.meshes.get(this.selected)?.mesh;if(mesh){const object=this.data.objects.find(o=>o.id===this.selected);if(object){object.position=mesh.position.asArray();object.rotation=mesh.rotationQuaternion?mesh.rotationQuaternion.toEulerAngles().asArray():mesh.rotation.asArray();object.scaling=mesh.scaling.asArray();this.edit(object);}}}});
  this.engine.runRenderLoop(()=>this.scene?.render());this.observer?.disconnect();this.observer=new ResizeObserver(()=>this.engine?.resize());this.observer.observe(this.container);
 }
 setMode(mode){this.mode=mode;if(this.cpu){this.cpu.mode=mode;this.cpu.draw();return;}if(!this.gizmos)return;this.gizmos.positionGizmoEnabled=mode==='move';this.gizmos.rotationGizmoEnabled=mode==='rotate';this.gizmos.scaleGizmoEnabled=mode==='scale';}
 select(id){this.selected=id;if(this.cpu){this.cpu.selected=id;this.cpu.draw();}else this.gizmos?.attachToMesh(id?this.meshes.get(id)?.mesh:null);this.onSelect(id?this.data.objects.find(o=>o.id===id)||null:null);}
 edit(object){const original=this.data.objects.find(o=>o.id===object.id);if(original)Object.assign(original,structuredClone(object));this.onEdit(structuredClone(object));}
 material(color){if(!this.materials.has(color)){const m=new BABYLON.StandardMaterial(color,this.scene);m.diffuseColor=BABYLON.Color3.FromHexString(color);m.specularColor=new BABYLON.Color3(.17,.17,.17);m.specularPower=48;this.materials.set(color,m);}return this.materials.get(color);}
 createMesh(o){const B=BABYLON,g=o.geometry;let m;
  if(o.kind==='sphere')m=B.MeshBuilder.CreateSphere(o.id,{diameter:g.radius*2,segments:16},this.scene);
  if(o.kind==='box')m=B.MeshBuilder.CreateBox(o.id,{width:g.size[0],height:g.size[1],depth:g.size[2]},this.scene);
  if(o.kind==='cylinder'||o.kind==='cone')m=B.MeshBuilder.CreateCylinder(o.id,{height:g.height,diameterBottom:g.radius*2,diameterTop:o.kind==='cone'?0:g.radius*2,tessellation:24},this.scene);
  if(o.kind==='torus')m=B.MeshBuilder.CreateTorus(o.id,{diameter:g.radius*2,thickness:g.thickness,tessellation:40},this.scene);
  if(o.kind==='plane')m=B.MeshBuilder.CreateGround(o.id,{width:g.width,height:g.depth},this.scene);
  if(o.kind==='line')m=B.MeshBuilder.CreateTube(o.id,{path:g.points.map(p=>B.Vector3.FromArray(p)),radius:g.width/2,tessellation:8,cap:B.Mesh.CAP_ALL},this.scene);
  if(o.kind==='mesh'){m=new B.Mesh(o.id,this.scene);const vd=new B.VertexData();vd.positions=g.vertices.flat();vd.indices=g.faces.flat();vd.normals=[];B.VertexData.ComputeNormals(vd.positions,vd.indices,vd.normals);vd.applyToMesh(m);}
  m.metadata={id:o.id};m.material=this.material(o.color);m.material.backFaceCulling=false;return m;
 }
 load(data,reset=true){validate(data);this.data=structuredClone(data);if(this.cpu){this.cpu.setScene(this.data,reset);return;}
  const ids=new Set(data.objects.map(o=>o.id));for(const[id,entry]of this.meshes)if(!ids.has(id)){entry.mesh.dispose();this.meshes.delete(id);if(this.selected===id)this.select(null);}
  for(const o of data.objects){const signature=JSON.stringify([o.kind,o.geometry]);let entry=this.meshes.get(o.id);if(!entry||entry.signature!==signature){entry?.mesh.dispose();entry={signature,mesh:this.createMesh(o)};this.meshes.set(o.id,entry);}const m=entry.mesh;m.position=BABYLON.Vector3.FromArray(o.position);m.rotationQuaternion=null;m.rotation=BABYLON.Vector3.FromArray(o.rotation);m.scaling=BABYLON.Vector3.FromArray(o.scaling);m.isVisible=o.visible;m.material=this.material(o.color);m.material.wireframe=!!this.wireframe;}
  this.scene.clearColor=BABYLON.Color4.FromHexString((data.background||'#10141d')+'ff');this.ground.isVisible=data.ground!==false;this.grid.isVisible=data.ground!==false;this.ground.material.diffuseColor=BABYLON.Color3.FromHexString(data.ground_color||'#1b2329');this.ground.scaling.x=this.ground.scaling.z=(data.ground_size||40)/40;
  if(reset)this.resetCamera();if(this.selected)this.gizmos.attachToMesh(this.meshes.get(this.selected)?.mesh||null);
 }
 resetCamera(){if(this.cpu){this.cpu.reset(this.data.camera);return;}if(!this.camera)return;const c=this.data.camera||{};this.camera.setTarget(BABYLON.Vector3.FromArray(c.target||[0,2,0]));this.camera.radius=c.radius||24;this.camera.alpha=c.alpha??-1.15;this.camera.beta=Math.PI/2-(c.elevation??.5);}
 switch(mode){const saved=this.export();this.init(mode);this.load(saved,true);}
 export(){return structuredClone(this.cpu?this.cpu.data:this.data);}
 patch(id,patch){const o=this.data.objects.find(o=>o.id===id);if(!o)return;Object.assign(o,patch);validate(this.data);this.edit(o);this.load(this.data,false);this.select(id);}
 remove(){if(!this.selected)return;const o=this.data.objects.find(o=>o.id===this.selected);if(!o)return;this.onEdit({...o,deleted:true});this.data.objects=this.data.objects.filter(o=>o.id!==this.selected);this.select(null);this.load(this.data,false);}
 setWireframe(value){this.wireframe=value;if(this.cpu){this.cpu.wireframe=value;this.cpu.draw();}else for(const m of this.materials.values())m.wireframe=value;}
 screenshot(){this.scene?.render();return this.canvas.toDataURL('image/png');}
}
window.StudioViewport=StudioViewport;
})();
