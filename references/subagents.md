# Escrever com sub-agentes (um por capítulo)

## Perguntar ao usuário (obrigatório) e AVISAR do custo
Depois de o plano estar aprovado, pergunte com `AskUserQuestion`. A pergunta TEM de conter o alerta:

> Como escrever os capítulos?
> - **Sequencial (Recomendado para economia):** eu escrevo e verifico uma aula por vez, no contexto
>   principal. Mais lento, mas gasta menos tokens e fica mais coeso.
> - **Um sub-agente por capítulo (mais rápido, gasta MUITO mais tokens):** cada capítulo é escrito em
>   paralelo por um agente com o contexto próprio. Cada agente relê as regras, o plano e o mapa de
>   conceitos e roda as verificações, então o consumo total costuma ser várias vezes o do modo
>   sequencial (estimativa: um livro de 3 capítulos x 4 aulas passa de 3 a 5 vezes o custo).
> - **Híbrido:** sub-agentes só para capítulos grandes ou independentes (ex.: o extra); o resto, sequencial.

Se o usuário não escolher sub-agentes, siga o modo sequencial e não volte a perguntar.

## Pré-requisitos para paralelizar com segurança
Prepare, ANTES de lançar qualquer agente (isso é o que impede inconsistência):
1. `CLAUDE.md` do projeto (regras), `book.py` completo e `PROGRESS.md` com o **mapa de conceitos**.
2. Um **guia de estilo e de continuidade**: vocabulário/glossário fixo (como cada termo é chamado), o
   exemplo corrente de cada capítulo, o tom, como citar aulas ("veremos na Aula 7").
3. Uma aula-modelo já escrita (a Aula 1, por você) como referência concreta de tom e profundidade.
4. Ferramentas fixadas e testadas (versão da linguagem, `verify_code.py` funcionando com um bloco).

## Regras de execução
- **Um agente por capítulo**, dono exclusivo dos arquivos daquele capítulo (aulas + projeto +
  imagens do capítulo). Ninguém edita `book.py`, `build.py`, `tools/`, `CLAUDE.md` nem arquivos de outro
  capítulo; pedidos de mudança voltam como texto no relatório.
- Dependência entre capítulos: o capítulo N+1 só pode assumir o que o mapa diz que o N introduz. Se a
  dependência for forte (o projeto reutiliza código), escreva em ondas (N, depois N+1), não em paralelo.
- **Recursos compartilhados**: cada agente usa o seu diretório de trabalho temporário e o seu
  `CARGO_TARGET_DIR`/venv/cache. Dois agentes compilando na mesma pasta quebram um ao outro.
- Lance os agentes da mesma onda em UMA mensagem (várias chamadas `Agent` juntas) e em segundo plano.
- Cada agente verifica o que escreveu (`verify_code.py --fill`, `show_blocks.py`, `lint_book.py`) e só
  então reporta. O relatório diz: arquivos criados, conceitos introduzidos, descobertas que mudaram o
  texto, o que NÃO foi possível verificar, e pedidos para o coordenador.

## Modelo de prompt para cada agente de capítulo
```
Você escreve o capítulo "<título>" (arquivos: <lista de .md do book.py>) do livro "<TÍTULO>".
Pasta do projeto: <caminho>. Leia ANTES, nesta ordem: CLAUDE.md, PROGRESS.md (mapa de conceitos e
decisões), book.py (só o seu capítulo e vizinhos), o guia de estilo, e a aula-modelo <arquivo>.
Regras inegociáveis: <cole as regras técnicas do CLAUDE.md que mais importam: código roda, saídas
capturadas com verify_code --fill, versões fixadas, linhas <= 85, testes que podem falhar, nada de
afirmações não medidas>.
Escreva SÓ os seus arquivos. Não edite book.py, build.py, tools/ nem outros capítulos.
Você pode assumir apenas: <conceitos introduzidos antes>. Você introduz: <conceitos do capítulo>.
Use diretório de trabalho próprio em <tmp>/<capitulo> e não compartilhe caches de compilação.
Para cada peça: escreva -> verify_code --fill -> show_blocks -> lint_book. Plante um bug nos testes do
projeto e confirme que algum teste falha.
Entregue um relatório curto: arquivos, conceitos introduzidos, descobertas (o que o código real
contradisse), o que não pôde verificar, pedidos ao coordenador. Não cole as aulas no relatório.
```
Use `model` do agente conforme a complexidade (o padrão herda o do coordenador); não passe `effort`
a menos que o usuário peça.

## Integração (o coordenador faz, nunca delega)
1. Ler cada relatório; abrir 1 ou 2 aulas por capítulo para conferir tom e profundidade.
2. Reconciliar o mapa de conceitos (algum agente introduziu algo a mais? mover ou ajustar referências).
3. `lint_book.py` (todas as peças), `verify_code.py` em todas as aulas, `build.py`, regressão de páginas.
4. Passe de consistência entre capítulos: vocabulário, referências cruzadas ("Aula N" existe e diz o
   que se promete), duplicações, lacunas. Corrija você mesmo ou reabra o agente com `SendMessage`.
5. Revisão visual do PDF (capas, plano, páginas com código/imagens, gabaritos).
6. Atualizar `PROGRESS.md` e entregar o relatório final ao usuário, com o que não foi verificado.
