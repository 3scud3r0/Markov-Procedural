import {basicSetup} from 'codemirror';
import {EditorView,keymap} from '@codemirror/view';
import {EditorState} from '@codemirror/state';
import {python} from '@codemirror/lang-python';
import {autocompletion} from '@codemirror/autocomplete';
import {setDiagnostics} from '@codemirror/lint';
import {indentWithTab,undo,redo} from '@codemirror/commands';
import {HighlightStyle,syntaxHighlighting} from '@codemirror/language';
import {tags} from '@lezer/highlight';

const names=['sphere','box','cylinder','cone','torus','plane','line','mesh','scene','seed','random','randint','choose','noise','param','rule','emit','grammar','generate','keys','mouse','PI','TAU','sin','cos','lerp','clamp'];
const signatures={sphere:'sphere(radius=1, position=[0,0,0], color="#e8bb80")',param:'param("name", default, min=None, max=None, step=None)',mesh:'mesh(vertices, faces, position=[0,0,0], color="#e8bb80")',noise:'noise(x, y=0, z=0)',rule:'@rule — marks a reusable procedural function',emit:'emit("output.json", data)'};
const theme=EditorView.theme({
 '&':{height:'100%',backgroundColor:'#101319',color:'#ccd5df',fontSize:'13px'},
 '.cm-content':{fontFamily:'"JetBrains Mono", "SFMono-Regular", Consolas, monospace',padding:'20px 0',caretColor:'#d8f783'},
 '.cm-scroller':{fontFamily:'"JetBrains Mono", monospace',overflow:'auto',lineHeight:'1.85'},
 '.cm-gutters':{backgroundColor:'#101319',color:'#46515e',borderRight:'none',minWidth:'48px'},
 '.cm-lineNumbers .cm-gutterElement':{padding:'0 12px 0 8px'},
 '.cm-activeLine':{backgroundColor:'#171e28'},'.cm-activeLineGutter':{backgroundColor:'#171e28',color:'#b6c4d2'},
 '.cm-selectionBackground, ::selection':{backgroundColor:'#364639 !important'},
 '.cm-cursor':{borderLeftColor:'#d8f783'},'.cm-tooltip':{backgroundColor:'#222b35',border:'1px solid #394551',color:'#e8eef4'},
 '.cm-search':{backgroundColor:'#1d2530'},'.cm-panel':{color:'#c9d7e6',backgroundColor:'#19212b'}
},{dark:true});
class StudioEditor{
 constructor(parent,source,onChange,onRun){
  this.view=new EditorView({parent,state:EditorState.create({doc:source,extensions:[basicSetup,python(),theme,EditorView.lineWrapping,
   syntaxHighlighting(HighlightStyle.define([{tag:tags.keyword,color:'#b8bcdf'},{tag:tags.string,color:'#c2d79f'},{tag:tags.number,color:'#e4b58c'},{tag:tags.comment,color:'#657988',fontStyle:'italic'},{tag:tags.function(tags.variableName),color:'#b2d3cd'},{tag:tags.definition(tags.variableName),color:'#cfd3a4'},{tag:tags.operator,color:'#9cb1c1'}])),
   keymap.of([indentWithTab,{key:'Mod-Enter',run:()=>{onRun();return true;}}]),
   autocompletion({override:[context=>{const word=context.matchBefore(/[A-Za-z_]\w*/);if(!word&&!context.explicit)return null;return{from:word?word.from:context.pos,options:names.map(label=>({label,type:label==='scene'?'variable':'function',detail:signatures[label]||'Markov procedural API'}))};}]}),
   EditorView.updateListener.of(update=>{if(update.docChanged)onChange(update.state.doc.toString());if(update.selectionSet){const line=update.state.doc.lineAt(update.state.selection.main.head);document.dispatchEvent(new CustomEvent('editor-cursor',{detail:{line:line.number,column:update.state.selection.main.head-line.from+1}}));}})
  ]})});
 }
 getValue(){return this.view.state.doc.toString();}
 setValue(source){this.view.dispatch({changes:{from:0,to:this.view.state.doc.length,insert:source}});this.clearError();}
 setError(error){if(!error?.line)return;const line=this.view.state.doc.line(Math.min(error.line,this.view.state.doc.lines));this.view.dispatch(setDiagnostics(this.view.state,[{from:line.from,to:line.to,severity:'error',message:error.type+': '+error.message}]));this.view.dispatch({selection:{anchor:line.from},scrollIntoView:true});}
 clearError(){this.view.dispatch(setDiagnostics(this.view.state,[]));}
 focus(){this.view.focus();}
 undo(){undo(this.view);}
 redo(){redo(this.view);}
}
window.StudioEditor=StudioEditor;
