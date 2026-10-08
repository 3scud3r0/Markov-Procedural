"""Seeded generators for typed programs, grammars, structured data and scenes."""
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from .ir import Program,Function,Literal,Ref,Binary,Set,If,Repeat,Return,identifier
from .model import Document
from ..core import weighted,Interpreter


def integer(params,name,default,minimum,maximum):
    v=params.get(name,default)
    if type(v) is not int or not minimum<=v<=maximum:
        raise ValueError(f'{name} must be an integer in {minimum}..{maximum}')
    return v


def program(params,context):
    rng=context.random
    count=integer(params,'functions',4,1,64)
    depth=integer(params,'expression_depth',2,0,4)
    loops=integer(params,'iterations',4,1,8)
    prefix=params.get('prefix','proc')
    identifier(prefix)
    def expression(d):
        if d==0:
            return (Ref('x'),Ref('y'),Literal(rng.next(19)-9))[rng.next(3)]
        op=('+','-','*')[rng.next(3)]
        return Binary(op,expression(d-1),Literal(rng.next(9)+1) if op=='*' else expression(d-1))
    functions=[]
    for k in range(count):
        condition=Binary(('<','>','==')[rng.next(3)],Ref('value'),Binary('+',Ref('x'),Literal(rng.next(41)-20)))
        step=Binary('+',Ref('iteration'),Literal(rng.next(9)+1))
        functions.append(Function(f'{prefix}_{k:03d}',('x','y'),(
            Set('value',expression(depth)),
            Repeat('iteration',loops,(
                If(condition,(Set('value',Binary('+',Ref('value'),step)),),
                             (Set('value',Binary('-',Ref('value'),Literal(rng.next(9)+1))),)),
                Set('value',Binary('+',Ref('value'),Ref('y'))),
            )),
            Return(Ref('value')),
        )))
    return Document('program',Program(tuple(functions)).validate(),{'input_limit':1_000_000})


REF_PATTERN=re.compile(r'(?<!\\)<([^<>\s]+)>')


class Grammar:
    """Weighted productions with a productive-depth bound, not blind recursion."""
    def __init__(self,rules):
        if not isinstance(rules,dict) or not rules or len(rules)>500:
            raise ValueError('rules must be an object with 1..500 productions')
        self.rules={}
        for name,alternatives in rules.items():
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',name):
                raise ValueError('invalid grammar rule name')
            if not isinstance(alternatives,list) or not 1<=len(alternatives)<=500:
                raise ValueError(f'{name}: expected a nonempty list of alternatives')
            checked=[]
            for a in alternatives:
                text,weight=(a,1.0) if isinstance(a,str) else (a.get('text'),a.get('weight',1.0)) if isinstance(a,dict) else (None,0)
                if not isinstance(text,str) or len(text)>100_000 or type(weight) not in (int,float) or not math.isfinite(weight) or weight<=0:
                    raise ValueError(f'{name}: invalid text or weight')
                checked.append((text,float(weight)))
            self.rules[name]=checked
        for alternatives in self.rules.values():
            for text,_ in alternatives:
                for ref in REF_PATTERN.findall(text):
                    if ref.startswith('int:'):
                        self.int_bounds(ref)
                    elif ref not in self.rules:raise ValueError(f'undefined grammar rule: {ref}')
        self.depths={name:math.inf for name in self.rules}
        for _ in range(len(self.rules)+1):
            changed=False
            for name,alts in self.rules.items():
                best=min(self.cost(text) for text,_ in alts)
                if best<self.depths[name]:
                    self.depths[name]=best
                    changed=True
            if not changed:break

    @staticmethod
    def int_bounds(ref):
        try:
            _,a,b=ref.split(':')
            a,b=int(a),int(b)
        except (ValueError,TypeError):raise ValueError('integer reference must be <int:minimum:maximum>') from None
        if not -1_000_000_000<=a<=b<=1_000_000_000:
            raise ValueError('integer reference bounds must be ordered and within ±1,000,000,000')
        return a,b

    def cost(self,text):
        return 1+max((self.depths[ref] for ref in REF_PATTERN.findall(text) if not ref.startswith('int:')),default=0)

    def expand(self,start,rng,max_depth=24,max_expansions=5000,max_chars=100_000):
        trace=[]
        characters=0
        def expand_text(text,remaining):
            nonlocal characters
            pieces=[]
            end=0
            for m in REF_PATTERN.finditer(text):
                literal=text[end:m.start()].replace('\\<','<')
                characters+=len(literal)
                pieces.append(literal)
                ref=m.group(1)
                if ref.startswith('int:'):
                    a,b=self.int_bounds(ref)
                    v=str(a+rng.next(b-a+1))
                    characters+=len(v)
                    pieces.append(v)
                else:
                    if ref not in self.rules:raise ValueError(f'undefined grammar rule: {ref}')
                    if len(trace)>=max_expansions:raise ValueError('grammar expansion budget exceeded')
                    viable=[(i,t,w) for i,(t,w) in enumerate(self.rules[ref]) if self.cost(t)<=remaining]
                    if not viable:raise ValueError(f'grammar cannot finish {ref!r} within the depth budget')
                    # Normalize large finite weights before addition to avoid infinity.
                    scale=max(w for _,_,w in viable)
                    i,t,w=viable[weighted([w/scale for _,_,w in viable],rng.double())]
                    trace.append({'rule':ref,'alternative':i})
                    pieces.append(expand_text(t,remaining-1))
                if characters>max_chars:raise ValueError('grammar character budget exceeded')
                end=m.end()
            tail=text[end:].replace('\\<','<')
            characters+=len(tail)
            if characters>max_chars:raise ValueError('grammar character budget exceeded')
            pieces.append(tail)
            return ''.join(pieces)
        return expand_text(start,max_depth),trace


def grammar(params,context):
    depth=integer(params,'max_depth',24,1,128)
    expansions=integer(params,'max_expansions',5000,1,100_000)
    chars=integer(params,'max_chars',100_000,1,1_000_000)
    start=params.get('start','<start>')
    if not isinstance(start,str):raise ValueError('grammar start must be text')
    g=Grammar(params.get('rules'))
    text,trace=g.expand(start,context.random,depth,expansions,chars)
    return Document('text',text,{'expansions':len(trace),'trace':trace})


def data(params,context):
    rng=context.random
    budget=integer(params,'max_nodes',10000,1,100_000)
    nodes=0
    def generate(schema,depth=0):
        nonlocal nodes
        nodes+=1
        if nodes>budget or depth>20:raise ValueError('data structure budget exceeded')
        if not isinstance(schema,dict):raise ValueError('data schema must be an object')
        kind=schema.get('type')
        if kind=='object':
            properties=schema.get('properties')
            if not isinstance(properties,dict):raise ValueError('object needs properties')
            return {key:generate(value,depth+1) for key,value in properties.items()}
        if kind=='array':
            n=integer(schema,'length',5,0,10000)
            return [generate(schema.get('items'),depth+1) for _ in range(n)]
        if kind=='integer':
            a=integer(schema,'min',0,-1_000_000_000,1_000_000_000)
            b=integer(schema,'max',100,a,1_000_000_000)
            return a+rng.next(b-a+1)
        if kind=='number':
            a,b=schema.get('min',0),schema.get('max',1)
            if type(a) not in (int,float) or type(b) not in (int,float) or not math.isfinite(a) or not math.isfinite(b) or a>b or max(abs(a),abs(b))>1e12:
                raise ValueError('number bounds must be finite, ordered and within ±1e12')
            return round(a+(b-a)*rng.double(),6)
        if kind=='boolean':
            p=schema.get('probability',0.5)
            if type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1:raise ValueError('boolean probability must be in 0..1')
            return rng.double()<p
        if kind=='string':
            choices=schema.get('choices')
            if choices is not None:
                if not isinstance(choices,list) or not choices or not all(isinstance(s,str) for s in choices):raise ValueError('string choices must be a nonempty list of strings')
                return choices[rng.next(len(choices))]
            length=integer(schema,'length',12,0,10000)
            alphabet=schema.get('alphabet','abcdefghijklmnopqrstuvwxyz')
            if not isinstance(alphabet,str) or not alphabet:raise ValueError('string needs a nonempty alphabet')
            return ''.join(alphabet[rng.next(len(alphabet))] for _ in range(length))
        if kind=='literal':return schema.get('value')
        raise ValueError(f'unknown data schema type: {kind}')
    return Document('data',generate(params.get('schema')),{'nodes':nodes})


def scene(params,context):
    rng=context.random
    width=integer(params,'width',1000,100,4000)
    height=integer(params,'height',600,100,4000)
    trees=integer(params,'trees',7,1,40)
    depth=integer(params,'depth',5,1,7)
    shapes=[]
    def add(tag,**attrs):
        shapes.append({'tag':tag,'attrs':{k.replace('_','-'):round(v,3) if isinstance(v,float) else v for k,v in attrs.items()}})
    add('rect',x=0,y=0,width=width,height=height,fill='#101827')
    add('circle',cx=width*0.79,cy=height*0.18,r=height*0.082,fill='#f1d998',opacity=0.92)
    for layer,color in enumerate(('#1c2d3d','#244437','#315845')):
        y=height*(0.57+layer*0.12)
        c1=height*(0.15+0.2*rng.double())
        c2=height*(0.2+0.2*rng.double())
        path=f'M 0 {y:.3f} C {width*.3:.3f} {y-c1:.3f}, {width*.64:.3f} {y+c2:.3f}, {width} {y:.3f} L {width} {height} L 0 {height} Z'
        add('path',d=path,fill=color)
    palette=('#82d6ae','#b9de8b','#e8b16e','#efcf9c')
    def branch(x,y,length,angle,remaining,thickness,color):
        xx,yy=x+math.cos(angle)*length,y+math.sin(angle)*length
        bend=(rng.double()-0.5)*length*0.3
        path=f'M {x:.3f} {y:.3f} Q {(x+xx)/2+bend:.3f} {(y+yy)/2:.3f} {xx:.3f} {yy:.3f}'
        add('path',d=path,fill='none',stroke='#b6aa8b',stroke_width=thickness,stroke_linecap='round')
        if remaining==0:
            add('circle',cx=xx,cy=yy,r=max(2,length*0.38),fill=color,opacity=0.82)
            return
        spread=0.22+rng.double()*0.33
        for direction in (-1,1):
            branch(xx,yy,length*(0.63+0.11*rng.double()),angle+direction*spread,remaining-1,max(0.7,thickness*0.68),color)
    for k in range(trees):
        x=width*(k+0.5)/trees+(rng.double()-0.5)*width/(trees*3)
        y=height*(0.82+0.08*rng.double())
        length=height*(0.1+0.06*rng.double())
        branch(x,y,length,-math.pi/2+(rng.double()-0.5)*0.2,depth,3.5+rng.double()*3,palette[rng.next(len(palette))])
    return Document('scene',{'width':width,'height':height,'elements':shapes}, {'entities':len(shapes),'theme':'branching garden'})


def grid(params,context):
    name=params.get('model','MazeGrowth')
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',name):raise ValueError('invalid model name')
    mx=integer(params,'width',31,1,128)
    my=integer(params,'height',31,1,128)
    mz=integer(params,'depth',1,1,64)
    steps=integer(params,'steps',50000,1,1_000_000)
    cell_size=integer(params,'cell_size',12,1,32)
    model=context.base/'models'/(name+'.xml')
    ip=Interpreter(ET.parse(model).getroot(),mx,my,mz,context.base)
    state,legend,mx,my,mz=list(ip.run(context.seed,steps))[-1]
    layer=integer(params,'layer',0,0,mz-1)
    colors={e.attrib['symbol']:'#'+e.attrib['value'] for e in ET.parse(context.base/'resources'/'palette.xml').getroot()}
    elements=[]
    for y in range(my):
        for x in range(mx):
            symbol=legend[state[x+y*mx+layer*mx*my]]
            elements.append({'tag':'rect','attrs':{'x':x*cell_size,'y':y*cell_size,'width':cell_size,'height':cell_size,'fill':colors[symbol]},'symbol':symbol})
    return Document('scene',{'width':mx*cell_size,'height':my*cell_size,'elements':elements},
                    {'model':name,'grid':[mx,my,mz],'layer':layer,'steps':ip.counter,'entities':len(elements)})


def program_ir(params,context):
    return Document('program',Program.from_data(params.get('ir')),{'input_limit':1_000_000,'source':'explicit IR'})
