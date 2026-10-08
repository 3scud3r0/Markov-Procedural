"""Overlapping and tiled Wave Function Collapse, translated from MarkovJunior."""
import copy
import math
import random
import xml.etree.ElementTree as ET
from .core import Branch,Grid,DotNetRandom,attr,symmetry,symmetries,rotated,reflected,ords,positions,weighted
from .graphics import load_bitmap,load_vox

DIRS = ((1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,1),(0,0,-1))
OPPOSITE = (2,3,0,1,5,4)


class Wave:
    def __init__(self,length,propagator,weights,shannon):
        p = len(weights)
        self.data = [[True]*p for _ in range(length)]
        initial = [[len(propagator[OPPOSITE[d]][t]) for d in range(len(propagator))] for t in range(p)]
        self.compatible = [[r[:] for r in initial] for _ in range(length)]
        self.ones = [p]*length
        if shannon:
            total = sum(weights)
            logs = sum(w*math.log(w) for w in weights)
            self.weights,self.logs = [total]*length,[logs]*length
            self.entropies = [math.log(total)-logs/total]*length


class WFCNode(Branch):
    def finish_load(self,e,group,ip,g):
        self.P = len(self.weights)
        self.shannon,self.tries = attr(e,'shannon',False),attr(e,'tries',1000)
        self.weightlogs = [w*math.log(w) for w in self.weights]
        self.wave = None
        self.stack = []
        super().__init__(e,group,ip,self.newgrid)
        self.grid = g
        self.reset()

    def reset(self):
        super().reset()
        self.n,self.firstgo = -1,True

    def ban(self,i,t):
        w = self.wave
        w.data[i][t] = False
        w.compatible[i][t][:] = [0]*len(self.propagator)
        self.stack.append((i,t))
        w.ones[i] -= 1
        if self.shannon:
            total = w.weights[i]
            if total>0:
                w.entropies[i] += w.logs[i]/total-math.log(total)
            else:
                w.entropies[i] = math.nan
            w.weights[i] -= self.weights[t]
            w.logs[i] -= self.weightlogs[t]
            total = w.weights[i]
            if total>0:
                w.entropies[i] -= w.logs[i]/total-math.log(total)
            else:
                w.entropies[i] = math.nan

    def propagate(self):
        g = self.grid
        while self.stack:
            i,p = self.stack.pop()
            x,y,z = i%g.MX,i//g.MX%g.MY,i//(g.MX*g.MY)
            for d,(dx,dy,dz) in enumerate(DIRS[:len(self.propagator)]):
                xx,yy,zz = x+dx,y+dy,z+dz
                if not self.periodic and (xx<0 or yy<0 or zz<0 or xx+self.N>g.MX or yy+self.N>g.MY or zz+1>g.MZ):
                    continue
                i2 = g.index(xx%g.MX,yy%g.MY,zz%g.MZ)
                for t in self.propagator[d][p]:
                    comp = self.wave.compatible[i2][t]
                    comp[d] -= 1
                    if comp[d]==0:
                        self.ban(i2,t)
        return self.wave.ones[0]>0

    def next_node(self,rng):
        g,w = self.grid,self.wave
        best,arg = 1e4,-1
        for x,y,z in positions(g.MX,g.MY,g.MZ):
            if not self.periodic and (x+self.N>g.MX or y+self.N>g.MY or z+1>g.MZ):
                continue
            i = g.index(x,y,z)
            remaining = w.ones[i]
            entropy = w.entropies[i] if self.shannon else remaining
            if remaining>1 and entropy<=best:
                noise = 1e-6*rng.double()
                if entropy+noise<best:
                    best,arg = entropy+noise,i
        return arg

    def observe(self,i,rng):
        row = self.wave.data[i]
        r = weighted([self.weights[t] if flag else 0.0 for t,flag in enumerate(row)],rng.double())
        for t in range(self.P):
            if row[t] != (t==r):
                self.ban(i,t)

    def good_seed(self):
        for _ in range(self.tries):
            seed = self.ip.random.next()
            rng = DotNetRandom(seed)
            self.stack.clear()
            self.wave = copy.deepcopy(self.startwave)
            while True:
                node = self.next_node(rng)
                if node<0:
                    return seed
                self.observe(node,rng)
                if not self.propagate():
                    break
        return None

    def go(self):
        if self.n>=0:
            return super().go()
        if self.firstgo:
            self.wave = Wave(len(self.grid.state),self.propagator,self.weights,self.shannon)
            self.stack.clear()
            for i,v in enumerate(self.grid.state):
                if v in self.map:
                    for t,flag in enumerate(self.map[v]):
                        if not flag:
                            self.ban(i,t)
            if not self.propagate():
                return False
            self.startwave = copy.deepcopy(self.wave)
            seed = self.good_seed()
            if seed is None:
                return False
            self.random = DotNetRandom(seed)
            self.stack.clear()
            self.wave = copy.deepcopy(self.startwave)
            self.firstgo = False
            self.newgrid.clear()
            self.ip.grid = self.newgrid
            return True
        node = self.next_node(self.random)
        if node>=0:
            self.observe(node,self.random)
            self.propagate()
        else:
            self.n += 1
        if self.n>=0 or self.ip.gif:
            self.update_state()
        return True


class OverlapNode(WFCNode):
    def __init__(self,e,group,ip,g):
        if g.MZ!=1:
            raise ValueError('overlap WFC is 2D')
        self.N = attr(e,'n',3)
        group = symmetry(True,e.get('symmetry'),group)
        periodic_input = attr(e,'periodicInput',True)
        self.newgrid = Grid(e,g.MX,g.MY,g.MZ)
        self.periodic = True  # The upstream overlap node always uses a periodic output.
        self.name = e.attrib['sample']
        bitmap,sx,sy,_ = load_bitmap(ip.base/'resources'/'samples'/(self.name+'.png'))
        sample,c = ords(bitmap)
        if c>self.newgrid.C:
            raise ValueError('sample has too many colors')
        patterns = {}
        n = self.N
        # Upstream samples grid.MX/MY positions, not sample dimensions; preserve this.
        for y in range(g.MY if periodic_input else g.MY-n+1):
            for x in range(g.MX if periodic_input else g.MX-n+1):
                pattern = [sample[(x+dx)%sx+(y+dy)%sy*sx] for dy in range(n) for dx in range(n)]
                for p in symmetries(pattern,lambda q:rotated(q,n),lambda q:reflected(q,n),lambda a,b:False,group):
                    key = tuple(p)
                    patterns[key] = patterns.get(key,0)+1
        self.patterns = list(patterns)
        self.weights = [float(w) for w in patterns.values()]
        def agrees(p,q,dx,dy):
            return all(p[x+n*y]==q[x-dx+n*(y-dy)] for y in range(max(0,dy),min(n,n+dy)) for x in range(max(0,dx),min(n,n+dx)))
        self.propagator = [[[t2 for t2,q in enumerate(self.patterns) if agrees(p,q,dx,dy)] for p in self.patterns] for dx,dy,dz in DIRS[:4]]
        self.map = {}
        for er in e.findall('rule'):
            out = [self.newgrid.values[s[0]] for s in er.attrib['out'].split('|')]
            self.map[g.values[er.attrib['in']]] = [p[0] in out for p in self.patterns]
        self.map.setdefault(0,[True]*len(self.weights))
        self.finish_load(e,group,ip,g)

    def update_state(self):
        o = self.newgrid
        votes = [[0]*o.C for _ in o.state]
        for i,row in enumerate(self.wave.data):
            x,y = i%o.MX,i//o.MX
            for p,flag in enumerate(row):
                if flag:
                    for dy in range(self.N):
                        for dx in range(self.N):
                            v = self.patterns[p][dx+dy*self.N]
                            votes[(x+dx)%o.MX+(y+dy)%o.MY*o.MX][v] += 1
        # Original uses unseeded Random for preview ties. Final collapsed votes agree.
        rng = random.Random()
        for i,row in enumerate(votes):
            o.state[i] = max(range(o.C),key=lambda c:row[c]+0.1*rng.random())


class TileNode(WFCNode):
    def __init__(self,e,group,ip,g):
        self.N = 1
        self.periodic = attr(e,'periodic',False)
        self.name = e.attrib['tileset']
        tilesname = e.get('tiles',self.name)
        self.overlap,self.overlapz = attr(e,'overlap',0),attr(e,'overlapz',0)
        root = ET.parse(ip.base/'resources'/'tilesets'/(self.name+'.xml')).getroot()
        full = attr(root,'fullSymmetry',False)
        xtiles = root.find('tiles').findall('tile')
        _,s,sy,sz = load_vox(ip.base/'resources'/'tilesets'/tilesname/(xtiles[0].attrib['name']+'.vox'))
        if s!=sy or full and s!=sz:
            raise ValueError('invalid tile dimensions')
        self.S,self.SZ = s,sz
        self.newgrid = Grid(e,(s-self.overlap)*g.MX+self.overlap,(s-self.overlap)*g.MY+self.overlap,(sz-self.overlapz)*g.MZ+self.overlapz)
        def transform(p,kind):
            functions = {'zr':lambda x,y,z:y+(s-1-x)*s+z*s*s,
                         'yr':lambda x,y,z:z+y*s+(s-1-x)*s*s,
                         'xr':lambda x,y,z:x+z*s+(s-1-y)*s*s,
                         'xf':lambda x,y,z:s-1-x+y*s+z*s*s,
                         'yf':lambda x,y,z:x+(s-1-y)*s+z*s*s,
                         'zf':lambda x,y,z:x+y*s+(s-1-z)*s*s}
            f = functions[kind]
            return tuple(p[f(x,y,z)] for x,y,z in positions(s,s,sz))
        zr,yr,xr,xf,yf,zf = [lambda p,k=k:transform(p,k) for k in ('zr','yr','xr','xf','yf','zf')]
        self.tiledata,self.weights = [],[]
        named,sets,uniques = {},{},[]
        for et in xtiles:
            name = et.attrib['name']
            vox,tx,ty,tz = load_vox(ip.base/'resources'/'tilesets'/tilesname/(name+'.vox'))
            if (tx,ty,tz)!=(s,s,sz):
                raise ValueError('inconsistent tile dimensions')
            flat,c = ords(vox,uniques)
            if c>self.newgrid.C:
                raise ValueError('too many tile colors')
            local = symmetries(tuple(flat),zr,xf,lambda a,b:a==b,b=yr if full else None)
            named[name] = local
            sets[name] = set(range(len(self.tiledata),len(self.tiledata)+len(local)))
            self.tiledata.extend(local)
            self.weights.extend([attr(et,'weight',1.0)]*len(local))
        pcount = len(self.tiledata)
        self.map = {}
        for er in e.findall('rule'):
            selected = set().union(*(sets[name] for name in er.attrib['out'].split('|')))
            self.map[g.values[er.attrib['in']]] = [p in selected for p in range(pcount)]
        self.map.setdefault(0,[True]*pcount)
        # First matching index is significant when different named tiles share data.
        index = {}
        for i,t in enumerate(self.tiledata):
            index.setdefault(t,i)
        def tile(code):
            words = code.split(' ')
            t = named[words[-1]][0]
            for action in (words[0][::-1] if len(words)==2 else ''):
                t = {'x':xr,'y':yr,'z':zr}[action](t)
            return t
        dense = [[set() for _ in range(pcount)] for _ in range(6)]
        def add(d,a,b):
            dense[d][index[a]].add(index[b])
        def sq(t,a,r):
            return symmetries(t,a,r,lambda x,y:False)
        for en in root.find('neighbors').findall('neighbor'):
            if full:
                left,right = tile(en.attrib['left']),tile(en.attrib['right'])
                for a,b in zip(sq(left,xr,yf),sq(right,xr,yf)):
                    add(0,a,b)
                    add(0,xf(b),xf(a))
                down,up = zr(left),zr(right)
                for a,b in zip(sq(down,yr,zf),sq(up,yr,zf)):
                    add(1,a,b)
                    add(1,yf(b),yf(a))
                bottom,top = yr(left),yr(right)
                for a,b in zip(sq(bottom,zr,xf),sq(top,zr,xf)):
                    add(4,a,b)
                    add(4,zf(b),zf(a))
            elif en.get('left') is not None:
                left,right = tile(en.attrib['left']),tile(en.attrib['right'])
                for a,b in ((left,right),(yf(left),yf(right)),(xf(right),xf(left)),(yf(xf(right)),yf(xf(left)))):
                    add(0,a,b)
                down,up = zr(left),zr(right)
                for a,b in ((down,up),(xf(down),xf(up)),(yf(up),yf(down)),(xf(yf(up)),xf(yf(down)))):
                    add(1,a,b)
            else:
                top,bottom = tile(en.attrib['top']),tile(en.attrib['bottom'])
                for a,b in zip(sq(bottom,zr,xf),sq(top,zr,xf)):
                    add(4,a,b)
        for d,op in ((0,2),(1,3),(4,5)):
            for i,row in enumerate(dense[d]):
                for j in row:
                    dense[op][j].add(i)
        self.propagator = [[sorted(row) for row in direction] for direction in dense]
        self.finish_load(e,group,ip,g)

    def update_state(self):
        g,o = self.grid,self.newgrid
        rng = random.Random()
        for x,y,z in positions(g.MX,g.MY,g.MZ):
            row = self.wave.data[g.index(x,y,z)]
            votes = [[0]*o.C for _ in range(self.S*self.S*self.SZ)]
            for t,flag in enumerate(row):
                if flag:
                    for i,v in enumerate(self.tiledata[t]):
                        votes[i][v] += 1
            for i,(dx,dy,dz) in enumerate(positions(self.S,self.S,self.SZ)):
                v = max(range(o.C),key=lambda c:votes[i][c]+0.1*rng.random())
                sx,sy,sz = x*(self.S-self.overlap)+dx,y*(self.S-self.overlap)+dy,z*(self.SZ-self.overlapz)+dz
                o.state[o.index(sx,sy,sz)] = v
