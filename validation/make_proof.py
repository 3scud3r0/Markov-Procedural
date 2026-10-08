"""Build an evidence figure exclusively from independently generated PNGs."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont


def main():
    base=Path(__file__).resolve().parents[1]
    report=json.loads((base/'validation/report.json').read_text())
    records={r['case']['id']:r for r in report['records']}
    selected=['Flowers_full_12345','MazeGrowth_full_12345','WaveFlowers_full_0','Knots3D_showcase','Apartemazements_showcase']
    fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    boldpath=fontpath.with_name('DejaVuSans-Bold.ttf')
    font=lambda size,bold=False: ImageFont.truetype(str(boldpath if bold else fontpath),size) if fontpath.exists() else ImageFont.load_default()
    background=(15,23,34)
    canvas=Image.new('RGB',(1600,3380),background)
    d=ImageDraw.Draw(canvas)
    white=(236,242,250); muted=(154,173,195); green=(97,231,170)
    d.text((42,28),'MARKOVJUNIOR · C# → PYTHON',font=font(34,True),fill=white)
    summary=report['summary']
    d.text((44,78),f"{summary['pass']} casos idênticos · {summary['fail']} divergências · {summary['missing']} testes de busca com tempo excedido",font=font(21),fill=green)
    d.text((44,112),'Comparação real de pixels RGBA · mesmo modelo, dimensões e semente · commit 42aaf24',font=font(18),fill=muted)
    for row,id in enumerate(selected):
        record=records[id]
        assert record['status']=='pass' and record['different_pixels']==0
        c=record['case']; y=166+row*630
        d.rounded_rectangle((30,y,1570,y+610),radius=14,fill=(23,34,49))
        d.text((48,y+14),c['model'],font=font(25,True),fill=white)
        md=record['python_metadata']
        detail=f"Semente {c['seed']} · grade final {md['mx']}×{md['my']}×{md['mz']} · término em {md['counter']} passos"
        d.text((330,y+20),detail,font=font(17),fill=muted)
        for x,label in ((48,'ORIGINAL · C#'),(628,'TRADUÇÃO · PYTHON'),(1208,'DIFERENÇA')):
            d.text((x,y+58),label,font=font(16,True),fill=muted)
        a=Image.open(base/'validation/original'/(id+'.png')).convert('RGBA')
        b=Image.open(base/'validation/python'/(id+'.png')).convert('RGBA')
        aa,bb=np.array(a),np.array(b)
        assert aa.shape==bb.shape and np.array_equal(aa,bb)
        for x,im in ((48,a),(628,b)):
            scale=min(550/im.width,500/im.height)
            if scale>=1:
                scale=int(scale)
            size=(max(1,int(im.width*scale)),max(1,int(im.height*scale)))
            # Every actual comparison uses native pixels; display resizes use nearest neighbor.
            shown=im.resize(size,Image.Resampling.NEAREST).convert('RGB')
            canvas.paste(shown,(x+(550-shown.width)//2,y+86+(500-shown.height)//2))
        delta=np.max(np.abs(aa.astype('int16')-bb.astype('int16')),axis=2).astype('uint8')
        diff=Image.fromarray(delta).convert('RGB')
        diff.thumbnail((300,205),Image.Resampling.NEAREST)
        canvas.paste(diff,(1208+(300-diff.width)//2,y+88))
        d.text((1214,y+432),'0 pixels diferentes',font=font(20,True),fill=green)
        d.text((1214,y+468),'RGBA 100% idêntico',font=font(17),fill=white)
        d.text((48,y+590),'SHA-256 dos pixels (ambos): '+record['pixel_sha256_original'],font=font(14),fill=muted)
    d.text((44,3340),'Relatório, referências C# e resultados Python incluídos no ZIP. Igualdade verificada nos casos registrados.',font=font(16),fill=muted)
    canvas.save(base/'prova_visual.png')

if __name__=='__main__':
    main()
