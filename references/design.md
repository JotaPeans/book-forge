# O design do livro (fixo: reaproveite sempre)

O motor `assets/engine/build.py` implementa o design aprovado do livro "Rust do Zero ao Avançado".
**Não redesenhe.** O scaffold copia o motor para o projeto; só se mexe em `book.py`.

## O que o design é
- Página A4, margens 20 mm. Faixa de destaque de 4 mm no topo, cabeçalho corrente (título do livro à
  esquerda, capítulo/aula à direita) e rodapé com título da aula e número da página.
- Fontes embutidas (`fonts/`): Liberation Sans (texto) e DejaVu Sans Mono (código). Funciona em qualquer
  máquina e cobre acentos latinos.
- Capa do livro: título gigante na cor de destaque, tagline, subtítulo, cartões dos capítulos.
- Capa de capítulo: número enorme, kicker, título, lista de aulas (● pronta / ○ pendente) com tempo de
  leitura, cartão do projeto e barra "sua jornada".
- Aula: kicker, título, subtítulo, faixa de metadados (duração, pré-requisito, dificuldade em bolinhas,
  entrega), seções numeradas `01 02 03`.
- Caixas com barra lateral colorida:
  - `objetivos`, `conceito`, `resumo`, `checkpoint`: cor de destaque, fundo claro.
  - `pausa`: borda tracejada (pergunta para responder antes de seguir).
  - `erro-comum`: âmbar. `dica`: verde. `pratica`: cinza. `exercicios`: lista numerada em cartão.
  - bloco `erro`: vermelho (saída real de erro). `saida`: cinza (saída real do programa).
- Código: cabeçalho com o nome do arquivo, destaque de sintaxe leve, fonte que encolhe sozinha em linhas
  largas (piso 6,6 pt). Legendas "Listagem X.n" e "Figura X.n".
- Fim do livro: página de corte "spoilers à frente" com checklist, gabaritos por aula, apêndices,
  referências (links clicáveis). PDF com marcadores (outline) navegáveis.

## O que se pode mudar (em `book.py`)
- `THEME`: `orange` (original, padrão), `blue`, `green`, `purple`, `teal`, `red`. Muda só a cor de
  destaque; cinzas, âmbar, vermelho e verde das caixas ficam iguais.
- `LANG`: `pt-BR` ou `en` (rótulos, capas, caixas, legendas). Qualquer texto: `STRINGS = {...}`.
- `HEADER`, `COVER_KICKER`, `CUT_CHECKLIST`, `FILE_NAMES`, `OUT_NAME`, `AUTHOR`.
- Linguagens com destaque de sintaxe: rust, python, js/ts, c/cpp, go, java/kotlin/cs, sh. Outra linguagem
  sai sem cor (texto simples); para colorir, adicione uma linha em `_LANGS` no `build.py` do projeto.
- Mais de 4 capítulos: a capa quebra em linhas de cartões e a barra "jornada" encolhe a fonte. Use
  `journey="Rótulo curto"` no capítulo se o título for longo.

## Armadilhas aprendidas
- Tabelas Markdown NÃO são renderizadas: use listas.
- Texto de tela de jogos/GUI com fonte padrão do motor gráfico costuma ser só ASCII: renderize e olhe.
- Sub/sobrescritos Unicode não existem nas fontes: escreva "x2", "10^6" em texto.
- O rótulo do projeto (`P1`...) não pode ser usado por nenhuma aula (o motor identifica projetos por rótulo).
- Plano: se uma tabela do plano estourar a página, reduza o número de aulas por capítulo ou encurte títulos.
- Sempre abra o PDF: converta páginas em PNG (`pdftoppm -r 60 -png`) e olhe capa, plano, uma aula cheia
  de código e a página de gabaritos.
