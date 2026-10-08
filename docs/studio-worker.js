'use strict';
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
let pyodide;
const ready=(async()=>{
 postMessage({type:'status',message:'Carregando Python 3.12…',progress:25});
 pyodide=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
 postMessage({type:'status',message:'Preparando a linguagem Markov…',progress:65});
 await pyodide.loadPackage('pillow');
 const response=await fetch('python-runtime.zip?v=1.0.0-core1');if(!response.ok)throw Error('Motor Python indisponível: '+response.status);
 pyodide.unpackArchive(await response.arrayBuffer(),'zip',{extractDir:'/home/pyodide'});
 await pyodide.runPythonAsync('import json, sys\nsys.path.insert(0, "/home/pyodide")\nfrom markovjunior.language import Session\nmarkov_session = Session()');
 postMessage({type:'ready',version:'1.0.0'});
})();
ready.catch(error=>postMessage({type:'fatal',message:String(error)}));
onmessage=async({data})=>{
 try{
  await ready;
  pyodide.globals.set('markov_request_json',JSON.stringify(data));
  let result;
  if(data.type==='run'){
   // Load supported Pyodide packages explicitly imported by project code.
   for(const file of data.project.files)if(file.name.endsWith('.mp')||file.name.endsWith('.py')){
    try{await pyodide.loadPackagesFromImports(file.content);}catch(error){if(!String(error).includes('SyntaxError'))throw error;}
   }
   result=await pyodide.runPythonAsync('markov_request = json.loads(markov_request_json)\njson.dumps(markov_session.execute(markov_request["project"]), ensure_ascii=False, allow_nan=False)');
  }else if(data.type==='frame'){
   result=await pyodide.runPythonAsync('markov_request = json.loads(markov_request_json)\njson.dumps(markov_session.frame(markov_request["t"], markov_request["dt"], markov_request.get("inputs")), ensure_ascii=False, allow_nan=False)');
  }else return;
  postMessage({type:data.type==='frame'?'frame':'result',id:data.id,result:JSON.parse(result)});
 }catch(error){postMessage({type:'error',id:data.id,message:String(error)});}
};
