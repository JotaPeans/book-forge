# Fase de planejamento: entrevista, currículo e plano

Objetivo: sair daqui com `book.py` preenchido e `PROGRESS.md` com todas as peças `planejada`.
Faça as perguntas com `AskUserQuestion` (até 4 por chamada). Não pergunte o que dá para decidir com um
padrão sensato: proponha e siga, dizendo a escolha em uma linha.

## 1. Entrevista (o que só o usuário sabe)
Chamada 1:
- **Tema e objetivo**: o que o leitor sabe fazer ao terminar? (frase única e verificável)
- **Público**: o que já domina (linguagens, áreas) e o que nunca viu. Pontes só funcionam se você sabe
  de onde o leitor vem.
- **Idioma do livro**: Português (pt-BR) ou Inglês (en). Define `LANG` e o idioma do texto, dos
  comentários de código e dos exemplos.
- **Escala**: curto (1 a 2 capítulos, ≈ 8 aulas), médio (3 capítulos, ≈ 12 aulas, como o livro de Rust)
  ou longo (4+ capítulos).
Chamada 2:
- **Cor**: manter o design original (laranja, recomendado) ou outro tema (azul, verde, roxo, verde-água,
  vermelho). O layout é sempre o mesmo.
- **Abordagem**: ver a seção 3. Proponha uma e justifique.
- **Projetos**: quer um projeto por capítulo (padrão)? Algum domínio de preferência?
- **Extras**: capítulo bônus (um tema à parte, como o Bevy), comando `/professor` de revisão, apêndices.
Chamada 3 (SÓ depois de o plano estar desenhado): **modo de escrita**, ver `subagents.md`.

## 2. Pesquisa antes de desenhar
- Fixe as versões das ferramentas (linguagem, frameworks) e anote em `PROGRESS.md`. Verifique que elas
  instalam e rodam nesta máquina ANTES de planejar aulas em cima delas (versões novas mudam APIs: baixe
  os exemplos da mesma versão e leia o código-fonte, não a memória).
- Veja o que já existe (livro oficial, cursos populares) para decidir o que NÃO repetir e quais
  referências listar. Só inclua URLs que você abriu.
- Descubra os erros reais mais comuns do iniciante nesse tema: eles viram as caixas `erro-comum` e os
  blocos de erro das aulas.

## 3. Abordagem pedagógica (escolha e declare)
- **Ponte com o que o leitor sabe** (padrão para quem já programa): cada conceito novo ancora em algo
  conhecido ("é como X em C/Python, mas...").
- **Erro primeiro**: mostra o erro real, depois explica a regra. Funciona para linguagens com compilador
  rígido e para qualquer tema em que "a regra" é abstrata.
- **Projeto guiado**: cada capítulo termina em um projeto que usa tudo, com checkpoint.
- **Espiral**: conceitos centrais voltam em capítulos seguintes mais fundos (declare onde).
Combine no máximo duas. Escreva em `PROGRESS.md` qual é a abordagem e por quê.

## 4. Desenho do currículo
- **Capítulos** (níveis): 3 a 5. Cada um termina em um projeto real e pequeno o bastante para caber em
  uma sessão longa. Um tema opcional vira capítulo "Extra" (não bloqueia o resto).
- **Aulas**: 4 por capítulo é um bom padrão (45 a 80 min de leitura cada). Uma aula = um grupo coeso de
  ideias, com o exemplo que as une. Se não cabe em 80 min, divida.
- **Mapa de conceitos (ledger)**: tabela "aula -> conceitos que INTRODUZ -> conceitos que ASSUME".
  Regra: nenhum conceito é usado antes de ser introduzido (ou ganha uma frase "veremos na aula N").
  Esse mapa é o contrato que permite escrever capítulos em paralelo. Guarde em `PROGRESS.md`.
- **Dificuldade** (1 a 5) e **pré-requisito** de cada aula; o mapa acima valida a cadeia.
- **Projeto de cada capítulo**: especificação curta (o que o programa faz), arquitetura em passos,
  testes, versão estendida como desafio. Prefira projetos que o leitor queira usar ou mostrar.
- **Estimativas**: leitura = tempo de ler e digitar; com exercícios conte ≈ 3x. `hours` e `weeks` do
  capítulo = soma realista no ritmo de `HOURS_PER_WEEK`.
- **Referências**: por categoria, só links conferidos; avise a versão da documentação.

## 5. Entregáveis desta fase
1. `python scripts/scaffold.py <pasta> ...` (veja SKILL.md) para criar o projeto.
2. `book.py` com todos os capítulos, aulas (label, título, tempo, arquivo), projetos e referências.
3. `PROGRESS.md` com decisões fixas, versões, abordagem, mapa de conceitos e a tabela de peças.
4. `python build.py` gera o PDF só com capa, guia e plano (tudo "pendente"): **mostre o plano ao usuário**
   (páginas em PNG) e só avance com o OK dele.
