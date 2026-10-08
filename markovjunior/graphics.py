"""Pixel-exact 2D/isometric rendering and MagicaVoxel I/O (MIT translation)."""
import struct
from pathlib import Path
from PIL import Image
from .core import positions


def load_bitmap(filename):
    with Image.open(filename) as im:
        im = im.convert('RGBA')
        return [a<<24 | r<<16 | g<<8 | b for r,g,b,a in im.getdata()],im.width,im.height,1


def save_bitmap(data,width,height,filename):
    im = Image.new('RGBA',(width,height))
    im.putdata([((v>>16)&255,(v>>8)&255,v&255,(v>>24)&255) for v in data])
    im.save(filename)
    return im


def load_vox(filename):
    data = Path(filename).read_bytes()
    if data[:4]!=b'VOX ':
        raise ValueError('not a VOX file')
    mx=my=mz=-1
    result = None
    offset = 8
    # Follow chunk headers, including children (MAIN). Preserve upstream color IDs.
    while offset+12<=len(data):
        kind,size,children = struct.unpack_from('<4sII',data,offset)
        offset += 12
        content = data[offset:offset+size]
        if kind==b'SIZE':
            mx,my,mz = struct.unpack_from('<iii',content)
        elif kind==b'XYZI':
            if min(mx,my,mz)<=0:
                raise ValueError('XYZI before SIZE')
            result = [-1]*(mx*my*mz)
            count, = struct.unpack_from('<I',content)
            for i in range(count):
                x,y,z,c = content[4+i*4:8+i*4]
                result[x+y*mx+z*mx*my] = c
        offset += size
    if result is None:
        raise ValueError('missing XYZI chunk')
    return result,mx,my,mz


def save_vox(state,mx,my,mz,palette,filename):
    if max(mx,my,mz)>255:
        raise ValueError('VOX export supports dimensions up to 255')
    vox = bytes(v for x,y,z in positions(mx,my,mz) if state[x+y*mx+z*mx*my]!=0 for v in (x,y,z,state[x+y*mx+z*mx*my]+1))
    def chunk(name,content,children=b''):
        return struct.pack('<4sII',name,len(content),len(children))+content+children
    colors = bytes(v for c in palette for v in ((c>>16)&255,(c>>8)&255,c&255,0))
    colors += bytes(v for i in range(len(palette),255) for v in (254-i,254-i,254-i,255)) + bytes(4)
    children = chunk(b'PACK',struct.pack('<I',1))+chunk(b'SIZE',struct.pack('<iii',mx,my,mz))+chunk(b'XYZI',struct.pack('<I',len(vox)//4)+vox)+chunk(b'RGBA',colors)
    Path(filename).write_bytes(b'VOX '+struct.pack('<I',150)+chunk(b'MAIN',b'',children))


def sprite(size):
    width,height = 2*size,2*size-1
    def texture(f):
        return [f(i-size+1,size-j-1) for j in range(height) for i in range(width)]
    def cube(x,y):
        if 2*y-x>=2*size or 2*y+x>2*size or 2*y-x<-2*size or 2*y+x<=-2*size:
            return -1
        if x>0 and 2*y<x:
            return 71
        if x<=0 and 2*y<=-x:
            return 143
        return 215
    conditions = [lambda x,y:x==1 and y<=0,lambda x,y:x==0 and y<=0,
                  lambda x,y:x==1-size and 2*y<size and 2*y>=-size,
                  lambda x,y:x<=0 and y==int(x/2)+size-1,
                  lambda x,y:x==size and 2*y<size and 2*y>=-size,
                  lambda x,y:x>0 and y==int(-(x+1)/2)+size,
                  lambda x,y:x>0 and y==int((x+1)/2)-size,
                  lambda x,y:x<=0 and y==int(-x/2)-size+1]
    edges = [texture(lambda x,y,f=f,c=(215 if i<2 else 0): c if f(x,y) else -1) for i,f in enumerate(conditions)]
    return texture(cube),edges,width,height


def render(state,mx,my,mz,colors,pixelsize=4,margin=0,background=0xff222222):
    if pixelsize<1:
        raise ValueError('pixelsize must be positive')
    if mz==1:
        width,height = margin+mx*pixelsize,my*pixelsize
        screen = [background]*(width*height)
        for y in range(my):
            for x in range(mx):
                c = colors[state[x+y*mx]]
                for dy in range(pixelsize):
                    start = margin+x*pixelsize+(y*pixelsize+dy)*width
                    screen[start:start+pixelsize] = [c]*pixelsize
        return screen,width,height
    voxels = [[] for _ in range(mx+my+mz-2)]
    shown = [[] for _ in voxels]
    visible = [v!=0 for v in state]
    def vis(x,y,z):
        return visible[x+y*mx+z*mx*my]
    for x,y,z in positions(mx,my,mz):
        value = state[x+y*mx+z*mx*my]
        if value!=0:
            voxels[x+y+z].append((colors[value],x,y,z))
    seen = set()
    for i in range(len(voxels)-1,-1,-1):
        for c,x,y,z in voxels[i]:
            u,v = x-y+my-1,x+y-2*z+2*mz-2
            if (u,v) in seen:
                continue
            xx = x==0 or not vis(x-1,y,z)
            yy = y==0 or not vis(x,y-1,z)
            zz = z==0 or not vis(x,y,z-1)
            edges = [y==my-1 or not vis(x,y+1,z),x==mx-1 or not vis(x+1,y,z),
                     xx or (y!=my-1 and vis(x-1,y+1,z)),xx or (z!=mz-1 and vis(x-1,y,z+1)),
                     yy or (x!=mx-1 and vis(x+1,y-1,z)),yy or (z!=mz-1 and vis(x,y-1,z+1)),
                     zz or (x!=mx-1 and vis(x+1,y,z-1)),zz or (y!=my-1 and vis(x,y+1,z-1))]
            shown[i].append((c,x,y,z,edges))
            seen.add((u,v))
    s = pixelsize
    fitwidth,fitheight = (mx+my)*s,((mx+my)//2+mz)*s
    width,height = fitwidth+2*s,fitheight+2*s
    stride = margin+width
    screen = [background]*(stride*height)
    cube,edge_sprites,sw,sh = sprite(s)
    def blit(texture,x,y,c):
        r,g,b = (c>>16)&255,(c>>8)&255,c&255
        for dy in range(sh):
            for dx in range(sw):
                grey = texture[dx+dy*sw]
                if grey<0:
                    continue
                xx,yy = x+dx,y+dy
                if margin+xx>=0 and xx<width and 0<=yy<height:
                    screen[margin+xx+yy*stride] = 0xff000000 | (r*grey//256)<<16 | (g*grey//256)<<8 | b*grey//256
    for row in shown:
        for c,x,y,z,edges in row:
            u,v = s*(x-y),s*(x+y)//2-s*z
            px,py = width//2+u-s,(height-fitheight)//2+(mz-1)*s+v
            blit(cube,px,py,c)
            for j,flag in enumerate(edges):
                if flag:
                    blit(edge_sprites[j],px,py,c)
    return screen,stride,height
