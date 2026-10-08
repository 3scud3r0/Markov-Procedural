# Especificação de evolução — proposta

Não existia uma especificação para 0.5 a 1.0 na entrega 0.2.0. Este documento é uma **proposta de escopo**, sem datas ou garantia de implementação. Os números abaixo são marcos futuros, não funcionalidades já disponíveis.

## Disponível hoje

- Motor Python, nove exportadores de funções numéricas, gramáticas, dados e SVG.
- Playground estático com Python real via Pyodide em Web Worker e cenas editáveis no Babylon.js.
- Gerador de jardim 3D, controle de semente, seleção, movimento, rotação, escala e remoção de objetos.
- Exportação/importação das edições em JSON; exportação individual dos códigos e SVGs gerados.
- Renderização alternativa Canvas 2D na CPU, com projeção da cena 3D e edição sem WebGL; visual simplificado em relação ao Babylon.js.
- Compiladores C/C++/Rust não são executados no playground. O Python gera os fontes.

## 0.5 — Representação de cenas e editor

Proposto: unificar o esquema de cenas 2D/3D, grupos, hierarquia, materiais e transformações; acrescentar desfazer/refazer e salvar projetos completos.

Aceite: exportar e reimportar um projeto preserva cena, receita e edições; mesmos parâmetros e semente produzem o mesmo documento; testes de migração de esquemas e de histórico passam.

## 0.6 — Linguagens e gramáticas

Proposto: ferramentas para definir tokens, gramáticas, parsers e ASTs; mensagens de erro com linha/coluna; interpretador executável da linguagem Garden.

Aceite: uma linguagem criada pelo usuário consegue gerar, analisar e executar um programa de exemplo; entradas inválidas têm diagnóstico preciso; gramáticas recursivas respeitam limites.

## 0.7 — Representação de programas mais ampla

Proposto: ampliar a IR com tipos, strings, arrays e funções chamadas por outras funções; definir capacidades por backend; ampliar geração de programas em C, C++, Rust e demais destinos.

Aceite: cada backend anuncia os nós suportados e rejeita os demais antes da exportação; baterias de equivalência incluem os novos tipos e chamadas, com regras de memória/overflow documentadas.

## 0.8 — Mundos procedurais

Proposto: terreno, biomas, arquitetura, redes e grafos; composição de geradores; níveis de detalhe e exportação glTF.

Aceite: um projeto combina pelo menos três geradores; exportação glTF abre em outro visualizador; documentação registra orçamento de geometria e métricas nos dispositivos de referência.

## 0.9 — Extensões e desempenho

Proposto: API versionada de extensões, catálogo de exemplos, cancelamento de geração, limites de execução e cache/offline do playground.

Aceite: extensões demonstrativas funcionam nas APIs documentadas; tarefas longas podem ser canceladas; o modo offline funciona após baixar os pacotes e mostra quais recursos estão disponíveis.

## 1.0 — Contratos estáveis

Proposto: estabilizar formato de projeto, IR, esquema de cenas e API pública; publicar política de compatibilidade, migrações, instalação e matriz de suporte.

Aceite: testes de equivalência, round-trip e integração passam na matriz publicada; exemplos executam a partir de instalação limpa; limitações dos backends e do navegador são explícitas. Recursos experimentais ficam identificados.

## Limites e decisões ainda abertas

A execução nativa de C/C++/Rust exige infraestrutura adicional ou toolchains WebAssembly; GitHub Pages não oferece compiladores de servidor. Bibliotecas específicas de linguagens, múltiplos usuários, persistência remota e colaboração exigem especificações próprias. Nenhum desses recursos está prometido como pronto nesta versão.
