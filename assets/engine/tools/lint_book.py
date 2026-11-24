#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confere a estrutura de cada aula contra as regras do livro (as mesmas do CLAUDE.md do projeto).

    python tools/lint_book.py                # todas as aulas listadas em book.py
    python tools/lint_book.py content/cap1/aula_02.md

Regras (ERRO = precisa corrigir; AVISO = confira):
  ERRO  front matter sem title/subtitle/duration/prereq/difficulty/deliverable
  ERRO  falta objetivos, resumo, exercicios (3 a 5 itens) ou gabarito
  ERRO  bloco de erro/saida vazio (rode verify_code.py --fill)
  ERRO  checkpoint ausente na última aula e no projeto do capítulo
  AVISO checkpoint em aula comum; falta pausa, erro-comum ou bloco de erro real
  AVISO linha de código com mais de MAX_COLS colunas; sub/sobrescritos Unicode no texto
Os nomes das caixas aceitam português e inglês. Opções em book.py: MAX_COLS (85), MIN_EX/MAX_EX.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import book as B  # noqa: E402

ALIAS = {"objectives": "objetivos", "concept": "conceito", "pause": "pausa",
         "common-mistake": "erro-comum", "practice": "pratica", "tip": "dica", "summary": "resumo",
         "exercises": "exercicios", "answers": "gabarito", "answer": "gabarito"}
FM_KEYS = ("title", "subtitle", "duration", "prereq", "difficulty", "deliverable")
MAX_COLS = getattr(B, "MAX_COLS", 85)
MIN_EX, MAX_EX = getattr(B, "MIN_EX", 3), getattr(B, "MAX_EX", 5)
SUBSUP = re.compile("[²³¹⁰-₟]")


def lint(path, is_last, is_project):
    errs, warns = [], []
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")
    meta = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
            k, _, v = lines[i].partition(":")
            meta[k.strip()] = v.strip()
    for k in FM_KEYS:
        if not meta.get(k):
            errs.append("front matter sem '%s'" % k)
    boxes, fence = {}, 0
    in_box = None
    for i in range(body_start, len(lines)):
        s = lines[i].strip()
        m = re.match(r"^(`{3,})(.*)$", s)
        if m and fence == 0:
            fence = len(m.group(1))
            lang = (m.group(2).split() or [""])[0]
            blk_start, blk = i, []
            continue
        if fence:
            if re.fullmatch(r"`{%d,}" % fence, s):
                fence = 0
                if lang in ("erro", "error", "saida", "output") and not "".join(blk).strip():
                    errs.append("linha %d: bloco %s vazio (use verify_code.py --fill)" % (blk_start + 1, lang))
                boxes.setdefault("_code_" + lang, 0)
                boxes["_code_" + lang] += 1
            else:
                blk.append(lines[i])
                if len(lines[i]) > MAX_COLS and lang not in ("erro", "error", "saida", "output", "text", "imagem", "image"):
                    warns.append("linha %d: código com %d colunas (> %d)" % (i + 1, len(lines[i]), MAX_COLS))
            continue
        m = re.match(r"^:::\s*(\S+)", s)
        if m:
            name = ALIAS.get(m.group(1), m.group(1))
            boxes[name] = boxes.get(name, 0) + 1
            in_box = name
            continue
        if s == ":::":
            in_box = None
            continue
        if SUBSUP.search(lines[i]):
            warns.append("linha %d: sub/sobrescrito Unicode (use texto normal)" % (i + 1))
        if in_box == "exercicios":
            pass
    for need in ("objetivos", "resumo", "exercicios", "gabarito"):
        if not boxes.get(need):
            errs.append("falta a caixa '%s'" % need)
    # exercícios: conta itens numerados da caixa
    m = re.search(r"^:::\s*(?:exercicios|exercises)\b.*?^:::\s*$", text, re.S | re.M)
    if m:
        n = len(re.findall(r"^\d+\.\s", m.group(0), re.M))
        if not MIN_EX <= n <= MAX_EX:
            errs.append("exercícios: %d itens (esperado %d a %d)" % (n, MIN_EX, MAX_EX))
    if (is_last or is_project) and not boxes.get("checkpoint"):
        errs.append("falta o checkpoint (última aula e projeto do capítulo)")
    if boxes.get("checkpoint") and not (is_last or is_project):
        warns.append("checkpoint em aula comum (a regra manda só no projeto/última aula)")
    if not is_project:
        for need in ("pausa", "erro-comum"):
            if not boxes.get(need):
                warns.append("sem caixa '%s'" % need)
        if not (boxes.get("_code_erro") or boxes.get("_code_error")):
            warns.append("sem bloco de erro real (erro/error)")
    return errs, warns


def main():
    targets = []
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            targets.append((Path(a), False, "projeto" in a or "project" in a))
    else:
        cdir = getattr(B, "CONTENT_DIR", "content")
        for ch in B.CHAPTERS:
            for j, ls in enumerate(ch["lessons"]):
                targets.append((ROOT / cdir / ls["file"], j == len(ch["lessons"]) - 1, False))
            targets.append((ROOT / cdir / ch["project"]["file"], False, True))
    bad = 0
    for p, last, proj in targets:
        if not p.exists():
            continue
        errs, warns = lint(p, last, proj)
        for e in errs:
            print("ERRO  %s: %s" % (p.name, e))
        for w in warns:
            print("aviso %s: %s" % (p.name, w))
        bad += len(errs)
    print("lint: %d erro(s)" % bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
