# Markov 1.0 — Procedural Studio

**Uma linguagem procedural compatível com Python e um ambiente para escrever e executar seus próprios programas.** Funções, classes, algoritmos, imports entre arquivos e comandos procedurais produzem geometria, animação, textos, dados e arquivos. O projeto mantém o motor MarkovJunior e seus modelos originais.

**[Abrir o Studio](https://3scud3r0.github.io/Markov-Procedural/)** · [Referência](https://3scud3r0.github.io/Markov-Procedural/reference.html) · [Especificação executável da 1.0](LANGUAGE_SPEC.md)

```python
@rule
def constellation(count):
    for i in range(count):
        sphere(radius=random(0.1, 0.4),
               position=[random(-5, 5), random(1, 6), random(-5, 5)],
               color=choose(["#d6ec9f", "#e8a16f"]))

count = param("count", 20, min=1, max=100)
constellation(count)
print(f"{count} objetos criados pelo meu programa")
emit("result.json", {"count": count, "seed": seed()})
```

## No navegador

Abra um exemplo ou um projeto em branco, edite os arquivos `.mp` e use **Executar** ou **Ctrl + Enter**. O Studio inclui editor CodeMirror com autocomplete e diagnósticos, console, parâmetros declarados no código, inspector de objetos, saídas para download, módulos editáveis e callbacks `update(t, dt)` para animação e interação.

Python real roda em um **Web Worker via Pyodide**. Babylon.js renderiza quando há WebGL; sem WebGL, **Canvas 2D na CPU** projeta a mesma cena e oferece seleção e transformações, com iluminação simplificada. O botão Parar termina o Worker sem descartar o código.

Salvar/reabrir projeto preserva código, parâmetros e edições. Há persistência local no navegador, histórico e compartilhamento do código por link. Edições visuais são sobreposições, não alterações silenciosas no programa.

## Executar localmente

Python 3.10+:

```bash
python -m pip install .
python -m markovjunior run examples/language/orbits/main.mp --seed 42 --output output
```

A CLI executa código com permissões locais; use programas confiáveis. Para servir o Studio:

```bash
python -m http.server 8000 --directory docs
```

Abra `http://localhost:8000`. O primeiro carregamento requer internet para Pyodide/Pillow. Após alterar o motor ou os exemplos:

```bash
python scripts/build_browser_runtime.py
```

Após alterar o editor:

```bash
npm ci --prefix web
npm run --prefix web build
```

A publicação usa GitHub Actions em [.github/workflows/pages.yml](.github/workflows/pages.yml).

## O contrato da linguagem

Markov usa o parser e a semântica de Python. `.mp` não é uma sintaxe fictícia ou um formulário de JSON: é código executável, com APIs procedurais documentadas. A biblioteca padrão e os pacotes disponíveis no ambiente podem ser importados.

“Programação livre” não significa executar qualquer linguagem, acessar irrestritamente o sistema operacional ou dispor de todas as bibliotecas Python no navegador. O filesystem do navegador é virtual. Veja [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md) para recursos, formatos e orçamentos.

Os nove exportadores antigos — Python, JS, TS, C, C++, Rust, Go, Lua, SQL — continuam disponíveis por `generate("program", ...)`. Eles exportam **a IR numérica comum**, não qualquer programa Markov/Python para nove linguagens. O Pages não executa compiladores nativos.

## Compatibilidade com o porte original

```bash
python -m markovjunior --model Flowers --size 16 --seed 42 --steps 300
python -m markovjunior generate examples/procedural/project.json --output generated
```

159 modelos e seus recursos continuam incluídos. O guia dos geradores e extensões está em [GENERATOR_GUIDE.md](GENERATOR_GUIDE.md); a documentação do porte original, em [PORT_ORIGINAL.md](PORT_ORIGINAL.md). A referência integral é preservada em `original/`.

## Validação

```bash
python -m unittest discover -s tests -v
node validation/test_studio.cjs
STUDIO_CPU=1 node validation/test_studio.cjs
```

Os 31 testes Python e os testes de navegador verificam o contrato da linguagem. Os testes de navegador exigem Playwright e Chromium, e o Studio servido em `http://127.0.0.1:8765/` por padrão; `STUDIO_URL` permite testar outra URL. `STUDIO_CHROMIUM` seleciona o executável. Testam programas criados no editor, módulos, classes, controles, diagnósticos, callbacks, parada/recuperação, downloads, persistência e visualização com WebGL desativado.

A validação anterior entre compiladores registra 2.673 resultados equivalentes nas nove linguagens em `validation/backend_report.json`. As evidências de paridade visual e RNG do porte estão preservadas; os módulos do motor original não foram alterados para implementar a linguagem.

## Downloads

**1.0:** [Projeto completo — ZIP](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/Markov_Studio_1.0.zip) · [Código consolidado — TXT](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/codigo_markov_1_0.txt) · [Prévia sem WebGL — PNG](https://github.com/3scud3r0/Markov-Procedural/raw/refs/heads/main/downloads/studio_1_0_cpu.png)

A pasta [downloads/](https://github.com/3scud3r0/Markov-Procedural/tree/main/downloads) mantém as entregas para download. Os arquivos antigos da plataforma 0.2.0 estão identificados pelo conteúdo e pela wheel 0.2.0; a 1.0 tem sua entrega própria. O botão **Code → Download ZIP** do GitHub baixa os fontes atuais do repositório.

## Origem, versões e licença

Baseado em [mxgmn/MarkovJunior](https://github.com/mxgmn/MarkovJunior), commit `42aaf24bcf54ae164fba49c0a59348297904a676`, de Maxim Gumin, MIT. A linguagem e o Studio são extensões do porte Python. Babylon.js: Apache-2.0; CodeMirror: MIT. Veja [THIRD_PARTY.md](THIRD_PARTY.md).

A evolução e os recursos ainda futuros estão em [ROADMAP.md](ROADMAP.md). A versão 1.0 estabiliza o contrato executável definido nesta entrega; não declara prontas todas as ideias do roadmap anterior.
