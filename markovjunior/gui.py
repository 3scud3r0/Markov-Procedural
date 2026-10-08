"""Original bitmap rule-tree overlay using the bundled Tamzen fonts (MIT)."""
import xml.etree.ElementTree as ET
from .core import Branch,MarkovNode,attr,positions
from .rules import RuleNode,OneNode
from .operations import MapNode,PathNode,ConvolutionNode,ConvChainNode
from .wfc import WFCNode
from .graphics import load_bitmap

LEGEND = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 12345abcdefghijklmnopqrstuvwxyzλ67890{}[]()<>$*-+=/#_%^@\\&|~?'\"`!,.;:"


def draw(name,root,current,bitmap,width,height,palette,base):
    e = ET.parse(base/'resources'/'settings.xml').getroot()
    s,small,maxwidth,zshift,hindent,hgap,harrow,hline,vskip,smallvskip,fontshift,afterfont = [attr(e,k,d) for k,d in [('squareSize',7),('smallSquareSize',3),('maxwidth',10),('zshift',2),('hindent',30),('hgap',2),('harrow',10),('hline',14),('vskip',2),('smallvskip',2),('fontshift',2),('afterfont',4)]]
    dense,d3 = attr(e,'dense',True),attr(e,'d3',True)
    background,inactive,activecolor = [0xff000000|int(e.get(k,d),16) for k,d in [('background','222222'),('inactive','666666'),('active','ffffff')]]
    fonts = []
    for namefont in ('Tamzen8x16r','Tamzen8x16b'):
        data,w,h,_ = load_bitmap(base/'resources'/'fonts'/(namefont+'.png'))
        b0,b1 = data[0],data[w-1]
        fonts.append(([v!=b0 and v!=b1 for v in data],w//32,h//3))
    def rect(x,y,w,h,c):
        if y+h>height:
            return
        for dy in range(h):
            for dx in range(w):
                bitmap[x+dx+(y+dy)*width] = c
    def square(x,y,size,c):
        rect(x,y,size,size,palette[c])
    def shaded(x,y,size,c):
        rect(x,y,size,size,c)
        rect(x+size,y,1,size+1,background)
        rect(x,y+size,size+1,1,background)
    def horizontal(x,y,length,c,dashed=False):
        if length<=0 or x<0 or x+length>=width:
            return
        if not dashed:
            rect(x,y,length,1,c)
        elif y<height:
            shift = 1 if length%4==0 else 0
            for dx in range(length):
                if (dx+shift)//2%2==0:
                    bitmap[x+dx+y*width] = c
    def vertical(x,y,h,c):
        if x>=0:
            rect(x,y,1,min(y+h,height)-y,c)
    def write(text,x,y,c,font=0):
        f,fx,fy = fonts[font]
        shift = fontshift if font==0 else 0
        if y-fontshift+fy>=height:
            return -1
        for i,ch in enumerate(text):
            p = LEGEND.index(ch)
            px,py = p%32,p//32
            for dy in range(fy):
                for dx in range(fx):
                    if f[px*fx+dx+(py*fy+dy)*fx*32]:
                        bitmap[x+i*fx+dx+(y+dy-shift)*width] = c
        return len(text)*fx
    lh = {}
    def dash(node,markov,on):
        if node is root:
            return
        level,y = lh[node]
        extra = 3 if markov else 1
        horizontal(level*hindent-hline-hgap-extra,y+s//2,(hindent if type(node) in (Branch,MarkovNode) else hline)+extra,activecolor if on else inactive)
    def bracket(branch,level,n,on):
        first,last = lh[branch.nodes[0]][1],lh[branch.nodes[n]][1]
        x = (level+1)*hindent-hgap-hline
        c = activecolor if on else inactive
        vertical(x,first+s//2,last-first+1,c)
        vertical(x-(3 if isinstance(branch,MarkovNode) else 1),first+s//2,last-first+1,c)
    def array(a,x,y,mx,my,mz,chars,size):
        for i,(dx,dy,dz) in enumerate(positions(mx,my,mz)):
            c = palette[chars[a[i]]] if a[i]!=255 else inactive if d3 else background
            shaded(x+dx*size+(mz-dz-1)*zshift,y+dy*size+(mz-dz-1)*zshift,size,c)
        return mx*size+(mz-1)*zshift
    def bits(w):
        return [i for i in range(32) if w & 1<<i]
    def blocks(w,x,y,chars):
        for c in bits(w):
            square(x,y,s,chars[c])
            x += s
        return x
    def isactive(node,index):
        if node.last[index]:
            return True
        for ri in range(index+1,len(node.rules)):
            if node.rules[ri].original:
                break
            if node.last[ri]:
                return True
        return False
    y = fonts[1][2]//2
    write(name,8,y,activecolor,1)
    y += afterfont*fonts[1][2]//2
    def visit(node,level):
        nonlocal y
        lh[node] = level,y
        x,chars = level*hindent,node.grid.characters
        if isinstance(node,Branch):
            linecolor = activecolor if node is current and node.n<0 else inactive
            if isinstance(node,WFCNode):
                write('wfc '+node.name,x,y,linecolor)
                y += fonts[0][2]+vskip
            elif isinstance(node,MapNode):
                for r in node.rules:
                    if not r.original:
                        continue
                    size = small if r.IMX*r.IMY>maxwidth else s
                    x += array(r.binput,x,y,r.IMX,r.IMY,r.IMZ,chars,size)+hgap
                    horizontal(x,y+s//2,harrow,linecolor,True)
                    x += harrow+hgap
                    x += array(r.output,x,y,r.OMX,r.OMY,r.OMZ,node.newgrid.characters,size)+hgap
                    y += max(r.IMY,r.OMY)*size+(max(r.IMZ,r.OMZ)-1)*zshift+smallvskip
                    x = level*hindent
                y += vskip
            markov = isinstance(node,MarkovNode)
            for child in node.nodes:
                visit(child,level+1 if type(node) in (Branch,MarkovNode) else level)
                dash(child,markov,False)
            return
        on = current is not None and 0<=current.n<len(current.nodes) and current.nodes[current.n] is node
        nodecolor = activecolor if on else inactive
        if isinstance(node,RuleNode):
            for ri,r in enumerate(node.rules[:40]):
                if not r.original:
                    continue
                size = small if r.IMX*r.IMY>maxwidth else s
                linecolor = activecolor if on and isactive(node,ri) else inactive
                x += array(r.binput,x,y,r.IMX,r.IMY,r.IMZ,chars,size)+hgap
                horizontal(x,y+s//2,harrow,linecolor,not isinstance(node,OneNode))
                x += harrow+hgap
                x += array(r.output,x,y,r.OMX,r.OMY,r.OMZ,chars,size)+hgap
                if node.steps>0:
                    write(f' {node.counter}/{node.steps}',x,y,linecolor)
                y += r.IMY*size+(r.IMZ-1)*zshift+smallvskip
                x = level*hindent
            if node.fields:
                y += smallvskip
                for c,f in enumerate(node.fields):
                    if f is None:
                        continue
                    x += write('field ' if dense else 'field for ',x,y,nodecolor)
                    square(x,y,s,chars[c])
                    x += s+hgap if dense else s
                    if not dense:
                        x += write(' from ' if f.inversed else ' to ',x,y,nodecolor)
                    x = blocks(f.zero,x,y,chars)
                    x += hgap if dense else write(' on ',x,y,nodecolor)
                    blocks(f.substrate,x,y,chars)
                    x = level*hindent
                    y += fonts[0][2]
            y += vskip
        elif isinstance(node,PathNode):
            shift = (fonts[0][2]-fontshift-s)//2
            x += write('path ' if dense else 'path from ',x,y,nodecolor)
            x = blocks(node.start,x,y+shift,chars)
            x += hgap if dense else write(' to ',x,y,nodecolor)
            x = blocks(node.finish,x,y+shift,chars)
            x += hgap if dense else write(' on ',x,y,nodecolor)
            x = blocks(node.substrate,x,y+shift,chars)
            x += hgap if dense else write(' colored ',x,y,nodecolor)
            square(x,y+shift,s,chars[node.value])
            y += fonts[0][2]+vskip
        elif isinstance(node,ConvolutionNode):
            text = 'convolution'+(f' {node.counter}/{node.steps}' if node.steps>0 else '')
            write(text,x,y,nodecolor)
            y += fonts[0][2]+vskip
        elif isinstance(node,ConvChainNode):
            x += write('convchain ',x,y,nodecolor)
            for dy in range(node.SMY):
                for dx in range(node.SMX):
                    v = node.c1 if node.sample[dx+dy*node.SMX] else node.c0
                    square(x+dx*7,y+dy*7,7,chars[v])
            y += fonts[0][2]+vskip
    def lines(branch):
        if not branch.nodes:
            return
        bracket(branch,lh[branch.nodes[0]][0]-1,len(branch.nodes)-1,False)
        for child in branch.nodes:
            if isinstance(child,Branch):
                lines(child)
    visit(root,0)
    lines(root)
    b = current
    while b is not None:
        if 0<=b.n<len(b.nodes):
            dash(b.nodes[b.n],isinstance(b,MarkovNode),True)
            bracket(b,lh[b.nodes[0]][0]-1,b.n,True)
        b = b.parent
