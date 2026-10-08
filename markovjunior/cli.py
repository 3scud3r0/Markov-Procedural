"""Command-line generation using original XML models and palettes."""
import argparse
import sys
import secrets
import xml.etree.ElementTree as ET
from pathlib import Path
from .core import Interpreter,attr
from .paths import data_root
from .graphics import render,save_bitmap,save_vox


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "generate":
        from .procedural.cli import main as procedural_main
        return procedural_main(argv[1:])
    parser = argparse.ArgumentParser(description='MarkovJunior Python — compatible XML models')
    parser.add_argument('--base',type=Path,default=data_root())
    parser.add_argument('--models',default='models.xml')
    parser.add_argument('--model',help='Run a single model by name')
    parser.add_argument('--size',type=int)
    parser.add_argument('--length',type=int)
    parser.add_argument('--width',type=int)
    parser.add_argument('--height',type=int)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--steps',type=int)
    parser.add_argument('--pixelsize',type=int)
    parser.add_argument('--iso',action='store_true')
    parser.add_argument('--frames',action='store_true',help='Save successive PNG frames')
    parser.add_argument('--output',type=Path,default=Path('output'))
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True,exist_ok=True)
    palette = {e.attrib['symbol']:0xff000000|int(e.attrib['value'],16) for e in ET.parse(args.base/'resources'/'palette.xml').getroot()}
    entries = list(ET.parse(args.base/args.models).getroot())
    entries = [e for e in entries if e.tag=='model']
    if args.model:
        entries = [e for e in entries if e.get('name')==args.model][:1] or [ET.Element('model',name=args.model,size=str(args.size or 32))]
    for e in entries:
        name = e.attrib['name']
        size = args.size if args.size is not None else attr(e,'size',-1)
        mx = args.length or (size if args.size is not None else attr(e,'length',size))
        my = args.width or (size if args.size is not None else attr(e,'width',size))
        mz = args.height or attr(e,'height',1 if attr(e,'d',2)==2 else size)
        if min(mx,my,mz)<=0:
            raise ValueError(f'{name}: specify positive dimensions')
        frames = args.frames or attr(e,'gif',False)
        steps = args.steps if args.steps is not None else attr(e,'steps',1000 if frames else 50000)
        pixelsize = args.pixelsize or attr(e,'pixelsize',4)
        margin = attr(e,'gui',0)
        custom = dict(palette)
        for color in e.findall('color'):
            custom[color.attrib['symbol']] = 0xff000000|int(color.attrib['value'],16)
        ip = Interpreter(ET.parse(args.base/'models'/(name+'.xml')).getroot(),mx,my,mz,args.base)
        seeds = [int(v) for v in e.get('seeds','').split()]
        amount = 1 if frames or args.seed is not None else attr(e,'amount',2)
        for k in range(amount):
            seed = args.seed if args.seed is not None else seeds[k] if k<len(seeds) else secrets.randbelow(2147483647)
            for state,legend,fx,fy,fz in ip.run(seed,steps,frames):
                colors = [custom[c] for c in legend]
                stem = f'{name}_{seed}_{ip.counter:06d}' if frames else f'{name}_{seed}'
                if fz==1 or args.iso or attr(e,'iso',False):
                    bitmap,w,h = render(state,fx,fy,fz,colors,pixelsize,margin,int(ET.parse(args.base/'resources'/'settings.xml').getroot().get('background','222222'),16)|0xff000000)
                    if margin:
                        from .gui import draw
                        draw(name,ip.root,ip.current,bitmap,w,h,custom,args.base)
                    save_bitmap(bitmap,w,h,args.output/(stem+'.png'))
                else:
                    save_vox(state,fx,fy,fz,colors,args.output/(stem+'.vox'))
            print(f'{name}: seed={seed}, steps={ip.counter}, dimensions={fx}x{fy}x{fz}')
