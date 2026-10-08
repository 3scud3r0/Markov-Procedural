"""Emit checked IR as executable functions in independent target languages."""
from .ir import Literal,Ref,Binary,Set,If,Repeat,Return

CODE_TARGETS = {
    'python':('.py','text/x-python'), 'javascript':('.mjs','text/javascript'),
    'typescript':('.ts','text/typescript'), 'lua':('.lua','text/x-lua'),
    'c':('.c','text/x-c'), 'cpp':('.cpp','text/x-c++'),
    'rust':('.rs','text/x-rust'), 'go':('.go','text/x-go'), 'sql':('.sql','application/sql'),
}


def expression(e,target):
    if isinstance(e,Literal):
        if target=='c':return f'INT64_C({e.value})'
        if target=='cpp':return f'std::int64_t({e.value})'
        if target=='rust':return f'{e.value}_i64'
        if target=='go':return f'int64({e.value})'
        return str(e.value)
    if isinstance(e,Ref):return e.name
    op='~=' if target=='lua' and e.op=='!=' else e.op
    return f'({expression(e.left,target)} {op} {expression(e.right,target)})'


def emit_code(program,target):
    program.validate()
    if target=='sql':return emit_sql(program)
    header={
        'python':'"""Procedurally generated functions; integer inputs within ±1,000,000."""\n',
        'javascript':'// Generated portable integer functions (inputs within +/-1,000,000).\n',
        'typescript':'// Generated portable integer functions (inputs within +/-1,000,000).\n',
        'lua':'-- Generated portable integer functions (inputs within +/-1,000,000).\n',
        'c':'/* Generated portable integer functions. */\n#include <stdint.h>\n',
        'cpp':'// Generated portable integer functions.\n#include <cstdint>\n',
        'rust':'// Generated portable integer functions (inputs within +/-1,000,000).\n',
        'go':'// Generated portable integer functions (inputs within +/-1,000,000).\npackage generated\n',
    }[target]
    lines=[header.rstrip(),'']
    for f in program.functions:
        names=set(f.parameters)
        p=', '.join(f.parameters)
        if target=='python':signature=f'def {f.name}('+', '.join(v+': int' for v in f.parameters)+') -> int:'
        elif target=='javascript':signature=f'export function {f.name}({p}) {{'
        elif target=='typescript':signature=f'export function {f.name}('+', '.join(v+': number' for v in f.parameters)+'): number {'
        elif target=='lua':signature=f'local function {f.name}({p})'
        elif target=='c':signature=f'int64_t {f.name}('+', '.join('int64_t '+v for v in f.parameters)+') {'
        elif target=='cpp':signature=f'std::int64_t {f.name}('+', '.join('std::int64_t '+v for v in f.parameters)+') {'
        elif target=='rust':signature=f'pub fn {f.name}('+', '.join(v+': i64' for v in f.parameters)+') -> i64 {'
        else:signature=f'func {f.name}('+', '.join(v+' int64' for v in f.parameters)+') int64 {'
        lines.append(signature)
        def emit_body(statements,level):
            indent='    '*level
            for s in statements:
                if isinstance(s,Set):
                    value=expression(s.value,target)
                    fresh=s.name not in names
                    names.add(s.name)
                    prefix={'python':'','lua':'local ' if fresh else '',
                            'javascript':'let ' if fresh else '', 'typescript':'let ' if fresh else '',
                            'c':'int64_t ' if fresh else '', 'cpp':'std::int64_t ' if fresh else '',
                            'rust':'let mut ' if fresh else '', 'go':''}[target]
                    op=':=' if target=='go' and fresh else '='
                    end=';' if target in ('javascript','typescript','c','cpp','rust') else ''
                    lines.append(f'{indent}{prefix}{s.name} {op} {value}{end}')
                elif isinstance(s,If):
                    condition=expression(s.condition,target)
                    if target=='python':lines.append(f'{indent}if {condition}:')
                    elif target=='lua':lines.append(f'{indent}if {condition} then')
                    else:lines.append(f'{indent}if {condition} {{')
                    emit_body(s.yes,level+1)
                    if not s.yes and target=='python':lines.append(indent+'    pass')
                    lines.append(indent+('else:' if target=='python' else 'else' if target=='lua' else '} else {'))
                    emit_body(s.no,level+1)
                    if not s.no and target=='python':lines.append(indent+'    pass')
                    if target!='python':lines.append(indent+('end' if target=='lua' else '}'))
                elif isinstance(s,Repeat):
                    i,n=s.index,s.count
                    if target=='python':loop=f'for {i} in range({n}):'
                    elif target=='lua':loop=f'for {i} = 0, {n-1} do'
                    elif target=='rust':loop=f'for {i} in 0_i64..{n}_i64 {{'
                    elif target=='go':loop=f'for {i} := int64(0); {i} < int64({n}); {i}++ {{'
                    elif target in ('c','cpp'):
                        typ='int64_t' if target=='c' else 'std::int64_t'
                        loop=f'for ({typ} {i} = 0; {i} < {n}; ++{i}) {{'
                    else:loop=f'for (let {i} = 0; {i} < {n}; {i}++) {{'
                    lines.append(indent+loop)
                    names.add(i)
                    emit_body(s.body,level+1)
                    names.remove(i)
                    if not s.body and target=='python':lines.append(indent+'    pass')
                    if target!='python':lines.append(indent+('end' if target=='lua' else '}'))
                elif isinstance(s,Return):
                    value=expression(s.value,target)
                    if target=='rust':lines.append(indent+value)
                    else:lines.append(indent+'return '+value+(';' if target in ('javascript','typescript','c','cpp') else ''))
        emit_body(f.body,1)
        if target!='python':lines.append('end' if target=='lua' else '}')
        lines.append('')
    if target=='lua':lines.append('return { '+', '.join(f.name+' = '+f.name for f in program.functions)+' }')
    return '\n'.join(lines)+'\n'


def emit_sql(program):
    """Lower assignments/branches/loops into SQLite CTEs with bound parameters."""
    parameters=list(dict.fromkeys(p for f in program.functions for p in f.parameters))
    ctes=['inputs AS (SELECT '+', '.join(':'+p+' AS '+p for p in parameters)+')']
    selects=[]
    for f in program.functions:
        previous='inputs'
        env={p:p for p in f.parameters}
        counter=0
        def sql_expr(e,scope):
            if isinstance(e,Literal):return str(e.value)
            if isinstance(e,Ref):return scope[e.name]
            return f'({sql_expr(e.left,scope)} {e.op} {sql_expr(e.right,scope)})'
        def symbolic(body,scope):
            result=scope.copy()
            for s in body:
                if isinstance(s,Set):result[s.name]=sql_expr(s.value,result)
                elif isinstance(s,If):
                    test=sql_expr(s.condition,result)
                    yes,no=symbolic(s.yes,result),symbolic(s.no,result)
                    result={k:yes[k] if yes[k]==no[k] else f'(CASE WHEN {test} THEN {yes[k]} ELSE {no[k]} END)' for k in result}
                elif isinstance(s,Repeat):
                    for i in range(s.count):
                        result[s.index]=str(i)
                        result=symbolic(s.body,result)
                    result.pop(s.index)
                else:raise ValueError('unexpected statement inside SQL branch')
            return result
        def step(values):
            nonlocal previous,counter,env
            counter+=1
            current=f'{f.name}_s{counter}'
            ctes.append(current+' AS (SELECT '+', '.join(value+' AS '+name for name,value in values.items())+' FROM '+previous+')')
            env={name:name for name in values}
            previous=current
        def lower(body,indices=None):
            indices=indices or {}
            for s in body:
                scope={**env,**indices}
                if isinstance(s,Set):step({**env,s.name:sql_expr(s.value,scope)})
                elif isinstance(s,If):
                    lowered=symbolic((s,),scope)
                    step({k:lowered[k] for k in env})
                elif isinstance(s,Repeat):
                    for i in range(s.count):lower(s.body,{**indices,s.index:str(i)})
                elif isinstance(s,Return):
                    selects.append(f"SELECT '{f.name}' AS function_name, {sql_expr(s.value,scope)} AS result FROM {previous}")
        lower(f.body)
    return '-- Generated SQLite query. Bind integer inputs within +/-1,000,000.\nWITH\n'+',\n'.join(ctes)+'\n'+'\nUNION ALL\n'.join(selects)+';\n'
