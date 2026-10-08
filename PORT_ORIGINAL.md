# MarkovJunior em Python

Tradução do motor de [mxgmn/MarkovJunior](https://github.com/mxgmn/MarkovJunior), commit `42aaf24bcf54ae164fba49c0a59348297904a676`. Licença MIT; autoria original de Maxim Gumin. A cópia integral e sem alterações desse commit está em `original/`, incluindo fontes C#, modelos, imagens e recursos.

## Executar

Requer Python 3.10+ e Pillow. Execute os comandos na pasta extraída:

```bash
python -m pip install -r requirements.txt
python -m markovjunior --model Flowers --size 60 --seed 42 --output output
python -m markovjunior --model MazeGrowth --size 59 --seed 12345 --output output
python -m markovjunior --model Apartemazements --length 6 --width 6 --height 3 --seed 42 --iso --pixelsize 6 --output output
```

`--steps` limita os passos; `--steps 0` executa até o término natural. `--frames` salva quadros PNG sucessivos. Sem `--iso`, grades 3D são exportadas em VOX. Sem `--model`, o catálogo `models.xml` é executado; ele inclui modelos grandes e pode demorar bastante. A versão Python é mais lenta que o C# original, especialmente em grades grandes, busca e WFC.

API:

```python
from pathlib import Path
import xml.etree.ElementTree as ET
from markovjunior import Interpreter

base = Path('.')
ip = Interpreter(ET.parse(base / 'models/MazeGrowth.xml').getroot(), 59, 59, 1, base)
state, legend, width, height, depth = list(ip.run(seed=42, steps=0))[-1]
```

## O que foi traduzido

Motor e controle de execução; grades e regras 2D/3D; todos os grupos de simetria do original; cache incremental de correspondências; nós `one`, `all`, `prl`, `markov`, `sequence`, `path`, `map`, `convolution`, `convchain`; campos, observações e busca heurística; WFC por sobreposição e por tiles; leitura/escrita de PNG e VOX; projeção isométrica e painel visual de regras com as fontes originais.

O gerador aleatório reproduz `System.Random(int seed)` do .NET 10, inclusive overflow de inteiros de 32 bits. Modelos XML, paletas, fontes, amostras e tiles foram preservados. A CLI aceita as configurações do catálogo original e acrescenta argumentos para execução individual. Arquivos de saída existentes não são apagados automaticamente.

## Evidência e limites

A comparação executa C# original e Python separadamente, com os mesmos modelos, dimensões, limites e sementes. Verifica estado binário da grade, dimensões, símbolos, contador de passos, pixels RGBA decodificados e bytes dos arquivos VOX. O PNG `prova_visual.png` apresenta saídas reais das duas implementações lado a lado e a diferença pixel a pixel. `validation/report.json` registra todos os casos e os hashes das grades e dos pixels.

Os 159 modelos originais foram carregados e submetidos a uma bateria com dimensões reduzidas e limite de 300 passos. Dois problemas de busca, `MultiSokoban8` e `SokobanLevel2`, excederam 35 segundos nas duas implementações; suas execuções completas não foram verificadas. O resultado final foi **189 casos idênticos, zero divergências e dois testes com tempo excedido**. Casos adicionais executam gerações completas até o término natural com sementes 0, 12345 e 2147483647 e verificam o painel visual, buscas simples com solução e cenas 3D no tamanho original. Consulte o relatório para os resultados finais e configurações exatas.

Igualdade comprovada refere-se aos casos registrados: não é uma prova matemática de igualdade de todos os modelos, dimensões e sementes possíveis. WFC usa aleatoriedade sem semente no desempate de votos de prévias intermediárias no C# original; essas prévias podem variar entre execuções, e a versão Python conserva esse comportamento. As saídas finais dos casos WFC verificados são comparadas normalmente. A busca original é essencialmente 2D; essa restrição foi conservada.

A implementação roda somente em Python e não chama o C# para gerar resultados. O .NET é necessário apenas para reproduzir a validação comparativa.

## Reproduzir os testes

```bash
python -m pip install -r requirements-validation.txt
python validation/test_rng.py
python validation/compare.py
# Opcional: gerar novamente as referências, com .NET SDK 10 instalado:
bash validation/build_reference.sh
```

O teste do RNG compara 14.208 valores efetivamente emitidos por `System.Random` em 111 sementes, incluindo extremos e as sementes que expuseram o problema de overflow. A reprodução da bateria inteira pode demorar; os dois puzzles sem limite de busca podem ser interrompidos.

`codigo_completo.txt` reúne as fontes Python, os modelos e recursos XML, o harness C# de validação e a referência C# original, identificados por caminho. É código-fonte consolidado em texto; TXT não é um executável. Os arquivos `.py` foram compilados e verificados com `compileall`; o bytecode Python 3.12 está em `bytecode_python312/` no ZIP. Para outro Python, o interpretador recompila as fontes automaticamente.
