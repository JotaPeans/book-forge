# -*- coding: utf-8 -*-
"""
Manifesto do livro. É AQUI que o plano de ensino vive.

- Para publicar uma aula: crie o arquivo .md indicado em `file` e rode `python build.py`.
- Aulas cujo arquivo ainda não existe aparecem como "pendentes" no plano e não geram páginas.
  Um capítulo só ganha capa quando tem ao menos uma aula pronta.
- Rótulos: aulas "1", "2"... ; projeto "P1", "P2"... (o rótulo do projeto NÃO pode colidir com o de aulas).
"""

TITLE = "@@TITLE@@"
TAGLINE = "@@TAGLINE@@"
SUBTITLE = "@@SUBTITLE@@"
AUDIENCE = "@@AUDIENCE@@"

# ---- opções do motor (todas opcionais) --------------------------------------------------------
LANG = "@@LANG@@"            # "pt-BR" ou "en": rótulos, capas, caixas
THEME = "@@THEME@@"          # orange (padrão do livro original) | blue | green | purple | teal | red
CODE_LANG = "@@CODE_LANG@@"  # linguagem padrão dos blocos de código
OUT_NAME = "@@OUT_NAME@@"    # dist/<OUT_NAME>
HEADER = "@@HEADER@@"        # texto do cabeçalho corrente
# FILE_NAMES = {"python": "main.py"}          # nome exibido no topo do bloco de código
# CUT_CHECKLIST = ["...", "...", "..."]       # checklist da página de corte dos gabaritos
# STRINGS = {"error_title": "Saída do erro"}  # sobrescreve qualquer texto da interface
# MAX_COLS = 85; MIN_EX = 3; MAX_EX = 5       # limites do lint_book.py
HOURS_PER_WEEK = 6

FRONT = [
    "content/00_como_usar.md",
    "@plano",
]
BACK = []

CHAPTERS = [
    dict(
        id="c1", number="01", kicker="@@KICKER1@@", title="@@CH1@@",
        short="@@CH1_SHORT@@", hdr="@@CH1_HDR@@", journey="@@CH1_JOURNEY@@",
        subtitle="Uma frase que diz o que o aluno ganha neste capítulo.",
        hours="≈ 10 h", weeks="@@WEEKS@@",
        lessons=[
            dict(label="1", title="Título da aula 1", reading="≈ 45 min", file="c1/aula_01.md"),
        ],
        project=dict(label="P1", title="Título do projeto", reading="≈ 4 h", file="c1/projeto_01.md"),
    ),
]

# (categoria, [(título, descrição, url)]). Só URLs que você conferiu.
REFERENCES = [
    ("Documentação oficial", [
        ("Nome", "Para que serve.", "https://example.org/"),
    ]),
]
