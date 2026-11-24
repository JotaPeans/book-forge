# Verificação: nada entra no livro sem ter rodado de verdade

Esta é a regra que mais pesa na qualidade. Tudo abaixo vem de erros reais cometidos e corrigidos ao
escrever o livro de Rust.

## 1. Código e saídas
- Todo bloco de código compila/roda (`tools/verify_code.py`; a flag `test` em Python exige `pytest` instalado, em JS usa `node --test`, em Go `go test`). Linguagens prontas: python, js, ts, c, cpp,
  go, sh, rust simples. Outra linguagem: acrescente um runner em `RUNNERS` do script.
- Nunca digite erro ou saída: flags `run`/`fail`/`panic`/`test`, blocos `erro`/`saida` vazios,
  `--fill`, e depois `show_blocks.py` para ler o que foi capturado.
- **Fixe a versão** da ferramenta que gera as mensagens (o compilador novo escreve erros diferentes do
  antigo). Documente em `PROGRESS.md` e rode tudo com ela (ex.: `RUSTUP_TOOLCHAIN`, `pyenv`, `nvm`).
- Evite avisos de compilação nos exemplos; use os valores para não haver "nunca usado".
- Linhas de código <= 85 colunas.

## 2. Afirmações do texto
- Qualquer número, limite, ordem de execução ou "o X sempre faz Y" é medido, não lembrado. Exemplos de
  correções reais: um clamp de delta de tempo (250 ms) que não era o que se imaginava; uma ordem de
  execução anotada errada; uma mensagem de erro cujo código mudou. Rode e use o resultado.
- Se a execução contradisse a sua expectativa, escreva a descoberta no texto: é ótima pedagogia.

## 3. Projetos com vários arquivos
- Monte um projeto de verdade (pasta fora do livro), rode build, testes, formatador e linter, e só então
  embuta os arquivos e a sessão de terminal capturada. Guarde esses projetos de apoio (fora de `content/`)
  se quiser reproduzir depois.
- Dependências externas: fixe versões exatas (`=1.2.3`), compatíveis com a versão do compilador usada.

## 4. Testes que podem falhar (mutação)
- Depois de escrever os testes de um projeto, **plante bugs de propósito** (inverter uma condição, tirar
  uma checagem, trocar um sinal) e veja um teste falhar. Se nenhum falha, o teste é decorativo.
- Cuidado com teste que passa pelo motivo errado (ex.: o objeto "novo" substitui o antigo e o assert
  passa). Reforce o teste com um estado que só existe no cenário certo.
- Mostre uma mutação no texto do projeto quando houver história boa ("o teste que deixa um bug passar").

## 5. Verificação visual (GUI, jogos, gráficos, PDF)
- Exemplos com janela: renderize para imagem (captura de tela, ou renderização fora da tela) e olhe a
  imagem. Janelas sem sessão gráfica saem pretas: use a técnica de renderizar para textura/arquivo.
- Fontes embutidas de motores gráficos costumam ser ASCII: acentos viram quadrados. Renderize e confirme.
- PDF: `pdftoppm -r 60 -png dist/x.pdf pg` e abra capa, plano, página de código largo, gabaritos, e cada
  página de projeto. O motor avisa de linhas longas e imagens ausentes no terminal: leia os avisos.
- O que você não pôde verificar (entrada real do mouse, áudio, hardware): diga isso ao usuário no
  relatório final. Nunca declare "testado" sem ter rodado.

## 6. Regressão do livro todo
- Ao mexer no motor ou no `book.py`, reconstrua e compare o número de páginas e o texto das páginas
  antigas (`pypdf`: `extract_text()` por página). Diferenças devem ser só as intencionais.
- Antes de fechar uma sessão, atualize `PROGRESS.md` (a sessão pode acabar por falta de contexto).
