#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cria a pasta de um livro novo com o motor, as fontes, as ferramentas e os modelos.

    python scaffold.py <pasta> --title "Python" --tagline "do zero ao avançado" \
        --lang pt-BR --theme orange --code-lang python --audience "Escrito para ..." \
        --subtitle "..." [--max-cols 85] [--out-name livro.pdf]
"""
import argparse
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ENGINE, SC = SKILL / "assets" / "engine", SKILL / "assets" / "scaffold"
LANG_NAME = {"pt-BR": "português do Brasil", "en": "inglês"}
THEMES = ("orange", "blue", "green", "purple", "teal", "red")


def fill(text, d):
    for k, v in d.items():
        text = text.replace("@@%s@@" % k, v)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--title", required=True)
    ap.add_argument("--tagline", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--audience", default="")
    ap.add_argument("--lang", default="pt-BR", choices=list(LANG_NAME))
    ap.add_argument("--theme", default="orange", choices=THEMES)
    ap.add_argument("--code-lang", default="python")
    ap.add_argument("--max-cols", default="85")
    ap.add_argument("--out-name", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    dest = Path(a.dest).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()) and not a.force:
        sys.exit("A pasta %s não está vazia (use --force para sobrescrever o motor)." % dest)
    dest.mkdir(parents=True, exist_ok=True)

    slug = "".join(c if c.isalnum() else "_" for c in a.title.lower()).strip("_") or "livro"
    out_name = a.out_name or "livro_%s.pdf" % slug
    d = dict(TITLE=a.title, TAGLINE=a.tagline or a.title, SUBTITLE=a.subtitle or "Um curso em aulas, com exercícios e projetos.",
             AUDIENCE=a.audience or "Escrito para quem quer aprender do zero.", LANG=a.lang, THEME=a.theme,
             CODE_LANG=a.code_lang, OUT_NAME=out_name, HEADER=("%s · %s" % (a.title, a.tagline)).upper(),
             LANG_NAME=LANG_NAME[a.lang], MAX_COLS=a.max_cols, KICKER1="PARTE 1 DE N" if a.lang == "pt-BR" else "PART 1 OF N",
             CH1="Fundamentos" if a.lang == "pt-BR" else "Fundamentals", CH1_SHORT="PARTE 1 · FUNDAMENTOS" if a.lang == "pt-BR" else "PART 1 · FUNDAMENTALS",
             CH1_HDR="Parte 1" if a.lang == "pt-BR" else "Part 1", CH1_JOURNEY="01  Fundamentos" if a.lang == "pt-BR" else "01  Fundamentals",
             WEEKS="2 semanas" if a.lang == "pt-BR" else "2 weeks")

    # motor (sempre atualizado) e fontes
    for name in ("build.py",):
        shutil.copy2(ENGINE / name, dest / name)
    shutil.copytree(ENGINE / "fonts", dest / "fonts", dirs_exist_ok=True)
    shutil.copytree(ENGINE / "tools", dest / "tools", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "bevy_shot*", "verify_rust.py"))
    shutil.copy2(ENGINE / "tools" / "verify_rust.py", dest / "tools" / "verify_rust.py") if a.code_lang == "rust" else None

    # arquivos do projeto (não sobrescreve o que já existe)
    def put(path, text):
        p = dest / path
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text(text, encoding="utf-8")

    put("book.py", fill((SC / "book.py.tpl").read_text(encoding="utf-8"), d))
    put("CLAUDE.md", fill((SC / "CLAUDE.md.tpl").read_text(encoding="utf-8"), d))
    put("README.md", fill((SC / "README.md.tpl").read_text(encoding="utf-8"), d))
    put("PROGRESS.md", fill((SC / "PROGRESS.md.tpl").read_text(encoding="utf-8"), d))
    lang_key = "pt-BR" if a.lang == "pt-BR" else "en"
    put("content/00_como_usar.md", (SC / ("como_usar.%s.md" % lang_key)).read_text(encoding="utf-8"))
    put("content/_modelo_aula.md", (SC / ("lesson.%s.md" % lang_key)).read_text(encoding="utf-8").replace("```python", "```" + a.code_lang))
    (dest / "dist").mkdir(exist_ok=True)
    print("Projeto criado em", dest)
    print("Próximo passo: preencher book.py (CHAPTERS) com o plano e rodar `python build.py`.")


if __name__ == "__main__":
    main()
