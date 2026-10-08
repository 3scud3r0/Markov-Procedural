"""Rule matching, fields and observations; translated from the MIT C# source."""
import math
from collections import deque
from .core import Node, Rule, attr, symmetry, positions


def directions(x,y,z,mx,my,mz,edges=False,vertices=False):
    result = []
    for dx,dy,dz in ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)):
        if 0<=x+dx<mx and 0<=y+dy<my and 0<=z+dz<mz:
            result.append((dx,dy,dz))
    if edges:
        for ds in (((-1,-1,0),(-1,1,0),(1,-1,0),(1,1,0)),
                   ((-1,0,-1),(-1,0,1),(1,0,-1),(1,0,1)),
                   ((0,-1,-1),(0,-1,1),(0,1,-1),(0,1,1))):
            for dx,dy,dz in ds:
                if 0<=x+dx<mx and 0<=y+dy<my and 0<=z+dz<mz:
                    result.append((dx,dy,dz))
    if vertices and mz>1:
        for dx in (-1,1):
            for dy in (-1,1):
                for dz in (-1,1):
                    if 0<=x+dx<mx and 0<=y+dy<my and 0<=z+dz<mz:
                        result.append((dx,dy,dz))
    return result


class Field:
    def __init__(self,e,g):
        self.recompute,self.essential = attr(e,'recompute',False),attr(e,'essential',False)
        self.substrate = g.wave(e.attrib['on'])
        self.inversed = e.get('from') is not None
        self.zero = g.wave(e.attrib['from'] if self.inversed else e.attrib['to'])

    def compute(self,p,g):
        p[:] = [-1]*len(p)
        q = deque()
        for i,s in enumerate(g.state):
            if self.zero & 1<<s:
                p[i] = 0
                q.append((0,i%g.MX,i//g.MX%g.MY,i//(g.MX*g.MY)))
        if not q:
            return False
        while q:
            t,x,y,z = q.popleft()
            for dx,dy,dz in directions(x,y,z,g.MX,g.MY,g.MZ):
                i = g.index(x+dx,y+dy,z+dz)
                if p[i] == -1 and self.substrate & 1<<g.state[i]:
                    p[i] = t+1
                    q.append((t+1,x+dx,y+dy,z+dz))
        return True


def delta(state,r,x,y,z,fields,p,mx,my):
    total = 0
    for di,(dx,dy,dz) in enumerate(positions(r.IMX,r.IMY,r.IMZ)):
        v = r.output[di]
        if v != 255 and not r.input[di] & 1<<v:
            i = x+dx+(y+dy)*mx+(z+dz)*mx*my
            new = p[v][i]
            if new == -1:
                return None
            oldv = state[i]
            old = p[oldv][i]
            total += new-old
            if fields:
                if fields[oldv] and fields[oldv].inversed:
                    total += 2*old
                if fields[v] and fields[v].inversed:
                    total -= 2*new
    return total


def goal(state,future):
    return all(f & 1<<v for v,f in zip(state,future))


def compute_future(future,state,obs):
    mask = [v is None for v in obs]
    for i,v in enumerate(state):
        mask[v] = True
        o = obs[v]
        if o is not None:
            state[i],future[i] = o
        else:
            future[i] = 1<<v
    return all(mask)


def potentials(initial,mx,my,mz,rules,c,backwards):
    p = [[(0 if (initial[i] & 1<<v if backwards else initial[i]==v) else -1) for i in range(len(initial))] for v in range(c)]
    q = deque((v,i%mx,i//mx%my,i//(mx*my)) for v in range(c) for i,t in enumerate(p[v]) if t==0)
    mask = [[False]*len(initial) for _ in rules]
    while q:
        value,x,y,z = q.popleft()
        t = p[value][x+y*mx+z*mx*my]
        for ri,r in enumerate(rules):
            shifts = r.oshifts if backwards else r.ishifts
            for dx,dy,dz in shifts[value]:
                sx,sy,sz = x-dx,y-dy,z-dz
                if sx<0 or sy<0 or sz<0 or sx+r.IMX>mx or sy+r.IMY>my or sz+r.IMZ>mz:
                    continue
                si = sx+sy*mx+sz*mx*my
                if mask[ri][si]:
                    continue
                a = r.output if backwards else r.binput
                coords = list(positions(r.IMX,r.IMY,r.IMZ))
                if any(v!=255 and (p[v][sx+xx+(sy+yy)*mx+(sz+zz)*mx*my]<0 or p[v][sx+xx+(sy+yy)*mx+(sz+zz)*mx*my]>t) for v,(xx,yy,zz) in zip(a,coords)):
                    continue
                mask[ri][si] = True
                a = r.binput if backwards else r.output
                for v,(xx,yy,zz) in zip(a,coords):
                    i = sx+xx+(sy+yy)*mx+(sz+zz)*mx*my
                    if v!=255 and p[v][i]==-1:
                        p[v][i] = t+1
                        q.append((v,sx+xx,sy+yy,sz+zz))
    return p


def backward_score(p,state):
    values = [p[v][i] for i,v in enumerate(state)]
    return -1 if any(v<0 for v in values) else sum(values)


def forward_score(p,future):
    values = [min((p[v][i] for v in range(len(p)) if f & 1<<v and 0<=p[v][i]<1000),default=-1) for i,f in enumerate(future)]
    return -1 if any(v<0 for v in values) else sum(values)


def heuristic_key(h,first,temperature,u):
    if temperature <= 0:
        return -h+0.001*u
    try:
        exponent = math.exp((h-first)/temperature)
    except OverflowError:
        exponent = math.inf
    return u**exponent


class RuleNode(Node):
    def __init__(self,e,group,ip,g):
        super().__init__(e,group,ip,g)
        group = symmetry(g.MZ==1,e.get('symmetry'),group)
        self.rules = []
        for er in e.findall('rule') or [e]:
            r = Rule.load(er,g,g,ip.base)
            r.original = True
            self.rules.extend(r.variants(symmetry(g.MZ==1,er.get('symmetry'),group),g.MZ==1))
        self.last = [False]*len(self.rules)
        self.steps = attr(e,'steps',0)
        self.temperature = attr(e,'temperature',0.0)
        self.fields,self.observations,self.potentials,self.trajectory = None,None,None,None
        if e.findall('field'):
            self.fields = [None]*g.C
            for ef in e.findall('field'):
                self.fields[g.values[ef.attrib['for']]] = Field(ef,g)
            self.potentials = [[0]*len(g.state) for _ in range(g.C)]
        self.search = attr(e,'search',False)
        self.limit,self.depthCoefficient = attr(e,'limit',-1),attr(e,'depthCoefficient',0.5)
        if e.findall('observe'):
            self.observations = [None]*g.C
            for eo in e.findall('observe'):
                v = g.values[eo.attrib['value']]
                self.observations[v] = g.values[eo.get('from',g.characters[v])],g.wave(eo.attrib['to'])
            if not self.search:
                self.potentials = [[0]*len(g.state) for _ in range(g.C)]
            self.future = [0]*len(g.state)
        self.matches,self.matchCount = [],0
        self.matchMask = None if isinstance(self,ParallelNode) else [bytearray(len(g.state)) for _ in self.rules]
        self.reset()

    def reset(self):
        self.lastMatchedTurn,self.counter,self.futureComputed = -1,0,False
        self.last[:] = [False]*len(self.last)

    def add(self,r,x,y,z,mask):
        mask[self.grid.index(x,y,z)] = True
        match = r,x,y,z
        if self.matchCount < len(self.matches):
            self.matches[self.matchCount] = match
        else:
            self.matches.append(match)
        self.matchCount += 1

    def prepare(self):
        self.last[:] = [False]*len(self.last)
        if self.steps>0 and self.counter>=self.steps:
            return False
        g,ip = self.grid,self.ip
        if self.observations is not None and not self.futureComputed:
            if not compute_future(self.future,g.state,self.observations):
                return False
            self.futureComputed = True
            if self.search:
                from .search import search
                self.trajectory = None
                for _ in range(1 if self.limit<0 else 20):
                    self.trajectory = search(g.state,self.future,self.rules,g.MX,g.MY,g.MZ,g.C,isinstance(self,AllNode),self.limit,self.depthCoefficient,ip.random.next())
                    if self.trajectory is not None:
                        break
            else:
                self.potentials = potentials(self.future,g.MX,g.MY,g.MZ,self.rules,g.C,True)
        if self.lastMatchedTurn>=0:
            for x,y,z in ip.changes[ip.first[self.lastMatchedTurn]:]:
                value = g.state[g.index(x,y,z)]
                for ri,r in enumerate(self.rules):
                    mask = self.matchMask[ri]
                    for dx,dy,dz in r.ishifts[value]:
                        sx,sy,sz = x-dx,y-dy,z-dz
                        if sx<0 or sy<0 or sz<0 or sx+r.IMX>g.MX or sy+r.IMY>g.MY or sz+r.IMZ>g.MZ:
                            continue
                        if not mask[g.index(sx,sy,sz)] and g.matches(r,sx,sy,sz):
                            self.add(ri,sx,sy,sz,mask)
        else:
            self.matchCount = 0
            for ri,r in enumerate(self.rules):
                mask = self.matchMask[ri] if self.matchMask else None
                for z in range(r.IMZ-1,g.MZ,r.IMZ):
                    for y in range(r.IMY-1,g.MY,r.IMY):
                        for x in range(r.IMX-1,g.MX,r.IMX):
                            for dx,dy,dz in r.ishifts[g.state[g.index(x,y,z)]]:
                                sx,sy,sz = x-dx,y-dy,z-dz
                                if sx<0 or sy<0 or sz<0 or sx+r.IMX>g.MX or sy+r.IMY>g.MY or sz+r.IMZ>g.MZ:
                                    continue
                                if g.matches(r,sx,sy,sz):
                                    self.add(ri,sx,sy,sz,mask)
        if self.fields:
            anysuccess,anycomputation = False,False
            for c,f in enumerate(self.fields):
                if f and (self.counter==0 or f.recompute):
                    success = f.compute(self.potentials[c],g)
                    if not success and f.essential:
                        return False
                    anysuccess |= success
                    anycomputation = True
            if anycomputation and not anysuccess:
                return False
        return True

    def replay(self):
        if self.counter>=len(self.trajectory):
            return False
        self.grid.state[:] = self.trajectory[self.counter]
        self.counter += 1
        return True


class OneNode(RuleNode):
    def reset(self):
        super().reset()
        if self.matchCount:
            for mask in self.matchMask:
                mask[:] = bytes(len(mask))
            self.matchCount = 0

    def apply(self,r,x,y,z):
        g = self.grid
        for v,(dx,dy,dz) in zip(r.output,positions(r.OMX,r.OMY,r.OMZ)):
            if v!=255:
                i = g.index(x+dx,y+dy,z+dz)
                if g.state[i]!=v:
                    g.state[i] = v
                    self.ip.changes.append((x+dx,y+dy,z+dz))

    def random_match(self):
        g,rng = self.grid,self.ip.random
        if self.potentials is not None:
            if self.observations is not None and goal(g.state,self.future):
                self.futureComputed = False
                return None
            best,arg,first = -1000.0,None,None
            k = 0
            while k<self.matchCount:
                ri,x,y,z = self.matches[k]
                if not g.matches(self.rules[ri],x,y,z):
                    self.matchMask[ri][g.index(x,y,z)] = False
                    self.matchCount -= 1
                    self.matches[k] = self.matches[self.matchCount]
                    continue
                h = delta(g.state,self.rules[ri],x,y,z,self.fields,self.potentials,g.MX,g.MY)
                if h is not None:
                    if first is None:
                        first = h
                    key = heuristic_key(h,first,self.temperature,rng.double())
                    if key>best:
                        best,arg = key,k
                k += 1
            return self.matches[arg] if arg is not None else None
        while self.matchCount>0:
            k = rng.next(self.matchCount)
            ri,x,y,z = self.matches[k]
            self.matchMask[ri][g.index(x,y,z)] = False
            self.matchCount -= 1
            self.matches[k] = self.matches[self.matchCount]
            if g.matches(self.rules[ri],x,y,z):
                return ri,x,y,z
        return None

    def go(self):
        if not self.prepare():
            return False
        self.lastMatchedTurn = self.ip.counter
        if self.trajectory is not None:
            return self.replay()
        match = self.random_match()
        if match is None:
            return False
        ri,x,y,z = match
        self.last[ri] = True
        self.apply(self.rules[ri],x,y,z)
        self.counter += 1
        return True


class AllNode(RuleNode):
    def fit(self,ri,x,y,z):
        g,r = self.grid,self.rules[ri]
        cells = [(v,g.index(x+dx,y+dy,z+dz),x+dx,y+dy,z+dz) for v,(dx,dy,dz) in zip(r.output,positions(r.OMX,r.OMY,r.OMZ)) if v!=255]
        if any(g.mask[i] for v,i,xx,yy,zz in cells):
            return
        self.last[ri] = True
        for v,i,xx,yy,zz in cells:
            g.mask[i],g.state[i] = True,v
            self.ip.changes.append((xx,yy,zz))

    def go(self):
        if not self.prepare():
            return False
        self.lastMatchedTurn = self.ip.counter
        if self.trajectory is not None:
            return self.replay()
        if self.matchCount==0:
            return False
        g = self.grid
        if self.potentials is not None:
            ordered,first = [],None
            for m,(ri,x,y,z) in enumerate(self.matches[:self.matchCount]):
                h = delta(g.state,self.rules[ri],x,y,z,self.fields,self.potentials,g.MX,g.MY)
                if h is not None:
                    if first is None:
                        first = h
                    ordered.append((m,heuristic_key(h,first,self.temperature,self.ip.random.double())))
            indices = [m for m,k in sorted(ordered,key=lambda p:-p[1])]
        else:
            indices = self.ip.random.shuffle(self.matchCount)
        for k in indices:
            ri,x,y,z = self.matches[k]
            self.matchMask[ri][g.index(x,y,z)] = False
            self.fit(ri,x,y,z)
        for x,y,z in self.ip.changes[self.ip.first[self.lastMatchedTurn]:]:
            g.mask[g.index(x,y,z)] = False
        self.counter += 1
        self.matchCount = 0
        return True


class ParallelNode(RuleNode):
    def __init__(self,e,group,ip,g):
        super().__init__(e,group,ip,g)
        self.newstate = bytearray(len(g.state))

    def add(self,ri,x,y,z,mask):
        r,g = self.rules[ri],self.grid
        if self.ip.random.double()>r.p:
            return
        self.last[ri] = True
        for v,(dx,dy,dz) in zip(r.output,positions(r.OMX,r.OMY,r.OMZ)):
            i = g.index(x+dx,y+dy,z+dz)
            if v!=255 and v!=g.state[i]:
                self.newstate[i] = v
                self.ip.changes.append((x+dx,y+dy,z+dz))
        self.matchCount += 1

    def go(self):
        if not self.prepare():
            return False
        g = self.grid
        for x,y,z in self.ip.changes[self.ip.first[self.ip.counter]:]:
            i = g.index(x,y,z)
            g.state[i] = self.newstate[i]
        self.counter += 1
        return self.matchCount>0
