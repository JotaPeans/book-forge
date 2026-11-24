# Escrever uma aula (o formato e a pedagogia)

Parta de `content/_modelo_aula.md` do projeto. Cada aula é um `.md` no caminho de `book.py`.

## Anatomia obrigatória (o `lint_book.py` confere)
1. Front matter: `title`, `subtitle`, `duration`, `prereq`, `difficulty` (1 a 5), `deliverable`.
2. `::: objetivos` (3 a 5 itens com verbo e resultado verificável).
3. Seções `##`: problema antes da solução; conceito + analogia; exemplo comentado; para que serve.
4. Pelo menos uma `::: pausa` (pergunta antes de seguir), uma `::: erro-comum` e um bloco `erro` REAL.
5. `::: pratica` e `::: dica` quando agregarem.
6. `::: exercicios` (3 a 5, do fácil ao desafio) e `::: resumo`.
7. `::: gabarito` (vai para o fim do livro; respostas completas e explicadas, com o porquê).
8. `::: checkpoint` só na última aula do capítulo e no projeto (lista de "consigo...").

## Dialeto de Markdown suportado pelo motor
- `## Título`, `### Subtítulo`, parágrafos, listas `-`/`1.`, `**negrito**`, `*itálico*`, `` `código` ``.
- Caixas: `::: tipo Título opcional` ... `:::` (tipos: objetivos, conceito, pausa, erro-comum, pratica, dica,
  resumo, checkpoint, exercicios, gabarito; aceita também objectives, concept, pause, common-mistake,
  practice, tip, summary, exercises, answers). Dentro de caixas podem entrar listas e blocos de código.
- Código: ```` ```lang flags file=nome caption="Legenda" ````. Flags: `run`, `fail`, `panic`, `test`, `frag`.
  `erro`/`error` e `saida`/`output` são blocos de saída capturada (ficam vazios até o `--fill`).
- Imagem: ```` ```imagem file=content/img/x.png caption="..." largura=0.55 ```` (fração da largura).
- NÃO existe tabela Markdown. Sem sub/sobrescrito Unicode. Linhas de código <= 85 colunas.

## Pedagogia
- Tom de professor, direto e gentil, no idioma escolhido. Sem enrolação, sem elogio vazio.
- Ponte com o que o leitor já sabe, mas só quando ela esclarece (uma ponte forçada atrapalha).
- Mostre o erro real ANTES de proibir algo: o aluno precisa saber ler a mensagem.
- Cada exemplo tem um propósito e roda. Exemplo mínimo primeiro, variações depois.
- Exercícios: o primeiro é quase mecânico, o último exige pensar; todos têm gabarito que ensina.
- Pausas boas: "prevê a saída", "o que acontece se...", "por que isto não compila/funciona?".
- Não afirme limites, tempos ou comportamentos sem medir. A saída real manda: se ela contradisse o que
  você esperava, o texto muda e a descoberta vira ensinamento (isso aconteceu várias vezes no livro de Rust).
- Projeto de capítulo: especificação, passos, código completo em arquivos, sessão de terminal capturada,
  testes que podem falhar, desafios extras, checkpoint.

## Qualidade antes de entregar uma peça
`verify_code.py --fill` (0 problemas) -> `show_blocks.py` (conferir o que foi preenchido) ->
`lint_book.py` (0 erros) -> `build.py` -> olhar as páginas novas (quebras e larguras).
