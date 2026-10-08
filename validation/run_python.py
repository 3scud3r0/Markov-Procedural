"""Execute precisely the JSON cases also consumed by the original C# harness."""
import json
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from markovjunior import Interpreter
from markovjunior.graphics import render,save_bitmap,save_vox
from markovjunior.gui import draw

def run(case,base,output):
    model_path = base/'validation'/'fixtures'/(case['model']+'.xml') if case.get('fixture') else base/'models'/(case['model']+'.xml')
    ip = Interpreter(ET.parse(model_path).getroot(),case['mx'],case['my'],case['mz'],base)
    state,legend,mx,my,mz = list(ip.run(case['seed'],case['steps'],False))[-1]
    palette = {e.attrib['symbol']:0xff000000|int(e.attrib['value'],16) for e in ET.parse(base/'resources'/'palette.xml').getroot()}
    colors = [palette[c] for c in legend]
    output.mkdir(parents=True,exist_ok=True)
    stem = output/case['id']
    stem.with_suffix('.state').write_bytes(state)
    stem.with_suffix('.json').write_text(json.dumps(dict(mx=mx,my=my,mz=mz,counter=ip.counter,legend=''.join(legend))))
    bitmap,w,h = render(state,mx,my,mz,colors,case['pixelsize'],case.get('margin',0))
    if case.get('margin',0):
        draw(case['model'],ip.root,ip.current,bitmap,w,h,palette,base)
    save_bitmap(bitmap,w,h,stem.with_suffix('.png'))
    if mz>1 and max(mx,my,mz)<256:
        save_vox(state,mx,my,mz,colors,stem.with_suffix('.vox'))

if __name__=='__main__':
    cases = json.loads(Path(sys.argv[1]).read_text())
    base,output = Path(sys.argv[2]).resolve(),Path(sys.argv[3]).resolve()
    selected = [c for c in cases if len(sys.argv)<5 or c['id']==sys.argv[4]]
    for c in selected:
        try:
            run(c,base,output)
            print(c['id'],'OK',flush=True)
        except Exception:
            output.mkdir(parents=True,exist_ok=True)
            (output/(c['id']+'.error')).write_text(traceback.format_exc())
            print(c['id'],'ERROR',flush=True)
