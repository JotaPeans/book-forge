---
name: book-forge
description: Planeja e escreve um livro/curso técnico em PDF, aula por aula, com o design do livro "Rust do Zero ao Avançado" (capas de capítulo, caixas coloridas, gabaritos, referências). Cobre entrevista e plano de conteúdo, abordagem pedagógica, idioma (pt-BR ou inglês), cor do tema, código verificado de verdade (saídas e erros capturados), lint de estrutura, build do PDF e, opcionalmente, um sub-agente por capítulo. Use quando o usuário pedir para criar um livro, curso, apostila, ebook ou material didático em PDF sobre qualquer tema técnico, ou para continuar/estender um livro já criado com esta skill (existe um book.py e um PROGRESS.md na pasta).
---

# book-forge: do plano ao PDF

Você reproduz o processo que produziu o livro "Rust do Zero ao Avançado" (25 peças, 469 páginas): planejar,
escrever aula por aula com código que **roda de verdade**, montar um PDF único com um design fixo.
Responda ao usuário no idioma dele; o idioma do LIVRO é uma decisão da entrevista.

Arquivos da skill (caminhos relativos a esta pasta):
- `assets/engine/`: motor pronto (`build.py`, `fonts/`, `tools/verify_code.py`, `lint_book.py`, `show_blocks.py`).
- `assets/scaffold/`: modelos de `book.py`, `CLAUDE.md`, `PROGRESS.md`, aula (pt-BR/en), guia "como usar".
- `scripts/scaffold.py`: cria a pasta do livro.
- `references/`: `planning.md`, `design.md`, `writing-lessons.md`, `verification.md`, `subagents.md`.
  Leia o que a fase pede, no momento da fase (não tudo de uma vez).
- `assets/design_preview.png`: como o design fica (mostre ao usuário se ele quiser ver).

## Fluxo

### Fase 0: retomar ou começar
Se a pasta atual (ou a indicada) já tem `book.py` e `PROGRESS.md`, **retome**: leia `PROGRESS.md`,
`CLAUDE.md` e `book.py`, rode `python build.py` e `python tools/lint_book.py`, e continue da próxima
peça `planejada`. Senão, comece a Fase 1.

### Fase 1: entrevista e plano (leia `references/planning.md`)
1. Entreviste com `AskUserQuestion`: tema/objetivo, público e o que já sabe, **idioma do livro** (pt-BR ou
   en), escala, **cor do tema** (padrão: manter o design original laranja; alternativas azul, verde, roxo,
   verde-água, vermelho), abordagem, projetos, extras. Não pergunte o que tem padrão sensato.
2. Pesquise e fixe as versões das ferramentas; confirme que instalam e rodam aqui.
3. Desenhe capítulos, aulas, projetos, **mapa de conceitos** e estimativas.
4. Crie o projeto:
   `python <skill>/scripts/scaffold.py <pasta> --title "..." --tagline "..." --subtitle "..." --audience "..."
   --lang pt-BR|en --theme orange|blue|green|purple|teal|red --code-lang <linguagem>`
   Preencha `book.py` (CHAPTERS, REFERENCES), `PROGRESS.md` e ajuste o `CLAUDE.md` do livro ao tema.
5. `pip install reportlab` (use um venv se o Python do sistema recusar) e `python build.py`: mostre o
   plano (PNG das páginas) e **só avance com o OK do usuário**.

### Fase 2: escolher o modo de escrita (leia `references/subagents.md`)
Pergunte ao usuário, **com o alerta de que sub-agentes gastam bem mais tokens**:
sequencial (padrão e mais econômico), um sub-agente por capítulo (mais rápido, custo várias vezes maior),
ou híbrido. Anote a escolha em `PROGRESS.md`. Sem resposta clara, vá sequencial.
Mesmo no modo sub-agentes, **você escreve a Aula 1** antes (aula-modelo de tom e profundidade).

### Fase 3: escrever e verificar cada peça (leia `references/writing-lessons.md` e `verification.md`)
Para cada aula/projeto, nesta ordem: escrever a partir de `content/_modelo_aula.md` -> 
`python tools/verify_code.py <arquivo> --fill` -> `python tools/show_blocks.py <arquivo>` ->
`python tools/lint_book.py <arquivo>` -> `python build.py` e olhar as páginas novas. Depois atualize
`PROGRESS.md` (estados: planejada, escrita, verificada, no PDF).
Projetos: monte e teste um projeto real fora de `content/`, plante bugs para provar que os testes
falham, e só então embuta código e sessão de terminal capturada.
A cada fechamento de peça, entregue o PDF atualizado e diga em uma linha o que a peça cobre.

### Fase 4: fechamento do livro
- Passe de consistência: vocabulário, referências cruzadas ("Aula N"), repetições, lacunas, mapa de
  conceitos x o que de fato foi escrito. Corrija.
- `lint_book.py` sem erros, `verify_code.py` em todas as aulas, `build.py` sem avisos, regressão de
  páginas, conferência visual (capa, plano, páginas com código, gabaritos, projetos).
- Opcional (ofereça, não imponha): comando `/professor` de revisão para o aluno (veja
  `assets/scaffold/professor.rust-example.md` e adapte à linguagem e ao idioma); apêndice "como este
  livro é gerado"; página de referências revisada.
- Relatório final ao usuário: o que foi entregue, números reais (aulas, páginas, testes, mutações
  capturadas), as descobertas em que o código real contradisse a expectativa, e **o que não foi
  verificado** (entrada real, áudio, hardware, jogabilidade). Nunca declare "testado" sem ter rodado.

## Regras que valem sempre
- **O design é fixo**: não altere o layout do `build.py` por livro. Só `THEME`, `LANG`, textos em
  `STRINGS`, cabeçalho, nomes de arquivo e checklist do corte. Nova linguagem de código com cor = uma
  linha em `_LANGS`.
- **Nada de saída digitada à mão.** Erros e saídas vêm de `verify_code.py --fill`.
- **Versões fixadas e documentadas**; se a saída real contradisse o que você esperava, o livro segue a
  saída real e a descoberta vira texto.
- **Estado em arquivo**: `PROGRESS.md` é a memória entre sessões (a conversa pode acabar). Atualize
  sempre que uma peça mudar de estado.
- **Não ultrapasse o escopo aprovado** (plano, modo de escrita, tema). Mudanças de escopo: pergunte.
- Peças com janela/GUI/gráficos: renderize e olhe a imagem (veja `verification.md`, seção 5).
- Se o motor precisar de um recurso novo (outro tipo de caixa, outra capa), proponha ao usuário antes
  e implemente de forma compatível com os livros já criados (a skill deve continuar gerando o mesmo
  design); registre a mudança aqui na skill, não só no projeto.

## Mais coisas que valem a pena oferecer ao usuário
- **Revisão de aluno-fantasma**: depois de cada capítulo, um sub-agente lê as aulas como um aluno do
  público-alvo e lista onde travou (custo extra: avise).
- **Glossário** no apêndice e **mapa visual** da jornada, se o livro for grande.
- **Capítulo extra** independente (como o Bevy no livro de Rust) para temas laterais, sem bloquear o resto.
- **Repositório git** para o livro e seus projetos de apoio (o histórico salva o trabalho entre sessões).
- **Versão em outro idioma**: o motor já tem `LANG`; traduzir é reescrever `content/`, mantendo o código
  verificado (rode `verify_code.py` de novo: as mensagens de erro devem vir do mesmo toolchain).
