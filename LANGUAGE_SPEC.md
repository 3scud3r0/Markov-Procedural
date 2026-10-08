# Markov 1.0 — especificação executável

Status: contrato implementado e testado no runtime `markovjunior.language`, no Studio e na CLI. Sintaxe escolhida: **compatível com Python, com operações procedurais próprias**.

Markov 1.0 é um ambiente de programação procedural construído sobre a sintaxe e a semântica de Python. Não exige JSON para escrever programas. Arquivos `.mp` são compilados pelo parser e compilador Python e executados pelo runtime Markov. O Studio executa Python real com Pyodide em um Web Worker; a CLI executa CPython.

## 1. Linguagem e execução

Estão disponíveis variáveis, expressões, inteiros Python, floats, strings, listas, tuplas, conjuntos, dicionários, funções, recursão, classes, condições, laços, comprehensions, exceções e imports. A programação não fica limitada ao subconjunto numérico dos nove exportadores antigos.

A entrada é `main.mp` por padrão. Outros arquivos `.mp` e `.py` no projeto podem ser importados por nome: `from shapes import orbit`. O runtime fornece implicitamente as operações abaixo; `from markov import *` é uma forma explícita de obtê-las.

Os imports da biblioteca padrão disponíveis no ambiente funcionam. No navegador, pacotes de Python reconhecidos pela distribuição Pyodide são carregados quando importados. Pacotes não incluídos na distribuição não são instalados automaticamente. Código de um programa ou link compartilhado é executado quando o usuário usa **Executar**; exemplos distribuídos com o Studio podem executar no primeiro carregamento.

“Programação livre” significa escrever e executar lógica própria dentro deste ambiente. Não significa acesso irrestrito ao sistema operacional, execução nativa de qualquer linguagem ou disponibilidade de todas as bibliotecas Python no navegador. O filesystem do navegador é virtual. APIs de navegador e rede obedecem às restrições de Workers e CORS. CLI executa código local com as permissões do usuário; o runtime não é uma sandbox de segurança para código não confiável.

## 2. Aleatoriedade e parâmetros

| Operação | Contrato |
| --- | --- |
| `seed(n)` / `seed()` | Define / consulta a semente inteira com sinal de 32 bits; redefinir reinicia o RNG procedural. |
| `random(minimum=0, maximum=1)` | Float no intervalo ordenado. Usa o RNG determinístico compatível com o porte original. |
| `randint(minimum, maximum)` | Inteiro, incluindo os dois limites. |
| `choose(values, weights=None)` | Escolha uniforme ou com pesos positivos. |
| `noise(x, y=0, z=0)` | Ruído de valor contínuo em [0,1], interpolado em 3D e determinado pela semente. |
| `param(name, default, min=None, max=None, step=None)` | Retorna o valor e declara um controle no inspector. Aceita número, bool ou string. Overrides são validados. |
| `@rule` | Registra uma função procedural reutilizável. Sua chamada continua sendo uma chamada de função Python. |

A reprodutibilidade vale para o mesmo código, parâmetros e chamadas dessas APIs. Uso de tempo real, rede ou RNGs externos pode tornar um programa não determinístico.

## 3. Geometria e cena

Construtores retornam objetos mutáveis `Node`:

```python
sphere(radius=1, **options)
box(size=[1, 1, 1], **options)
cylinder(radius=0.5, height=2, **options)
cone(radius=1, height=2, **options)
torus(radius=1, thickness=0.2, **options)
plane(width=2, depth=2, **options)
line(points, width=0.05, **options)
mesh(vertices, faces, **options)
```

Opções comuns: `name`, `position=[x,y,z]`, `rotation=[x,y,z]` em radianos, `scale=[x,y,z]`, `color="#rrggbb"`.

Um objeto possui `id`, `name`, `kind`, `position`, `rotation`, `scaling`, `color`, `visible`, `tags`. Métodos: `translate(x=0,y=0,z=0)`, `rotate(x=0,y=0,z=0)`, `resize(x,y=None,z=None)` e `remove()`. As transformações são locais e a ordem de rotação segue yaw/pitch/roll do Babylon.js.

`scene.objects` lista os objetos. `scene.find(name)` procura pelo nome. `scene.clear()` remove todos. Configure `scene.background`, `scene.ground`, `scene.ground_color`, `scene.ground_size` e `scene.camera`. Câmera aceita `target`, `radius`, `alpha` e `elevation`.

O documento de cena usa `schema: "markov.scene/1"`, com objetos identificados, geometria, transformações e cores. O mesmo documento alimenta Babylon.js e o renderizador CPU independente. O modo CPU usa projeção em perspectiva, triângulos ordenados e iluminação simplificada; não reproduz todos os efeitos do WebGL.

## 4. Textos, dados e arquivos

- `print(...)` e stderr aparecem no console.
- `emit(name, value, media_type=None)` cria uma saída: strings como texto, objetos serializáveis como JSON, bytes como arquivo binário.
- Escritas Python normais com `open()` criam arquivos no diretório virtual temporário do programa e são coletadas ao final da execução inicial.
- `grammar(rules, start="<start>", max_depth=8)` executa as gramáticas ponderadas da plataforma.
- `generate(generator, params=None, targets=None, name="generated")` acessa os geradores existentes e registra seus arquivos como saídas.

Os nove exportadores de código continuam disponíveis por `generate("program", ...)`. Eles traduzem **a IR numérica comum**, não um programa Markov/Python arbitrário para nove linguagens. Compiladores nativos não são executados no GitHub Pages.

## 5. Interação e animação

Uma função `update(t, dt)` ativa o botão de animação. `t` e `dt` estão em segundos. Cada callback usa o estado persistente do programa; `keys` é o conjunto de teclas pressionadas e `mouse` contém `x`, `y`, `pressed`.

```python
ball = sphere(position=[0,1,0])
def update(t, dt):
    ball.position[0] += dt if "ArrowRight" in keys else 0
```

O Studio solicita callbacks em até aproximadamente 15 Hz e mantém a câmera. Pausar interrompe os callbacks; retomar reinicia `t`, mantendo os objetos e variáveis. Erros em callbacks pausam a animação e mostram o arquivo e a linha. O código Python roda no Worker; a renderização roda na interface.

## 6. Projetos e edições

Um projeto JSON possui:

```json
{
  "schema": "markov.project/1",
  "name": "Meu programa",
  "seed": 42,
  "entry": "main.mp",
  "activeFile": "main.mp",
  "parameters": {},
  "files": [{"name": "main.mp", "content": "sphere()"}],
  "edits": {}
}
```

O Studio pode incluir `savedScene` com a prévia editada. Salvar/reabrir preserva arquivos, entrada, parâmetros e edições. Edições manuais são sobreposições da visualização, identificadas por id, nome e tipo; não reescrevem silenciosamente o programa. Limpar edições restaura a cena produzida pelo código. Voltar a executar calcula a cena novamente e aplica as sobreposições compatíveis.

Há salvamento local no navegador, histórico de projetos recentes, exportação/importação JSON e compartilhamento do código por URL. Não há sincronização remota ou colaboração multiusuário nesta versão.

## 7. Diagnóstico, parada e limites

Erros de sintaxe e de execução retornam tipo, mensagem, arquivo, linha e traceback; o editor destaca a linha. O console mantém a saída produzida antes do erro.

Parar termina o Worker e reinicializa o runtime sem descartar o código. Um watchdog da interface interrompe execuções que ultrapassam 20 segundos. Existe também um orçamento cooperativo de 8 segundos / 1 milhão de eventos de linha na execução inicial, e 1 segundo / 100 mil eventos nos callbacks. Operações nativas longas podem não produzir eventos de trace; a parada pelo Worker cobre esse caso no navegador.

Orçamentos atuais: 50 arquivos de projeto, até 1 MB por arquivo e 2 MB de fontes por projeto; 5.000 objetos; 10.000 vértices / 20.000 faces por malha; a visualização limita a soma de malhas a 100.000 vértices / 150.000 faces. Saídas: até 100 arquivos e 5 MB por arquivo. Console: 100.000 caracteres. Coordenadas precisam ser finitas e estar em ±1.000.000. Essas restrições são orçamentos práticos, não uma garantia de proteção contra esgotamento de memória por código arbitrário.

## 8. Critérios de aceite da 1.0

- Escrever um programa que não existia nos exemplos e executá-lo no editor.
- Executar classes, recursão, estruturas de dados, imports entre arquivos e operações procedurais.
- Obter console, arquivos e cenas; alterar parâmetros declarados no código.
- Localizar erros no arquivo e linha e preservar stdout parcial.
- Executar, pausar e interromper callbacks; recuperar o runtime após parada.
- Salvar/reabrir projeto preservando código e edições.
- Renderizar e manipular cena sem WebGL, por Canvas 2D.
- Manter o motor MarkovJunior e a equivalência dos exportadores já validados.

Os testes estão em `tests/test_language.py`, `validation/test_studio.cjs` e nos testes anteriores. A especificação não promete todas as ideias do roadmap anterior: glTF, editor de gramáticas com parser/interpretador genérico, toda a IR tipada em nove backends, biomas, trabalho offline e catálogo remoto de plugins são expansões futuras.
