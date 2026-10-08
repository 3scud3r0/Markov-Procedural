# MarkovJunior — Plataforma Procedural

## Downloads

[Baixar projeto completo (ZIP)](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/MarkovJunior_Procedural.zip) · [Código consolidado (TXT)](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/codigo_procedural_completo.txt) · [Demonstração visual (PNG)](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/prova_procedural.png)

Todos os arquivos estão em [downloads/](https://github.com/3scud3r0/Markov-Procedural/tree/main/downloads), incluindo a wheel instalável e o relatório de validação.


A versão Python evoluiu para uma base extensível que gera **programas em várias linguagens, linguagens próprias, textos, dados e cenas vetoriais**. Uma semente determina o conteúdo; um documento intermediário é exportado para os formatos escolhidos. O motor visual original e os 159 modelos continuam disponíveis.

## Começar

### Playground no navegador

A interface [Babylon.js + Pyodide](https://3scud3r0.github.io/Markov-Procedural/) fica em `docs/`. O Python real roda em um Web Worker: gera jardim 3D, SVG, gramáticas e os nove formatos de código. Selecione objetos para mover, girar, escalar ou excluir; exporte/importe as edições em JSON. O modo de arquivos permite baixar o conteúdo gerado. Não executa compiladores C/C++/Rust.

**Sem WebGL:** a página usa automaticamente um renderizador Canvas 2D na CPU, com projeção da mesma cena 3D. Também pode escolher **Canvas 2D · sem WebGL** no seletor. Orbite arrastando o fundo (ou com o botão direito), use a roda para zoom e arraste objetos selecionados para mover, girar ou escalar. Exportação/importação de edições funciona nos dois modos. O modo CPU usa formas e cores simplificadas, sem os efeitos de iluminação do Babylon.js.

Para testar localmente, execute `python -m http.server 8000 --directory docs` e abra `http://localhost:8000`. O primeiro carregamento usa internet para baixar Pyodide 0.27.7 e Pillow; Babylon.js 9.30.0 está incluído localmente. Depois de alterar os fontes Python, execute `python scripts/build_browser_runtime.py`.

A publicação está definida em `.github/workflows/pages.yml`. Em **Settings → Pages → Build and deployment**, selecione **GitHub Actions**. Para publicar sem workflow, use **Deploy from a branch → main → /docs**. A proposta de especificação das versões 0.5 a 1.0 está em [ROADMAP.md](ROADMAP.md), com critérios de aceite e recursos ainda não implementados.

Requer Python 3.10+. Na pasta extraída:

```bash
python -m pip install -r requirements.txt
python -m markovjunior generate examples/procedural/project.json --output generated
```

O projeto de exemplo gera três variantes do mesmo conjunto de funções em **Python, JavaScript, TypeScript, C, C++, Rust, Go, Lua e SQL**, além de jardim SVG, labirinto SVG, narrativa, entidades JSON e texto de uma linguagem própria chamada Garden. Cada variante fica em uma pasta independente para não haver conflito de funções ao compilar.

```bash
python -m markovjunior generate examples/procedural/project.json --seed 12345 --output outra_geracao
python -m markovjunior generate --list-targets
```

Também é um pacote instalável:

```bash
python -m pip install .
markovjunior generate examples/procedural/project.json --output generated
```

A instalação inclui modelos e recursos. A CLI lê os recursos da pasta do projeto quando executada das fontes e os recursos empacotados quando instalada por wheel. A wheel distribuída funciona em plataformas com Python compatível; os compiladores de destino só são necessários para executar ou validar os códigos gerados.

## Uma receita, várias saídas

```json
{
  "version": 1,
  "seed": 42,
  "jobs": [
    {
      "name": "calculos",
      "generator": "program",
      "params": {"functions": 4, "expression_depth": 3, "iterations": 5},
      "targets": ["python", "c", "cpp", "rust", "sql", "json"]
    }
  ]
}
```

Execute com `python -m markovjunior generate minha_receita.json --output saida`. O código fica em `saida/calculos/`. `manifest.json` registra as sementes de cada tarefa, os parâmetros e o SHA-256 de cada arquivo. Adicionar um formato ou mudar a ordem das tarefas não altera o documento gerado. `count` cria várias instâncias com sementes independentes e reproduzíveis.

| Gerador | O que produz | Formatos incluídos |
| --- | --- | --- |
| `program` | Programa numérico com funções, expressões, condições e laços | Python, JS, TS, C, C++, Rust, Go, Lua, SQL, JSON |
| `program-ir` | Programa a partir da representação JSON exportada e editada | Os mesmos formatos de código |
| `grammar` | Expansões de regras com alternativas ponderadas, recursão e inteiros | TXT, Markdown, JSON |
| `data` | Objetos e arrays definidos por um esquema | JSON |
| `scene` | Jardim vetorial com curvas, árvores e folhas | SVG, JSON |
| `grid` | Saída dos modelos visuais MarkovJunior como cena estruturada | SVG, JSON |

A representação de programas é uma árvore tipada, não uma substituição de nomes de linguagens em um texto. Ela possui uma interpretação de referência e valida variáveis, escopos, condições, laços finitos e intervalos numéricos antes da exportação. Isso dá um ponto comum para desenvolver novos geradores e exportadores.

## Criar uma linguagem própria

Gramáticas são declarativas. `<nome>` referencia uma produção e `<int:min:max>` gera um inteiro. `weight` define o peso de uma alternativa. Regras recursivas são expandidas apenas quando existe uma derivação que cabe no limite de profundidade. Há limites de expansões e caracteres. `\<` representa um sinal `<` literal.

```json
{
  "version": 1,
  "seed": 42,
  "jobs": [{
    "name": "idioma",
    "generator": "grammar",
    "params": {
      "start": "<programa>",
      "rules": {
        "programa": ["plant <arvore> at <int:0:100>,<int:0:100>;"],
        "arvore": ["oak", "fern", "willow"]
      }
    },
    "targets": ["text", "json"]
  }]
}
```

A receita `examples/procedural/extensions.json` usa uma extensão real: um gerador de vocabulário, um exportador CSV e um exportador `.garden` que valida a sintaxe e os comandos da nova linguagem.

```bash
python -m markovjunior generate examples/procedural/extensions.json \
  --plugin examples/procedural/extension.py --output generated_extensions
```

Uma gramática define como produzir textos na sua linguagem. Para interpretá-la, compilá-la ou executar suas ações, acrescente um parser/interpretador ou um exportador específico; o exemplo Garden inclui validação de sintaxe, não um interpretador completo.

## Acrescentar outros geradores e linguagens

Um arquivo de extensão implementa `register(registry)`. Geradores retornam `Document`; exportadores retornam um ou mais `Artifact`. Não há limite fixo na lista de linguagens. Novos formatos precisam de um exportador que conheça a semântica e a sintaxe desejadas.

```python
from markovjunior.procedural import Artifact, Document


def generate_greeting(params, context):
    choices = params.get("choices", ["olá", "mundo"])
    text = choices[context.random.next(len(choices))]
    return Document("text", text)


def emit_custom(doc, stem):
    return (Artifact(stem + ".custom", "say " + repr(doc.value), "text/plain"),)


def register(registry):
    registry.register_generator("greeting", generate_greeting)
    registry.register_target("custom", {"text"}, emit_custom)
```

Para uma linguagem de programação, percorra `doc.value.functions` e os nós `Literal`, `Ref`, `Binary`, `Set`, `If`, `Repeat` e `Return`. Os nove exportadores existentes estão em `markovjunior/procedural/backends.py`. A validação comum está em `ir.py`. Extensões Python são carregadas somente quando indicadas por `--plugin`; são código local executável.

API:

```python
from markovjunior.procedural import run_project, default_registry, Program

registry = default_registry()
manifest = run_project(receita, "saida", seed=42, registry=registry)
# Para editar uma árvore exportada: Program.from_data(documento_json["value"])
```

## Usar os códigos gerados

Os arquivos são bibliotecas de funções. Exemplos da primeira variante:

```bash
python -m py_compile generated/calculos/variant_000/calculos.py
node --check generated/calculos/variant_000/calculos.mjs
gcc -std=c11 -c generated/calculos/variant_000/calculos.c -o calculos_c.o
g++ -std=c++17 -c generated/calculos/variant_000/calculos.cpp -o calculos_cpp.o
rustc --crate-type lib generated/calculos/variant_000/calculos.rs -o libcalculos.rlib
```

`proc_000`, `proc_001` e as demais funções recebem `x` e `y` e retornam um inteiro. Em Go, o arquivo usa `package generated`; em Lua, retorna uma tabela de funções; em JavaScript, exporta funções ES modules. SQL é uma consulta SQLite com parâmetros `:x` e `:y` e uma linha de resultado por função. JSON de `program` contém a árvore, não código para execução direta.

O núcleo atual cobre um **subconjunto numérico** com inteiros, soma, subtração, multiplicação, comparações, atribuições, condições e repetições finitas. As entradas precisam estar em ±1.000.000, e a análise limita os intermediários ao intervalo inteiro exato compartilhado pelos destinos. Não há geração arbitrária de aplicações completas, APIs externas, strings tipadas ou bibliotecas específicas de cada linguagem nesta versão. Essas funcionalidades podem ser acrescentadas com novos nós, geradores e exportadores.

## Testes e evidência

```bash
python -m unittest discover -s tests -v
python validation/validate_backends.py
```

A validação entre linguagens compila/executa 33 funções, geradas com oito sementes e incluindo um caso com laços e condições aninhados. Testa nove pares de entradas, incluindo os limites positivos e negativos. **2.673 resultados coincidiram: 297 em cada uma das nove linguagens.** Versões dos compiladores e resultados estão em `validation/backend_report.json`. Um compilador ausente é registrado como indisponível, não como teste aprovado; opções `--gcc`, `--gpp`, `--rustc`, `--node`, `--go`, `--lua` e `--tsc` permitem informar executáveis.

Os 13 testes de integração verificam reprodutibilidade, ordem das tarefas, importação da árvore JSON, recursão e limites das gramáticas, extensões, dados e SVG, falhas sem saídas parciais de geração, caminhos de arquivos e compatibilidade do comando visual antigo. Os 14.208 valores de referência do RNG também continuam idênticos.

A evidência visual antiga e a bateria do porte original estão preservadas em `prova_visual.png`, `validation/report.json` e `PORT_ORIGINAL.md`. O motor original não foi alterado; a CLI passou a reconhecer o novo comando `generate`.

`prova_procedural.png` mostra uma cena produzida pelo novo gerador e trechos reais de código. Os PNGs de prévia foram renderizados a partir dos SVGs; para reproduzi-los, instale `requirements-preview.txt` e execute `python validation/make_procedural_proof.py`.

## Origem e licença

A entrega inclui `codigo_procedural_completo.txt` com os fontes consolidados, uma wheel em `dist/`, bytecode em `bytecode_python312/`, receitas e saídas prontas. O TXT reúne código legível; os arquivos `.pyc` são o código Python compilado e dependem da versão 3.12. O código gerado nas outras linguagens foi compilado/executado para validação; compiladores e seus arquivos temporários não fazem parte do pacote. `manifesto_entrega.json` permite conferir a integridade dos arquivos distribuídos.

Baseado em [mxgmn/MarkovJunior](https://github.com/mxgmn/MarkovJunior), commit `42aaf24bcf54ae164fba49c0a59348297904a676`, de Maxim Gumin, licença MIT. `original/` contém a cópia integral desse commit. A nova plataforma é uma extensão Python do projeto, com exemplos e pontos de integração abertos.
