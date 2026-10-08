"""Faithful Python translation of MarkovJunior core. MIT, Maxim Gumin (2022)."""
import math
from collections import deque
from pathlib import Path
import xml.etree.ElementTree as ET


def attr(e, name, default=None, kind=None):
    v = e.get(name)
    if v is None:
        return default
    if kind is None:
        kind = type(default) if default is not None else str
    if kind is bool:
        return v.lower() == 'true'
    return kind(v)


def int32(value):
    """Unchecked signed Int32 arithmetic, as used by the original C# RNG."""
    return (value + 2147483648) % 4294967296 - 2147483648


class DotNetRandom:
    """System.Random(seed), including the legacy seeded algorithm in .NET 10."""
    BIG = 2147483647

    def __init__(self, seed):
        seed = int(seed)
        subtraction = self.BIG if seed == -2147483648 else abs(seed)
        mj = 161803398 - subtraction
        self.a = [0] * 56
        self.a[55] = mj
        mk = 1
        for i in range(1, 55):
            ii = 21 * i % 55
            self.a[ii] = mk
            mk = int32(mj - mk)
            if mk < 0:
                mk = int32(mk + self.BIG)
            mj = self.a[ii]
        for _ in range(4):
            for i in range(1, 56):
                self.a[i] = int32(self.a[i] - self.a[1 + (i + 30) % 55])
                if self.a[i] < 0:
                    self.a[i] = int32(self.a[i] + self.BIG)
        self.i, self.j = 0, 21

    def sample_int(self):
        self.i = 1 if self.i + 1 >= 56 else self.i + 1
        self.j = 1 if self.j + 1 >= 56 else self.j + 1
        v = int32(self.a[self.i] - self.a[self.j])
        if v == self.BIG:
            v -= 1
        if v < 0:
            v += self.BIG
        self.a[self.i] = v
        return v

    def double(self):
        return self.sample_int() * (1.0 / self.BIG)

    def next(self, maximum=None):
        if maximum is None:
            return self.sample_int()
        if maximum < 0:
            raise ValueError('maximum must be nonnegative')
        return int(self.double() * maximum)

    def shuffle(self, n):
        a = [0] * n
        for i in range(n):
            j = self.next(i + 1)
            a[i] = a[j]
            a[j] = i
        return a


def weighted(weights, r):
    threshold = r * sum(weights)
    partial = 0.0
    for i, w in enumerate(weights):
        partial += w
        if partial >= threshold:
            return i
    return 0


def ords(data, uniques=None):
    uniques = [] if uniques is None else uniques
    lookup = {v: i for i, v in enumerate(uniques)}
    result = []
    for v in data:
        if v not in lookup:
            lookup[v] = len(uniques)
            uniques.append(v)
        result.append(lookup[v])
    return result, len(uniques)


def symmetry(d2, name, default):
    if name is None:
        return default
    square = {'()':[0], '(x)':[0,1], '(y)':[0,5], '(x)(y)':[0,1,4,5],
              '(xy+)':[0,2,4,6], '(xy)':list(range(8))}
    cube = {'()':[0], '(x)':[0,1], '(z)':[0,17], '(xy)':list(range(8)),
            '(xyz+)':list(range(0,48,2)), '(xyz)':list(range(48))}
    indices = (square if d2 else cube)[name]
    return [i in indices for i in range(8 if d2 else 48)]


def symmetries(thing, a, r, same, subgroup=None, b=None):
    s = [None] * (8 if b is None else 48)
    s[0] = thing
    for i in (2,4,6):
        s[i] = a(s[i-2])
    if b is not None:
        for i in range(8,32,2):
            s[i] = b(s[i-8])
        for i in range(32,40,2):
            s[i] = a(s[i-24])
        for i in range(40,48,2):
            s[i] = a(s[i-16])
    for i in range(1,len(s),2):
        s[i] = r(s[i-1])
    result = []
    for i, t in enumerate(s):
        if (subgroup is None or subgroup[i]) and not any(same(t, q) for q in result):
            result.append(t)
    return result


def rotated(p, n):
    return [p[n-1-y+x*n] for y in range(n) for x in range(n)]


def reflected(p, n):
    return [p[n-1-x+y*n] for y in range(n) for x in range(n)]


def positions(mx, my, mz):
    for z in range(mz):
        for y in range(my):
            for x in range(mx):
                yield x,y,z


class Grid:
    def __init__(self, e, mx, my, mz):
        self.MX, self.MY, self.MZ = mx,my,mz
        self.characters = list(e.attrib['values'].replace(' ', ''))
        self.C = len(self.characters)
        if len(set(self.characters)) != self.C:
            raise ValueError('repeated grid symbols')
        self.values = {c:i for i,c in enumerate(self.characters)}
        self.waves = {c:1<<i for c,i in self.values.items()}
        self.waves['*'] = (1 << self.C) - 1
        q = deque([e])
        while q:
            p = q.popleft()
            if p.tag == 'union':
                c = p.attrib['symbol']
                if c in self.waves:
                    raise ValueError('repeated union symbol')
                self.waves[c] = self.wave(p.attrib['values'])
            q.extend(c for c in p if c.tag in ('markov','sequence','union'))
        self.folder = e.get('folder')
        self.state = bytearray(mx*my*mz)
        self.mask = [False] * len(self.state)

    def wave(self, s):
        return sum(1 << self.values[c] for c in s)

    def clear(self):
        self.state[:] = bytes(len(self.state))

    def index(self, x,y,z):
        return x+y*self.MX+z*self.MX*self.MY

    def matches(self, rule, x,y,z):
        for dx,dy,dz in positions(rule.IMX, rule.IMY, rule.IMZ):
            if not rule.input[dx+dy*rule.IMX+dz*rule.IMX*rule.IMY] & (1 << self.state[self.index(x+dx,y+dy,z+dz)]):
                return False
        return True


class Rule:
    def __init__(self, inp, idims, out, odims, c, p=1.0):
        self.input, self.output = list(inp), list(out)
        self.IMX,self.IMY,self.IMZ = idims
        self.OMX,self.OMY,self.OMZ = odims
        self.p, self.original = p,False
        self.ishifts = [[] for _ in range(c)]
        self.oshifts = [[] for _ in range(c)] if idims == odims else None
        for i,(x,y,z) in enumerate(positions(*idims)):
            for v in range(c):
                if inp[i] & 1 << v:
                    self.ishifts[v].append((x,y,z))
                if self.oshifts is not None and (out[i] == 255 or out[i] == v):
                    self.oshifts[v].append((x,y,z))
        wildcard = (1<<c)-1
        self.binput = [255 if w == wildcard else (w & -w).bit_length()-1 for w in inp]

    def transform(self, kind):
        def tr(data, mx,my,mz):
            if kind == 'z':
                return [data[mx-1-y+x*mx+z*mx*my] for x,y,z in positions(my,mx,mz)], (my,mx,mz)
            if kind == 'y':
                return [data[mx-1-z+y*mx+x*mx*my] for x,y,z in positions(mz,my,mx)], (mz,my,mx)
            return [data[mx-1-x+y*mx+z*mx*my] for x,y,z in positions(mx,my,mz)], (mx,my,mz)
        inp, di = tr(self.input,self.IMX,self.IMY,self.IMZ)
        out, do = tr(self.output,self.OMX,self.OMY,self.OMZ)
        return Rule(inp,di,out,do,len(self.ishifts),self.p)

    def same(self, other):
        return (self.IMX,self.IMY,self.IMZ,self.OMX,self.OMY,self.OMZ,self.input,self.output) == (other.IMX,other.IMY,other.IMZ,other.OMX,other.OMY,other.OMZ,other.input,other.output)

    def variants(self, group, d2):
        return symmetries(self,lambda q:q.transform('z'),lambda q:q.transform('r'),Rule.same,group,None if d2 else lambda q:q.transform('y'))

    @staticmethod
    def parse(s):
        layers = [a.split('/') for a in s.split(' ')][::-1]
        mx,my,mz = len(layers[0][0]),len(layers[0]),len(layers)
        if any(len(a)!=my or any(len(row)!=mx for row in a) for a in layers):
            raise ValueError('nonrectangular pattern')
        return [v for a in layers for row in a for v in row], (mx,my,mz)

    @classmethod
    def load(cls, e, gin, gout, base):
        from .graphics import load_bitmap, load_vox
        def resource(name):
            filename = Path(base)/'resources'/'rules'
            if gout.folder:
                filename /= gout.folder
            filename /= name + ('.png' if gin.MZ == 1 else '.vox')
            data,mx,my,mz = (load_bitmap if gin.MZ == 1 else load_vox)(filename)
            legend = e.attrib['legend']
            indices, n = ords(data)
            if n > len(legend):
                raise ValueError(f'legend too short: {filename}')
            return [legend[i] for i in indices],(mx,my,mz)
        if e.get('file') is not None:
            data,(mx,my,mz) = resource(e.get('file'))
            if mx % 2:
                raise ValueError('odd rule resource width')
            dims = mx//2,my,mz
            inp = [data[x+y*mx+z*mx*my] for x,y,z in positions(*dims)]
            out = [data[x+mx//2+y*mx+z*mx*my] for x,y,z in positions(*dims)]
            di = do = dims
        else:
            inp,di = cls.parse(e.get('in')) if e.get('in') is not None else resource(e.attrib['fin'])
            out,do = cls.parse(e.get('out')) if e.get('out') is not None else resource(e.attrib['fout'])
        if gin is gout and di != do:
            raise ValueError('input/output dimensions differ')
        return cls([gin.waves[c] for c in inp],di,[255 if c=='*' else gout.values[c] for c in out],do,gin.C,attr(e,'p',1.0))


NODE_NAMES = ('one','all','prl','markov','sequence','path','map','convolution','convchain','wfc')


class Node:
    def __init__(self, e, group, ip, grid):
        self.ip,self.grid = ip,grid
    def reset(self):
        pass


class Branch(Node):
    def __init__(self,e,group,ip,grid):
        super().__init__(e,group,ip,grid)
        self.parent,self.n = None,0
        group = symmetry(ip.grid.MZ == 1,e.get('symmetry'),group)
        self.nodes = [factory(c,group,ip,grid) for c in e if c.tag in NODE_NAMES]
        for child in self.nodes:
            if isinstance(child,Branch):
                child.parent = None if child.__class__.__name__ in ('MapNode','OverlapNode','TileNode') else self

    def reset(self):
        for node in self.nodes:
            node.reset()
        self.n = 0

    def go(self):
        while self.n < len(self.nodes):
            node = self.nodes[self.n]
            if isinstance(node,Branch):
                self.ip.current = node
            if node.go():
                return True
            self.n += 1
        self.ip.current = self.ip.current.parent
        self.reset()
        return False


class MarkovNode(Branch):
    def go(self):
        self.n = 0
        return super().go()


class Interpreter:
    def __init__(self,e,mx,my,mz,base='.'):
        self.base = Path(base)
        self.origin = attr(e,'origin',False)
        self.grid = self.startgrid = Grid(e,mx,my,mz)
        group = symmetry(mz==1,e.get('symmetry'),[True]*(8 if mz==1 else 48))
        top = factory(e,group,self,self.grid)
        if isinstance(top,Branch):
            self.root = top
        else:
            self.root = MarkovNode(ET.Element('markov'),group,self,self.grid)
            self.root.nodes = [top]
        self.changes,self.first = [],[]
        self.counter = 0

    def run(self,seed,steps=50000,frames=False):
        self.random = DotNetRandom(seed)
        self.grid = self.startgrid
        self.grid.clear()
        if self.origin:
            self.grid.state[self.grid.index(self.grid.MX//2,self.grid.MY//2,self.grid.MZ//2)] = 1
        self.changes.clear()
        self.first = [0]
        self.root.reset()
        self.current,self.counter,self.gif = self.root,0,frames
        while self.current is not None and (steps <= 0 or self.counter < steps):
            if frames:
                yield self.snapshot()
            self.current.go()
            self.counter += 1
            self.first.append(len(self.changes))
        yield self.snapshot()

    def snapshot(self):
        g = self.grid
        return bytes(g.state),g.characters,g.MX,g.MY,g.MZ


def factory(e,group,ip,grid):
    from .rules import OneNode,AllNode,ParallelNode
    from .operations import PathNode,MapNode,ConvolutionNode,ConvChainNode
    from .wfc import OverlapNode,TileNode
    classes = {'markov':MarkovNode,'sequence':Branch,'one':OneNode,'all':AllNode,'prl':ParallelNode,
               'path':PathNode,'map':MapNode,'convolution':ConvolutionNode,'convchain':ConvChainNode,
               'wfc':OverlapNode if e.get('sample') else TileNode}
    return classes[e.tag](e,group,ip,grid)
