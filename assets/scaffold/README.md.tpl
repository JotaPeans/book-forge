# @@TITLE@@ · kit do livro

Um PDF único, estilo livro, montado aula por aula. Plano em `book.py`, aulas em `content/`.

```sh
pip install reportlab
python build.py                                   # dist/@@OUT_NAME@@
python tools/verify_code.py content/c1/aula_01.md --fill   # roda o código e captura erros/saídas
python tools/lint_book.py                         # confere a estrutura de todas as aulas
```

Caixas: `objetivos`, `conceito`, `pausa`, `erro-comum`, `pratica`, `dica`, `resumo`, `checkpoint`,
`exercicios`, `gabarito` (aceitam também os nomes em inglês). Blocos de código: a linguagem seguida das
flags `run`, `fail`, `panic`, `test`, `frag`; `erro`/`saida` são preenchidos pela ferramenta.
Imagens: ```` ```imagem file=content/img/x.png caption="..." largura=0.55 ````.
