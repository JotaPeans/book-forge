#!/usr/bin/env python3
"""Mostra os blocos erro/saida (error/output) de um .md, para conferir o que foi preenchido."""
import re, sys
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
i = 0
while i < len(lines):
    m = re.match(r"^```(error|erro|saida|output)(.*)$", lines[i].strip())
    if m:
        print("---", m.group(1), "(linha %d)" % (i + 1)); i += 1
        while not lines[i].startswith("```"):
            print(("  ! LARGA " if len(lines[i]) > 98 else "  ") + lines[i]); i += 1
    i += 1
