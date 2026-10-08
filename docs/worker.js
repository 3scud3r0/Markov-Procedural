/* Pyodide stays off the rendering/UI thread. Versions are pinned. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
let pyodide;
async function init(){
  pyodide=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
  postMessage({type:'status',message:'Carregando Pillow e o motor Python…'});
  await pyodide.loadPackage('pillow');
  const response=await fetch('python-runtime.zip');
  if(!response.ok)throw Error('Falha ao baixar o motor Python: '+response.status);
  pyodide.unpackArchive(await response.arrayBuffer(),'zip',{extractDir:'/home/pyodide'});
  await pyodide.runPythonAsync('from markovjunior.procedural.browser import browser_generate');
  postMessage({type:'ready'});
}
const ready=init().catch(error=>{postMessage({type:'error',message:String(error)});throw error;});
onmessage=async({data})=>{
  try{
    await ready;
    pyodide.globals.set('browser_recipe_json',JSON.stringify(data.recipe));
    const result=await pyodide.runPythonAsync('import json\nbrowser_generate(json.loads(browser_recipe_json))');
    postMessage({type:'result',result:JSON.parse(result)});
  }catch(error){postMessage({type:'error',message:String(error)});}
};
