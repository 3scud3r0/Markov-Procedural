"""Recipe execution with deterministic job seeds and an audited output manifest."""
import hashlib
import json
import re
from dataclasses import dataclass,replace
from pathlib import Path,PurePosixPath
from .model import Document,Artifact
from .registry import default_registry
from ..core import DotNetRandom
from ..paths import data_root


@dataclass(frozen=True)
class Context:
    seed: int
    random: DotNetRandom
    base: Path


def run_project(recipe,output,*,seed=None,registry=None,base=None):
    registry=registry or default_registry()
    base=Path(base or data_root()).resolve()
    if not isinstance(recipe,dict) or type(recipe.get('version')) is not int or recipe.get('version')!=1:raise ValueError('recipe version must be 1')
    project_seed=recipe.get('seed',42) if seed is None else seed
    if type(project_seed) is not int or not -2147483648<=project_seed<=2147483647:raise ValueError('seed must be a signed 32-bit integer')
    jobs=recipe.get('jobs')
    if not isinstance(jobs,list) or not 1<=len(jobs)<=100:raise ValueError('recipe needs 1..100 jobs')
    names=set()
    # Validate recipe topology before asking any generator to run.
    for job in jobs:
        if not isinstance(job,dict):raise ValueError('job must be an object')
        name=job.get('name')
        if not isinstance(name,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,63}',name) or name in names:raise ValueError('job names must be distinct portable names')
        names.add(name)
        if job.get('generator') not in registry.generators:raise ValueError(f'unknown generator: {job.get("generator")}')
        targets=job.get('targets')
        if not isinstance(targets,list) or not targets or any(not isinstance(t,str) or t not in registry.targets for t in targets) or len(set(targets))!=len(targets):raise ValueError(f'{name}: invalid or duplicate targets')
        if not isinstance(job.get('params',{}),dict):raise ValueError('params must be an object')
        amount=job.get('count',1)
        if type(amount) is not int or not 1<=amount<=100:raise ValueError('count must be 1..100')
    artifacts=[]
    entries=[]
    paths=set()
    for job in jobs:
        for instance in range(job.get('count',1)):
            name=job['name']
            # Job order and adding a new target do not change the generated document.
            digest=hashlib.sha256(f'markovjunior/1/{project_seed}/{name}/{instance}'.encode()).digest()
            job_seed=int.from_bytes(digest[:4],'little') & 0x7fffffff
            context=Context(job_seed,DotNetRandom(job_seed),base)
            doc=registry.generate(job['generator'],job.get('params',{}),context)
            meta={**doc.metadata,'job':name,'generator':job['generator'],'seed':job_seed,'project_seed':project_seed,'instance':instance}
            doc=replace(doc,metadata=meta)
            stem=f'{name}/{name}' if job.get('count',1)==1 else f'{name}/variant_{instance:03d}/{name}'
            entry={'name':name,'instance':instance,'generator':job['generator'],'kind':doc.kind,'seed':job_seed,'params':job.get('params',{}),'outputs':[]}
            for target in job['targets']:
                for artifact in registry.render(doc,target,stem):
                    path=PurePosixPath(artifact.filename)
                    if not artifact.filename or path.as_posix()!=artifact.filename or path.is_absolute() or any(part in ('..','.') for part in path.parts) or '\\' in artifact.filename or ':' in artifact.filename or str(path) in paths or str(path)=='manifest.json':
                        raise ValueError('invalid or colliding artifact path')
                    paths.add(str(path))
                    payload=artifact.bytes()
                    artifacts.append((path,payload))
                    entry['outputs'].append({'target':target,'path':str(path),'media_type':artifact.media_type,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
            entries.append(entry)
    output=Path(output).resolve()
    # Prepare every document before writing output; reject paths through symlinks.
    for path,payload in artifacts:
        destination=output/path
        if not destination.resolve().is_relative_to(output):raise ValueError('artifact path leaves output directory')
        if destination.is_symlink():raise ValueError('artifact destination cannot be a symlink')
    if (output/'manifest.json').is_symlink():raise ValueError('manifest destination cannot be a symlink')
    manifest={'schema':'markovjunior.generation/1','version':1,'seed':project_seed,'jobs':entries}
    manifest_text=json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    for path,payload in artifacts:
        destination=output/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(payload)
    output.mkdir(parents=True,exist_ok=True)
    (output/'manifest.json').write_text(manifest_text,encoding='utf-8')
    return manifest
