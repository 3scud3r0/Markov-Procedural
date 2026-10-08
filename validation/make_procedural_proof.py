"""Render actual SVG output and actual source snippets into a shareable figure."""
import json
import textwrap
from pathlib import Path
import cairosvg
from PIL import Image,ImageDraw,ImageFont

BASE=Path(__file__).resolve().parents[1]


def main():
    previews=BASE/'previews'
    previews.mkdir(exist_ok=True)
    for name in ('jardim','labirinto'):
        cairosvg.svg2png(url=str(BASE/'generated'/name/(name+'.svg')),write_to=str(previews/(name+'.png')))
    report=json.loads((BASE/'validation/backend_report.json').read_text())
    assert len(report['targets'])==9 and all(t['status']=='pass' for t in report['targets'])
    canvas=Image.new('RGB',(1600,1640),'#0d1421')
    draw=ImageDraw.Draw(canvas)
    fontdir=Path('/usr/share/fonts/truetype/dejavu')
    def font(size,bold=False,mono=False):
        name='DejaVuSansMono.ttf' if mono else 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
        return ImageFont.truetype(str(fontdir/name),size) if (fontdir/name).exists() else ImageFont.load_default()
    white='#f0f4fa'; muted='#a6b6cf'; mint='#88dfb5'
    draw.text((40,28),'MARKOVJUNIOR · PLATAFORMA PROCEDURAL',font=font(34,True),fill=white)
    draw.text((42,78),'C · C++ · Rust · Python · JavaScript · TypeScript · Go · Lua · SQL',font=font(23),fill=mint)
    draw.rounded_rectangle((40,132,1560,870),radius=18,fill='#162133')
    garden=Image.open(previews/'jardim.png').convert('RGB')
    canvas.paste(garden,((1600-garden.width)//2,150))
    draw.text((60,850),'Cena real gerada por regras: curvas, ramificações e folhas · exportada em SVG e JSON',font=font(17),fill=muted)
    for x,label,extension in [(40,'C++','cpp'),(548,'RUST','rs'),(1056,'PYTHON','py')]:
        draw.rounded_rectangle((x,906,x+504,1540),radius=16,fill='#162133')
        draw.text((x+18,922),label,font=font(22,True),fill=mint)
        source=(BASE/'generated/calculos/variant_000'/('calculos.'+extension)).read_text()
        lines=source.splitlines()
        start=next(i for i,line in enumerate(lines) if 'proc_000(' in line)
        finish=next((i+1 for i in range(start+1,len(lines)) if lines[i] in ('}','') and i>start+1),len(lines))
        snippet=lines[start:finish]
        y=966
        for line in snippet:
            for wrapped in textwrap.wrap(line,width=54,subsequent_indent='    ',replace_whitespace=False,drop_whitespace=False) or ['']:
                draw.text((x+18,y),wrapped,font=font(13,mono=True),fill=white)
                y+=19
                if y>1500:break
            if y>1500:break
    draw.text((42,1574),f"9 linguagens verificadas · {report['total_checks']:,} resultados iguais à referência · geração reproduzível por semente".replace(',','.'),font=font(21,True),fill=mint)
    draw.text((42,1610),'Fontes, receitas, extensões, exemplos gerados e relatório de compilação incluídos no ZIP.',font=font(17),fill=muted)
    canvas.save(BASE/'prova_procedural.png')

if __name__=='__main__':main()
