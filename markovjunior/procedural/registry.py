"""Public extension points: generators create documents; targets create artifacts."""
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from .model import Artifact,Document
from .backends import CODE_TARGETS,emit_code
from . import generators


def name_check(name):
    if not isinstance(name,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,63}',name):
        raise ValueError(f'invalid extension name: {name!r}')


@dataclass(frozen=True)
class Target:
    kinds: frozenset
    emit: object


class Registry:
    def __init__(self):
        self.generators={}
        self.targets={}

    def register_generator(self,name,generate):
        name_check(name)
        if name in self.generators or not callable(generate):raise ValueError('duplicate or invalid generator')
        self.generators[name]=generate

    def register_target(self,name,kinds,emit):
        name_check(name)
        kinds=frozenset(kinds)
        if name in self.targets or not kinds or not all(isinstance(k,str) for k in kinds) or not callable(emit):
            raise ValueError('duplicate or invalid target')
        self.targets[name]=Target(kinds,emit)

    def generate(self,name,params,context):
        if name not in self.generators:raise ValueError(f'unknown generator {name!r}; available: {", ".join(self.generators)}')
        doc=self.generators[name](params,context)
        if not isinstance(doc,Document):raise ValueError('a generator must return Document')
        return doc

    def render(self,doc,target,stem):
        if target not in self.targets:raise ValueError(f'unknown target {target!r}; available: {", ".join(self.targets)}')
        entry=self.targets[target]
        if doc.kind not in entry.kinds:raise ValueError(f'{target} cannot render {doc.kind}; supported: {sorted(entry.kinds)}')
        result=tuple(entry.emit(doc,stem))
        if not result or any(not isinstance(a,Artifact) for a in result):raise ValueError('target must return one or more Artifact objects')
        return result

    def load_plugin(self,path):
        path=Path(path).resolve()
        if not path.is_file():raise ValueError(f'plugin file not found: {path}')
        spec=importlib.util.spec_from_file_location('markovjunior_extension_'+str(len(self.generators)),path)
        if spec is None or spec.loader is None:raise ValueError('cannot load plugin')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        register=getattr(module,'register',None)
        if not callable(register):raise ValueError('plugin must define register(registry)')
        register(self)


def json_target(doc,stem):
    return (Artifact(stem+'.json',json.dumps(doc.to_data(),ensure_ascii=False,indent=2,allow_nan=False)+'\n','application/json'),)


def text_target(doc,stem):
    return (Artifact(stem+'.txt',str(doc.value)+'\n','text/plain'),)


def markdown_target(doc,stem):
    title=doc.metadata.get('job',stem)
    return (Artifact(stem+'.md','# '+title+'\n\n'+str(doc.value)+'\n','text/markdown'),)


def svg_target(doc,stem):
    value=doc.value
    allowed={'rect','circle','ellipse','line','polyline','polygon','path'}
    allowed_attributes={'id','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry','width','height','d','points','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity'}
    width,height=value['width'],value['height']
    root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':str(width),'height':str(height),'viewBox':f'0 0 {width} {height}','role':'img'})
    ET.SubElement(root,'title').text=doc.metadata.get('job',stem)
    for element in value['elements']:
        if element['tag'] not in allowed or any(k not in allowed_attributes for k in element['attrs']):
            raise ValueError('unsupported scene geometry or SVG attribute')
        ET.SubElement(root,element['tag'],{k:str(v) for k,v in element['attrs'].items()})
    return (Artifact(stem+'.svg',ET.tostring(root,encoding='unicode')+'\n','image/svg+xml'),)


def default_registry():
    registry=Registry()
    for name,generate in [('program',generators.program),('program-ir',generators.program_ir),('grammar',generators.grammar),('data',generators.data),('scene',generators.scene),('grid',generators.grid)]:
        registry.register_generator(name,generate)
    for name,(extension,media) in CODE_TARGETS.items():
        def emit(doc,stem,name=name,extension=extension,media=media):
            return (Artifact(stem+extension,emit_code(doc.value,name),media),)
        registry.register_target(name,{'program'},emit)
    registry.register_target('json',{'program','text','data','scene'},json_target)
    registry.register_target('text',{'text'},text_target)
    registry.register_target('markdown',{'text'},markdown_target)
    registry.register_target('svg',{'scene'},svg_target)
    return registry
