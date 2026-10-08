"""Language-independent integer programs with bounded, checked semantics."""
from dataclasses import dataclass
import keyword
import re

INPUT_LIMIT = 1_000_000
EXACT_LIMIT = 2**53 - 1  # Exact integer range shared by JS Number and all targets.
RESERVED = set('gen defer fallthrough chan map make abstract become box final macro override priv typeof unsized virtual dyn impl trait move ref unsafe where use mod table group order limit join index pragma references collate desc asc constraint key left right cross natural inner outer distinct values having primary foreign check alter create insert update drop unique trigger view union all offset null exists on'.split()) | set(keyword.kwlist) | set('fn let mut pub func var const function export return if else for while do end local package int int64_t bool true false null nil class struct auto case switch default static void main type interface select range break continue new delete namespace using public private protected self crate super import from as in match loop print require undefined yield await try catch throw async then and or not goto float double char short long signed unsigned sizeof typedef union enum volatile extern register restrict inline'.split())


@dataclass(frozen=True)
class Literal:
    value: int


@dataclass(frozen=True)
class Ref:
    name: str


@dataclass(frozen=True)
class Binary:
    op: str
    left: object
    right: object


@dataclass(frozen=True)
class Set:
    name: str
    value: object


@dataclass(frozen=True)
class If:
    condition: object
    yes: tuple
    no: tuple


@dataclass(frozen=True)
class Repeat:
    index: str
    count: int
    body: tuple


@dataclass(frozen=True)
class Return:
    value: object


@dataclass(frozen=True)
class Function:
    name: str
    parameters: tuple
    body: tuple


@dataclass(frozen=True)
class Program:
    functions: tuple

    def to_data(self):
        def encode(v):
            if hasattr(v, '__dataclass_fields__'):
                return {'node': type(v).__name__, **{k: encode(getattr(v,k)) for k in v.__dataclass_fields__}}
            if isinstance(v, (tuple,list)):
                return [encode(x) for x in v]
            return v
        return {'schema':'markovjunior.program/1','input_limit':INPUT_LIMIT,'program':encode(self)}

    @classmethod
    def from_data(cls, data):
        """Read the exported JSON IR without executing source code."""
        if not isinstance(data, dict) or data.get('schema') != 'markovjunior.program/1' or data.get('input_limit') != INPUT_LIMIT:
            raise ValueError('unsupported program IR schema or input domain')
        classes = {c.__name__: c for c in (Literal, Ref, Binary, Set, If, Repeat, Return, Function, Program)}
        count = 0
        def decode(value, depth=0):
            nonlocal count
            count += 1
            if count > 10000 or depth > 32:
                raise ValueError('program IR budget exceeded')
            if isinstance(value, list):
                return tuple(decode(v, depth + 1) for v in value)
            if isinstance(value, dict):
                kind = classes.get(value.get('node'))
                if kind is None or set(value) != set(kind.__dataclass_fields__) | {'node'}:
                    raise ValueError('unknown IR node or fields')
                return kind(**{k: decode(value[k], depth + 1) for k in kind.__dataclass_fields__})
            if type(value) not in (str, int):
                raise ValueError('invalid IR value')
            return value
        result = decode(data.get('program'))
        if not isinstance(result, cls):
            raise ValueError('root IR node must be Program')
        return result.validate()

    def validate(self):
        if not isinstance(self.functions,tuple) or not 1 <= len(self.functions) <= 64 or not all(isinstance(f,Function) for f in self.functions):
            raise ValueError('program needs 1..64 functions')
        names=set()
        for f in self.functions:
            identifier(f.name)
            if f.name in names:
                raise ValueError('duplicate function name')
            names.add(f.name)
            if not isinstance(f.parameters,tuple) or not all(isinstance(p,str) for p in f.parameters) or not 1 <= len(f.parameters) <= 8 or len(set(f.parameters)) != len(f.parameters):
                raise ValueError('function needs 1..8 distinct parameters')
            for p in f.parameters:
                identifier(p)
            if not f.body or not isinstance(f.body[-1], Return) or any(isinstance(s, Return) for s in f.body[:-1]):
                raise ValueError('function must end in a single return')
            env={p:(-INPUT_LIMIT,INPUT_LIMIT) for p in f.parameters}
            checked_body(f.body,env,set(f.parameters),0,allow_return=True)
        return self

    def evaluate(self, name, *arguments):
        f=next((f for f in self.functions if f.name==name),None)
        if f is None:
            raise KeyError(name)
        if len(arguments)!=len(f.parameters) or any(type(a) is not int or abs(a)>INPUT_LIMIT for a in arguments):
            raise ValueError(f'arguments must be integers within ±{INPUT_LIMIT}')
        env=dict(zip(f.parameters,arguments))
        def expr(e):
            if isinstance(e,Literal):return e.value
            if isinstance(e,Ref):return env[e.name]
            a,b=expr(e.left),expr(e.right)
            return {'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,
                    '<':lambda:a<b,'<=':lambda:a<=b,'>':lambda:a>b,'>=':lambda:a>=b,
                    '==':lambda:a==b,'!=':lambda:a!=b}[e.op]()
        def body(statements):
            for s in statements:
                if isinstance(s,Set):env[s.name]=expr(s.value)
                elif isinstance(s,If):body(s.yes if expr(s.condition) else s.no)
                elif isinstance(s,Repeat):
                    for i in range(s.count):
                        env[s.index]=i
                        body(s.body)
                    env.pop(s.index,None)
                elif isinstance(s,Return):return expr(s.value)
        return body(f.body)


def identifier(name):
    if not isinstance(name,str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,47}',name) or name in RESERVED:
        raise ValueError(f'invalid portable identifier: {name!r}')


def checked_expr(e,env,depth=0):
    if depth>8:
        raise ValueError('expression depth exceeds 8')
    if isinstance(e,Literal):
        if type(e.value) is not int:
            raise ValueError('integer literal required')
        bounds=(e.value,e.value)
    elif isinstance(e,Ref):
        if e.name not in env:
            raise ValueError(f'undefined variable: {e.name}')
        bounds=env[e.name]
    elif isinstance(e,Binary):
        a,b=checked_expr(e.left,env,depth+1),checked_expr(e.right,env,depth+1)
        if a is None or b is None:
            raise ValueError('arithmetic operands must be integers')
        if e.op in ('<','<=','>','>=','==','!='):
            return None
        if e.op=='+':bounds=(a[0]+b[0],a[1]+b[1])
        elif e.op=='-':bounds=(a[0]-b[1],a[1]-b[0])
        elif e.op=='*':
            vals=[x*y for x in a for y in b]
            bounds=min(vals),max(vals)
        else:raise ValueError(f'unsupported portable operator: {e.op}')
    else:raise ValueError(f'unknown expression {type(e).__name__}')
    if max(abs(x) for x in bounds)>EXACT_LIMIT:
        raise ValueError('program can exceed the exact integer range of a target language')
    return bounds


def checked_body(statements,env,immutable,depth,allow_return=False):
    if not isinstance(statements,tuple) or depth>12 or len(statements)>64:
        raise ValueError('statement budget exceeded')
    for s in statements:
        if isinstance(s,Set):
            identifier(s.name)
            if s.name in immutable:
                raise ValueError('parameters and loop indices are immutable')
            value=checked_expr(s.value,env)
            if value is None:raise ValueError('assignment must contain an integer')
            env[s.name]=value
        elif isinstance(s,If):
            if checked_expr(s.condition,env) is not None:
                raise ValueError('if requires a comparison')
            a,b=env.copy(),env.copy()
            checked_body(s.yes,a,immutable,depth+1)
            checked_body(s.no,b,immutable,depth+1)
            if set(a)!=set(env) or set(b)!=set(env):
                raise ValueError('initialize variables before conditionals')
            for key in env:env[key]=(min(a[key][0],b[key][0]),max(a[key][1],b[key][1]))
        elif isinstance(s,Repeat):
            identifier(s.index)
            if s.index in env or type(s.count) is not int or not 1<=s.count<=16:
                raise ValueError('repeat needs a fresh index and count 1..16')
            original_keys=set(env)
            for i in range(s.count):
                env[s.index]=(i,i)
                checked_body(s.body,env,immutable|{s.index},depth+1)
                if set(env)-{s.index}!=original_keys:
                    raise ValueError('initialize variables before loops')
            env.pop(s.index)
        elif isinstance(s,Return):
            if not allow_return or checked_expr(s.value,env) is None:
                raise ValueError('return must be the final integer expression of the function')
        else:raise ValueError(f'unknown statement {type(s).__name__}')
