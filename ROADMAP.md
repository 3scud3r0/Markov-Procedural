# Evolução e estado real

## 1.0 — linguagem procedural executável e Studio

Disponível: sintaxe e semântica compatíveis com Python; programas escritos pelo usuário; funções, classes, recursão, estruturas de dados e módulos; regras procedurais, RNG, ruído, geometria e malhas; parâmetros declarados no código; console, arquivos e diagnósticos com linha; callbacks de animação e teclado; execução isolada em Worker; parada e recuperação; editor, inspector e projetos persistidos/exportáveis; visualização WebGL e CPU.

O contrato está em [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md). Os testes de aceite executam programas novos no editor, incluindo modos com WebGL desativado. **1.0 identifica esse contrato de linguagem e ambiente**, não o cumprimento automático de todas as ideias sugeridas anteriormente.

## O que aconteceu com a proposta 0.5–1.0

A entrega 0.2.0 não continha uma especificação prévia dessas versões. Um roadmap foi proposto depois, com ideias para editor, gramáticas, IR, mundos e extensões. Esses números eram marcos propostos; as versões intermediárias não foram lançadas.

| Ideia anterior | Estado nesta entrega |
| --- | --- |
| Cenas 2D/3D, transformações e projetos | Cena 3D versionada e Studio; geradores SVG existentes; projetos completos. Não há um esquema único que converta todo SVG em 3D. |
| Desfazer/refazer | Histórico do editor de código. Histórico de transformações da cena ainda futuro. |
| Linguagem programável, funções e strings | Executadas em Python/Markov. |
| Editor genérico de parsers/ASTs e interpretador Garden | Futuro. A biblioteca de gramáticas e o exportador Garden continuam existentes. |
| Ampliar todos os nove backends com strings, arrays e chamadas | Futuro. Os backends continuam com a IR numérica validada. |
| Terreno, arquitetura e composição | Programáveis por funções e malhas, com exemplos executáveis. Catálogo completo de biomas e redes ainda futuro. |
| glTF | Futuro. A exportação atual é JSON de cena e PNG. |
| Parar execução e limites | Implementados no Worker e no runtime. |
| Offline completo, plugins remotos e colaboração | Futuros. Há módulos locais, geradores extensíveis, armazenamento local e links de projeto. |

## Próximas extensões

1. Histórico de transformações e hierarquia de cenas.
2. Exportação glTF e materiais mais ricos.
3. Pacotes e dependências de projetos, com matriz de suporte por runtime.
4. Novos nós tipados e capacidades dos exportadores existentes.
5. Ferramentas de parser/AST e linguagem Garden executável.
6. Cache offline, cancelamento mais granular e benchmarks por dispositivo.

Cada extensão exige contrato, exemplo executável e validação antes de aparecer como disponível no Studio. Não há datas prometidas.
