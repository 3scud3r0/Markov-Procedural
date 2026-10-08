"""Compile/run each backend against the same IR oracle and boundary inputs.

A missing compiler is recorded as 'unavailable', never treated as a passing test.
Generated programs are deterministic local numeric code. External binaries live only
in a temporary directory; the report stores results and compiler versions.
"""
import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from markovjunior.procedural import Context,Program,Function,Literal,Ref,Binary,Set,If,Repeat,Return
from markovjunior.procedural.generators import program
from markovjunior.procedural.backends import emit_code
from markovjunior.core import DotNetRandom

BASE=Path(__file__).resolve().parents[1]
INPUTS=[(0,0),(1,-1),(-7,11),(42,23),(-999,77),(1_000_000,1_000_000),(-1_000_000,-1_000_000),(1_000_000,-1_000_000),(-1_000_000,1_000_000)]
SEEDS=[-2147483648,-1,0,42,12345,161803398,1923919228,2147483647]


def corpus():
    functions=[]
    for k,seed in enumerate(SEEDS):
        functions.extend(program({'prefix':f's{k}','functions':4,'expression_depth':3,'iterations':5},Context(seed,DotNetRandom(seed),BASE)).value.functions)
    # Includes simultaneous branch updates and nested loops, beyond the recipe default.
    functions.append(Function('nested',('x','y'),(
        Set('value',Ref('x')),Set('other',Ref('y')),
        Repeat('outer_step',2,(Repeat('inner_step',3,(
            If(Binary('!=',Ref('value'),Ref('other')),
               (Set('other',Binary('+',Ref('value'),Ref('inner_step'))),Set('value',Binary('-',Ref('other'),Ref('outer_step')))),
               (Set('value',Binary('+',Ref('value'),Literal(7))),Set('other',Binary('*',Ref('value'),Literal(2))))),
        )),)),Return(Binary('+',Ref('value'),Ref('other'))),
    )))
    return Program(tuple(functions)).validate()


def main():
    p=argparse.ArgumentParser()
    for name in ('node','gcc','gpp','rustc','go','lua','tsc'):p.add_argument('--'+name,default={'gpp':'g++'}.get(name,name))
    p.add_argument('--report',type=Path,default=BASE/'validation/backend_report.json')
    args=p.parse_args()
    ir=corpus()
    cases=[(f.name,x,y) for f in ir.functions for x,y in INPUTS]
    expected=[ir.evaluate(name,x,y) for name,x,y in cases]
    reports=[]
    sources={target:emit_code(ir,target) for target in ('python','javascript','typescript','c','cpp','rust','go','lua','sql')}
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        def run(command):
            return subprocess.run(command,cwd=root,text=True,capture_output=True,check=True,timeout=120).stdout
        def check(target,values,version):
            if values!=expected:
                i=next((i for i,(a,b) in enumerate(zip(values,expected)) if a!=b),min(len(values),len(expected)))
                raise AssertionError(f'{target}: semantic mismatch at {i}; count {len(values)} vs {len(expected)}')
            reports.append({'target':target,'status':'pass','checks':len(expected),'version':version})
            print(target,'PASS',len(expected),'outputs',flush=True)
        def tool(target,name):
            path=shutil.which(name)
            if path is None:
                reports.append({'target':target,'status':'unavailable','compiler':name})
                print(target,'UNAVAILABLE',flush=True)
            return path
        namespace={}
        exec(compile(sources['python'],'generated.py','exec'),namespace)
        check('python',[namespace[name](x,y) for name,x,y in cases],sys.version.split()[0])
        connection=sqlite3.connect(':memory:')
        sqlvalues=[]
        for x,y in INPUTS:
            rows=dict(connection.execute(sources['sql'],{'x':x,'y':y}))
            sqlvalues.append(rows)
        check('sql',[sqlvalues[INPUTS.index((x,y))][name] for name,x,y in cases],sqlite3.sqlite_version)
        node=tool('javascript',args.node)
        if node:
            (root/'generated.mjs').write_text(sources['javascript'])
            wrapper="import * as p from './generated.mjs';\nconst cases = "+json.dumps(cases)+";\nconsole.log(JSON.stringify(cases.map(([name,x,y]) => p[name](x,y))));\n"
            (root/'run.mjs').write_text(wrapper)
            check('javascript',json.loads(run([node,'run.mjs'])),run([node,'--version']).strip())
        tsc=tool('typescript',args.tsc)
        if tsc and node:
            (root/'generated.ts').write_text(sources['typescript'])
            run([tsc,'--strict','--target','ES2020','--module','commonjs','--outDir','ts-output','generated.ts'])
            (root/'run.cjs').write_text("const p = require('./ts-output/generated.js');\nconsole.log(JSON.stringify("+json.dumps(cases)+".map(([name,x,y]) => p[name](x,y))));\n")
            check('typescript',json.loads(run([node,'run.cjs'])),run([tsc,'--version']).strip())
        elif tsc and not node:
            reports.append({'target':'typescript','status':'unavailable','compiler':'node'})
        for target,command,standard,extension in [('c',args.gcc,'-std=c11','.c'),('cpp',args.gpp,'-std=c++17','.cpp')]:
            compiler=tool(target,command)
            if not compiler:continue
            source=sources[target]+'\n#include <stdio.h>\nint main(void) {\n'
            for name,x,y in cases:source+=f'    printf("%lld\\n", (long long){name}({x}, {y}));\n'
            source+='    return 0;\n}\n'
            filename='generated'+extension
            (root/filename).write_text(source)
            run([compiler,standard,'-O1','-Wall','-Wextra',filename,'-o',str(root/(target+'-run'))])
            check(target,[int(v) for v in run([str(root/(target+'-run'))]).splitlines()],run([compiler,'--version']).splitlines()[0])
        rustc=tool('rust',args.rustc)
        if rustc:
            source=sources['rust']+'\nfn main() {\n'
            for name,x,y in cases:source+=f'    println!("{{}}", {name}({x}_i64, {y}_i64));\n'
            source+='}\n'
            (root/'generated.rs').write_text(source)
            run([rustc,'--edition=2021','generated.rs','-o',str(root/'rust-run')])
            check('rust',[int(v) for v in run([str(root/'rust-run')]).splitlines()],run([rustc,'--version']).strip())
        go=tool('go',args.go)
        if go:
            source=sources['go'].replace('package generated','package main\nimport "fmt"')+'\nfunc main() {\n'
            for name,x,y in cases:source+=f'    fmt.Println({name}(int64({x}), int64({y})))\n'
            source+='}\n'
            (root/'generated.go').write_text(source)
            check('go',[int(v) for v in run([go,'run','generated.go']).splitlines()],run([go,'version']).strip())
        lua=tool('lua',args.lua)
        if lua:
            (root/'generated.lua').write_text(sources['lua'])
            source="local p = dofile('generated.lua')\n"
            for name,x,y in cases:source+=f'print(p.{name}({x}, {y}))\n'
            (root/'run.lua').write_text(source)
            check('lua',[int(v) for v in run([lua,'run.lua']).splitlines()],run([lua,'-v']).strip())
    result={'schema':'markovjunior.backend-validation/1','functions':len(ir.functions),'input_vectors':INPUTS,'seeds':SEEDS,'per_backend_checks':len(expected),'total_checks':sum(r.get('checks',0) for r in reports),'targets':reports}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    if any(r['status']!='pass' for r in reports):print('Some compilers were unavailable; see report.',flush=True)

if __name__=='__main__':main()
