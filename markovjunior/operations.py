"""Paths, maps, cellular automata and ConvChain. MIT translation."""
import math
from fractions import Fraction
from collections import deque
from .core import Node, Branch, Grid, Rule, DotNetRandom, attr, symmetry, positions, symmetries, rotated, reflected
from .rules import directions


class PathNode(Node):
    def __init__(self,e,group,ip,g):
        super().__init__(e,group,ip,g)
        self.start,self.finish,self.substrate = [g.wave(e.attrib[k]) for k in ('from','to','on')]
        self.value = g.values[e.get('color',e.attrib['from'][0])]
        self.inertia,self.longest,self.edges,self.vertices = [attr(e,k,False) for k in ('inertia','longest','edges','vertices')]

    def direction(self,x,y,z,dx,dy,dz,generations,rng):
        g = self.grid
        t = generations[g.index(x,y,z)]
        if not self.edges and not self.vertices and self.inertia and (dx or dy or dz):
            cx,cy,cz = x+dx,y+dy,z+dz
            if 0<=cx<g.MX and 0<=cy<g.MY and 0<=cz<g.MZ and generations[g.index(cx,cy,cz)] == t-1:
                return dx,dy,dz
        candidates = [(xx,yy,zz) for xx,yy,zz in directions(x,y,z,g.MX,g.MY,g.MZ,self.edges,self.vertices) if generations[g.index(x+xx,y+yy,z+zz)]==t-1]
        if (self.edges or self.vertices) and self.inertia and (dx or dy or dz):
            best,result = -4,None
            for xx,yy,zz in candidates:
                noise = 0.1*rng.double()
                cosine = (xx*dx+yy*dy+zz*dz)/math.sqrt((xx*xx+yy*yy+zz*zz)*(dx*dx+dy*dy+dz*dz))
                if cosine+noise>best:
                    best,result = cosine+noise,(xx,yy,zz)
            return result
        return candidates[rng.next(len(candidates))]

    def go(self):
        g = self.grid
        gens = [-1]*len(g.state)
        q,starts = deque(),[]
        for x,y,z in positions(g.MX,g.MY,g.MZ):
            i = g.index(x,y,z)
            if self.start & 1<<g.state[i]:
                starts.append((x,y,z))
            if self.finish & 1<<g.state[i]:
                gens[i] = 0
                q.append((0,x,y,z))
        if not starts or not q:
            return False
        while q:
            t,x,y,z = q.popleft()
            for dx,dy,dz in directions(x,y,z,g.MX,g.MY,g.MZ,self.edges,self.vertices):
                xx,yy,zz = x+dx,y+dy,z+dz
                i = g.index(xx,yy,zz)
                v = g.state[i]
                if gens[i]==-1 and (self.substrate & 1<<v or self.start & 1<<v):
                    if self.substrate & 1<<v:
                        q.append((t+1,xx,yy,zz))
                    gens[i] = t+1
        if not any(gens[g.index(*p)]>0 for p in starts):
            return False
        rng = DotNetRandom(self.ip.random.next())
        low,high = len(g.state),-2
        pmin=pmax=None
        for p in starts:
            t = gens[g.index(*p)]
            if t==-1:
                continue
            value = t+0.1*rng.double()
            if value<low:
                low,pmin=value,p
            if value>high:
                high,pmax=value,p
        x,y,z = pmax if self.longest else pmin
        dx,dy,dz = self.direction(x,y,z,0,0,0,gens,rng)
        x,y,z = x+dx,y+dy,z+dz
        while gens[g.index(x,y,z)]!=0:
            g.state[g.index(x,y,z)] = self.value
            self.ip.changes.append((x,y,z))
            dx,dy,dz = self.direction(x,y,z,dx,dy,dz,gens,rng)
            x,y,z = x+dx,y+dy,z+dz
        return True


class MapNode(Branch):
    def __init__(self,e,group,ip,g):
        self.scale = [Fraction(s) for s in e.attrib['scale'].split(' ')]
        if len(self.scale)!=3:
            raise ValueError('map needs three scale components')
        self.newgrid = Grid(e,*(int(v*s) for v,s in zip((g.MX,g.MY,g.MZ),self.scale)))
        super().__init__(e,group,ip,self.newgrid)
        self.grid = g
        group = symmetry(g.MZ==1,e.get('symmetry'),group)
        self.rules = []
        for er in e.findall('rule'):
            r = Rule.load(er,g,self.newgrid,ip.base)
            r.original = True
            self.rules.extend(r.variants(group,g.MZ==1))

    def reset(self):
        super().reset()
        self.n = -1

    def go(self):
        if self.n>=0:
            return super().go()
        g,o = self.grid,self.newgrid
        o.clear()
        for r in self.rules:
            for x,y,z in positions(g.MX,g.MY,g.MZ):
                if not all(w & 1<<g.state[g.index((x+dx)%g.MX,(y+dy)%g.MY,(z+dz)%g.MZ)] for w,(dx,dy,dz) in zip(r.input,positions(r.IMX,r.IMY,r.IMZ))):
                    continue
                sx,sy,sz = [int(v*s) for v,s in zip((x,y,z),self.scale)]
                for v,(dx,dy,dz) in zip(r.output,positions(r.OMX,r.OMY,r.OMZ)):
                    if v!=255:
                        o.state[o.index((sx+dx)%o.MX,(sy+dy)%o.MY,(sz+dz)%o.MZ)] = v
        self.ip.grid = o
        self.n += 1
        return True


class ConvolutionNode(Node):
    def __init__(self,e,group,ip,g):
        super().__init__(e,group,ip,g)
        self.steps,self.periodic = attr(e,'steps',-1),attr(e,'periodic',False)
        name = e.attrib['neighborhood']
        self.offsets = []
        for dz in (range(-1,2) if g.MZ>1 else [0]):
            for dy in range(-1,2):
                for dx in range(-1,2):
                    distance = abs(dx)+abs(dy)+abs(dz)
                    if (name=='VonNeumann' and distance==1 or name=='Moore' and distance>0 or name=='NoCorners' and 0<distance<3):
                        self.offsets.append((dx,dy,dz))
        self.rules = []
        for er in e.findall('rule') or [e]:
            values,sums = er.get('values'),er.get('sum')
            if (values is None)!=(sums is None):
                raise ValueError('convolution needs both values and sum')
            allowed = None
            if sums is not None:
                allowed = set()
                for s in sums.split(','):
                    if '..' in s:
                        a,b = map(int,s.split('..'))
                        allowed.update(range(a,b+1))
                    else:
                        allowed.add(int(s))
            self.rules.append((g.values[er.attrib['in']],g.values[er.attrib['out']],attr(er,'p',1.0),None if values is None else [g.values[c] for c in values],allowed))
        self.reset()

    def reset(self):
        self.counter = 0

    def go(self):
        if self.steps>0 and self.counter>=self.steps:
            return False
        g = self.grid
        sums = [[0]*g.C for _ in g.state]
        for x,y,z in positions(g.MX,g.MY,g.MZ):
            row = sums[g.index(x,y,z)]
            for dx,dy,dz in self.offsets:
                sx,sy,sz = x+dx,y+dy,z+dz
                if self.periodic:
                    sx,sy,sz = sx%g.MX,sy%g.MY,sz%g.MZ
                elif not (0<=sx<g.MX and 0<=sy<g.MY and 0<=sz<g.MZ):
                    continue
                row[g.state[g.index(sx,sy,sz)]] += 1
        change = False
        for i,row in enumerate(sums):
            v = g.state[i]
            for inp,out,p,values,allowed in self.rules:
                if v==inp and out!=g.state[i] and (p==1.0 or self.ip.random.next()<p*2147483647):
                    if allowed is None or sum(row[c] for c in values) in allowed:
                        g.state[i] = out
                        change = True
                        break
        self.counter += 1
        return change


class ConvChainNode(Node):
    def __init__(self,e,group,ip,g):
        from .graphics import load_bitmap
        super().__init__(e,group,ip,g)
        if g.MZ!=1:
            raise ValueError('ConvChain is 2D')
        bitmap,self.SMX,self.SMY,_ = load_bitmap(ip.base/'resources'/'samples'/(e.attrib['sample']+'.png'))
        self.sample = [v==0xffffffff for v in bitmap]
        self.N,self.steps,self.temperature = attr(e,'n',3),attr(e,'steps',-1),attr(e,'temperature',1.0)
        self.c0,self.c1,self.substrateColor = [g.values[e.attrib[k]] for k in ('black','white','on')]
        self.substrate = [False]*len(g.state)
        self.weights = [0.0]*(1<<(self.N*self.N))
        for y in range(self.SMY):
            for x in range(self.SMX):
                p = [self.sample[(x+dx)%self.SMX+(y+dy)%self.SMY*self.SMX] for dy in range(self.N) for dx in range(self.N)]
                for q in symmetries(p,lambda a:rotated(a,self.N),lambda a:reflected(a,self.N),lambda a,b:False,group):
                    self.weights[sum(1<<i for i,v in enumerate(q) if v)] += 1
        self.weights = [w if w>0 else 0.1 for w in self.weights]
        self.reset()

    def reset(self):
        self.substrate[:] = [False]*len(self.substrate)
        self.counter = 0

    def go(self):
        if self.steps>0 and self.counter>=self.steps:
            return False
        g,rng,n = self.grid,self.ip.random,self.N
        if self.counter==0:
            anysubstrate = False
            for i,v in enumerate(g.state):
                if v==self.substrateColor:
                    g.state[i] = self.c0 if rng.next(2)==0 else self.c1
                    self.substrate[i] = anysubstrate = True
            self.counter += 1
            return anysubstrate
        for _ in g.state:
            r = rng.next(len(g.state))
            if not self.substrate[r]:
                continue
            x,y = r%g.MX,r//g.MX
            q = 1.0
            for sy in range(y-n+1,y+n):
                for sx in range(x-n+1,x+n):
                    ind,difference = 0,0
                    for dy in range(n):
                        for dx in range(n):
                            xx,yy = (sx+dx)%g.MX,(sy+dy)%g.MY
                            value = g.state[xx+yy*g.MX]==self.c1
                            power = 1<<(dy*n+dx)
                            if value:
                                ind += power
                            if xx==x and yy==y:
                                difference = power if value else -power
                    q *= self.weights[ind-difference]/self.weights[ind]
            if q>=1:
                g.state[r] = self.c1 if g.state[r]==self.c0 else self.c0
                continue
            if self.temperature!=1:
                q = q**(1.0/self.temperature)
            if q>rng.double():
                g.state[r] = self.c1 if g.state[r]==self.c0 else self.c0
        self.counter += 1
        return True
