# Diretrizes para escrever as aulas do livro "@@TITLE@@"

Projeto gerado com a skill `book-forge`. O motor (`build.py`, `fonts/`, `tools/`) NÃO se edita por aula:
o design é fixo. O plano vive em `book.py`; o conteúdo, em `content/`; o estado, em `PROGRESS.md`.

## Público e tom
- Leitor: @@AUDIENCE@@
- Idioma do texto: @@LANG_NAME@@. Tom de professor: claro, direto, gentil. Sem enrolação.
- Faça pontes com o que o leitor já domina quando ajudar. Não repita setup que ele já tem.

## Estrutura obrigatória de cada aula
1. Front matter completo (`title`, `subtitle`, `duration`, `prereq`, `difficulty`, `deliverable`).
2. `::: objetivos` no início.
3. Seções `##` com: conceito + analogia, exemplo comentado, para que serve na prática.
4. Pelo menos uma `::: pausa`, uma `::: erro-comum` e um bloco ```` ```erro ```` com saída REAL.
5. `::: pratica` e `::: dica` quando fizerem sentido.
6. `::: exercicios` (3 a 5, do fácil ao desafio) e `::: resumo`.
7. `::: gabarito` com respostas completas e explicadas (vão para o fim do livro).
8. Última aula e projeto de cada capítulo: `::: checkpoint`. Aulas comuns NÃO têm checkpoint.
(Os nomes das caixas também podem ser escritos em inglês: objectives, concept, pause, common-mistake,
practice, tip, exercises, summary, answers.)

## Regras técnicas
- **Todo código compila/roda.** Nunca digite mensagens de erro ou saídas à mão: use as flags `fail`,
  `panic`, `run`, `test` e `frag` nos blocos de código, deixe os blocos `erro`/`saida` vazios e rode
  `python tools/verify_code.py content/<arquivo>.md --fill`. Depois confira com `tools/show_blocks.py`.
- Linhas de código com no máximo @@MAX_COLS@@ colunas (`lint_book.py` e `build.py` avisam).
- Não afirme limites numéricos nem comportamentos sem testar: rode e use o resultado real.
- Não use caracteres sub/sobrescritos Unicode no texto. O `build.py` não renderiza tabelas Markdown:
  use listas com marcadores.
- Versões das ferramentas ficam FIXADAS (veja `PROGRESS.md`); se a saída real discordar do que você
  esperava, o livro segue a saída real (e a descoberta vira texto).
- Projetos com vários arquivos: monte um projeto de verdade, teste, e só então embuta os arquivos e a
  sessão de terminal (capturada) no livro.
- Todo teste deve poder falhar: depois de escrever, plante um bug de propósito e veja o teste reclamar.
- Imagens: bloco ```` ```imagem file=content/img/x.png caption="..." largura=0.55 ````.

## Fluxo de cada peça
1. Crie o arquivo no caminho indicado em `book.py` (parta de `content/_modelo_aula.md`).
2. `python tools/verify_code.py <arquivo> --fill` e `python tools/show_blocks.py <arquivo>`.
3. `python tools/lint_book.py <arquivo>` (0 erros).
4. `python build.py` e confira as páginas novas (quebras, larguras). Atualize `PROGRESS.md`.
