'use strict';
const $=id=>document.getElementById(id);
const status=message=>{$('status').textContent=message;};
let engine,scene,camera,gizmos,fallback,files=[],meshes=[],selected=null,busy=true;
const presets={
 garden:()=>({version:1,seed:Number($('seed').value),jobs:[{name:'jardim',generator:'scene3d',params:{trees:Number($('trees').value),depth:Number($('depth').value)},targets:['scene3d-json']},{name:'funcoes',generator:'program',params:{functions:4},targets:['python','javascript','typescript','c','cpp','rust','go','lua','sql','json']}]}),
 maze:()=>({version:1,seed:Number($('seed').value),jobs:[{name:'labirinto',generator:'grid',params:{model:'MazeGrowth',width:31,height:31,cell:14},targets:['svg','json']}]}),
 svg:()=>({version:1,seed:Number($('seed').value),jobs:[{name:'jardim',generator:'scene',params:{width:1000,height:600,trees:Number($('trees').value),depth:Number($('depth').value)},targets:['svg','json']}]}),
 grammar:()=>({version:1,seed:Number($('seed').value),jobs:[{name:'garden_dsl',generator:'grammar',params:{start:'<programa>',rules:{programa:['garden {\n<plantas>\n}'],plantas:['  plant <arvore> at <int:0:100>,<int:0:100>;','<plantas>\n<plantas>'],arvore:['oak','fern','willow']},max_depth:6},targets:['text','json']}]})
};
function updateRecipe(){$('recipe').value=JSON.stringify(presets[$('preset').value](),null,2);}
function setBusy(value){busy=value;$('generate').disabled=value;$('run-recipe').disabled=value;$('generate').textContent=value?'Gerando em Python…':'Gerar com esta semente';}
function download(name,content,type='application/json'){
 const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name.split('/').pop();a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function tab(name){$('scene-panel').hidden=name!=='scene';$('files-panel').hidden=name!=='files';$('tab-scene').classList.toggle('active',name==='scene');$('tab-files').classList.toggle('active',name==='files');engine?.resize();}
function material(color){const mat=new BABYLON.StandardMaterial('color',scene);mat.diffuseColor=BABYLON.Color3.FromHexString(color);mat.specularColor=new BABYLON.Color3(.08,.08,.08);return mat;}
function select(mesh){selected=mesh;gizmos?.attachToMesh(mesh);}
function transform(){if(fallback){fallback.mode=$('transform').value;fallback.draw();return;}if(!gizmos)return;gizmos.positionGizmoEnabled=$('transform').value==='move';gizmos.rotationGizmoEnabled=$('transform').value==='rotate';gizmos.scaleGizmoEnabled=$('transform').value==='scale';}
function resetCamera(){if(fallback){fallback.reset();return;}if(!camera)return;camera.setTarget(new BABYLON.Vector3(0,2.5,0));camera.alpha=-Math.PI/2.3;camera.beta=1.12;camera.radius=24;}
function initBabylon(){
 if(!window.BABYLON)throw Error('Babylon.js não carregou. Recarregue a página.');
 engine=new BABYLON.Engine($('render'),true,{preserveDrawingBuffer:true});scene=new BABYLON.Scene(engine);scene.clearColor=new BABYLON.Color4(.05,.08,.13,1);
 camera=new BABYLON.ArcRotateCamera('camera',0,0,24,BABYLON.Vector3.Zero(),scene);resetCamera();camera.attachControl($('render'),true);camera.lowerRadiusLimit=3;camera.upperRadiusLimit=90;camera.wheelPrecision=25;
 const light=new BABYLON.HemisphericLight('sky',new BABYLON.Vector3(.4,1,.3),scene);light.intensity=1.15;
 const ground=BABYLON.MeshBuilder.CreateGround('ground',{width:30,height:30},scene);ground.material=material('#244437');ground.isPickable=false;
 gizmos=new BABYLON.GizmoManager(scene);gizmos.usePointerToAttachGizmos=false;transform();
 scene.onPointerObservable.add(event=>{if(event.type===BABYLON.PointerEventTypes.POINTERPICK){const mesh=event.pickInfo?.pickedMesh;select(mesh?.metadata?.editable?mesh:null);}});
 engine.runRenderLoop(()=>scene.render());window.addEventListener('resize',()=>engine?.resize());
}
function renderScene(data){
 if(data.schema!=='markovjunior.scene3d/1'||!Array.isArray(data.objects)||data.objects.length>3000)throw Error('Cena 3D inválida ou acima do limite de 3.000 objetos.');
 // Validate imported data before replacing the visible scene.
 for(const obj of data.objects){
  const vector=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<=1000);
  if(!/^#[0-9a-f]{6}$/i.test(obj.color)||!Number.isFinite(obj.radius)||obj.radius<=0||obj.radius>20)throw Error('Cor ou raio inválido.');
  if(obj.kind==='branch'){if(!vector(obj.start)||!vector(obj.end))throw Error('Ramo inválido.');}
  else if(obj.kind==='leaf'){if(!vector(obj.position))throw Error('Folha inválida.');}
  else throw Error('Tipo de objeto desconhecido.');
  if(obj.transform){for(const field of ['position','rotation','scaling'])if(!vector(obj.transform[field]))throw Error('Transformação inválida.');}
 }
 if(fallback){fallback.load(data);tab('scene');return;}
 if(!scene)throw Error('Renderizador indisponível. Os arquivos gerados continuam acessíveis.');
 select(null);for(const mesh of meshes)mesh.dispose(false,true);meshes=[];
 const materials=new Map();
 for(const obj of data.objects){
  let mesh;
  if(obj.kind==='branch'){
   const start=BABYLON.Vector3.FromArray(obj.start),end=BABYLON.Vector3.FromArray(obj.end),direction=end.subtract(start),length=direction.length();
   if(length<1e-6)continue;
   mesh=BABYLON.MeshBuilder.CreateCylinder('ramo',{height:length,diameter:obj.radius*2,tessellation:6},scene);mesh.position=start.add(end).scale(.5);
   mesh.rotationQuaternion=BABYLON.Quaternion.FromUnitVectorsToRef(BABYLON.Axis.Y,direction.normalize(),new BABYLON.Quaternion());
  }else{mesh=BABYLON.MeshBuilder.CreateSphere('folha',{diameter:obj.radius*2,segments:6},scene);mesh.position=BABYLON.Vector3.FromArray(obj.position);mesh.scaling=new BABYLON.Vector3(1,.65,1);}
  if(!materials.has(obj.color))materials.set(obj.color,material(obj.color));mesh.material=materials.get(obj.color);mesh.metadata={editable:true,original:structuredClone(obj)};
  if(obj.transform){mesh.position=BABYLON.Vector3.FromArray(obj.transform.position);mesh.rotationQuaternion=null;mesh.rotation=BABYLON.Vector3.FromArray(obj.transform.rotation);mesh.scaling=BABYLON.Vector3.FromArray(obj.transform.scaling);}
  meshes.push(mesh);
 }
 $('stats').textContent=meshes.length+' objetos · Python → Babylon.js';resetCamera();tab('scene');
}
function showFile(){
 const file=files[Number($('file-list').value)];if(!file)return;
 $('source').textContent=file.content;$('svg-preview').hidden=!file.name.endsWith('.svg');
 if(file.name.endsWith('.svg'))$('svg-preview').srcdoc=file.content;
}
function showResult(result){
 files=result.files;files.push({name:'manifest.json',content:JSON.stringify(result.manifest,null,2),media_type:'application/json'});
 $('file-list').replaceChildren(...files.map((file,index)=>{const option=document.createElement('option');option.value=index;option.textContent=file.name;return option;}));showFile();
 if(result.scenes.length)renderScene(result.scenes[0]);else tab('files');
 status('Pronto · '+result.manifest.jobs.length+' tarefas · '+result.files.length+' arquivos · semente '+result.manifest.seed+'.');
}
updateRecipe();
let webglError=null;
function initRenderer(){
 if(fallback){fallback.dispose();fallback=null;}if(engine){engine.dispose();engine=null;}scene=null;camera=null;gizmos=null;selected=null;meshes=[];
 // A canvas that acquired WebGL cannot acquire a 2D context. Use a fresh element.
 const old=$('render'),fresh=old.cloneNode(false);old.replaceWith(fresh);
 if($('renderer').value!=='canvas')try{initBabylon();return;}catch(error){webglError=String(error);engine?.dispose();engine=null;scene=null;camera=null;gizmos=null;const old=$('render');old.replaceWith(old.cloneNode(false));}
 fallback=new CanvasSceneEngine($('render'),count=>{$('stats').textContent=count+' objetos · Canvas 2D / CPU';});
 transform();$('stats').textContent='Canvas 2D / CPU · sem WebGL';
}
initRenderer();
const worker=new Worker('worker.js');
worker.onmessage=({data})=>{
 if(data.type==='status')status(data.message);
 if(data.type==='ready'){setBusy(false);status('Python pronto. Gerando o primeiro jardim…');run(false);}
 if(data.type==='result'){setBusy(false);try{showResult(data.result);}catch(error){status(String(error));tab('files');}}
 if(data.type==='error'){setBusy(false);status('Erro: '+data.message);}
};
worker.onerror=event=>{setBusy(false);status('Falha ao carregar Python: '+event.message+'. Verifique sua conexão e recarregue.');};
function run(edited){if(busy)return;try{if(!edited)updateRecipe();const recipe=JSON.parse($('recipe').value);setBusy(true);status('Executando o gerador Python no navegador…');worker.postMessage({recipe});}catch(error){setBusy(false);status('Receita inválida: '+error.message);}}
$('generate').onclick=()=>run(false);$('run-recipe').onclick=()=>run(true);$('preset').onchange=updateRecipe;
for(const id of ['seed','trees','depth'])$(id).onchange=updateRecipe;
$('tab-scene').onclick=()=>tab('scene');$('tab-files').onclick=()=>tab('files');$('transform').onchange=transform;$('reset-camera').onclick=resetCamera;
$('delete-object').onclick=()=>{if(fallback){fallback.remove();return;}if(!selected)return;const mesh=selected;select(null);meshes=meshes.filter(m=>m!==mesh);mesh.dispose();$('stats').textContent=meshes.length+' objetos';};
$('file-list').onchange=showFile;$('download-file').onclick=()=>{const file=files[Number($('file-list').value)];if(file)download(file.name,file.content,file.media_type);};
function editedScene(){if(fallback)return fallback.export();
 const objects=meshes.map(mesh=>({...mesh.metadata.original,transform:{position:mesh.position.asArray(),rotation:(mesh.rotationQuaternion?mesh.rotationQuaternion.toEulerAngles():mesh.rotation).asArray(),scaling:mesh.scaling.asArray()}}));
 return{schema:'markovjunior.scene3d/1',objects};}
$('export-scene').onclick=()=>download('cena-editada.json',JSON.stringify(editedScene(),null,2));
$('renderer').onchange=()=>{const saved=editedScene();initRenderer();renderScene(saved);};
$('import-scene').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>4_000_000)throw Error('Arquivo maior que 4 MB.');renderScene(JSON.parse(await file.text()));status('Edição importada.');}catch(error){status('Erro de importação: '+error.message);}finally{event.target.value='';}};
