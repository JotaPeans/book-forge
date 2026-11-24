#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica o código de uma aula (.md): cada bloco de código é executado/compilado de verdade, e as
mensagens de erro e saídas do livro são CAPTURADAS, nunca digitadas.

Linguagens: python, js, ts, c, cpp, go, sh, rust (rust simples; para Cargo/Tokio/Bevy use
tools/verify_rust.py, que veio junto como referência). Outras: adicione em RUNNERS.

Flags na linha da cerca, depois do nome da linguagem (ex.: ```python run caption="..."):
    (nenhuma)  o bloco DEVE compilar / ter sintaxe válida (não executa)
    run        executa (deve sair com código 0); a stdout alimenta o bloco ```saida / ```output seguinte
    fail       DEVE falhar (compilação ou execução); a saída alimenta o ```erro / ```error seguinte
    panic      compila e DEVE falhar ao executar (exceção, panic, exit != 0)
    test       roda os testes do bloco (pytest/unittest, node --test, go test); devem passar
    frag       trecho incompleto: não é verificado
    stdin="x"  texto enviado na entrada padrão ao executar

Blocos ```erro/```error e ```saida/```output vazios são preenchidos com --fill:
    erro  <- saída do último bloco `fail` ou `panic` anterior
    saida <- saída do último bloco `run` (ou `test`) anterior

Uso:
    python tools/verify_code.py content/cap1/aula_01.md            # só verifica
    python tools/verify_code.py content/cap1/aula_01.md --fill     # verifica e reescreve erro/saida
    python tools/verify_code.py content/cap1/aula_01.md --show     # mostra as saídas capturadas
Códigos de saída: 0 = tudo certo, 1 = algum bloco não fez o que a flag promete.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT = 30
ERR_NAMES, OUT_NAMES = ("erro", "error"), ("saida", "output")

# lang -> dict(ext, check=cmd|None, run=cmd, test=cmd|None); {f} = arquivo, {d} = pasta, {b} = binário
RUNNERS = {
    "python": dict(ext="py", check=["python3", "-m", "py_compile", "{f}"], run=["python3", "{f}"],
                   test=["python3", "-m", "pytest", "-q", "{f}"]),
    "js": dict(ext="js", check=["node", "--check", "{f}"], run=["node", "{f}"],
               test=["node", "--test", "{f}"]),
    "ts": dict(ext="ts", check=None, run=["node", "--experimental-strip-types", "--no-warnings", "{f}"],
               test=["node", "--experimental-strip-types", "--no-warnings", "--test", "{f}"]),
    "c": dict(ext="c", check=["cc", "-Wall", "-Wextra", "-fsyntax-only", "{f}"],
              build=["cc", "-Wall", "-Wextra", "-o", "{b}", "{f}"], run=["{b}"], test=None),
    "cpp": dict(ext="cpp", check=["c++", "-std=c++17", "-Wall", "-fsyntax-only", "{f}"],
                build=["c++", "-std=c++17", "-Wall", "-o", "{b}", "{f}"], run=["{b}"], test=None),
    "go": dict(ext="go", check=["go", "vet", "{f}"], run=["go", "run", "{f}"],
               test=["go", "test", "{f}"]),
    "sh": dict(ext="sh", check=["bash", "-n", "{f}"], run=["bash", "{f}"], test=None),
    "rust": dict(ext="rs", check=["rustc", "--edition", "2021", "--emit=metadata", "-o", "{b}.rmeta", "{f}"],
                 build=["rustc", "--edition", "2021", "-o", "{b}", "{f}"], run=["{b}"],
                 test=["rustc", "--edition", "2021", "--test", "-o", "{b}", "{f}"]),
}
ALIASES = {"py": "python", "python3": "python", "javascript": "js", "mjs": "js", "typescript": "ts",
           "bash": "sh", "shell": "sh", "c++": "cpp", "rs": "rust"}


def scan(lines):
    blocks, i = [], 0
    while i < len(lines):
        m = re.match(r"^(`{3,})(.*)$", lines[i].strip())
        if m:
            n, info, start = len(m.group(1)), m.group(2).strip(), i
            i += 1
            buf = []
            while i < len(lines) and not re.fullmatch(r"`{%d,}" % n, lines[i].strip()):
                buf.append(lines[i])
                i += 1
            try:
                toks = shlex.split(info)
            except ValueError:
                toks = info.split()
            blocks.append(dict(start=start, end=i, lang=toks[0] if toks else "", toks=toks[1:],
                               code="\n".join(buf), line=start + 1))
        i += 1
    return blocks


def sh(cmd, cwd, stdin=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=TIMEOUT)
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return 127, "", "ferramenta não encontrada: %s" % cmd[0]
    except subprocess.TimeoutExpired:
        return 124, "", "tempo esgotado (%ds)" % TIMEOUT


def subst(cmd, f, d, b):
    cmd = [sys.executable if c == "python3" else c for c in cmd]  # o mesmo Python (e venv) que roda isto
    return [c.replace("{f}", str(f)).replace("{d}", str(d)).replace("{b}", str(b)) for c in cmd]


def clean(text, d):
    """Troca caminhos temporários por nomes estáveis (a saída vira parte do livro)."""
    text = text.replace(str(d) + "/", "").replace(str(d), ".")
    text = re.sub(r"/private/var/folders/\S+?/T/", "", text)
    return text.rstrip("\n")


def verify_block(b, workdir):
    """Retorna (ok, mensagem, saída_capturada, tipo) para um bloco."""
    lang = ALIASES.get(b["lang"], b["lang"])
    r = RUNNERS[lang]
    toks = set(b["toks"])
    opts = dict(t.split("=", 1) for t in b["toks"] if "=" in t)
    name = opts.get("file", "main." + r["ext"])
    f = Path(workdir) / Path(name).name
    f.write_text(b["code"] + "\n", encoding="utf-8")
    binp = Path(workdir) / "prog"
    stdin = opts.get("stdin")

    def compile_step():
        cmd = r.get("build") or r.get("check")
        if not cmd:
            return 0, "", ""
        return sh(subst(cmd, f, workdir, binp), workdir)

    if "test" in toks:
        if not r.get("test"):
            return False, "'test' não é suportado para %s" % lang, "", None
        if lang in ("rust",):
            rc, o, e = sh(subst(r["test"], f, workdir, binp), workdir)
            if rc == 0:
                rc, o, e = sh([str(binp), "--test-threads=1"], workdir)
        else:
            rc, o, e = sh(subst(r["test"], f, workdir, binp), workdir)
        out = clean((o + ("\n" + e if e.strip() else "")).strip(), workdir)
        return (rc == 0, "os testes deveriam passar:\n" + out if rc else "", out, "out")

    if "fail" in toks or "panic" in toks:
        rc, o, e = compile_step()
        if rc != 0:
            if "panic" in toks:
                return False, "compilou? não: deveria compilar e falhar só ao executar:\n" + clean(e or o, workdir), "", None
            return True, "", clean(e or o, workdir), "err"
        rc, o, e = sh(subst(r["run"], f, workdir, binp), workdir, stdin)
        if rc == 0:
            return False, "deveria falhar (compilar ou executar), mas terminou com sucesso", "", None
        return True, "", clean((e or o), workdir), "err"

    rc, o, e = compile_step()
    if rc != 0:
        return False, "não compila:\n" + clean(e or o, workdir), "", None
    if "run" in toks:
        rc, o, e = sh(subst(r["run"], f, workdir, binp), workdir, stdin)
        if rc != 0:
            return False, "falhou ao executar (código %d):\n%s" % (rc, clean(e or o, workdir)), "", None
        return True, "", clean(o, workdir), "out"
    return True, "", "", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--fill", action="store_true", help="reescreve os blocos erro/saida vazios")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    path = Path(a.md)
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks = scan(lines)
    problems, last_err, last_out, edits = 0, None, None, []
    with tempfile.TemporaryDirectory() as td:
        for b in blocks:
            lang = ALIASES.get(b["lang"], b["lang"])
            if lang in ERR_NAMES + OUT_NAMES:
                src = last_err if lang in ERR_NAMES else last_out
                if src is None:
                    print("  linha %d: bloco %s sem fonte anterior (use fail/panic ou run)" % (b["line"], lang))
                    problems += 1
                elif a.fill:
                    edits.append((b["start"], b["end"], b["toks"], lang, src))
                elif b["code"].strip() != src.strip():
                    print("  linha %d: bloco %s difere da saída real (rode com --fill)" % (b["line"], lang))
                    problems += 1
                continue
            if lang not in RUNNERS or "frag" in b["toks"]:
                continue
            ok, msg, out, kind = verify_block(b, td)
            if not ok:
                problems += 1
                print("  linha %d [%s]: %s" % (b["line"], lang, msg))
                last_err = last_out = None  # não deixe o próximo bloco herdar uma saída velha
                continue
            if kind == "err":
                last_err = out
            elif kind == "out":
                last_out = out
            if a.show and out:
                print("--- linha %d (%s) ---\n%s" % (b["line"], lang, out))
    if a.fill and edits:
        for start, end, toks, lang, src in sorted(edits, reverse=True):
            head = lines[start]
            fence = re.match(r"\s*(`{3,})", head).group(1)
            lines[start:end + 1] = [head] + src.split("\n") + [fence]
        path.write_text("\n".join(lines), encoding="utf-8")
        print("  preenchidos %d bloco(s) de erro/saída" % len(edits))
    n = sum(1 for b in blocks if ALIASES.get(b["lang"], b["lang"]) in RUNNERS and "frag" not in b["toks"])
    print("%s: %d bloco(s) de código, %d problema(s)" % (path, n, problems))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
