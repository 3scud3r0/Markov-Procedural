"""Heuristic search and exhaustive nonoverlapping rule applications (MIT)."""
import heapq
from dataclasses import dataclass
from .core import DotNetRandom,positions
from .rules import potentials,backward_score,forward_score


@dataclass
class Board:
    state: bytes
    parent: int
    depth: int
    backward: int
    forward: int

    def rank(self,rng,coefficient):
        value = 1000-self.depth if coefficient<0 else self.forward+self.backward+2.0*coefficient*self.depth
        return value+0.0001*rng.double()


def matches(r,x,y,state,mx,my):
    if x+r.IMX>mx or y+r.IMY>my:
        return False
    # Original search is two-dimensional, including for flattened input patterns.
    for i,w in enumerate(r.input):
        si = x+i%r.IMX+(y+i//r.IMX)*mx
        if si>=len(state) or not w & 1<<state[si]:
            return False
    return True


def applied(r,x,y,state,mx):
    result = bytearray(state)
    for v,(dx,dy,dz) in zip(r.output,positions(r.OMX,r.OMY,r.OMZ)):
        if v!=255:
            result[x+dx+(y+dy)*mx] = v
    return bytes(result)


def one_children(state,mx,my,rules):
    for r in rules:
        for y in range(my):
            for x in range(mx):
                if matches(r,x,y,state,mx,my):
                    yield applied(r,x,y,state,mx)


def all_children(state,mx,my,rules):
    tiles,amounts = [],[0]*len(state)
    for i in range(len(state)):
        x,y = i%mx,i//mx
        for r in rules:
            if matches(r,x,y,state,mx,my):
                cells = [x+dx+(y+dy)*mx for dy in range(r.IMY) for dx in range(r.IMX)]
                tiles.append((r,i,cells))
                for j in cells:
                    amounts[j] += 1
    mask,solution = [True]*len(tiles),[]
    def hide(l,unhide):
        mask[l] = unhide
        for j in tiles[l][2]:
            amounts[j] += 1 if unhide else -1
    def enumerate_states():
        maximum = max(amounts,default=0)
        if maximum<=0:
            result = bytearray(state)
            for r,i,cells in solution:
                x,y = i%mx,i//mx
                for dy in range(r.OMY):
                    for dx in range(r.OMX):
                        # Preserves upstream Search.Apply, including wildcard bytes.
                        result[x+dx+(y+dy)*mx] = r.output[dx+dy*r.OMX]
            yield bytes(result)
            return
        cell = amounts.index(maximum)
        cover = [l for l,t in enumerate(tiles) if mask[l] and cell in t[2]]
        for l in cover:
            t = tiles[l]
            solution.append(t)
            occupied = set(t[2])
            intersect = [k for k,u in enumerate(tiles) if mask[k] and occupied.intersection(u[2])]
            for k in intersect:
                hide(k,False)
            yield from enumerate_states()
            for k in intersect:
                hide(k,True)
            solution.pop()
    yield from enumerate_states()


def search(present,future,rules,mx,my,mz,c,all_node,limit,depth_coefficient,seed):
    present = bytes(present)
    bp = potentials(future,mx,my,mz,rules,c,True)
    backward = backward_score(bp,present)
    fp = potentials(present,mx,my,mz,rules,c,False)
    forward = forward_score(fp,future)
    if backward<0 or forward<0:
        return None
    if backward==0:
        return []
    root = Board(present,-1,0,backward,forward)
    database,visited = [root],{present:0}
    rng = DotNetRandom(seed)
    frontier = [(root.rank(rng,depth_coefficient),0)]
    while frontier and (limit<0 or len(database)<limit):
        _,parent_index = heapq.heappop(frontier)
        parent = database[parent_index]
        children = all_children(parent.state,mx,my,rules) if all_node else one_children(parent.state,mx,my,rules)
        for state in children:
            if state in visited:
                index = visited[state]
                old = database[index]
                if parent.depth+1<old.depth:
                    old.depth,old.parent = parent.depth+1,parent_index
                    if old.backward>=0 and old.forward>=0:
                        heapq.heappush(frontier,(old.rank(rng,depth_coefficient),index))
                continue
            b = backward_score(bp,state)
            f = forward_score(potentials(state,mx,my,mz,rules,c,False),future)
            if b<0 or f<0:
                continue
            child = Board(state,parent_index,parent.depth+1,b,f)
            database.append(child)
            index = len(database)-1
            visited[state] = index
            if f==0:
                trajectory = []
                while child.parent>=0:
                    trajectory.append(child.state)
                    child = database[child.parent]
                return trajectory[::-1]
            heapq.heappush(frontier,(child.rank(rng,depth_coefficient),index))
    return None
